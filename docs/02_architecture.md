# 2 System Architecture

## 2.1 The three blocks

The system has three blocks ([@fig:doc-arch]):

1. **Synthetic data generation** in our own testbed: an attacker harness, three attacker models behind one API, and Cowrie running either its built-in shell or an LLM-written shell.
2. **Data preparation**: a streaming parser for the CyberLab export and a shared normalisation library used for both corpora.
3. **Analysis and outputs**: the label-free comparison, the annotation tools, the transfer experiment, and the scripts that write tables, figures, the paper and the report.

![System architecture.](images/d01_system_architecture.png){#fig:doc-arch}

## 2.2 Data flow

[@fig:doc-dfd] shows how files move between processes. Each data store is a folder in the repository: `logs/`, `normalized/`, `annotation/` and `results/`.

![Data-flow diagram, level 1.](images/d23_dfd_level1.png){#fig:doc-dfd}

## 2.3 Components

![Component diagram.](images/d24_component.png){#fig:doc-components}

The most important design rule is visible in [@fig:doc-components]: every analysis component imports the same `session_features` library, so synthetic and real sessions are always normalised, split and tagged in exactly the same way.

## 2.4 Deployment

![Docker deployment of the testbed.](images/d10_deployment_docker.png){#fig:doc-deploy}

The honeypot and the analysis code run as two Docker containers on a private bridge network ([@fig:doc-deploy]). Only the analysis container needs internet access, to reach the model API; the Cowrie container reaches its own model API only when the LLM backend is switched on.

## 2.5 Repository layout

Table: Repository layout. {#tab:doc-repo widths=6,10}

| Path | Contents |
|---|---|
| `better_ai_attacker.py` | Attacker harness used for the study |
| `cowrie_etc/cowrie.cfg` | Honeypot configuration (backend switch) |
| `docker-compose.yml`, `Dockerfile.attacker`, `run_docker.bat` | Containers and Windows helper |
| `logs/` | 120 raw synthetic session logs |
| `parse_cyberlab.py` | Parser for the CyberLab export |
| `session_features.py` | Shared normalisation, verbs, tactic tags, templates |
| `normalized/` | Normalised synthetic and real corpora |
| `domain_shift.py` | Label-free comparison |
| `make_annotation_sheet.py`, `agreement.py`, `annotation/` | Annotation kit and labels |
| `train_eval_classifier.py` | Four-quadrant transfer experiment |
| `generate_paper_tables.py`, `make_figures.py` | Paper tables and figures |
| `results/`, `figures/` | All reported numbers and paper figures |
| `paper/` | Springer LNNS paper (Overleaf project) |
| `report/` | Project report: Markdown, figures, draw.io sources, build scripts |
| `docs/` | This documentation |
