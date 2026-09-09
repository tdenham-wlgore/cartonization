"""Build a source ZIP from an explicit allowlist, excluding local data and caches."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.2.0"
FILES = [
    "MANIFEST.in",
    "README.md",
    "START_HERE.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "constraints.txt",
    "cartonization_functions.py",
    "setup_mac.command",
    ".gitignore",
]
PATTERNS = [
    "cartonization/*.py",
    "docs/*.md",
    "tools/*.py",
    "tests/*.py",
    "examples/*.py",
    "examples/*.json",
    "examples/data/*.xlsx",
    ".github/*.md",
    ".github/workflows/*.yml",
    ".vscode/*.json",
]
SAMPLE_DATA = ["data/reference_test_data.xlsx", "data/shipment_history_test_data.xlsx"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--without-windows-launcher",
        action="store_true",
        help="Omit the optional Windows launcher and create a separately named ZIP.",
    )
    args = parser.parse_args()
    launcher = ROOT / "setup_windows.cmd"
    without_launcher = args.without_windows_launcher or not launcher.exists()
    paths = {ROOT / p for p in FILES + SAMPLE_DATA}
    if not without_launcher:
        paths.add(launcher)
    for pattern in PATTERNS:
        paths.update(ROOT.glob(pattern))
    if any(not p.is_file() or p.is_symlink() for p in paths):
        raise ValueError("Release input is missing or is a symlink.")
    files = sorted(paths)
    payloads = {p: p.read_bytes() for p in files}
    if without_launcher:
        manifest_in = ROOT / "MANIFEST.in"
        payloads[manifest_in] = payloads[manifest_in].replace(b"setup_windows.cmd ", b"")
    manifest = {
        "version": VERSION,
        "distribution": "no-windows-launcher" if without_launcher else "standard",
        "files": [
            {
                "path": p.relative_to(ROOT).as_posix(),
                "bytes": len(payloads[p]),
                "sha256": hashlib.sha256(payloads[p]).hexdigest(),
            }
            for p in files
        ],
    }
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    suffix = "-no-windows-launcher" if without_launcher else ""
    target = output / f"cartonization-{VERSION}{suffix}.zip"
    prefix = f"cartonization-{VERSION}{suffix}/"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:
            info = zipfile.ZipInfo.from_file(p, prefix + p.relative_to(ROOT).as_posix())
            z.writestr(info, payloads[p], compress_type=zipfile.ZIP_DEFLATED)
        z.writestr(prefix + "MANIFEST.json", json.dumps(manifest, indent=2))
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(".zip.sha256").write_text(f"{digest}  {target.name}\n")
    print(f"{target}\n{len(files)} files; SHA-256 {digest}")


if __name__ == "__main__":
    main()
