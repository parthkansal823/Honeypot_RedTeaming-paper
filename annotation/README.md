# Annotation how-to (Parth and Keshav)
1. Copy your own sheet (sheet_annotator1.csv = Parth, sheet_annotator2.csv = Keshav); open it in Excel.
2. Read RUBRIC.md first (8 labels, tie-break order).
3. Fill `label` (exactly one rubric label), `confidence` (1-3), optional `notes`, for every row. Label independently.
4. Do NOT open key.csv and do not compare with each other until both are done.
5. Optional: put LLM pre-labels in labels_llm.csv (item_id,label,confidence) from annotation_sheet.csv.
6. Save as CSV, then run `python agreement.py`; adjudicate annotation/disagreements.csv into adjudicated.csv (item_id,label) and rerun to get labels_final.csv.
