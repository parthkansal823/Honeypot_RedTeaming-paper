# Project report

The UG project report (Chandigarh University format) for *Do LLM Red-Team Agents Generate Realistic Honeypot Traffic?*, built from Markdown into Microsoft Word.

| Output | File |
|---|---|
| Word report (editable) | `Project_Report.docx` |
| PDF of the same | `Project_Report.pdf` |
| Report text (source) | `md/*.md` |
| Figures used in the report | `images/*.png` |
| Editable flowcharts and UML diagrams | `diagrams/*.drawio` (open in draw.io / diagrams.net) |
| Numbers computed for the report | `data/report_stats.json`, `data/literature_corpus.csv` |
| Build scripts | `src/` |

## Editing

Edit the Markdown in `md/` and rebuild, or edit `Project_Report.docx` directly in Word. Yellow-highlighted text such as `[UID]`, `[Name of the Supervisor]` and `[MONTH YEAR]` are placeholders to fill in (Ctrl+H in Word, or `md/00_meta.md` before rebuilding).

In Word, after any change: press **Ctrl+A** then **F9** to refresh the table of contents, the lists of figures and tables, captions and cross-references. Citations such as [12] and references such as "Figure 3.2" are links: Ctrl+click jumps to the target.

Markdown conventions understood by the builder:

| Write | Result |
|---|---|
| `# 1 Introduction` | New chapter page: CHAPTER 1 / INTRODUCTION |
| `## 1.1 Title`, `### 1.1.1 Title` | Headings (they appear in the table of contents) |
| `![Caption.](images/x.png){#fig:id}` | Figure with a numbered caption below it |
| `Table: Caption. {#tab:id widths=3,5,4}` before a pipe table | Table with a numbered caption above it |
| ```` ```algorithm {#alg:id} Title ```` | Boxed pseudocode with a numbered caption |
| `$$ UnicodeMath $$ {#eq:id}` | Native, numbered Word equation |
| `[@fig:id]`, `[@tab:id]`, `[@alg:id]`, `[@eq:id]` | Cross-reference that Word keeps up to date |
| `(Author, 2020)` or `Author (2020)` | Numbered citation `[n]` linked to the reference list |
| `> text` | Shaded call-out box |

## Rebuilding

Requirements: Python 3.11 with `python-docx`, `matplotlib` and the project requirements; Microsoft Word (for the final step).

```powershell
python report\src\compute_stats.py      # report/data/report_stats.json
python report\src\make_diagrams.py      # report/diagrams/*.drawio + report/images/d*.png
python report\src\make_charts.py        # report/images/c*.png, t*.png
python report\src\make_appendix_md.py   # report/md/96_appendix_data.md
python report\src\build_report.py       # report/Project_Report.docx
powershell -ExecutionPolicy Bypass -File report\src\finalize_word.ps1 -Docx report\Project_Report.docx -Pdf
```

The last step opens the document in Word in the background, turns the equation paragraphs into native Word equations, refreshes every field and exports the PDF. Close the report in Word before running it.
