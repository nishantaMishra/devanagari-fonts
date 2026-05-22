from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
from urllib.error import URLError
from urllib.request import urlopen

from ._api import _cache_dir, _installed_fonts, _normalize, _registry, _slugify

FAMILY_ALIASES = {
    "noto-sans": "Noto Sans Devanagari",
    "noto-serif": "Noto Serif Devanagari",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="devanagari-fonts",
        description="List and install Devanagari font bundles.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List available bundles and font families.")
    subparsers.add_parser("cache-dir", help="Print the download cache directory.")

    install_parser = subparsers.add_parser(
        "install",
        help="Install a bundle or font family into the user cache.",
    )
    install_parser.add_argument(
        "name",
        help="Bundle or family name, for example: core, full, hind, noto-sans-devanagari.",
    )

    args = parser.parse_args(argv)

    if args.command == "list":
        _print_registry()
        return 0
    if args.command == "cache-dir":
        print(_cache_dir())
        return 0
    if args.command == "install":
        return _install(args.name)

    parser.error(f"Unknown command: {args.command}")
    return 2


def _print_registry() -> None:
    registry = _registry()
    print("Available bundles:\n")
    for bundle in ("core", "noto", "display", "full"):
        print(bundle)
        families = registry["bundles"][bundle]
        if bundle == "full":
            print("  All available open-source Devanagari font families")
        else:
            for family in families:
                print(f"  {family}")
        print()

    print("Available font families:\n")
    for family in sorted(entry["family"] for entry in registry["families"]):
        print(f"  {_slugify(family):32} {family}")


def _install(name: str) -> int:
    registry = _registry()
    family_names = _resolve_install_target(name)
    if family_names is None:
        print(f"Unknown bundle or font family: {name}", file=sys.stderr)
        print("Run `devanagari-fonts list` to see valid names.", file=sys.stderr)
        return 2

    family_entries = {
        entry["family"]: entry for entry in registry["families"] if entry["family"] in family_names
    }
    if not family_entries:
        print(f"No registry entries matched: {name}", file=sys.stderr)
        return 2

    cache_root = _cache_dir()
    for family in family_names:
        entry = family_entries[family]
        if family in registry["bundled_families"]:
            print(f"{family}: bundled with the package")
            continue

        print(f"{family}:")
        for file_info in entry["files"]:
            _download_file(cache_root, file_info)

    _installed_fonts.cache_clear()
    print(f"\nInstalled fonts are stored in: {cache_root}")
    return 0


def _resolve_install_target(name: str) -> list[str] | None:
    registry = _registry()
    normalized = _normalize(name)
    slug = _slugify(name)

    if slug in registry["bundles"]:
        return list(registry["bundles"][slug])

    if slug in FAMILY_ALIASES:
        return [FAMILY_ALIASES[slug]]

    for entry in registry["families"]:
        if slug == entry["slug"] or normalized == _normalize(entry["family"]):
            return [entry["family"]]
    return None


def _download_file(cache_root: Path, file_info: dict[str, object]) -> None:
    relative_path = str(file_info["relative_path"])
    destination = cache_root / relative_path
    expected_hash = str(file_info["sha256"])

    if destination.exists() and _sha256(destination) == expected_hash:
        print(f"  ok      {Path(relative_path).name}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(str(file_info["url"]), timeout=30) as response:
            data = response.read()
    except URLError as exc:
        raise SystemExit(f"Failed to download {relative_path}: {exc}") from exc

    actual_hash = hashlib.sha256(data).hexdigest()
    if actual_hash != expected_hash:
        raise SystemExit(
            f"Checksum mismatch for {relative_path}: expected {expected_hash}, got {actual_hash}"
        )

    destination.write_bytes(data)
    print(f"  install {Path(relative_path).name}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
