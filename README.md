# CVPR 2026 Poster Skill

A reusable AI skill for turning a CVPR 2026 paper into an editable poster workspace under the official conference constraints.

The generated output is not just a brief. It includes a browser-editable `poster/index.html` plus planning files and print checks.

## 3-Minute Quick Start

If you just want the shortest path, do this:

1. Clone the repo:

```bash
git clone https://github.com/yunyiliu/cvpr-2026-poster-skill.git
cd cvpr-2026-poster-skill
```

2. Create a workspace:

```bash
python3 cvpr-2026-poster/scripts/init_poster_project.py \
  --project-dir ./poster-workspace \
  --track main \
  --paper-id 12345 \
  --title "Your Paper Title"
```

3. Put your assets here:

- figures: `poster-workspace/assets/figures/`
- school or lab logos: `poster-workspace/assets/logos/`

4. Fill `poster-workspace/poster_brief.md`

5. Sync the brief into the editable poster:

```bash
python3 cvpr-2026-poster/scripts/sync_poster_from_brief.py \
  --project-dir ./poster-workspace
```

6. Open the editable poster:

```bash
open poster-workspace/poster/index.html
```

7. If you are using Codex or Claude Code, ask the agent to refine the generated poster.

That is the main workflow. Everything else in this README is detail and optional customization.

It is designed for two use cases:

- `Codex` / OpenAI skill workflows
- `Claude Code` style skill workflows

The skill focuses on practical poster work:

- official CVPR 2026 size and printing constraints
- converting a paper into a 5 to 10 minute poster story
- adapting the official CVPR template as a style reference
- handling missing project URLs by falling back to paper or code links
- generating reusable working files for figures, notes, and print review
- generating a self-contained editable HTML poster you can open locally

This repo now supports both:

- bundled official assets shipped inside the skill
- user-supplied template and logo overrides

## Official asset source

If you have access to the official CVPR 2026 poster assets, use this Google Drive folder as the canonical source for templates, logos, and related conference artwork:

- `https://drive.google.com/drive/folders/1oaXlMOJzWMYUiFBImMepKsZcoicpks8Z`

Recommended workflow:

- export the official poster template to `PDF` or `PPTX`
- put exported templates into `references/`
- put logos into `assets/logos/`
- mention in your prompt which file should be treated as the primary style reference

## Built-in assets and override order

The skill now ships with bundled official assets:

- `cvpr-2026-poster/assets/official/templates/CVPR MAIN & FINDINGS Poster Template.pptx`
- `cvpr-2026-poster/assets/official/templates/CVPR Workshop ONLY Poster Template.pptx`
- `cvpr-2026-poster/assets/official/logos/CVPR_Logo2_Denver 2026_Color.eps`
- `cvpr-2026-poster/assets/official/logos/CVPR_Logo2_Denver_2026_Preview.svg`

When the agent looks for style assets, use this priority:

1. user-provided workspace files
2. bundled official assets inside the skill
3. the official CVPR shared Drive folder

User-provided files always win. That means:

- if the user puts a custom template in their workspace, use that instead of the bundled one
- if the user puts custom logos in `assets/logos/`, use those instead of bundled logos
- if the user provides nothing, fall back to the bundled official template and bundled official logo

Important:

- the bundled logo is only the conference branding
- users should still put their school, lab, or company logos into `assets/logos/`
- those institution logos should be added to the poster header when appropriate

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
├── assets/
│   ├── editor/
│   │   └── editable-poster-template.html
│   └── official/
│       ├── logos/
│       └── templates/
├── references/
│   ├── cvpr-2026-spec.md
│   ├── poster-brief-template.md
│   └── print-checklist.md
└── scripts/
    ├── init_poster_project.py
    └── sync_poster_from_brief.py
```

## Install

## Which tool should I use?

This repo supports two different AI-agent environments:

- `Codex`: use this if you work in the OpenAI Codex environment and your local skills live under `~/.codex/skills/`
- `Claude Code`: use this if you work in Anthropic Claude Code and your local skills live under `.claude/skills/` or your Claude user skill directory

Use only the install path for the tool you actually use. You do not need both.

Important distinction:

- terminal commands such as `git clone`, `cp`, and `python3 .../init_poster_project.py` are run in your shell
- prompts such as `Use $cvpr-2026-poster ...` are typed inside the AI agent session after the skill is installed

This repo does not require a special shell command like `codex cvpr-2026-poster` or `claude cvpr-2026-poster`.
You install the skill first, then call it from inside your agent conversation.

### Codex

Copy `cvpr-2026-poster/` into your Codex skills directory, for example:

```bash
cp -R cvpr-2026-poster ~/.codex/skills/
```

When to use this path:

- you are already working in Codex
- you want Codex to read your poster workspace and draft the brief or outline

After copying the skill:

1. start a new Codex session
2. open the folder that contains your poster materials
3. type a prompt such as:

```text
Use $cvpr-2026-poster to turn my paper into a 4-column CVPR 2026 poster brief.
```

### Claude Code

Copy `cvpr-2026-poster/` into `.claude/skills/` in your project or user-level Claude skills directory:

```bash
mkdir -p .claude/skills
cp -R cvpr-2026-poster .claude/skills/
```

When to use this path:

- you are already working in Claude Code
- you want Claude Code to use the skill while reading your paper files and figures

After copying the skill:

1. start a new Claude Code session
2. open the project that contains your poster materials
3. type a prompt such as:

```text
Use the cvpr-2026-poster skill to adapt the official CVPR 2026 template to my paper.
```

You can also usually say:

```text
Use $cvpr-2026-poster to build a CVPR 2026 poster outline from my files.
```

## If you are not using Codex or Claude Code

You can still use the scaffold script by itself:

```bash
python3 cvpr-2026-poster/scripts/init_poster_project.py \
  --project-dir ./poster-workspace \
  --track main \
  --paper-id 12345 \
  --title "Your Paper Title"
```

In that case, you can still use:

- `init_poster_project.py`
- `sync_poster_from_brief.py`
- `poster/index.html`

So the editable poster workflow still works. The only missing part is agent-assisted refinement from Codex or Claude Code.

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
├── poster/
│   ├── index.html
│   ├── poster-config.json
│   ├── figures/
│   └── logos/
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
- an official template export in `PDF` or `PPTX` if you want to override the bundled template
- a QR target link such as arXiv, GitHub, a lab page, or a demo page
- any CVPR logo, acronym, or poster header assets exported from the official Drive folder
- your school, lab, or company logos in `assets/logos/`
If you do not provide a template, the skill will use the bundled official template for the selected track by default.

Recommended figure filenames for auto-fill:

- `overview.png` or `method.png`
- `results.png`
- `qualitative.png`

The sync script looks for these names first when filling the editable poster cards.

### 3. Fill `poster_brief.md`

At minimum, fill these fields:

- `Title`
- `Authors`
- `Affiliations`
- `QR target`
- `One-sentence takeaway`
- `Problem`
- `Core idea`
- `Main result`
- `Method bullets`
- `Results bullets`
- `Conclusion bullets`

### 4. Sync the brief into the editable poster

Run:

```bash
python3 cvpr-2026-poster/scripts/sync_poster_from_brief.py \
  --project-dir ./poster-workspace
```

This updates:

- `poster/poster-config.json`
- `poster/index.html`
- copied user logos under `poster/logos/`
- copied displayable figures under `poster/figures/`

### 5. Ask the agent to use the skill

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

### 6. What the skill should produce

The expected outputs are:

- `poster/index.html`
- `poster/poster-config.json`
- `poster_brief.md`
- `poster_outline.md`
- `print_checklist.md`
- a recommended section structure for the poster
- concrete guidance on which figures and numbers to emphasize
- automatic use of the bundled official template when no override is supplied
- a generated `poster/index.html` visual editor with room for your institution logos

### 7. Edit and export the poster

Open the generated poster directly in your browser:

```bash
open poster-workspace/poster/index.html
```

The editor is meant for layout iteration:

- resize columns
- resize card heights
- move cards between columns
- load a pasted config JSON
- save or copy the current layout config
- export the final result to `PDF`

The planning files still matter, but the repo now also ships an actual editable poster layer.

### 8. Smallest possible test

If you want to test quickly before using your real paper:

1. Run `init_poster_project.py`
2. Edit only `Title`, `Authors`, `Affiliations`, `Problem`, and `Core idea` in `poster_brief.md`
3. Run `sync_poster_from_brief.py`
4. Open `poster/index.html`

If that works, the repo is installed correctly.

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
3. Open `poster/index.html` to verify the editable poster scaffold is there.
4. Drop figures, links, and school logos into the scaffolded workspace.
5. Ask the agent to fill `poster/index.html`, `poster_brief.md`, and `poster_outline.md`.
6. Use `print_checklist.md` before exporting the final PDF.

## Notes

- The bundled CVPR 2026 spec was verified against official CVPR pages on `2026-05-13`.
- Before ordering prints, verify the latest conference page in case deadlines or upload links change.
- The skill treats Google Slides or PowerPoint templates as style references unless the user explicitly wants the final artifact to remain editable in Slides or PPT.

## Example

See [examples/cvpr-poster-brief-example.md](examples/cvpr-poster-brief-example.md) for a filled example based on a generic CVPR-style medical vision paper.

## License

MIT
