"""
Builds every flowchart / block diagram used in the report.

Each diagram is written twice from one spec:
  report/diagrams/<name>.drawio   editable source (open in draw.io / diagrams.net)
  report/images/<name>.png        picture embedded in the Word report

The specs live in diagrams_a4.py (project flowcharts and block diagrams) and
diagrams_software.py (UML and data-flow diagrams); all are A4-portrait sized.

Run from the repository root:
    python report/src/make_diagrams.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagrams_a4 import (  # noqa: E402
    d01_architecture, d02_graphical_abstract, d03_session_flow, d04_recovery, d05_parser, d06_normalization,
    d07_label_free, d08_annotation, d09_quadrants, d10_deployment, d11_designs, d12_timeline, d13_data_model,
    d14_method_overview, d15_tiebreak, d16_concepts, d17_wbs, d18_harness_modules, d19_drain, d20_validation)
from diagrams_software import (  # noqa: E402
    d21_use_case, d22_dfd0, d23_dfd1, d24_component, d25_class, d26_sequence, d27_state, d28_sdlc)

DRAWIO = ROOT / "report" / "diagrams"
PNG = ROOT / "report" / "images"

ALL = [d01_architecture, d02_graphical_abstract, d03_session_flow, d04_recovery, d05_parser, d06_normalization,
       d07_label_free, d08_annotation, d09_quadrants, d10_deployment, d11_designs, d12_timeline, d13_data_model,
       d14_method_overview, d15_tiebreak, d16_concepts, d17_wbs, d18_harness_modules, d19_drain, d20_validation,
       d21_use_case, d22_dfd0, d23_dfd1, d24_component, d25_class, d26_sequence, d27_state, d28_sdlc]


def main():
    for fn in ALL:
        dg = fn().save(DRAWIO, PNG)
        print("wrote", dg.name)


if __name__ == "__main__":
    main()
