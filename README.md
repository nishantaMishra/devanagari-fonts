# devanagari-fonts

`devanagari-fonts` provides Devanagari font discovery, a small Python API for locating installed font files, and a command-line installer for downloading font families on demand.

The PyPI package is intentionally small. It includes the Python API, command-line tool, font registry metadata, and the Shobhika font family as a default bundled font. Other font families are downloaded into a user cache directory when requested.

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

List available bundles and font families:

```bash
devanagari-fonts list
```

Install a bundle:

```bash
devanagari-fonts install core
devanagari-fonts install noto
devanagari-fonts install display
devanagari-fonts install full
```

Install a single font family:

```bash
devanagari-fonts install hind
devanagari-fonts install akshar
devanagari-fonts install noto-sans-devanagari
```

Use installed fonts from Python:

```python
from devanagari_fonts import available_families, families, font_path, fonts

print(available_families())  # all registry fonts
print(families())            # installed fonts
print(fonts("Hind"))

path = font_path("Hind", style="Regular")
print(path)
```

Downloaded fonts are stored in the user cache directory. To see the active cache directory:

```bash
devanagari-fonts cache-dir
```

Each font family keeps its upstream license file alongside the downloaded font files.

## Available Fonts

<details>
<summary>Show registry font families</summary>

- Akshar
- Alkatra
- Amiko
- Amita
- Anek Devanagari
- Annapurna SIL
- Arya
- Asar
- Bakbak One
- Baloo 2
- Bhavuka
- Biryani
- Cambay
- Dekko
- Eczar
- Ek Mukta
- Gajraj One
- Glegoo
- Gotu
- Halant
- Hind
- IBM Plex Sans Devanagari
- Inknut Antiqua
- Jaini
- Jaini Purva
- Jaldi
- Kadwa
- Kalam
- Karma
- Khand
- Khula
- Kurale
- Laila
- Lohit Devanagari
- Martel
- Martel Sans
- Matangi
- Modak
- Mukta
- Noto Sans
- Noto Sans Devanagari
- Noto Sans Devanagari UI
- Noto Serif Devanagari
- Palanquin
- Palanquin Dark
- Playpen Sans Deva
- Poppins
- Pragati Narrow
- Rajdhani
- Ranga
- Rhodium Libre
- Rozha One
- Sahitya
- Sarala
- Sarpanch
- Shobhika-1.05
- Sitara
- Sumana
- Sura
- Teko
- Tillana
- Tiro Devanagari Hindi
- Tiro Devanagari Marathi
- Tiro Devanagari Sanskrit
- Vesper Libre
- Yantramanav
- Yatra One

</details>

## API

- `available_families()`: return all registry font family names.
- `families()`: return installed font family names.
- `fonts(family=None)`: return installed `Font` records for all fonts, or for one family.
- `font_files(family=None)`: return filesystem paths for installed font files.
- `get_font(family, name=None, style=None)`: return a single matching installed `Font`.
- `font_path(family, name=None, style=None)`: return the filesystem path for a single matching installed font.
- `cache_dir()`: return the font download cache directory.

## License

The Python package code is distributed under the MIT License. Bundled fonts are distributed under their own upstream licenses, included beside each font family.