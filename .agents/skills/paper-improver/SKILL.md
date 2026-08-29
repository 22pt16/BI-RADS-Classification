---
name: paper-improver
description: Use whenever the user uploads an existing research paper (PDF/LaTeX/docx) as a "base paper" together with a project repository, and wants the paper rewritten/improved using the actual code and results in that repo. Also use whenever the user asks to draft, restructure, or regenerate a research paper from a codebase into the fixed custom section format (Heading/Authors, Abstract, Introduction, Preliminaries, Related Works, Problem Statement, Proposed Work with Data Collection/Preprocessing/Model Construction/Experiments, Conclusion, Future Scope) rather than IEEE format. Covers mapping paper claims to repo evidence, finding new or better results not yet included, and producing a revised, evidence-grounded LaTeX draft with a changelog of what changed and why. Trigger this even if the user just says "improve my paper with my repo" or "write my paper in my format" without naming the skill.
---

# Paper Improver Skill

## Mandate
- The uploaded paper (if any) is a base draft, not ground truth. Every number and claim must be checked against the codebase before it is kept, changed, or cut.
- The **final LaTeX output must always follow the custom section format defined below** — never IEEE format, and never any other conference/journal template — unless the user explicitly asks for a different format in this conversation.
- Every improvement (new result, stronger baseline, better number, new ablation) must trace to a real file in the repo: a results table, log, metrics JSON, notebook output, or script. Never invent or "smooth over" a number.
- Track every change in a changelog so the user can see exactly what changed, why, and what evidence backs it.

## Required Output Format (custom — not IEEE)

The final LaTeX draft must be organized into exactly these sections, in this order. Use a plain, readable document class (e.g. `article` at 11pt, single or 1.5 spacing) — not an IEEEtran/ACM/Springer template — unless told otherwise.

1. **Page 1**
   - **Heading (Title)**: Must reflect *all* aspects of the tech/methods actually used in the work (e.g. model type, technique, domain) — not a vague or shortened title.
   - **Authors**: All author details as given by the user (names, affiliations, emails, etc.). If not provided, insert a clearly marked placeholder (`% TODO: author details`) rather than inventing names.

2. **Abstract** — a single paragraph that must cover, in this order:
   - Motivation
   - The proposed novelty of the paper
   - How the experiment was conducted
   - Dataset(s) used and relevant details
   - Experimental measures/metrics and values (results), if available
   - How the approach outperforms others
   - What baselines/methods it is compared against

3. **Introduction**

4. **Preliminaries / Background**

5. **Related Works**

6. **Problem Statement**
   - What is given (inputs/assumptions)
   - Objective (e.g. "Construct a model using n-grams to …")

7. **Proposed Work** (step-wise, each as its own subsection)
   - Data Collection
   - Preprocessing
   - Model Construction
   - Experiments
     - Setup (data split, hyperparameters, fine-tuning approach and what was tuned, evaluation measures and technique)
     - Results
     - Findings / Discussions (Inference)
     - Conclusion of this section, including a block diagram of the overall pipeline/architecture (as a TikZ figure or a clearly labeled `\includegraphics` placeholder if a diagram file exists in the repo)

8. **Conclusion**
   - Overall summary
   - Pros
   - Limitations

9. **Future Scope**

Do not add, remove, rename, or reorder these top-level sections. Do not substitute IEEE-style sections (e.g. "Methodology", "Results and Discussion" merged, "Literature Survey" instead of "Related Works", etc.) — map any equivalent content from the base paper into the section names above.

## Process
1. **Read everything in the repository** before writing a single line of the paper: source code, config files, notebooks, results/metrics files (CSV/JSON/logs), checkpoints' associated logs, README, existing figures/tables, and any prior paper draft. Do not sample a subset and assume — walk the full repo.
2. If a base paper was uploaded, read it fully and extract: claims, key numbers, tables, figures, related-work list, stated contributions.
3. Inventory the codebase (`scripts/inventory_repo.py` gives a deterministic first pass, if present) to catalog: results/metrics files, experiment logs, checkpoints, config files, notebooks, existing figures/tables.
4. Build a claim-evidence map. For each claim/number (from the base paper, or that you plan to state), find matching evidence in the repo and mark it:
   - `matches` — repo confirms the number
   - `outdated` — repo has a newer/better number
   - `missing` — no evidence found in the repo
   - `contradicted` — repo evidence disagrees
5. Identify improvement opportunities: results in the repo not yet written up (new experiments, ablations, baselines, larger sweeps), and any stale numbers.
6. Propose a section-by-section plan mapped onto the **Required Output Format** above — list what goes into each of the 9 sections and the evidence backing each factual claim — before writing full prose.
7. Write the paper as a single self-contained **LaTeX document** in the required format above. Regenerate any figures/tables from the underlying data or plotting scripts rather than hand-editing image files; use `booktabs`-style tables for results.
8. If revising an existing paper, apply changes to a **copy** — never overwrite the user's original upload.
9. Flag anything that could not be verified (from either the base paper or a claim you were tempted to add) instead of silently keeping or dropping it.
10. Deliver: the `.tex` file (and compiled `.pdf` if a LaTeX toolchain is available), a changelog (what changed + why + evidence source), and a list of open gaps needing human judgment (e.g. missing author details, unverifiable claims).

## Evidence rules
- A claim only counts as supported if you can point to a specific file (and ideally line/cell/column) in the repo.
- If there's no repo evidence for something the base paper already claims, don't delete it silently — flag it in the changelog as "unverified, kept from original" and let the user decide.
- Never fabricate citations, ablations, baselines, or numbers to fill a gap in any section — including the Abstract's "how we outperform others" claim.
- Generated/illustrative figures (e.g. a redrawn architecture/block diagram for the Proposed Work conclusion) are fine for exposition but must never stand in for a results figure — those must come from real data.

## Reference
`scripts/inventory_repo.py` — deterministic repo scan for results/metrics/log-like files, if bundled with this skill. Run this before manually reviewing the codebase; don't rely on ad hoc browsing to find evidence.

---

## Invoking this skill in Google Antigravity

Antigravity skills are plain Markdown files with YAML frontmatter, read directly off disk — no separate registration step beyond placing the file correctly.

1. **Choose a scope:**
   - **Project/workspace scope** (recommended for this skill, since it's tied to a specific repo + paper): place this file at
     `<project-root>/.agents/skills/paper-improver/SKILL.md`
   - **Global scope** (available across all your projects): place it at
     `~/.gemini/config/skills/paper-improver/SKILL.md`
2. Keep any bundled helper scripts alongside it, e.g. `.agents/skills/paper-improver/scripts/inventory_repo.py`.
3. Open the project in Antigravity (IDE or CLI) with your repo and the base paper (if any) present in the workspace.
4. You generally don't need to invoke it by name — Antigravity's agent reads the `description` field and decides on its own when a task matches (e.g. asking "revise my paper using the results in this repo, in my custom format"). To force it, reference it explicitly, e.g. type `/paper-improver` in the Antigravity CLI/TUI, or say "use the paper-improver skill."
5. The agent will read the SKILL.md body only once it decides the skill is relevant, then follow the Process above against your actual repo files.