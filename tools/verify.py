"""Verify the pinned Fidelity Audit Lab package, or build and verify its ZIP."""
import argparse
import hashlib
import json
import os
import sys
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import BadZipFile, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "plugin"
RELEASE = ROOT / "releases" / "0.1.0.json"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def exact_inventory(actual, expected, owner):
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    require(not missing and not extra, f"{owner}: missing {missing}, unexpected {extra}")


def check_bytes(data, entry, name):
    require(len(data) == entry["bytes"], f"{name}: byte length differs")
    require(hashlib.sha256(data).hexdigest() == entry["sha256"], f"{name}: SHA-256 differs")


def verify(payload, release):
    manifest = {item["path"]: item for item in release["files"]}
    require(len(manifest) == len(release["files"]), "release manifest repeats a path")
    exact_inventory(set(payload), set(manifest), "package")
    for name, item in manifest.items():
        check_bytes(payload[name], item, name)
    for name in ("plugin.json", ".codex-plugin/plugin.json"):
        identity = json.loads(payload[name])
        for field in ("name", "version"):
            require(identity[field] == release[field], f"{name}: {field} differs")

    index = json.loads(payload["references/source_snapshot.json"])
    entries = index["artifacts"]
    sources = {item["plugin_path"] for item in entries}
    require(len(sources) == len(entries) == index["artifact_count"], "source count differs")
    exact_inventory(sources, {k for k in payload if k.startswith("references/")
                              and k != "references/source_snapshot.json"}, "source index")
    for item in entries:
        name = item["plugin_path"]
        check_bytes(payload[name], item, name)
        status = {"governing": "GOVERNING", "proposed": "PROPOSED_NOT_ADOPTED"}[name.split("/")[1]]
        require(item["status"] == status, f"{name}: tier differs from its indexed status")
    return len(manifest), len(entries)


def directory_files():
    payload = {}
    for path in PACKAGE.rglob("*"):
        require(not path.is_symlink(), f"unexpected symlink in package: {path.name}")
        if path.is_file():
            payload[path.relative_to(PACKAGE).as_posix()] = path.read_bytes()
    return payload


def zip_files(path, release):
    # Authenticate the exact headers, payloads and trailer before any ZIP parsing.
    # Reading only the pinned length plus one also bounds oversized inputs.
    pin = release["canonical_zip"]
    with path.open("rb") as source:
        raw = source.read(pin["bytes"] + 1)
    check_bytes(raw, pin, "canonical ZIP")
    manifest = {item["path"]: item for item in release["files"]}
    with ZipFile(BytesIO(raw)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "ZIP repeats a member name")
        exact_inventory(set(names), set(manifest), "ZIP")
        for info in archive.infolist():
            require(info.file_size == manifest[info.filename]["bytes"],
                    f"{info.filename}: ZIP member size differs")
            require((info.external_attr >> 28) != 10, f"{info.filename}: ZIP symlink")
        return {name: archive.read(name) for name in names}


def build_archive(destination, payload, release):
    require(destination.suffix.lower() == ".zip", "choose a .zip output file")
    require(not destination.resolve().is_relative_to(PACKAGE.resolve()),
            "choose a ZIP path outside the plugin source")
    with NamedTemporaryFile(dir=destination.parent, delete=False) as temp:
        temporary = Path(temp.name)
    try:
        with ZipFile(temporary, "w") as archive:
            for name, data in sorted(payload.items()):
                info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        verify(zip_files(temporary, release), release)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--zip", type=Path, help="verify an existing release ZIP")
    mode.add_argument("--package", type=Path, help="write a release ZIP in an existing directory")
    args = parser.parse_args()
    release = json.loads(RELEASE.read_bytes())
    payload = zip_files(args.zip, release) if args.zip else directory_files()
    count, sources = verify(payload, release)
    if args.package:
        build_archive(args.package, payload, release)
    print(f"{release['name']} {release['version']}: {count} package files and {sources} pinned sources verified.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, BadZipFile, RuntimeError) as error:
        sys.exit(f"Verification failed: {error}")
