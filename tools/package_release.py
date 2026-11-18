"""Build both release ZIPs, or verify existing ZIPs against this source tree.

    python tools/package_release.py --output-dir dist
    python tools/package_release.py --output-dir dist --verify-only

Requires Python 3.11 or newer. Does not import Blender or publish anything.
"""
import argparse
import ast
import hashlib
import io
from pathlib import Path
import re
import tempfile
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "extension_src"
COPIES = (ROOT / "blender_buddy.py", ROOT / "blender_buddy" / "__init__.py")
TEMPLATES = ("templates/Blender_Buddy/__init__.py", "templates/Blender_Buddy/startup.blend")


def read_text_bytes(path):
    # A Windows checkout with core.autocrlf must build the same ZIP as Linux.
    return path.read_text(encoding="utf-8").encode("utf-8")


def release_inputs():
    manifest_bytes = read_text_bytes(EXTENSION / "blender_manifest.toml")
    manifest = tomllib.loads(manifest_bytes.decode("utf-8"))
    version = manifest["version"]
    if manifest["id"] != "blender_buddy" or not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){2}", version):
        raise ValueError("Expected blender_buddy and a three-part numeric version in the manifest")

    module = read_text_bytes(EXTENSION / "__init__.py")
    for path in COPIES:
        if read_text_bytes(path) != module:
            raise ValueError(f"Source copy differs from extension_src/__init__.py: {path}")
    tree = ast.parse(module)
    info = [ast.literal_eval(node.value) for node in tree.body
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "bl_info" for t in node.targets)]
    if len(info) != 1 or info[0]["version"] != tuple(map(int, version.split("."))):
        raise ValueError("bl_info version differs from the manifest")
    if info[0]["blender"] != tuple(map(int, manifest["blender_version_min"].split("."))):
        raise ValueError("bl_info minimum Blender version differs from the manifest")

    files = {"__init__.py": module}
    for name in TEMPLATES:
        path = EXTENSION / name
        files[name] = read_text_bytes(path) if name.endswith(".py") else path.read_bytes()
    classic = {"blender_buddy/" + name: content for name, content in files.items()}
    extension = {**files, "blender_manifest.toml": manifest_bytes}
    return version, {"": classic, "_extension": extension}


def archive_bytes(members):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, content in sorted(members.items()):
            # Fixed timestamps, modes and stored bytes keep builds independent of
            # the checkout platform, local clock and installed zlib version.
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--verify-only", action="store_true", help="compare existing ZIP bytes with a fresh build")
    args = parser.parse_args()
    version, packages = release_inputs()
    if not args.verify_only:
        args.output_dir.mkdir(parents=True, exist_ok=True)
    for suffix, members in packages.items():
        output = args.output_dir / f"blender_buddy_v{version}{suffix}.zip"
        data = archive_bytes(members)
        if not args.verify_only:
            with tempfile.TemporaryDirectory(dir=args.output_dir) as directory:
                temp = Path(directory) / output.name
                temp.write_bytes(data)
                temp.replace(output)
        if output.read_bytes() != data:
            raise ValueError(f"Package differs from source: {output}")
        print(f"{hashlib.sha256(data).hexdigest()}  {output.name}")


if __name__ == "__main__":
    main()
