# CVPR 2026 Poster Skill

Turn a CVPR 2026 paper into a print-ready 84"×42" poster by chatting
with an AI agent. No manual templating, no PowerPoint, no fighting
with print dialogs.

This is a Claude Code / Codex **skill** — not a standalone CLI tool.
You install it once into your agent, then talk to it in plain language.

---

## How to start

### 1. Install the skill (one time)

**Claude Code**

```bash
git clone https://github.com/yunyiliu/cvpr-2026-poster-skill.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/cvpr-2026-poster-skill/cvpr-2026-poster" ~/.claude/skills/cvpr-2026-poster
```

Start a new Claude Code session (existing sessions don't auto-pick-up
new skills). The skill appears in the available-skills list as
`cvpr-2026-poster`.

**Codex / other agents**: copy or symlink the same `cvpr-2026-poster/`
folder into your agent's skill location — refer to that tool's docs
for the exact path.

### 2. Ask the agent to build the poster

In a new session, write a single message like:

> Use `$cvpr-2026-poster` to create a poster workspace from my Overleaf
> folder at `/path/to/your/overleaf-folder/`. Fill the brief from
> LaTeX, copy figures, auto-fetch institution logos, and sync the
> editable poster.

The agent will:

- Run `init_poster_project.py` to scaffold the workspace
- Run `fill_brief_from_latex.py` to extract your paper's title,
  authors, affiliations, abstract, and figures
- Run `sync_poster_from_brief.py` to populate the editable HTML, copy
  figures into place, and fetch logos from your institutions' websites
- Open the resulting `poster/index.html` for you to inspect

If you have multiple institutions, list them in the same order as
`Affiliations` in `poster_brief.md` and add one institution website
per school. The agent does this automatically when the LaTeX is clear.

### 3. Iterate by talking to the agent

Once the poster is open in the browser, just describe edits in chat:

> Make the Results card use a side-by-side figure/text layout, and
> shrink the conference logo a bit.

> The Contributions card is too long — keep it to one lead sentence
> and three bullets.

> Move the Conclusion card to the bottom of the rightmost column.

The agent will edit `poster-config.json` (and re-embed it into
`index.html`) for you. Hard-refresh the browser tab to see the result.

You can also edit in the browser directly:

- Drag column dividers to change column widths
- Drag horizontal dividers to change card heights
- Drag a card's `◆` handle (or click two handles in sequence) to
  swap card positions
- Use `A+` / `A-` to scale all fonts globally
- Click **Save** when you're happy — that downloads
  `poster-config.json` to `~/Downloads/` with your layout

### 4. Export to a print-ready PDF

After you click **Save** in the browser, in a terminal:

```bash
cd poster-workspace
bash bake_and_export.sh
```

This picks up the saved `poster-config.json` from `~/Downloads/`,
re-embeds it into `index.html`, and runs headless Chrome to produce
`poster.pdf` at exactly **84.01" × 42.01"** (or the workshop size).

If you have not touched the layout in the browser since the last
agent edit, just run:

```bash
bash export_pdf.sh
```

Send `poster.pdf` directly to your printer.

---

## What you need

- Google Chrome (for the PDF export step)
- Python 3 (preinstalled on macOS and most Linux distros)

That's all. The skill ships the rest:

- LaTeX extractor
- Institution-logo auto-fetcher
- Editable HTML poster scaffold
- Headless-Chrome PDF exporter at the exact poster size
- Official CVPR 2026 Denver logo and template

---

## What gets created

A typical workspace looks like:

```
poster-workspace/
├── poster_brief.md         ← human-readable summary of paper content
├── poster/
│   ├── index.html          ← the editable poster, open in a browser
│   ├── poster-config.json  ← serialized layout + content
│   ├── figures/            ← display copies of figures
│   └── logos/
│       ├── user/           ← school logos (top-left)
│       └── official/       ← CVPR conference logo (top-right)
├── assets/
│   ├── figures/            ← original figures from the LaTeX project
│   └── logos/              ← school / lab logos (user or auto-fetched)
├── references/
│   └── latex-extract.md    ← summary of what was pulled from LaTeX
├── export_pdf.sh           ← one-command headless-Chrome PDF export
└── bake_and_export.sh      ← bake current browser layout, then export
```

---

## CVPR 2026 size reference

| Track | Poster size | Aspect ratio |
|-------|-------------|--------------|
| Main / Findings | 84" × 42" (2134 × 1067 mm) | 2 : 1 landscape |
| Workshop | 42" × 21" (1067 × 533 mm) | 2 : 1 landscape |

Output is PDF, no bleed. The exporter honors the poster's `@page`
declaration so the PDF page size matches the track exactly.

---

## Without an AI agent

If you want to drive the scripts manually instead of through an agent,
all of them are plain Python:

```bash
python3 cvpr-2026-poster/scripts/init_poster_project.py --project-dir ./poster-workspace --track main
python3 cvpr-2026-poster/scripts/fill_brief_from_latex.py --project-dir ./poster-workspace --latex-dir /path/to/overleaf --copy-figures
# edit poster-workspace/poster_brief.md
python3 cvpr-2026-poster/scripts/sync_poster_from_brief.py --project-dir ./poster-workspace --fetch-logos-if-missing
open poster-workspace/poster/index.html
# (edit in browser, click Save when done)
cd poster-workspace && bash bake_and_export.sh
```

---

## License

MIT. See [LICENSE](LICENSE).
