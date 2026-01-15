#!/usr/bin/env python3
"""
PicConverter GUI - Modernes Bildkonvertierungs-Tool
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image
try:
    from PIL import ImageTk
except ImportError:
    print("Fehler: ImageTk konnte nicht importiert werden.", file=sys.stderr)
    print("\nBitte installieren Sie das python3-pillow-tk Paket:", file=sys.stderr)
    print("  sudo dnf install python3-pillow-tk", file=sys.stderr)
    print("\nOder mit pip:", file=sys.stderr)
    print("  pip install Pillow[tk]", file=sys.stderr)
    sys.exit(1)
import threading


# Unterstützte Formate
SUPPORTED_FORMATS = {
    'JPEG (.jpg, .jpeg)': 'JPEG',
    'PNG (.png)': 'PNG',
    'BMP (.bmp)': 'BMP',
    'TIFF (.tiff, .tif)': 'TIFF',
    'GIF (.gif)': 'GIF',
    'WebP (.webp)': 'WebP',
    'ICO (.ico)': 'ICO'
}

# Qualitäts-/Kompressionseinstellungen je Format
QUALITY_SETTINGS = {
    'JPEG': {'min': 1, 'max': 100, 'default': 85, 'name': 'Qualität'},
    'PNG': {'min': 0, 'max': 9, 'default': 6, 'name': 'Kompression'},
    'WebP': {'min': 0, 'max': 100, 'default': 80, 'name': 'Qualität'},
    'TIFF': {'min': 0, 'max': 9, 'default': 6, 'name': 'Kompression'},
}

# Modernes Farbschema
COLORS = {
    'bg': '#1e1e2e',           # Dunkler Hintergrund
    'fg': '#cdd6f4',           # Heller Text
    'accent': '#89b4fa',       # Akzentfarbe (Blau)
    'accent_hover': '#74c7ec', # Akzent Hover
    'secondary': '#313244',    # Sekundärer Hintergrund
    'tertiary': '#45475a',     # Tertiärer Hintergrund
    'success': '#a6e3a1',      # Erfolgsfarbe (Grün)
    'error': '#f38ba8',        # Fehlerfarbe (Rot)
    'warning': '#f9e2af',      # Warnfarbe (Gelb)
    'border': '#585b70',       # Rahmenfarbe
}


class ModernButton(tk.Canvas):
    """Moderner Button mit Hover-Effekt"""
    def __init__(self, parent, text, command=None, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        
        # Standard-Größen
        self.config(width=kwargs.get('width', 140), height=kwargs.get('height', 40))
        self.bg_color = kwargs.get('bg', COLORS['accent'])
        self.hover_color = kwargs.get('hover_bg', COLORS['accent_hover'])
        self.fg_color = kwargs.get('fg', COLORS['bg'])
        
        self.draw_button()
        
        # Events
        self.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def draw_button(self, hover=False):
        self.delete('all')
        color = self.hover_color if hover else self.bg_color
        
        # Abgerundetes Rechteck
        x0, y0 = 0, 0
        x1, y1 = self.winfo_reqwidth(), self.winfo_reqheight()
        radius = 8
        
        self.create_arc(x0, y0, x0+radius*2, y0+radius*2, start=90, extent=90, fill=color, outline=color)
        self.create_arc(x1-radius*2, y0, x1, y0+radius*2, start=0, extent=90, fill=color, outline=color)
        self.create_arc(x0, y1-radius*2, x0+radius*2, y1, start=180, extent=90, fill=color, outline=color)
        self.create_arc(x1-radius*2, y1-radius*2, x1, y1, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(x0+radius, y0, x1-radius, y1, fill=color, outline=color)
        self.create_rectangle(x0, y0+radius, x1, y1-radius, fill=color, outline=color)
        
        # Text
        self.create_text(x1/2, y1/2, text=self.text, fill=self.fg_color, 
                        font=('Segoe UI', 10, 'bold'))
        
    def on_click(self, event):
        if self.command:
            self.command()
    
    def on_enter(self, event):
        self.draw_button(hover=True)
    
    def on_leave(self, event):
        self.draw_button(hover=False)


class PicConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PicConverter - Moderner Bildkonverter")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Dunkles Theme
        self.root.configure(bg=COLORS['bg'])
        
        self.input_path = None
        self.image = None
        self.preview_image = None
        self.output_path = None
        
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Konfiguriert moderne Styles"""
        style = ttk.Style()
        
        # Theme
        style.theme_use('clam')
        
        # Allgemeine Konfiguration
        style.configure('.', background=COLORS['bg'], foreground=COLORS['fg'],
                       fieldbackground=COLORS['secondary'], borderwidth=0)
        
        # Label
        style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['fg'],
                       font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'),
                       foreground=COLORS['accent'])
        style.configure('Subtitle.TLabel', font=('Segoe UI', 11),
                       foreground=COLORS['fg'])
        
        # Frame
        style.configure('TFrame', background=COLORS['bg'])
        style.configure('Card.TFrame', background=COLORS['secondary'], relief='flat')
        
        # LabelFrame
        style.configure('TLabelframe', background=COLORS['bg'],
                       foreground=COLORS['accent'], borderwidth=2,
                       relief='solid', bordercolor=COLORS['border'])
        style.configure('TLabelframe.Label', background=COLORS['bg'],
                       foreground=COLORS['accent'], font=('Segoe UI', 11, 'bold'))
        
        # Entry
        style.configure('TEntry', fieldbackground=COLORS['secondary'],
                       foreground=COLORS['fg'], borderwidth=1,
                       relief='solid', insertcolor=COLORS['fg'])
        
        # Combobox
        style.configure('TCombobox', fieldbackground=COLORS['secondary'],
                       foreground=COLORS['fg'], background=COLORS['secondary'],
                       selectbackground=COLORS['accent'],
                       selectforeground=COLORS['bg'], arrowcolor=COLORS['accent'])
        
        # Scale
        style.configure('TScale', background=COLORS['bg'],
                       troughcolor=COLORS['secondary'], borderwidth=0,
                       sliderthickness=20, sliderlength=30)
        
        # Checkbutton
        style.configure('TCheckbutton', background=COLORS['bg'],
                       foreground=COLORS['fg'], font=('Segoe UI', 10))
        
    def setup_ui(self):
        # Canvas mit Scrollbar
        canvas = tk.Canvas(self.root, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas_width)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        main_frame = scrollable_frame
        main_frame.configure(padding="20")
        
        # Mausrad-Scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        canvas.bind_all("<Button-4>", _on_mousewheel_linux)
        canvas.bind_all("<Button-5>", _on_mousewheel_linux)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 30))
        
        title_label = ttk.Label(header_frame, text="🖼️ PicConverter", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(header_frame, text="Moderner Bildkonverter",
                                   style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Eingabedatei Card
        input_card = self.create_card(main_frame, "📁 Eingabedatei")
        input_card.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        input_content = ttk.Frame(input_card)
        input_content.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=15)
        
        self.input_label = ttk.Label(input_content, text="Keine Datei ausgewählt",
                                     foreground=COLORS['fg'])
        self.input_label.grid(row=0, column=0, sticky=tk.W)
        
        select_btn = ModernButton(input_content, "Datei auswählen",
                                 command=self.select_file, width=150)
        select_btn.grid(row=0, column=1, padx=(20, 0))
        
        input_content.columnconfigure(0, weight=1)
        
        # Vorschau Card
        preview_card = self.create_card(main_frame, "👁️ Vorschau")
        preview_card.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        preview_content = ttk.Frame(preview_card)
        preview_content.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=15)
        
        self.preview_frame = tk.Frame(preview_content, bg=COLORS['tertiary'],
                                      highlightthickness=2,
                                      highlightbackground=COLORS['border'])
        self.preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.preview_label = tk.Label(self.preview_frame, text="Kein Bild geladen",
                                     bg=COLORS['tertiary'], fg=COLORS['fg'],
                                     font=('Segoe UI', 12), pady=60)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        preview_content.columnconfigure(0, weight=1)
        
        # Bildinformationen
        info_card = self.create_card(main_frame, "ℹ️ Bildinformationen")
        info_card.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        info_content = ttk.Frame(info_card)
        info_content.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=15)
        
        self.info_text = tk.Text(info_content, height=4, width=60,
                                bg=COLORS['tertiary'], fg=COLORS['fg'],
                                font=('Consolas', 9), relief='flat',
                                state=tk.DISABLED, padx=10, pady=10,
                                highlightthickness=1,
                                highlightbackground=COLORS['border'])
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        info_content.columnconfigure(0, weight=1)
        
        # Einstellungen Card
        settings_card = self.create_card(main_frame, "⚙️ Konvertierungseinstellungen")
        settings_card.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        settings_content = ttk.Frame(settings_card)
        settings_content.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=15)
        
        # Format
        format_frame = ttk.Frame(settings_content)
        format_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(format_frame, text="Ausgabeformat:").grid(row=0, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value=list(SUPPORTED_FORMATS.keys())[0])
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=list(SUPPORTED_FORMATS.keys()),
                                   state="readonly", width=30)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        # Qualität
        quality_frame = ttk.Frame(settings_content)
        quality_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.quality_label = ttk.Label(quality_frame, text="Qualität:")
        self.quality_label.grid(row=0, column=0, sticky=tk.W)
        
        self.quality_var = tk.IntVar(value=85)
        self.quality_scale = ttk.Scale(quality_frame, from_=1, to=100,
                                      orient=tk.HORIZONTAL, variable=self.quality_var,
                                      command=self.on_quality_change)
        self.quality_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        
        self.quality_value_label = ttk.Label(quality_frame, text="85",
                                            foreground=COLORS['accent'],
                                            font=('Segoe UI', 10, 'bold'))
        self.quality_value_label.grid(row=0, column=2)
        
        quality_frame.columnconfigure(1, weight=1)
        
        # Auflösung
        resolution_frame = ttk.Frame(settings_content)
        resolution_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(resolution_frame, text="Auflösung:").grid(row=0, column=0, sticky=tk.W)
        
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        
        ttk.Label(resolution_frame, text="Breite:").grid(row=0, column=1, padx=(15, 5))
        width_entry = ttk.Entry(resolution_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=2, padx=5)
        
        ttk.Label(resolution_frame, text="×").grid(row=0, column=3, padx=5)
        
        ttk.Label(resolution_frame, text="Höhe:").grid(row=0, column=4, padx=(5, 5))
        height_entry = ttk.Entry(resolution_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=0, column=5, padx=5)
        
        ttk.Label(resolution_frame, text="px").grid(row=0, column=6, padx=(5, 0))
        
        self.aspect_ratio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(resolution_frame, text="Seitenverhältnis beibehalten",
                       variable=self.aspect_ratio_var).grid(row=1, column=1, columnspan=6,
                                                           sticky=tk.W, pady=(10, 0))
        
        # Größenschätzung
        estimate_frame = ttk.Frame(settings_content)
        estimate_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.estimate_label = ttk.Label(estimate_frame,
                                       text="Geschätzte Ausgabegröße: -- MB",
                                       foreground=COLORS['warning'],
                                       font=('Segoe UI', 10, 'bold'))
        self.estimate_label.grid(row=0, column=0, sticky=tk.W)
        
        estimate_btn = ModernButton(estimate_frame, "Größe schätzen",
                                   command=self.estimate_size, width=150,
                                   bg=COLORS['tertiary'], hover_bg=COLORS['border'])
        estimate_btn.grid(row=0, column=1, padx=(15, 0))
        
        estimate_frame.columnconfigure(0, weight=1)
        settings_content.columnconfigure(0, weight=1)
        
        # Ausgabe Card
        output_card = self.create_card(main_frame, "💾 Ausgabedatei")
        output_card.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        output_content = ttk.Frame(output_card)
        output_content.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=15)
        
        self.output_label = ttk.Label(output_content, text="Automatisch generiert",
                                      foreground=COLORS['fg'])
        self.output_label.grid(row=0, column=0, sticky=tk.W)
        
        output_btn = ModernButton(output_content, "Speicherort wählen",
                                command=self.select_output, width=170)
        output_btn.grid(row=0, column=1, padx=(20, 0))
        
        output_content.columnconfigure(0, weight=1)
        
        # Konvertieren Button
        self.convert_button = ModernButton(main_frame, "🚀 Konvertieren starten",
                                          command=self.convert_image,
                                          width=300, height=50,
                                          bg=COLORS['success'],
                                          hover_bg='#94e2d5')
        self.convert_button.grid(row=6, column=0, pady=20)
        self.convert_button_enabled = False
        self.update_convert_button_state()
        
        # Statusleiste
        status_frame = tk.Frame(main_frame, bg=COLORS['secondary'],
                               height=40, relief='flat')
        status_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.grid_propagate(False)
        
        self.status_var = tk.StringVar(value="Bereit")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               bg=COLORS['secondary'], fg=COLORS['accent'],
                               font=('Segoe UI', 9), anchor=tk.W, padx=15)
        status_label.pack(fill=tk.BOTH, expand=True)
        
        main_frame.columnconfigure(0, weight=1)
        
        # Initiale Format-Einstellung
        self.on_format_change()
    
    def create_card(self, parent, title):
        """Erstellt eine Card mit Titel"""
        card = ttk.Frame(parent, style='Card.TFrame', relief='flat')
        card.configure(borderwidth=1, relief='solid')
        
        # Titel
        title_frame = tk.Frame(card, bg=COLORS['tertiary'], height=40)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        title_frame.grid_propagate(False)
        
        title_label = tk.Label(title_frame, text=title, bg=COLORS['tertiary'],
                              fg=COLORS['accent'], font=('Segoe UI', 12, 'bold'),
                              anchor=tk.W, padx=20)
        title_label.pack(fill=tk.BOTH, expand=True)
        
        # Content-Frame wird vom Aufrufer gefüllt
        card.columnconfigure(0, weight=1)
        
        return card
    
    def update_convert_button_state(self):
        """Aktualisiert den Zustand des Konvertieren-Buttons"""
        if self.convert_button_enabled:
            self.convert_button.config(bg=COLORS['success'], state='normal')
        else:
            self.convert_button.config(bg=COLORS['border'], state='disabled')
    
    def select_file(self):
        filetypes = [
            ("Alle Bilder", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.gif *.webp *.ico"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff *.tif"),
            ("GIF", "*.gif"),
            ("WebP", "*.webp"),
            ("ICO", "*.ico"),
            ("Alle Dateien", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Bild auswählen",
            filetypes=filetypes
        )
        
        if filename:
            self.input_path = Path(filename)
            self.load_image()
    
    def load_image(self):
        try:
            self.image = Image.open(self.input_path)
            
            # Bildinformationen
            info = f"📄 Datei: {self.input_path.name}\n"
            info += f"💾 Größe: {os.path.getsize(self.input_path) / (1024*1024):.2f} MB\n"
            info += f"📐 Auflösung: {self.image.size[0]} × {self.image.size[1]} Pixel\n"
            info += f"🎨 Format: {self.image.format}"
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            self.info_text.config(state=tk.DISABLED)
            
            # Vorschau
            preview_size = (400, 300)
            preview_img = self.image.copy()
            preview_img.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            self.preview_image = ImageTk.PhotoImage(preview_img)
            self.preview_label.config(image=self.preview_image, text="", bg=COLORS['tertiary'])
            
            # Eingabelabel
            short_name = self.input_path.name
            if len(short_name) > 40:
                short_name = short_name[:37] + "..."
            self.input_label.config(text=f"✓ {short_name}",
                                   foreground=COLORS['success'])
            
            # Standardauflösung
            self.width_var.set(str(self.image.size[0]))
            self.height_var.set(str(self.image.size[1]))
            
            # Button aktivieren
            self.convert_button_enabled = True
            self.update_convert_button_state()
            
            # Ausgabedatei
            self.update_output_path()
            
            self.status_var.set("✓ Bild erfolgreich geladen")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes:\n{e}")
            self.status_var.set("✗ Fehler beim Laden")
    
    def on_format_change(self, event=None):
        format_name = self.format_var.get()
        output_format = SUPPORTED_FORMATS[format_name]
        
        if output_format in QUALITY_SETTINGS:
            settings = QUALITY_SETTINGS[output_format]
            self.quality_scale.config(from_=settings['min'], to=settings['max'])
            self.quality_var.set(settings['default'])
            self.quality_label.config(text=f"{settings['name']}:")
            self.on_quality_change()
        else:
            self.quality_label.config(text="Qualität: (nicht verfügbar)")
            self.quality_value_label.config(text="--")
        
        self.update_output_path()
    
    def on_quality_change(self, event=None):
        value = int(self.quality_var.get())
        self.quality_value_label.config(text=str(value))
    
    def update_output_path(self):
        if self.input_path:
            format_name = self.format_var.get()
            ext_map = {
                'JPEG (.jpg, .jpeg)': '.jpg',
                'PNG (.png)': '.png',
                'BMP (.bmp)': '.bmp',
                'TIFF (.tiff, .tif)': '.tiff',
                'GIF (.gif)': '.gif',
                'WebP (.webp)': '.webp',
                'ICO (.ico)': '.ico'
            }
            ext = ext_map.get(format_name, '.jpg')
            output_name = self.input_path.stem + ext
            self.output_label.config(text=output_name)
            self.output_path = self.input_path.parent / output_name
    
    def select_output(self):
        if not self.input_path:
            messagebox.showwarning("Warnung", "Bitte wählen Sie zuerst eine Eingabedatei aus.")
            return
        
        format_name = self.format_var.get()
        ext_map = {
            'JPEG (.jpg, .jpeg)': '.jpg',
            'PNG (.png)': '.png',
            'BMP (.bmp)': '.bmp',
            'TIFF (.tiff, .tif)': '.tiff',
            'GIF (.gif)': '.gif',
            'WebP (.webp)': '.webp',
            'ICO (.ico)': '.ico'
        }
        ext = ext_map.get(format_name, '.jpg')
        
        filename = filedialog.asksaveasfilename(
            title="Ausgabedatei speichern",
            defaultextension=ext,
            filetypes=[(format_name, f"*{ext}"), ("Alle Dateien", "*.*")]
        )
        
        if filename:
            self.output_path = Path(filename)
            self.output_label.config(text=self.output_path.name)
    
    def estimate_size(self):
        if not self.image:
            messagebox.showwarning("Warnung", "Bitte wählen Sie zuerst eine Eingabedatei aus.")
            return
        
        try:
            format_name = self.format_var.get()
            output_format = SUPPORTED_FORMATS[format_name]
            
            quality = int(self.quality_var.get()) if output_format in QUALITY_SETTINGS else None
            
            width = None
            height = None
            try:
                if self.width_var.get():
                    width = int(self.width_var.get())
                if self.height_var.get():
                    height = int(self.height_var.get())
            except ValueError:
                pass
            
            estimated_size = self.calculate_estimated_size(self.image, output_format,
                                                          quality, width, height)
            
            if estimated_size is not None:
                original_size = os.path.getsize(self.input_path) / (1024 * 1024)
                self.estimate_label.config(
                    text=f"Geschätzte Ausgabegröße: {estimated_size:.2f} MB "
                         f"(Original: {original_size:.2f} MB)"
                )
                if original_size > 0:
                    compression = (1 - estimated_size / original_size) * 100
                    if compression > 0:
                        self.status_var.set(f"📉 Schätzung: -{compression:.1f}% kleiner")
                    else:
                        self.status_var.set(f"📈 Schätzung: +{abs(compression):.1f}% größer")
            else:
                self.estimate_label.config(text="Konnte Größe nicht schätzen")
                self.status_var.set("✗ Fehler bei Größenberechnung")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Größenberechnung:\n{e}")
    
    def calculate_estimated_size(self, image, output_format, quality, width=None, height=None):
        try:
            import tempfile
            
            temp_img = image.copy()
            
            if width and height:
                temp_img = temp_img.resize((width, height), Image.Resampling.LANCZOS)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format.lower()}') as tmp:
                temp_path = tmp.name
            
            save_kwargs = {}
            if output_format == 'JPEG':
                save_kwargs['quality'] = quality if quality else 85
                save_kwargs['optimize'] = True
            elif output_format == 'PNG':
                if quality is not None:
                    save_kwargs['compress_level'] = 9 - quality
            elif output_format == 'WebP':
                save_kwargs['quality'] = quality if quality else 80
            elif output_format == 'TIFF':
                save_kwargs['compression'] = 'tiff_lzw'
            
            temp_img.save(temp_path, format=output_format, **save_kwargs)
            
            size_mb = os.path.getsize(temp_path) / (1024 * 1024)
            
            os.unlink(temp_path)
            
            return size_mb
        except Exception:
            return None
    
    def convert_image(self):
        if not self.image:
            messagebox.showwarning("Warnung", "Bitte wählen Sie zuerst eine Eingabedatei aus.")
            return
        
        self.convert_button_enabled = False
        self.update_convert_button_state()
        self.status_var.set("⏳ Konvertiere...")
        
        thread = threading.Thread(target=self._convert_thread)
        thread.daemon = True
        thread.start()
    
    def _convert_thread(self):
        try:
            format_name = self.format_var.get()
            output_format = SUPPORTED_FORMATS[format_name]
            
            quality = None
            if output_format in QUALITY_SETTINGS:
                quality = int(self.quality_var.get())
            
            width = None
            height = None
            try:
                if self.width_var.get():
                    width = int(self.width_var.get())
                if self.height_var.get():
                    height = int(self.height_var.get())
            except ValueError:
                pass
            
            if self.aspect_ratio_var.get() and width and height and self.image:
                original_ratio = self.image.size[0] / self.image.size[1]
                if width / height != original_ratio:
                    width = int(height * original_ratio)
            
            success, error = self.perform_conversion(
                self.input_path, self.output_path, output_format,
                quality, width, height
            )
            
            if success:
                final_size = os.path.getsize(self.output_path) / (1024 * 1024)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Erfolg",
                    f"✓ Konvertierung erfolgreich!\n\n"
                    f"📁 Ausgabedatei: {self.output_path.name}\n"
                    f"💾 Größe: {final_size:.2f} MB"
                ))
                self.root.after(0, lambda: self.status_var.set("✓ Konvertierung abgeschlossen"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Fehler",
                                                                f"Fehler bei der Konvertierung:\n{error}"))
                self.root.after(0, lambda: self.status_var.set("✗ Fehler bei Konvertierung"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"Unerwarteter Fehler:\n{e}"))
            self.root.after(0, lambda: self.status_var.set("✗ Fehler"))
        finally:
            self.convert_button_enabled = True
            self.root.after(0, self.update_convert_button_state)
    
    def perform_conversion(self, input_path, output_path, output_format,
                          quality=None, width=None, height=None):
        try:
            img = Image.open(input_path)
            
            if output_format in ['JPEG', 'BMP'] and img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode not in ('RGB', 'RGBA', 'L', 'P'):
                img = img.convert('RGB')
            
            if width and height:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            save_kwargs = {}
            if output_format == 'JPEG':
                save_kwargs['quality'] = quality if quality else 85
                save_kwargs['optimize'] = True
            elif output_format == 'PNG':
                if quality is not None:
                    save_kwargs['compress_level'] = 9 - quality
            elif output_format == 'WebP':
                save_kwargs['quality'] = quality if quality else 80
            elif output_format == 'TIFF':
                save_kwargs['compression'] = 'tiff_lzw'
            
            img.save(output_path, format=output_format, **save_kwargs)
            return True, None
        except Exception as e:
            return False, str(e)


def main():
    root = tk.Tk()
    app = PicConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()