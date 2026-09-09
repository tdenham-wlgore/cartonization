"""Smoke-check the installed wheel from outside the source checkout."""

import subprocess
import sys
import tempfile
from argparse import ArgumentParser
from pathlib import Path


def main():
    parser = ArgumentParser()
    parser.add_argument("--install-wheel", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.install_wheel:
        wheels = sorted((root / "dist").glob("cartonization-*.whl"))
        if len(wheels) != 1:
            raise ValueError("Build exactly one release wheel in dist before this check.")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--force-reinstall",
                "--no-deps",
                str(wheels[0]),
            ],
            check=True,
        )
    code = (
        "from cartonization import max_cartons_four_quadrant,solve_min_integer; "
        "import cartonization; "
        "assert max_cartons_four_quadrant((.3,.3,.3),(.1,.1,.1)) == 27; "
        "assert solve_min_integer([2],[[1]],[3],upper_bounds=[2]) == ([2],6.0,'Optimal'); "
        "print('Installed package:',cartonization.__file__)"
    )
    with tempfile.TemporaryDirectory(prefix="carton installed check ") as temp:
        subprocess.run([sys.executable, "-I", "-c", code], cwd=temp, check=True)


if __name__ == "__main__":
    main()
