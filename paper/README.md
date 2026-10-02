# Paper source — how to edit and rebuild

`main.tex` (IEEEtran conference format) + `references.bib` (25 verified references) + figures.

## Edit on Overleaf (easiest)
1. Overleaf → New Project → Upload Project → choose `honeypot_paper_overleaf.zip`.
2. Set the compiler to pdfLaTeX (default). Click Recompile.
3. Edit `main.tex`. Figures are found automatically through `\graphicspath`.

## Edit locally
```
tectonic paper/main.tex          # or: latexmk -pdf main.tex (inside paper/)
```
Figures are read from `../figures/` (repo) or `figures/` (Overleaf zip).

## Where the numbers come from
Every number in the paper is copied from a file in `../results/`. If you change data or labels, re-run the pipeline (see the repo README), then update the matching numbers:

| Paper element | Source file |
| :-- | :-- |
| Table I (attackers, static vs. LLM honeypot) | `results/tables_1_2.md`, `results/domain_shift.md` (Table 4e) |
| Domain-shift numbers (AUC, JSD, tactic shares) | `results/domain_shift.md` |
| Table II (transfer matrix, label counts) | `results/table3_transfer.md` |
| Annotation agreement (kappa) | `results/annotation_agreement.md` |
| Figures | `python make_figures.py` → `figures/` |

`references_verification.md` lists how each reference was checked online.
Still to fill in: author affiliation ("Affiliation TBD" in `main.tex`).
