#!/usr/bin/env bash
# Render poster/index.html to poster.pdf at the poster's native size.
# The CSS `@page` rule inside the template controls the paper size, so
# this script honors whatever dimensions the workspace was initialized
# with (84"x42" Main/Findings, 42"x21" Workshop, custom override, ...).
#
# Override Chrome:
#   CHROME="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" bash export_pdf.sh
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
HTML="$DIR/poster/index.html"
PDF="$DIR/poster.pdf"

CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ ! -x "$CHROME" ]; then
  echo "Chrome not found at: $CHROME"
  echo "Set CHROME=/path/to/chrome and rerun."
  exit 1
fi

"$CHROME" \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --hide-scrollbars \
  --run-all-compositor-stages-before-draw \
  --virtual-time-budget=30000 \
  --allow-file-access-from-files \
  --force-device-scale-factor=3 \
  --high-dpi-support=1 \
  --print-to-pdf-no-header \
  --print-to-pdf="$PDF" \
  "file://$HTML"

echo "Wrote $PDF"
ls -lh "$PDF"
