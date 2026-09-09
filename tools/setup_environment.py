"""Create the user's local environment without changing machine-wide Python."""

import subprocess
import sys
import venv
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    if not (3, 10) <= sys.version_info[:2] <= (3, 13):
        print("Use Python 3.10 through 3.13 (3.12 recommended), then run setup again.")
        return 1
    environment = root / ".venv"
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not python.exists():
        print("Creating the local Python environment...", flush=True)
        venv.EnvBuilder(with_pip=True).create(environment)
    print("Installing the tested package versions...", flush=True)
    subprocess.run(
        [str(python), "-m", "pip", "install", "-c", str(root / "constraints.txt"), str(root)],
        check=True,
        cwd=root,
    )
    return subprocess.run([str(python), "-m", "cartonization", "doctor"], cwd=root).returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"Setup stopped: {exc}\nSee docs/TROUBLESHOOTING.md.")
        raise SystemExit(1)
