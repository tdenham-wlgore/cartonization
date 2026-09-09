"""Build a source ZIP from an explicit allowlist, excluding local data and caches."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.2.0"
FILES = [
    "MANIFEST.in",
    "README.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "constraints.txt",
    "cartonization_functions.py",
    ".gitattributes",
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
    paths = {ROOT / p for p in FILES + SAMPLE_DATA}
    for pattern in PATTERNS:
        paths.update(ROOT.glob(pattern))
    if any(not p.is_file() or p.is_symlink() for p in paths):
        raise ValueError("Release input is missing or is a symlink.")
    files = sorted(paths)
    payloads = {p: p.read_bytes() for p in files}
    manifest = {
        "version": VERSION,
        "distribution": "no-launchers",
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
    target = output / f"cartonization-{VERSION}-no-launchers.zip"
    prefix = f"cartonization-{VERSION}-no-launchers/"
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
