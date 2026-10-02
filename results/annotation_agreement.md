# Annotation agreement

Items labeled by both annotators: 184 of 184 (annotator1 184, annotator2 184).

## Cohen's kappa (annotator1 vs annotator2)

| subset | n | raw agreement | kappa |
|---|---|---|---|
| all | 184 | 0.935 | 0.898 |
| real | 64 | 0.953 | 0.873 |
| synthetic | 120 | 0.925 | 0.835 |

## Confusion (rows annotator1, columns annotator2)

| a1 / a2 | recon | credential_access | privilege_escalation | persistence | malware_drop | resource_hijacking |
|---|---|---|---|---|---|---|
| recon | 63 | 4 | 0 | 0 | 0 | 0 |
| credential_access | 0 | 83 | 1 | 1 | 0 | 0 |
| privilege_escalation | 1 | 0 | 1 | 0 | 0 | 0 |
| persistence | 0 | 1 | 0 | 13 | 1 | 0 |
| malware_drop | 0 | 0 | 0 | 1 | 12 | 0 |
| resource_hijacking | 0 | 0 | 0 | 0 | 2 | 0 |

## Final labels

- Items agreed: 172; adjudicated: 12; excluded (disagreement not adjudicated, or unlabeled by an annotator): 0 of 184 items (12 disagreements).
- Real sessions labeled via template broadcast: 1672; synthetic: 120.
- real label counts: recon=137, persistence=443, malware_drop=52, resource_hijacking=1040
- synthetic label counts: recon=14, credential_access=87, privilege_escalation=2, persistence=11, malware_drop=6
