---
name: cvpr-2026-poster
description: Use when the user needs to plan, draft, or refine a CVPR 2026 poster under the official CVPR 2026 size, layout, and printing constraints, including adapting the official template, turning a paper into a 5 to 10 minute poster story, or preparing a print-ready poster brief and checklist.
---

# CVPR 2026 Poster

## Overview

This skill turns a paper, a few figures, and optional template assets into a CVPR 2026 editable poster workspace. Prefer it for Main, Findings, or Workshop posters when the work must follow official CVPR 2026 poster sizing and printing rules and the user wants a directly editable poster output, not just planning notes.

## Workflow

1. Confirm the track and use the correct official size.
2. Gather the minimum poster inputs before writing any layout text.
3. Compress the paper into a 5 to 10 minute poster story instead of copying the paper.
4. Default to large figures and sparse text.
5. Use the official template as a style reference when available.
6. Fill the editable HTML poster scaffold in `poster/index.html`.
7. Keep `poster/poster-config.json` in sync with the HTML defaults.
8. Preflight the print export before calling the poster done.

## How To Use This Skill

Use the skill in three phases:

1. Create or organize a poster workspace.
2. If an Overleaf or LaTeX folder exists, run `scripts/fill_brief_from_latex.py` before hand-editing the brief.
3. Fill `poster_brief.md` with paper facts, figures, links, style constraints, and institution logos.
4. Run `scripts/sync_poster_from_brief.py` to seed `poster/index.html` and `poster/poster-config.json`.
5. Let the built-in optimizer adjust the first draft from figure aspect ratios.
6. Ask the agent to refine the generated poster, not start from scratch.

Typical prompts:

- `Use $cvpr-2026-poster to turn my paper into a CVPR 2026 poster brief.`
- `Use $cvpr-2026-poster to build a 4-column poster outline from my Overleaf folder and figures.`
- `Use $cvpr-2026-poster to adapt the official CVPR 2026 template and prepare a print checklist.`
- `Use $cvpr-2026-poster to refine the generated poster/index.html after I synced poster_brief.md.`

## Track and Size

Read [references/cvpr-2026-spec.md](references/cvpr-2026-spec.md) before making any poster-specific recommendation.

Default assumptions:

- `main` and `findings`: `84in x 42in`, landscape, aspect ratio `2:1`
- `workshop`: `42in x 21in`, landscape, aspect ratio `2:1`
- default layout: `4` columns for method-heavy papers, `3` columns when the central figure or result panels are unusually wide
- print export: `PDF`
- no bleed

## Minimum Inputs

Ask for or infer these before drafting:

- paper source, preferably Overleaf or LaTeX
- final title, authors, affiliations, and paper ID
- 3 to 6 must-have figures
- one main quantitative table
- a QR target link
- school, lab, or company logos when the header should show institution branding
- institution website URLs when the user wants the agent to try auto-fetching missing logos
  When there are multiple institutions, prefer one website per institution in the same order as `Affiliations`.
- Overleaf or LaTeX source when the user wants the brief auto-filled from the paper

If the user has no project website, use one of these as the QR target:

- arXiv page
- GitHub repository
- lab page
- personal page
- demo or video page

## Story Compression

Poster text should support a live explanation, not replace it.

Aim for:

- one-sentence takeaway near the title
- 3 to 5 concise method bullets
- 3 to 5 results bullets
- 2 to 4 conclusion bullets
- at most 1 to 2 equations unless the user explicitly wants a more technical poster

For CVPR papers, a reliable default structure is:

- `Problem / Motivation / Contribution`
- `Method Overview`
- `Key Mechanism or Ablation`
- `Results / Qualitative Examples / Conclusion`

## Editable Poster Output

The generated output should include:

- `poster/index.html` as the browser-editable poster
- `poster/poster-config.json` as the saved layout and content config
- `poster/logos/` for conference and institution logos
- `poster/figures/` for copied figures used by the poster
- `references/latex-extract.md` when `fill_brief_from_latex.py` is used
- a generated QR image URL when `QR target` is present in `poster_brief.md`
- a first-pass layout optimized from local figure aspect ratios

The bundled HTML editor already supports layout editing. When filling it:

- update the title, authors, affiliations, badge, and logo list
- replace placeholder card content with paper-specific content
- copy selected figures into `poster/figures/` and reference them from the HTML
- keep the poster self-contained enough to open locally via `file://`
- prefer refining the synced config over rebuilding the layout structure unless the existing scaffold is clearly wrong
- use `window.posterAPI.getWaste()` when you need a quick measurement of figure-related whitespace

## Template Adaptation

If the user provides the official template as Google Slides, PowerPoint, or PDF:

- treat it as a visual and spacing reference unless the user explicitly needs the final artifact to stay editable in Slides or PPT
- preserve the conference-like header hierarchy, margins, whitespace, and logo placement
- do not let the template force a text-heavy poster

Resolve template and logo assets in this order:

1. user workspace overrides
2. bundled official assets in this skill
3. official shared asset folder exports

Workspace overrides to prefer when present:

- templates under `references/` such as `official-template.pdf` or `official-template.pptx`
- logos under `assets/logos/`

Treat bundled conference logos and user institution logos differently:

- bundled conference logos provide CVPR branding by default
- user institution logos from `assets/logos/` should be added to the poster header when available

Bundled assets in this skill:

- `assets/official/templates/CVPR MAIN & FINDINGS Poster Template.pptx`
- `assets/official/templates/CVPR Workshop ONLY Poster Template.pptx`
- `assets/official/logos/CVPR_Logo2_Denver 2026_Color.eps`

If the user references an official shared asset folder and no local files exist, ask them to export the needed files and place them in:

- `references/` for templates and reference PDFs
- `assets/logos/` for logos and conference marks

If no template is provided, stay close to official guidance:

- `3` or `4` columns
- little text
- a few large expressive figures

## Output Files

When building or organizing poster work, prefer these working files:

- `poster/index.html`
- `poster/poster-config.json`
- `poster_brief.md`
- `poster_outline.md`
- `print_checklist.md`

You can scaffold them with:

```bash
python3 scripts/init_poster_project.py --project-dir ./poster-workspace --track main
```

The scaffold script will copy bundled official assets into the workspace when they are available for the selected track.

If the user has Overleaf or LaTeX source, prefer seeding the brief with:

```bash
python3 scripts/fill_brief_from_latex.py --project-dir ./poster-workspace --latex-dir ./overleaf --copy-figures
```

That script will try to:

- find the main `.tex` file automatically
- extract title, authors, affiliations, and abstract
- copy displayable figures into `assets/figures/`
- write a figure and caption summary into `references/latex-extract.md`
- let the later sync step reuse extracted figure captions inside the poster cards

After editing `poster_brief.md`, sync it with:

```bash
python3 scripts/sync_poster_from_brief.py --project-dir ./poster-workspace
```

If the user has no institution logos yet, prefer:

```bash
python3 scripts/sync_poster_from_brief.py --project-dir ./poster-workspace --fetch-logos-if-missing
```

When multiple schools or labs appear in the paper, make sure `poster_brief.md` lists one institution website per institution so the fallback fetch can add one logo per school instead of only one generic logo.

If the user later changes figures, rerun:

```bash
python3 scripts/optimize_poster_layout.py --project-dir ./poster-workspace
```

## Preflight

Before final export, read [references/print-checklist.md](references/print-checklist.md) and verify:

- the track matches the final size
- the export is `PDF`
- no bleed is included
- the job name uses full name and paper ID
- the user is not about to miss a printing deadline or poster upload requirement
