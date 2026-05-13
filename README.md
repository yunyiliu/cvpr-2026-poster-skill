# CVPR 2026 Poster Skill

Turn a CVPR 2026 paper into a print-ready 84"×42" poster by chatting
with an AI agent. No manual templating, no PowerPoint, no fighting
with print dialogs.

This is a Claude Code / Codex **skill** — not a standalone CLI tool.
You install it once into your agent, then talk to it in plain language.

---

## How to start

### 1. Install the skill (one time)

Drop the `cvpr-2026-poster/` folder of this repo into your agent's
skills directory:

**Claude Code** (recommended)

```bash
git clone https://github.com/yunyiliu/cvpr-2026-poster-skill.git
ln -s "$(pwd)/cvpr-2026-poster-skill/cvpr-2026-poster" ~/.claude/skills/cvpr-2026-poster
```

Restart Claude Code. The skill appears as `cvpr-2026-poster` in the
available-skills list.

**Codex** or other agents: copy the same `cvpr-2026-poster/` folder
into your agent's skill location (depends on the tool).

### 2. Talk to your agent

That's it. Examples:

> Use cvpr-2026-poster to build a poster from my Overleaf folder at
> `/Users/me/papers/sat-rrg/`. Auto-fetch institution logos.

> Use cvpr-2026-poster to refine the generated poster — make the
> method card use a side-by-side figure/text layout and shrink the
> conference logo a bit.

> Use cvpr-2026-poster to export the final PDF for printing.

The agent will scaffold the workspace, extract content from your
LaTeX source, fetch logos, populate the editable HTML, and run the
export — all from one conversation.

### 3. Open the poster in a browser to fine-tune

The agent gives you a `poster-workspace/poster/index.html`. Open it:

```bash
open poster-workspace/poster/index.html
```

You can:

- Drag column dividers to change column widths
- Drag horizontal dividers to change card heights
- Drag a card's `◆` handle (or click two handles in sequence) to
  swap card positions
- Use `A+` / `A-` to scale all fonts globally
- Click **Save** to download the current layout — then tell the
  agent to bake it into the final PDF

Or just describe what you want changed in chat — the agent will
make the edit for you.

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
