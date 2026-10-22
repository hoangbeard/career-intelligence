#!/usr/bin/env bash
# Installs the optional tools for scripts/export_cv.py: a virtual environment
# in .venv/ with the locked packages from requirements-pdf.txt, and the
# Chromium build that Playwright uses to print the PDF.
#
# Run once per machine (or cloud environment). Safe to run again.
# Needs Python 3.10+ and internet access (PyPI and the Playwright CDN).
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -x .venv/bin/python ]]; then
  echo "==> creating .venv"
  python3 -m venv .venv
fi

echo "==> installing locked packages"
.venv/bin/python -m pip install --quiet --disable-pip-version-check --require-hashes -r requirements-pdf.txt

echo "==> installing Chromium for Playwright"
if [[ "$(uname -s)" == "Linux" ]] && { [[ $(id -u) -eq 0 ]] || sudo -n true 2>/dev/null; }; then
  # Fresh Linux machines (cloud agents) also need Chromium's system libraries.
  .venv/bin/python -m playwright install --with-deps chromium
else
  .venv/bin/python -m playwright install chromium
fi

echo "Done. Export a CV with: python3 scripts/export_cv.py <job folder>"
