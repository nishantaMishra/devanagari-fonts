from __future__ import annotations

from pathlib import Path
import shutil

import pytest

import devanagari_fonts._api as api
from devanagari_fonts import (
    available_families,
    cache_dir,
    families,
    font_files,
    font_path,
    fonts,
    get_font,
)
from devanagari_fonts.cli import main


def test_available_families_include_known_fonts() -> None:
    names = available_families()

    assert "Hind" in names
    assert "Noto Sans Devanagari" in names


def test_only_shobhika_is_installed_by_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DEVANAGARI_FONTS_CACHE", str(tmp_path))
    api._installed_fonts.cache_clear()

    names = families()

    assert names == ("Shobhika-1.05",)
    assert all(font.family == "Shobhika-1.05" for font in fonts())


def test_font_path_returns_existing_bundled_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DEVANAGARI_FONTS_CACHE", str(tmp_path))
    api._installed_fonts.cache_clear()

    path = font_path("Shobhika-1.05", style="Regular")

    assert path.exists()
    assert path.name == "Shobhika-Regular.otf"


def test_cached_font_is_discovered(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DEVANAGARI_FONTS_CACHE", str(tmp_path))
    source = Path("src/devanagari_fonts/fonts/Hind/Hind-Regular.ttf")
    destination = tmp_path / "Hind" / "Hind-Regular.ttf"
    destination.parent.mkdir(parents=True)
    shutil.copyfile(source, destination)
    api._installed_fonts.cache_clear()

    path = font_path("Hind", style="Regular")

    assert path == destination
    assert font_files("Hind") == (destination,)


def test_get_font_raises_for_missing_family(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DEVANAGARI_FONTS_CACHE", str(tmp_path))
    api._installed_fonts.cache_clear()

    with pytest.raises(LookupError, match="devanagari-fonts install hind"):
        get_font("Hind")


def test_cli_list_outputs_bundles(capsys: pytest.CaptureFixture[str]) -> None:
    result = main(["list"])

    captured = capsys.readouterr()
    assert result == 0
    assert "Available bundles:" in captured.out
    assert "core" in captured.out
    assert "hind" in captured.out


def test_cache_dir_uses_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DEVANAGARI_FONTS_CACHE", str(tmp_path))

    assert cache_dir() == tmp_path
