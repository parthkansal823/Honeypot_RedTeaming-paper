# Project documentation

Documentation for the LLM red-team vs. real honeypot traffic project. Read the Markdown files here, or open `Project_Documentation.docx` (built from them) in Word.

| File | Contents |
|---|---|
| [01_overview.md](01_overview.md) | What the project does, the short answer, key numbers, safety |
| [02_architecture.md](02_architecture.md) | Blocks, data flow, components, deployment, repository layout |
| [03_installation.md](03_installation.md) | Requirements, setup, dataset download, API keys |
| [04_usage.md](04_usage.md) | Running every pipeline step |
| [05_data_formats.md](05_data_formats.md) | Log, session, annotation and result file formats |
| [06_script_reference.md](06_script_reference.md) | Options and functions of every script |
| [07_results.md](07_results.md) | All headline results in one place |
| [08_troubleshooting.md](08_troubleshooting.md) | Common problems and FAQ |

The full write-up is the project report in `../report/` (`Project_Report.docx` / `.pdf`), and the conference paper is in `../paper/`.

Rebuild this document with:

```powershell
python report\src\build_report.py --docs
powershell -ExecutionPolicy Bypass -File report\src\finalize_word.ps1 -Docx docs\Project_Documentation.docx -Pdf
```
