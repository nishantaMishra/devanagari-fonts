from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib import metadata, resources
import os
from pathlib import Path
import shutil
from typing import Iterable

FONT_EXTENSIONS = (".ttf", ".otf")


@dataclass(frozen=True, order=True)
class Font:
    """A bundled font file."""

    family: str
    filename: str
    relative_path: str
    format: str
    variable: bool

    @property
    def name(self) -> str:
        """The filename without its extension."""

        return Path(self.filename).stem

    @property
    def path(self) -> Path:
        """A filesystem path to the font file."""

        return _font_path_from_relative(self.relative_path)


def families() -> tuple[str, ...]:
    """Return the bundled font family names."""

    return tuple(sorted({font.family for font in fonts()}))


def fonts(family: str | None = None) -> tuple[Font, ...]:
    """Return bundled font records, optionally filtered by family."""

    all_fonts = _all_fonts()
    if family is None:
        return all_fonts

    normalized = _normalize(family)
    return tuple(font for font in all_fonts if _normalize(font.family) == normalized)


def font_files(family: str | None = None) -> tuple[Path, ...]:
    """Return filesystem paths to bundled font files."""

    return tuple(font.path for font in fonts(family))


def get_font(
    family: str,
    *,
    name: str | None = None,
    style: str | None = None,
) -> Font:
    """Return one bundled font matching a family and optional name or style."""

    matches = list(fonts(family))
    if not matches:
        raise LookupError(f"No bundled Devanagari font family named {family!r}.")

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
        raise LookupError(f"No bundled Devanagari font matched {criteria}.")

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
    """Return a filesystem path to one bundled font."""

    return get_font(family, name=name, style=style).path


def _iter_fonts() -> Iterable[Font]:
    root = _fonts_root()
    for family_dir in root.iterdir():
        if not family_dir.is_dir():
            continue

        for item in family_dir.iterdir():
            if not item.is_file():
                continue

            suffix = Path(item.name).suffix.lower()
            if suffix not in FONT_EXTENSIONS:
                continue

            yield Font(
                family=family_dir.name,
                filename=item.name,
                relative_path=f"fonts/{family_dir.name}/{item.name}",
                format=suffix.lstrip("."),
                variable="[" in item.name and "]" in item.name,
            )


@lru_cache(maxsize=1)
def _all_fonts() -> tuple[Font, ...]:
    return tuple(sorted(_iter_fonts()))


def _fonts_root() -> resources.abc.Traversable:
    return resources.files("devanagari_fonts").joinpath("fonts")


def _font_path_from_relative(relative_path: str) -> Path:
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
    base = os.environ.get("XDG_CACHE_HOME")
    root = Path(base).expanduser() if base else Path.home() / ".cache"
    return root / "devanagari-fonts" / _package_version()


def _package_version() -> str:
    try:
        return metadata.version("devanagari-fonts")
    except metadata.PackageNotFoundError:
        return "editable"


def _normalize(value: str) -> str:
    return "".join(ch for ch in value.casefold() if ch.isalnum())
