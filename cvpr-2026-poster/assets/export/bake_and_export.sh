#!/usr/bin/env bash
# Bake the latest poster-config.json into index.html, then export to PDF.
#
# Why: the browser editor stores your column-width / card-height tweaks
# in localStorage only. Headless Chrome doesn't see localStorage, so
# without this step the exported PDF would use the old embedded layout.
#
# Usage:
#   1. In the browser, click the toolbar's "Save" button — this writes
#      `poster-config.json` to ~/Downloads/.
#   2. bash bake_and_export.sh
#      (or pass a path: bash bake_and_export.sh /path/to/poster-config.json)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

SRC="${1:-}"
if [ -z "$SRC" ]; then
  SRC=$(ls -t "$HOME/Downloads/poster-config"*.json 2>/dev/null | head -1 || true)
fi
if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then
  echo "No poster-config.json found in ~/Downloads/ — pass a path:"
  echo "  bash bake_and_export.sh /path/to/poster-config.json"
  exit 1
fi

echo "Baking layout from: $SRC"
cp "$SRC" "$DIR/poster/poster-config.json"

# Re-embed the config into index.html by patching the EMBEDDED_CONFIG
# line in place. No skill checkout required.
python3 - "$DIR" <<'PYEOF'
import json, re, sys
from pathlib import Path
ws = Path(sys.argv[1])
idx = ws / "poster" / "index.html"
cfg = json.loads((ws / "poster" / "poster-config.json").read_text())
html = idx.read_text(encoding="utf-8")
new_line = f"const EMBEDDED_CONFIG = {json.dumps(cfg, ensure_ascii=False)};"
patched = re.sub(r"const EMBEDDED_CONFIG = .*?;", new_line, html, count=1, flags=re.DOTALL)
if patched == html:
    raise SystemExit("Could not find EMBEDDED_CONFIG in index.html — was it edited by hand?")
idx.write_text(patched, encoding="utf-8")
print(f"Re-embedded config into {idx}")
PYEOF

bash "$DIR/export_pdf.sh"
