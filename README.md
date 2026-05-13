# CVPR 2026 Poster Skill

Turn a CVPR 2026 paper into a print-ready poster in minutes, not days.

The skill scaffolds a workspace with:

- LaTeX-extracted title, authors, affiliations, abstract, and figures
- Auto-fetched institution logos (one per school)
- A browser-editable HTML poster at the official CVPR 2026 size
  (84"×42" Main / Findings, 42"×21" Workshop)
- One-command export to print-ready PDF

You can drag column widths, swap card positions, and resize cards
directly in the browser. Anything an agent (Claude Code, Codex, etc.)
can write into `poster_brief.md` flows through to the poster.

---

## How to start

You need Python 3 and Google Chrome installed.

### 1. Clone

```bash
git clone https://github.com/yunyiliu/cvpr-2026-poster-skill.git
cd cvpr-2026-poster-skill
```

### 2. Create a workspace

```bash
python3 cvpr-2026-poster/scripts/init_poster_project.py \
  --project-dir ./poster-workspace \
  --track main
```

`--track` is one of `main`, `findings`, or `workshop`.

### 3. Auto-fill the brief from your LaTeX source

```bash
python3 cvpr-2026-poster/scripts/fill_brief_from_latex.py \
  --project-dir ./poster-workspace \
  --latex-dir /path/to/overleaf \
  --copy-figures
```

If your main file is not auto-detected, add `--main-tex camera_ready.tex`.

### 4. Edit `poster-workspace/poster_brief.md`

Fill in (or trim) the story bullets, method bullets, results bullets,
the metrics table, and **institution websites** (one URL per school,
in the same order as `Affiliations` — these are used to auto-fetch
logos).

### 5. Sync the brief into the editable poster

```bash
python3 cvpr-2026-poster/scripts/sync_poster_from_brief.py \
  --project-dir ./poster-workspace \
  --fetch-logos-if-missing
```

This generates `poster/index.html` and `poster/poster-config.json`,
copies figures and logos into place, and fetches institution logos
from their websites if you have not added any yet.

### 6. Open and edit in the browser

```bash
open poster-workspace/poster/index.html
```

In the editor you can:

- Drag the divider between columns to change column widths
- Drag the divider between cards to change card heights
- Drag a card's `◆` handle onto a drop zone, or click two handles
  in sequence, to move or swap cards
- Use `A+` / `A-` to scale all fonts globally
- Click **Save** to download the current `poster-config.json` (your
  layout edits live in browser localStorage until you do this)

If you are using Claude Code or Codex, just tell the agent what you
want changed and it will edit the brief or call `posterAPI` on the
running editor.

### 7. Export to PDF

After clicking **Save** in the editor, run:

```bash
cd poster-workspace
bash bake_and_export.sh
```

This will:

1. Pick up the newest `poster-config.json` from `~/Downloads/`
2. Re-embed it into `poster/index.html`
3. Run headless Chrome to produce `poster.pdf` at the exact poster size

Pass an explicit path if the JSON is elsewhere:

```bash
bash bake_and_export.sh /path/to/poster-config.json
```

If you have not changed layout in the browser since the last sync,
skip the bake step:

```bash
bash export_pdf.sh
```

Verify the PDF dimensions — for a Main / Findings poster the page
should be exactly **84.01" × 42.01"**.

---

## What is in the workspace

```
poster-workspace/
├── poster_brief.md         ← you edit this
├── poster_outline.md       ← optional planning notes
├── print_checklist.md      ← preflight before sending to the printer
├── assets/
│   ├── figures/            ← copies of figures referenced in the paper
│   └── logos/              ← school / lab logos (user-supplied or fetched)
├── poster/
│   ├── index.html          ← the editable poster, open in a browser
│   ├── poster-config.json  ← serialized layout + content
│   ├── figures/            ← display copies of figures
│   └── logos/
│       ├── user/           ← school logos (rendered top-left of header)
│       └── official/       ← CVPR conference logo (rendered top-right)
├── references/
│   └── latex-extract.md    ← summary of what was pulled from LaTeX
├── export_pdf.sh           ← headless-Chrome PDF export
└── bake_and_export.sh      ← bake current layout, then export
```

---

## Programmatic editing from the agent

While the poster is open in the browser, an agent can call methods on
`window.posterAPI` to make targeted edits without a full sync. Useful
endpoints:

- `setCardHtml(cardId, html)` — replace a card's body
- `setCardTitle(cardId, title)` — rename a card
- `setCardAccent(cardId, color)` — recolor a card's top accent bar
- `moveCard(cardId, columnId, index)` — relocate a card
- `swapCards(a, b)` — swap two cards
- `setColumns(columns)` — restructure the column layout
- `setLogos([...])` / `setConferenceLogos([...])` — replace logos
- `setHeader({ title, authors, affiliations, badge })` — update the header
- `getConfig()` / `exportConfig()` — read the current state
- `resetLayout()` — discard local edits, revert to the embedded config

---

## CVPR 2026 size and format reference

| Track | Poster size | Aspect ratio | Notes |
|-------|-------------|--------------|-------|
| Main, Findings | 84" × 42" (2134 × 1067 mm) | 2 : 1 landscape | Default 4-column |
| Workshop | 42" × 21" (1067 × 533 mm) | 2 : 1 landscape | Default 3-column |

Output should be PDF with **no bleed**. The bundled `export_pdf.sh`
honors the poster's `@page` CSS so the page size matches exactly.

---

## Why headless Chrome, not File → Print

Chrome's print dialog defaults to Letter paper and silently downscales
the 84"×42" poster unless you create a matching custom paper size in
*System Settings → Printers & Scanners → Manage Custom Sizes*.
`export_pdf.sh` uses Chrome in headless mode, which honors the
`@page { size: 84in 42in; margin: 0; }` declaration directly.

---

## Print-resolution notes

Images are embedded at native pixel resolution. Vector content (text,
SVG logos, gradients, table borders) stays sharp at any zoom.

To maximize print sharpness:

- Re-render figures from the paper at high DPI (matplotlib `dpi=300`,
  TikZ → PDF → rasterize at 300 DPI, etc.)
- Drop the high-res copies into `assets/figures/` and re-run
  `sync_poster_from_brief.py`

A figure that is 1600 px wide displayed at 200 mm prints at ~203 DPI,
which is fine for poster viewing but below the 300 DPI threshold some
printers prefer.

---

## License

MIT. See [LICENSE](LICENSE).
