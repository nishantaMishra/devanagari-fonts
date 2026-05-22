from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
import json
import os
from pathlib import Path
import shutil
from typing import Any

FONT_EXTENSIONS = (".ttf", ".otf")


@dataclass(frozen=True, order=True)
class Font:
    """An installed Devanagari font file."""

    family: str
    filename: str
    relative_path: str
    format: str
    variable: bool
    source: str

    @property
    def name(self) -> str:
        """The filename without its extension."""

        return Path(self.filename).stem

    @property
    def path(self) -> Path:
        """A filesystem path to the installed font file."""

        if self.source == "bundled":
            return _bundled_font_path(self.relative_path)
        return _cache_dir() / self.relative_path


def families() -> tuple[str, ...]:
    """Return installed font family names."""

    return tuple(sorted({font.family for font in fonts()}))


def available_families() -> tuple[str, ...]:
    """Return all font family names known to the registry."""

    return tuple(entry["family"] for entry in _registry()["families"])


def fonts(family: str | None = None) -> tuple[Font, ...]:
    """Return installed font records, optionally filtered by family."""

    all_fonts = _installed_fonts()
    if family is None:
        return all_fonts

    normalized = _normalize(family)
    return tuple(font for font in all_fonts if _normalize(font.family) == normalized)


def font_files(family: str | None = None) -> tuple[Path, ...]:
    """Return filesystem paths to installed font files."""

    return tuple(font.path for font in fonts(family))


def get_font(
    family: str,
    *,
    name: str | None = None,
    style: str | None = None,
) -> Font:
    """Return one installed font matching a family and optional name or style."""

    matches = list(fonts(family))
    if not matches:
        raise LookupError(
            f"No installed Devanagari font family named {family!r}. "
            f"Install it with: devanagari-fonts install {_slugify(family)}"
        )

    if name is not None:
        normalized_name = _normalize(name)
        matches = [
            font
            for font in matches
            if _normalize(font.filename) == normalized_name
            or _normalize(font.name) == normalized_name
        ]

    if style is not None:
        normalized_style = _normalize(style)
        matches = [
            font
            for font in matches
            if normalized_style in _normalize(font.filename)
            or normalized_style in _normalize(font.name)
        ]

    if not matches:
        criteria = ", ".join(
            part
            for part in (
                f"family={family!r}",
                f"name={name!r}" if name is not None else "",
                f"style={style!r}" if style is not None else "",
            )
            if part
        )
        raise LookupError(f"No installed Devanagari font matched {criteria}.")

    regular = [font for font in matches if "regular" in _normalize(font.filename)]
    if len(regular) == 1:
        return regular[0]
    if len(matches) == 1:
        return matches[0]

    names = ", ".join(font.filename for font in matches[:10])
    if len(matches) > 10:
        names += ", ..."
    raise LookupError(f"Multiple fonts matched. Narrow the query: {names}")


def font_path(
    family: str,
    *,
    name: str | None = None,
    style: str | None = None,
) -> Path:
    """Return a filesystem path to one installed font."""

    return get_font(family, name=name, style=style).path


def cache_dir() -> Path:
    """Return the user cache directory used for downloaded fonts."""

    return _cache_dir()


@lru_cache(maxsize=1)
def _installed_fonts() -> tuple[Font, ...]:
    return tuple(sorted([*_bundled_fonts(), *_cached_fonts()]))


def _bundled_fonts() -> list[Font]:
    fonts: list[Font] = []
    root = resources.files("devanagari_fonts").joinpath("fonts")
    for family in _registry()["bundled_families"]:
        family_dir = root.joinpath(family)
        if not family_dir.is_dir():
            continue
        for item in family_dir.iterdir():
            suffix = Path(item.name).suffix.lower()
            if not item.is_file() or suffix not in FONT_EXTENSIONS:
                continue
            fonts.append(
                Font(
                    family=family,
                    filename=item.name,
                    relative_path=f"fonts/{family}/{item.name}",
                    format=suffix.lstrip("."),
                    variable="[" in item.name and "]" in item.name,
                    source="bundled",
                )
            )
    return fonts


def _cached_fonts() -> list[Font]:
    fonts: list[Font] = []
    root = _cache_dir()
    for entry in _registry()["families"]:
        family = entry["family"]
        for file_info in entry["files"]:
            if file_info["kind"] != "font":
                continue
            path = root / file_info["relative_path"]
            if not path.exists():
                continue
            suffix = path.suffix.lower()
            fonts.append(
                Font(
                    family=family,
                    filename=path.name,
                    relative_path=file_info["relative_path"],
                    format=suffix.lstrip("."),
                    variable="[" in path.name and "]" in path.name,
                    source="cache",
                )
            )
    return fonts


def _bundled_font_path(relative_path: str) -> Path:
    resource = resources.files("devanagari_fonts").joinpath(relative_path)
    direct_path = Path(str(resource))
    if direct_path.exists():
        return direct_path

    cache_path = _cache_dir() / relative_path
    if not cache_path.exists():
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with resources.as_file(resource) as extracted:
            shutil.copyfile(extracted, cache_path)
    return cache_path


def _cache_dir() -> Path:
    base = os.environ.get("DEVANAGARI_FONTS_CACHE") or os.environ.get("XDG_CACHE_HOME")
    root = Path(base).expanduser() if base else Path.home() / ".cache"
    if base and os.environ.get("DEVANAGARI_FONTS_CACHE"):
        return root
    return root / "devanagari-fonts"


@lru_cache(maxsize=1)
def _registry() -> dict[str, Any]:
    data = resources.files("devanagari_fonts").joinpath("registry.json").read_text()
    return json.loads(data)


def _normalize(value: str) -> str:
    return "".join(ch for ch in value.casefold() if ch.isalnum())


def _slugify(value: str) -> str:
    slug = "".join(ch if ch.isalnum() else "-" for ch in value.casefold()).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug
