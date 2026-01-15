#!/usr/bin/env python3
"""
PicConverter CLI - Bildkonvertierungs-Tool mit Kommandozeilen-Interface
"""

import os
import sys
from pathlib import Path
from PIL import Image
import argparse


# Unterstützte Formate
SUPPORTED_FORMATS = {
    'jpg': 'JPEG',
    'jpeg': 'JPEG',
    'png': 'PNG',
    'bmp': 'BMP',
    'tiff': 'TIFF',
    'tif': 'TIFF',
    'gif': 'GIF',
    'webp': 'WebP',
    'ico': 'ICO'
}

# Qualitäts-/Kompressionseinstellungen je Format
QUALITY_SETTINGS = {
    'JPEG': {'min': 1, 'max': 100, 'default': 85, 'name': 'Qualität'},
    'PNG': {'min': 0, 'max': 9, 'default': 6, 'name': 'Kompression'},
    'WebP': {'min': 0, 'max': 100, 'default': 80, 'name': 'Qualität'},
    'TIFF': {'min': 0, 'max': 9, 'default': 6, 'name': 'Kompression'},
}


def get_file_size_mb(filepath):
    """Gibt die Dateigröße in MB zurück"""
    return os.path.getsize(filepath) / (1024 * 1024)


def estimate_output_size(image, output_format, quality, width=None, height=None):
    """
    Schätzt die Größe der Ausgabedatei
    """
    try:
        # Temporäres Bild erstellen
        temp_img = image.copy()
        
        # Auflösung ändern falls angegeben
        if width and height:
            temp_img = temp_img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Temporäre Datei erstellen
        temp_path = Path('/tmp') / f'temp_estimate.{output_format.lower()}'
        
        # Speichern mit entsprechenden Parametern
        save_kwargs = {}
        if output_format == 'JPEG':
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif output_format == 'PNG':
            save_kwargs['compress_level'] = 9 - quality  # Umgekehrt für PNG
        elif output_format == 'WebP':
            save_kwargs['quality'] = quality
        elif output_format == 'TIFF':
            save_kwargs['compression'] = 'tiff_lzw'
        
        temp_img.save(temp_path, format=output_format, **save_kwargs)
        
        # Größe lesen
        size_mb = get_file_size_mb(temp_path)
        
        # Temporäre Datei löschen
        if temp_path.exists():
            temp_path.unlink()
        
        return size_mb
    except Exception as e:
        return None


def convert_image(input_path, output_path, output_format, quality=None, width=None, height=None):
    """
    Konvertiert ein Bild in das gewünschte Format
    """
    try:
        # Bild öffnen
        img = Image.open(input_path)
        
        # RGB konvertieren falls nötig (für Formate die kein RGBA unterstützen)
        if output_format in ['JPEG', 'BMP'] and img.mode in ('RGBA', 'LA', 'P'):
            # Transparenz entfernen
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode not in ('RGB', 'RGBA', 'L', 'P'):
            img = img.convert('RGB')
        
        # Auflösung ändern falls angegeben
        if width and height:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Speichern mit entsprechenden Parametern
        save_kwargs = {}
        if output_format == 'JPEG':
            save_kwargs['quality'] = quality if quality is not None else QUALITY_SETTINGS['JPEG']['default']
            save_kwargs['optimize'] = True
        elif output_format == 'PNG':
            if quality is not None:
                save_kwargs['compress_level'] = 9 - quality
        elif output_format == 'WebP':
            save_kwargs['quality'] = quality if quality is not None else QUALITY_SETTINGS['WebP']['default']
        elif output_format == 'TIFF':
            save_kwargs['compression'] = 'tiff_lzw'
            if quality is not None:
                save_kwargs['compression'] = 'tiff_lzw'
        
        img.save(output_path, format=output_format, **save_kwargs)
        return True, None
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(
        description='PicConverter CLI - Konvertiert Bilder zwischen verschiedenen Formaten',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Unterstützte Formate: {', '.join(SUPPORTED_FORMATS.keys())}

Beispiele:
  %(prog)s bild.jpg -f png -o ausgabe.png
  %(prog)s bild.jpg -f jpg -q 90 -w 1920 --height 1080
  %(prog)s bild.png -f webp -q 85
        """
    )
    
    parser.add_argument('input', help='Pfad zur Eingabedatei')
    parser.add_argument('-f', '--format', '--to', dest='format',
                       choices=list(SUPPORTED_FORMATS.keys()),
                       required=True,
                       help='Zielformat für die Konvertierung')
    parser.add_argument('-o', '--output', dest='output',
                       help='Ausgabedatei (optional, Standard: Eingabename mit neuem Format)')
    parser.add_argument('-q', '--quality', type=int,
                       help='Qualität/Kompression (JPEG/WebP: 1-100, PNG: 0-9)')
    parser.add_argument('-w', '--width', type=int,
                       help='Breite der Ausgabedatei in Pixeln')
    parser.add_argument('--height', type=int,
                       help='Höhe der Ausgabedatei in Pixeln')
    parser.add_argument('--estimate', action='store_true',
                       help='Zeigt geschätzte Ausgabegröße ohne zu konvertieren')
    
    args = parser.parse_args()
    
    # Eingabedatei prüfen
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Fehler: Datei '{input_path}' existiert nicht!", file=sys.stderr)
        sys.exit(1)
    
    # Ausgabedatei bestimmen
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}.{args.format}"
    
    # Format bestimmen
    output_format = SUPPORTED_FORMATS[args.format.lower()]
    
    # Standard-Qualität setzen falls nicht angegeben
    quality = args.quality
    if quality is None:
        if output_format in QUALITY_SETTINGS:
            quality = QUALITY_SETTINGS[output_format]['default']
    
    # Qualität validieren
    if quality is not None and output_format in QUALITY_SETTINGS:
        q_min = QUALITY_SETTINGS[output_format]['min']
        q_max = QUALITY_SETTINGS[output_format]['max']
        if not (q_min <= quality <= q_max):
            print(f"Warnung: Qualität {quality} außerhalb des Bereichs [{q_min}-{q_max}]. "
                  f"Verwende Standardwert.", file=sys.stderr)
            quality = QUALITY_SETTINGS[output_format]['default']
    
    # Bild öffnen für Informationen
    try:
        img = Image.open(input_path)
        original_size = get_file_size_mb(input_path)
        
        print(f"\n{'='*60}")
        print(f"Eingabedatei: {input_path.name}")
        print(f"Originalgröße: {original_size:.2f} MB")
        print(f"Originalauflösung: {img.size[0]}x{img.size[1]} Pixel")
        print(f"Originalformat: {img.format}")
        print(f"{'='*60}\n")
        
        # Zielauflösung
        target_width = args.width or img.size[0]
        target_height = args.height or img.size[1]
        
        if args.width or args.height:
            print(f"Zielauflösung: {target_width}x{target_height} Pixel")
        
        # Qualität anzeigen
        if quality is not None:
            q_name = QUALITY_SETTINGS.get(output_format, {}).get('name', 'Qualität')
            print(f"{q_name}: {quality}")
        
        # Größenprognose
        print(f"\nBerechne Größenprognose...")
        estimated_size = estimate_output_size(img, output_format, quality, target_width, target_height)
        
        if estimated_size is not None:
            print(f"Geschätzte Ausgabegröße: {estimated_size:.2f} MB")
            if original_size > 0:
                compression_ratio = (1 - estimated_size / original_size) * 100
                print(f"Kompression: {compression_ratio:+.1f}%")
        else:
            print("Konnte Größe nicht schätzen.")
        
        # Nur Schätzung anzeigen?
        if args.estimate:
            print("\nNur Schätzung angefordert. Keine Konvertierung durchgeführt.")
            sys.exit(0)
        
        print(f"\nKonvertiere nach: {output_path}")
        print(f"Format: {output_format}\n")
        
        # Konvertierung durchführen
        success, error = convert_image(
            input_path, output_path, output_format,
            quality, target_width, target_height
        )
        
        if success:
            final_size = get_file_size_mb(output_path)
            print(f"✓ Konvertierung erfolgreich!")
            print(f"  Ausgabedatei: {output_path}")
            print(f"  Endgröße: {final_size:.2f} MB")
            if estimated_size:
                diff = abs(final_size - estimated_size)
                print(f"  Abweichung von Schätzung: {diff:.2f} MB")
        else:
            print(f"✗ Fehler bei der Konvertierung: {error}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
