#!/usr/bin/env python3
"""
PicConverter GUI - Bildkonvertierungs-Tool mit grafischer Benutzeroberfläche
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
# Versuche tkinterdnd2 zu importieren (optional für Drag & Drop)
TkinterDnD = None
DND_FILES = None
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    # Teste ob es funktioniert
    try:
        test_root = TkinterDnD.Tk()
        test_root.destroy()
    except (RuntimeError, Exception):
        # tkinterdnd2 ist installiert, aber funktioniert nicht (z.B. Tcl-Version-Konflikt)
        TkinterDnD = None
        DND_FILES = None
except ImportError:
    # tkinterdnd2 ist nicht installiert
    pass
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


class PicConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PicConverter - Bildkonverter")
        self.root.geometry("720x600")
        self.root.resizable(True, True)
        
        self.input_path = None
        self.image = None
        self.preview_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Hauptcontainer - einfache Version ohne Canvas
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid-Konfiguration für Root-Fenster
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Titel
        title_label = ttk.Label(main_frame, text="PicConverter", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Eingabedatei
        input_frame = ttk.LabelFrame(main_frame, text="Eingabedatei", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.input_label = ttk.Label(input_frame, text="Keine Datei ausgewählt")
        self.input_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        ttk.Button(input_frame, text="Datei auswählen", command=self.select_file).grid(row=0, column=1)
        
        # Drag & Drop Bereich hinzufügen
        if TkinterDnD:
            drop_label = tk.Label(input_frame, 
                                 text="📁 Datei hierher ziehen (Drag & Drop)", 
                                 bg="#e0e0e0", 
                                 relief=tk.RAISED,
                                 padx=20, 
                                 pady=10,
                                 font=("Arial", 10))
            drop_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
            
            # Drag & Drop registrieren
            drop_label.drop_target_register(DND_FILES)
            drop_label.dnd_bind('<<Drop>>', self.on_drop)
            
            # Visuelles Feedback beim Überfahren
            def on_enter(event):
                drop_label.config(bg="#c0c0c0", relief=tk.SUNKEN)
            def on_leave(event):
                drop_label.config(bg="#e0e0e0", relief=tk.RAISED)
            
            drop_label.bind("<Enter>", on_enter)
            drop_label.bind("<Leave>", on_leave)
        
        # Bildvorschau
        preview_frame = ttk.LabelFrame(main_frame, text="Vorschau", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.preview_label = ttk.Label(preview_frame, text="Kein Bild geladen", anchor="center")
        self.preview_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Bildinformationen
        info_frame = ttk.LabelFrame(main_frame, text="Bildinformationen", padding="10")
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.info_text = tk.Text(info_frame, height=4, width=60, state=tk.DISABLED)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Konvertierungseinstellungen
        settings_frame = ttk.LabelFrame(main_frame, text="Konvertierungseinstellungen", padding="10")
        settings_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Format
        ttk.Label(settings_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value=list(SUPPORTED_FORMATS.keys())[0])
        format_combo = ttk.Combobox(settings_frame, textvariable=self.format_var,
                                    values=list(SUPPORTED_FORMATS.keys()), state="readonly", width=25)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        # Qualität/Kompression
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.quality_label = ttk.Label(quality_frame, text="Qualität:")
        self.quality_label.grid(row=0, column=0, sticky=tk.W)
        
        self.quality_var = tk.IntVar(value=85)
        self.quality_scale = ttk.Scale(quality_frame, from_=1, to=100, 
                                       orient=tk.HORIZONTAL, variable=self.quality_var,
                                       command=self.on_quality_change)
        self.quality_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        
        self.quality_value_label = ttk.Label(quality_frame, text="85")
        self.quality_value_label.grid(row=0, column=2)
        
        quality_frame.columnconfigure(1, weight=1)
        
        # Auflösung
        resolution_frame = ttk.Frame(settings_frame)
        resolution_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(resolution_frame, text="Auflösung:").grid(row=0, column=0, sticky=tk.W)
        
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        
        ttk.Label(resolution_frame, text="Breite:").grid(row=0, column=1, padx=(10, 5))
        width_entry = ttk.Entry(resolution_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=2, padx=5)
        
        ttk.Label(resolution_frame, text="Höhe:").grid(row=0, column=3, padx=(10, 5))
        height_entry = ttk.Entry(resolution_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=0, column=4, padx=5)
        
        ttk.Label(resolution_frame, text="Pixel").grid(row=0, column=5, padx=5)
        
        self.aspect_ratio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(resolution_frame, text="Seitenverhältnis beibehalten",
                       variable=self.aspect_ratio_var).grid(row=1, column=1, columnspan=5, sticky=tk.W, pady=5)
        
        # Größenprognose
        estimate_frame = ttk.Frame(settings_frame)
        estimate_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.estimate_label = ttk.Label(estimate_frame, text="Geschätzte Ausgabegröße: -- MB", 
                                        font=("Arial", 10, "bold"))
        self.estimate_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(estimate_frame, text="Größe schätzen", command=self.estimate_size).grid(row=0, column=1, padx=10)
        
        # Ausgabedatei
        output_frame = ttk.LabelFrame(main_frame, text="Ausgabedatei", padding="10")
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.output_label = ttk.Label(output_frame, text="Automatisch generiert")
        self.output_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        ttk.Button(output_frame, text="Speicherort wählen", command=self.select_output).grid(row=0, column=1)
        
        # Konvertieren Button
        self.convert_button = ttk.Button(main_frame, text="Konvertieren", command=self.convert_image,
                                        state=tk.DISABLED)
        self.convert_button.grid(row=6, column=0, columnspan=2, pady=20)
        
        # Statusleiste
        self.status_var = tk.StringVar(value="Bereit")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Spalten konfigurieren
        main_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        
        # Initiale Format-Einstellung
        self.on_format_change()
        
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
    
    def on_drop(self, event):
        """Verarbeitet Drag & Drop Events"""
        if not TkinterDnD:
            messagebox.showwarning("Warnung", "Drag & Drop ist nicht verfügbar. Bitte installieren Sie tkinterdnd2.")
            return
        
        # Dateipfad aus dem Event extrahieren
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = Path(files[0])
            
            # Prüfen ob es eine Bilddatei ist
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp', '.ico'}
            if file_path.suffix.lower() in image_extensions:
                if file_path.exists():
                    self.input_path = file_path
                    self.load_image()
                else:
                    messagebox.showerror("Fehler", f"Datei existiert nicht: {file_path}")
            else:
                messagebox.showwarning("Warnung", f"Keine unterstützte Bilddatei: {file_path.name}\n\nUnterstützte Formate: {', '.join(image_extensions)}")
            
    def load_image(self):
        try:
            self.image = Image.open(self.input_path)
            
            # Bildinformationen anzeigen
            info = f"Datei: {self.input_path.name}\n"
            info += f"Größe: {os.path.getsize(self.input_path) / (1024*1024):.2f} MB\n"
            info += f"Auflösung: {self.image.size[0]}x{self.image.size[1]} Pixel\n"
            info += f"Format: {self.image.format}"
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            self.info_text.config(state=tk.DISABLED)
            
            # Vorschau erstellen
            preview_size = (300, 200)
            preview_img = self.image.copy()
            preview_img.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            # Stelle sicher, dass das Fenster existiert bevor ImageTk verwendet wird
            self.root.update_idletasks()
            self.preview_image = ImageTk.PhotoImage(preview_img)
            self.preview_label.config(image=self.preview_image, text="")
            # Wichtig: Referenz behalten, damit das Bild nicht garbage collected wird
            self.preview_label.image = self.preview_image
            
            # Eingabelabel aktualisieren
            self.input_label.config(text=self.input_path.name)
            
            # Standardauflösung setzen
            self.width_var.set(str(self.image.size[0]))
            self.height_var.set(str(self.image.size[1]))
            
            # Konvertieren-Button aktivieren
            self.convert_button.config(state=tk.NORMAL)
            
            # Ausgabedatei aktualisieren
            self.update_output_path()
            
            self.status_var.set("Bild geladen")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes:\n{e}")
            self.status_var.set("Fehler beim Laden")
    
    def on_format_change(self, event=None):
        format_name = self.format_var.get()
        output_format = SUPPORTED_FORMATS[format_name]
        
        # Qualitätsskala anpassen
        if output_format in QUALITY_SETTINGS:
            settings = QUALITY_SETTINGS[output_format]
            self.quality_scale.config(from_=settings['min'], to=settings['max'])
            self.quality_var.set(settings['default'])
            self.quality_label.config(text=f"{settings['name']}:")
            self.on_quality_change()
        else:
            self.quality_label.config(text="Qualität: (nicht verfügbar)")
            self.quality_value_label.config(text="--")
        
        # Ausgabepfad aktualisieren
        self.update_output_path()
        
    def on_quality_change(self, event=None):
        value = int(self.quality_var.get())
        self.quality_value_label.config(text=str(value))
        
    def update_output_path(self):
        if self.input_path:
            format_name = self.format_var.get()
            # Dateierweiterung extrahieren
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
            
            # Qualität
            quality = int(self.quality_var.get()) if output_format in QUALITY_SETTINGS else None
            
            # Auflösung
            width = None
            height = None
            try:
                if self.width_var.get():
                    width = int(self.width_var.get())
                if self.height_var.get():
                    height = int(self.height_var.get())
            except ValueError:
                pass
            
            # Größe schätzen
            estimated_size = self.calculate_estimated_size(self.image, output_format, quality, width, height)
            
            if estimated_size is not None:
                original_size = os.path.getsize(self.input_path) / (1024 * 1024)
                self.estimate_label.config(
                    text=f"Geschätzte Ausgabegröße: {estimated_size:.2f} MB "
                         f"(Original: {original_size:.2f} MB)"
                )
                if original_size > 0:
                    compression = (1 - estimated_size / original_size) * 100
                    self.status_var.set(f"Schätzung: {compression:+.1f}% Kompression")
            else:
                self.estimate_label.config(text="Konnte Größe nicht schätzen")
                self.status_var.set("Fehler bei Größenberechnung")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Größenberechnung:\n{e}")
    
    def calculate_estimated_size(self, image, output_format, quality, width=None, height=None):
        """Schätzt die Ausgabegröße"""
        try:
            import tempfile
            
            temp_img = image.copy()
            
            # Auflösung ändern
            if width and height:
                temp_img = temp_img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Temporäre Datei
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format.lower()}') as tmp:
                temp_path = tmp.name
            
            # Speichern
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
            
            # Größe lesen
            size_mb = os.path.getsize(temp_path) / (1024 * 1024)
            
            # Löschen
            os.unlink(temp_path)
            
            return size_mb
        except Exception:
            return None
    
    def convert_image(self):
        if not self.image:
            messagebox.showwarning("Warnung", "Bitte wählen Sie zuerst eine Eingabedatei aus.")
            return
        
        # In separatem Thread ausführen, damit UI nicht einfriert
        self.convert_button.config(state=tk.DISABLED)
        self.status_var.set("Konvertiere...")
        
        thread = threading.Thread(target=self._convert_thread)
        thread.daemon = True
        thread.start()
    
    def _convert_thread(self):
        try:
            format_name = self.format_var.get()
            output_format = SUPPORTED_FORMATS[format_name]
            
            # Qualität
            quality = None
            if output_format in QUALITY_SETTINGS:
                quality = int(self.quality_var.get())
            
            # Auflösung
            width = None
            height = None
            try:
                if self.width_var.get():
                    width = int(self.width_var.get())
                if self.height_var.get():
                    height = int(self.height_var.get())
            except ValueError:
                pass
            
            # Seitenverhältnis beibehalten
            if self.aspect_ratio_var.get() and width and height and self.image:
                original_ratio = self.image.size[0] / self.image.size[1]
                if width / height != original_ratio:
                    # Breite anpassen
                    width = int(height * original_ratio)
            
            # Konvertierung
            success, error = self.perform_conversion(
                self.input_path, self.output_path, output_format,
                quality, width, height
            )
            
            if success:
                final_size = os.path.getsize(self.output_path) / (1024 * 1024)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Erfolg",
                    f"Konvertierung erfolgreich!\n\n"
                    f"Ausgabedatei: {self.output_path.name}\n"
                    f"Größe: {final_size:.2f} MB"
                ))
                self.root.after(0, lambda: self.status_var.set("Konvertierung abgeschlossen"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Fehler bei der Konvertierung:\n{error}"))
                self.root.after(0, lambda: self.status_var.set("Fehler bei Konvertierung"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"Unerwarteter Fehler:\n{e}"))
            self.root.after(0, lambda: self.status_var.set("Fehler"))
        finally:
            self.root.after(0, lambda: self.convert_button.config(state=tk.NORMAL))
    
    def perform_conversion(self, input_path, output_path, output_format, quality=None, width=None, height=None):
        """Führt die Konvertierung durch"""
        try:
            img = Image.open(input_path)
            
            # RGB konvertieren falls nötig
            if output_format in ['JPEG', 'BMP'] and img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode not in ('RGB', 'RGBA', 'L', 'P'):
                img = img.convert('RGB')
            
            # Auflösung ändern
            if width and height:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Speichern
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
    # Verwende TkinterDnD wenn verfügbar und funktionsfähig, sonst normales Tk
    if TkinterDnD:
        try:
            root = TkinterDnD.Tk()
        except (RuntimeError, Exception) as e:
            print(f"Warnung: Drag & Drop nicht verfügbar ({e}). Verwende normale GUI.", file=sys.stderr)
            root = tk.Tk()
    else:
        root = tk.Tk()
    app = PicConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
