"""Access bundled Devanagari font files."""

from ._api import (
    Font,
    available_families,
    cache_dir,
    families,
    font_files,
    font_path,
    fonts,
    get_font,
)

__all__ = [
    "Font",
    "available_families",
    "cache_dir",
    "families",
    "font_files",
    "font_path",
    "fonts",
    "get_font",
]
