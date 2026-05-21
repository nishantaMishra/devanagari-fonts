from __future__ import annotations

from pathlib import Path

import pytest

from devanagari_fonts import families, font_files, font_path, fonts, get_font


def test_families_include_known_fonts() -> None:
    names = families()

    assert "Hind" in names
    assert "Noto Sans Devanagari" in names


def test_fonts_returns_records() -> None:
    hind_fonts = fonts("Hind")

    assert hind_fonts
    assert all(font.family == "Hind" for font in hind_fonts)
    assert any(font.filename == "Hind-Regular.ttf" for font in hind_fonts)


def test_font_path_returns_existing_path() -> None:
    path = font_path("Hind", style="Regular")

    assert path.exists()
    assert path.name == "Hind-Regular.ttf"


def test_font_files_returns_paths() -> None:
    paths = font_files("Hind")

    assert paths
    assert all(isinstance(path, Path) for path in paths)
    assert all(path.exists() for path in paths)


def test_get_font_raises_for_ambiguous_match() -> None:
    with pytest.raises(LookupError, match="Multiple fonts matched"):
        get_font("Hind", style="Bold")
