# 8 Troubleshooting and FAQ

## 8.1 Common problems

Table: Problems and fixes. {#tab:doc-trouble widths=6,10}

| Symptom | Cause and fix |
|---|---|
| The parser reports 0 sessions | Wrong parser or the file is still gzip-compressed. Use `parse_cyberlab.py` on the extracted file |
| The honeypot stops answering | A heavy command froze Cowrie's single-threaded reactor; restart the container (`run_docker.bat stop-honeypot` then `start-honeypot`) |
| Honeypot replies are cut short | The LLM backend is slow; increase the harness's response wait |
| Commands contain English sentences | Chat-format leakage; make sure commands are cut at the first `<\|` |
| Scores look too good | Check that real folds are grouped by template and that labels did not come from keyword rules |
| `agreement.py` says the sheets are blank | Fill the `label` column of both annotator sheets first |
| The Word report shows "Update field" | Open it in Word, press Ctrl+A then F9 |
| `finalize_word.ps1` cannot save | Close the report in Word (and any preview pane), then run it again |

## 8.2 Frequently asked questions

**Why not just use keyword rules as labels?** The classifier's features contain the same keywords, so it would only re-learn the rules. Rule labels are kept only as a plumbing check.

**Why are the real labels "broadcast" from templates?** Many real sessions are byte-for-byte the same script after masking. Labelling one representative per distinct sequence and copying the label to its template is consistent and saves effort; it also means the effective real sample size is 22 templates, which the results always report.

**Why macro-F1 over present classes only?** A class that the model predicts but that never appears in the test set would add a zero to the average and make the score look worse than it is.

**Are the LLM labels as good as human labels?** They agree with each other very well (κ = 0.898) and were checked by the authors, but they come from one provider and are not an independent human audit. The report lists this as the main threat to validity.

**Can I use the harness against other systems?** No. It is designed and documented for use against your own honeypot only.

**Where is the editable version of each diagram?** In `report/diagrams/*.drawio`; open them in draw.io or diagrams.net.
