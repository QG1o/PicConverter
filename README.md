# PicConverter

Ein vielseitiges Bildkonvertierungs-Tool für Python, das sowohl über die Kommandozeile (CLI) als auch über eine grafische Benutzeroberfläche (GUI) verfügt.

## Features

- ✅ **Unterstützung für alle gängigen Bildformate**: JPEG, PNG, BMP, TIFF, GIF, WebP, ICO
- ✅ **Anpassbare Qualität/Kompression**: Optimieren Sie die Dateigröße nach Ihren Bedürfnissen
- ✅ **Auflösungsänderung**: Passen Sie die Bildgröße an
- ✅ **Größenprognose**: Sehen Sie die geschätzte Ausgabegröße vor der Konvertierung
- ✅ **Modernes Design**: Dunkles Theme mit intuitiver Benutzeroberfläche
- ✅ **Zwei Benutzeroberflächen**: CLI für Automatisierung und GUI für einfache Bedienung

## Installation

### Systemanforderungen

- Python 3.7 oder höher
- tkinter (meist bereits mit Python installiert)

### Installationsschritte

1. Repository klonen:
```bash
git clone https://github.com/QG1o/PicConverter.git
cd PicConverter
```

2. Systempakete installieren (für GUI-Version erforderlich):

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install python3-pillow python3-pillow-tk python3-tkinter
```

**Debian/Ubuntu:**
```bash
sudo apt-get install python3-pil python3-pil.imagetk python3-tk
```

**Arch Linux:**
```bash
sudo pacman -S python-pillow tk
```

**macOS (mit Homebrew):**
```bash
brew install python-tk
pip3 install Pillow
```

**Windows:**
- Python sollte bereits tkinter enthalten
- Installieren Sie Pillow mit: `pip install Pillow`

3. Python-Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

**Hinweis:** Für die GUI-Version wird zusätzlich `python3-pillow-tk` (oder `python3-pil.imagetk`) benötigt, damit die Bildvorschau funktioniert.

## Verwendung

### GUI-Version

Starten Sie die grafische Benutzeroberfläche:

```bash
python picconverter_gui.py
```

**Bedienung:**
1. Klicken Sie auf "Datei auswählen" und wählen Sie ein Bild aus
2. Wählen Sie das gewünschte Ausgabeformat
3. Passen Sie die Qualität/Kompression an (falls verfügbar)
4. Geben Sie optional eine neue Auflösung ein
5. Klicken Sie auf "Größe schätzen" für eine Prognose
6. Klicken Sie auf "🚀 Konvertieren starten"

**Design:**
- Modernes dunkles Theme für angenehme Augen
- Card-basierte Benutzeroberfläche für bessere Übersicht
- Intuitive Bedienung mit visuellen Feedback-Elementen

### CLI-Version

Verwenden Sie die Kommandozeilen-Version für Automatisierung oder Skripte:

```bash
python picconverter_cli.py <eingabedatei> -f <format> [optionen]
```

**Beispiele:**

```bash
# Einfache Konvertierung von JPG zu PNG
python picconverter_cli.py bild.jpg -f png

# Konvertierung mit angepasster Qualität
python picconverter_cli.py bild.jpg -f jpg -q 90

# Konvertierung mit neuer Auflösung
python picconverter_cli.py bild.jpg -f png -w 1920 --height 1080

# Nur Größenprognose anzeigen (ohne Konvertierung)
python picconverter_cli.py bild.jpg -f webp -q 85 --estimate

# Alle Optionen kombiniert
python picconverter_cli.py bild.png -f jpg -q 90 -w 1920 --height 1080 -o ausgabe.jpg
```

**Verfügbare Optionen:**

- `-f, --format`: Zielformat (jpg, jpeg, png, bmp, tiff, tif, gif, webp, ico)
- `-o, --output`: Ausgabedatei (optional, Standard: Eingabename mit neuem Format)
- `-q, --quality`: Qualität/Kompression
  - JPEG/WebP: 1-100 (Standard: 85)
  - PNG: 0-9 (Standard: 6)
- `-w, --width`: Breite in Pixeln
- `--height`: Höhe in Pixeln (Hinweis: `-h` ist für Hilfe reserviert)
- `--estimate`: Zeigt nur die geschätzte Ausgabegröße an

## Unterstützte Formate

| Format | Eingabe | Ausgabe | Qualitätseinstellung |
|--------|---------|---------|---------------------|
| JPEG   | ✅      | ✅      | 1-100               |
| PNG    | ✅      | ✅      | 0-9 (Kompression)   |
| BMP    | ✅      | ✅      | -                   |
| TIFF   | ✅      | ✅      | 0-9 (Kompression)   |
| GIF    | ✅      | ✅      | -                   |
| WebP   | ✅      | ✅      | 0-100               |
| ICO    | ✅      | ✅      | -                   |

## Technische Details

- **Python-Version**: 3.7+
- **Hauptbibliothek**: Pillow (PIL)
- **GUI-Framework**: tkinter (in Python enthalten)

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe LICENSE-Datei für Details.

## Beitragen

Beiträge sind willkommen! Bitte erstellen Sie einen Pull Request oder öffnen Sie ein Issue für Fehlerberichte oder Feature-Anfragen.

## Autor

Erstellt mit ❤️ für die Open-Source-Community
