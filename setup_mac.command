#!/bin/zsh
cd "$(dirname "$0")" || exit 1
if command -v python3.12 >/dev/null 2>&1; then
    python3.12 tools/setup_environment.py
else
    python3 tools/setup_environment.py
fi
setup_result=$?
if [ "$setup_result" -eq 0 ]; then
    echo "Setup complete. Open this folder in VS Code and follow START_HERE.md."
else
    echo "Setup did not complete. See docs/TROUBLESHOOTING.md."
fi
read "?Press Return to close."
exit "$setup_result"
