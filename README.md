# CVPR 2026 Poster Skill

A reusable AI skill for turning a CVPR 2026 paper into a poster brief, layout plan, and print checklist under the official conference constraints.

It is designed for two use cases:

- `Codex` / OpenAI skill workflows
- `Claude Code` style skill workflows

The skill focuses on practical poster work:

- official CVPR 2026 size and printing constraints
- converting a paper into a 5 to 10 minute poster story
- adapting the official CVPR template as a style reference
- handling missing project URLs by falling back to paper or code links
- generating reusable working files for figures, notes, and print review

## Official asset source

If you have access to the official CVPR 2026 poster assets, use this Google Drive folder as the canonical source for templates, logos, and related conference artwork:

- `https://drive.google.com/drive/folders/1oaXlMOJzWMYUiFBImMepKsZcoicpks8Z`

Recommended workflow:

- export the official poster template to `PDF` or `PPTX`
- put exported templates into `references/`
- put logos into `assets/logos/`
- mention in your prompt which file should be treated as the primary style reference

## Who this is for

Use this if you are:

- preparing a `CVPR 2026` Main, Findings, or Workshop poster
- using `Codex` or `Claude Code` and want a reusable poster workflow
- starting from a paper plus a few figures instead of a finished poster
- trying to match the official CVPR template style without manually rebuilding everything from scratch

## What is included

```text
cvpr-2026-poster/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── cvpr-2026-spec.md
│   ├── poster-brief-template.md
│   └── print-checklist.md
└── scripts/
    └── init_poster_project.py
```

## Install

### Codex

Copy `cvpr-2026-poster/` into your Codex skills directory, for example:

```bash
cp -R cvpr-2026-poster ~/.codex/skills/
```

Then invoke it with a prompt such as:

```text
Use $cvpr-2026-poster to turn my paper into a 4-column CVPR 2026 poster brief.
```

### Claude Code

Copy `cvpr-2026-poster/` into `.claude/skills/` in your project or user-level Claude skills directory:

```bash
mkdir -p .claude/skills
cp -R cvpr-2026-poster .claude/skills/
```

Then invoke it with a prompt such as:

```text
Use the cvpr-2026-poster skill to adapt the official CVPR 2026 template to my paper.
```

## Usage

This skill is designed to produce working poster materials, not just general advice.

### 1. Create a workspace

Run the scaffold script:

```bash
python3 cvpr-2026-poster/scripts/init_poster_project.py \
  --project-dir ./poster-workspace \
  --track main \
  --paper-id 12345 \
  --title "Your Paper Title"
```

This creates:

```text
poster-workspace/
├── assets/
│   ├── figures/
│   └── logos/
├── output/
├── references/
│   └── notes.md
├── poster_brief.md
├── poster_outline.md
└── print_checklist.md
```

### 2. Put your materials into the workspace

- `assets/figures/`
- `assets/logos/`
- `references/`

Recommended materials:

- your Overleaf or LaTeX source
- final title, authors, affiliations, and paper ID
- 3 to 6 must-have figures
- one main results table
- an official template export in `PDF` or `PPTX` if you want close visual matching
- a QR target link such as arXiv, GitHub, a lab page, or a demo page
- any CVPR logo, acronym, or poster header assets exported from the official Drive folder

### 3. Ask the agent to use the skill

Use one of these prompts:

```text
Use $cvpr-2026-poster to turn my paper into a CVPR 2026 poster brief.
```

```text
Use $cvpr-2026-poster to build a 4-column poster plan from my Overleaf folder and figures.
```

```text
Use $cvpr-2026-poster to adapt the official CVPR 2026 template and prepare a print checklist.
```

### 4. What the skill should produce

The expected outputs are:

- `poster_brief.md`
- `poster_outline.md`
- `print_checklist.md`
- a recommended section structure for the poster
- concrete guidance on which figures and numbers to emphasize

### 5. Build the actual poster

After the brief is ready, use your preferred poster generation workflow:

- HTML poster workflow
- PowerPoint or Google Slides
- Figma
- LaTeX beamerposter

This skill is mainly for the planning, structure, and CVPR-specific preflight layer.

## Recommended inputs

- Overleaf or LaTeX paper source
- title, authors, affiliations, paper ID
- 3 to 6 must-have figures
- one main results table
- official template exported as `PDF` or `PPTX` if you want visual matching
- QR target link such as arXiv, GitHub, lab page, or demo page

## No project page

If you do not have a project website yet, use one of these for the QR target:

- arXiv page
- GitHub repository
- lab page
- personal page
- demo or video page

The skill is written to handle this case directly.

## What makes the output CVPR-specific

The bundled references encode:

- the official `84in x 42in` Main and Findings poster size
- the official `42in x 21in` Workshop poster size
- the recommendation to use `3` or `4` columns
- the guidance to keep text light and figures large
- the print export and job-name requirements
- the main conference poster page upload reminder

## Example end-to-end workflow

1. Copy the skill into your AI tool.
2. Run `init_poster_project.py`.
3. Drop figures and links into the scaffolded workspace.
4. Ask the agent to produce `poster_brief.md` and `poster_outline.md`.
5. Build the final poster in your preferred editor.
6. Use `print_checklist.md` before exporting the final PDF.

## Notes

- The bundled CVPR 2026 spec was verified against official CVPR pages on `2026-05-13`.
- Before ordering prints, verify the latest conference page in case deadlines or upload links change.
- The skill treats Google Slides or PowerPoint templates as style references unless the user explicitly wants the final artifact to remain editable in Slides or PPT.

## Example

See [examples/cvpr-poster-brief-example.md](examples/cvpr-poster-brief-example.md) for a filled example based on a generic CVPR-style medical vision paper.

## License

MIT
