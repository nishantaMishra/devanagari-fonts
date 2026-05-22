# devanagari-fonts

`devanagari-fonts` bundles Devanagari font files and exposes a small Python API for listing families, locating files, and passing font paths to libraries such as Pillow, Matplotlib, ReportLab, or WeasyPrint.

## Installation

Install from PyPI:

```bash
pip install devanagari-fonts
```

Install from GitHub:

```bash
pip install git+https://github.com/nishantaMishra/devanagari-fonts.git
```

## Usage

```python
from devanagari_fonts import families, font_path, fonts

print(families())
print(fonts("Hind"))

path = font_path("Hind", style="Regular")
print(path)
```

The package includes `.ttf` and `.otf` font files. Each font family keeps its bundled upstream license file alongside the font files under `devanagari_fonts/fonts/`.

## API

- `families()`: return available font family names.
- `fonts(family=None)`: return `Font` records for all fonts, or for one family.
- `font_files(family=None)`: return filesystem paths for available font files.
- `get_font(family, name=None, style=None)`: return a single matching `Font`.
- `font_path(family, name=None, style=None)`: return the filesystem path for a single matching font.

## License

The Python package code is distributed under the MIT License. Bundled fonts are distributed under their own upstream licenses, included beside each font family.
