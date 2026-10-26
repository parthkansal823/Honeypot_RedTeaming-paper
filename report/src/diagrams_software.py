"""
Software-engineering diagrams for the report (A4 portrait, at most ~590 px wide):
use case, data-flow (levels 0 and 1), component, class, sequence, state machine
and development life cycle. Each is written as .drawio + .png by make_diagrams.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagram_lib import Diagram  # noqa: E402

EXT = {"fill": "#EEEEEE", "stroke": "#666666"}     # external entities in data-flow diagrams
STORE = {"fill": "#FFFFFF", "stroke": "#9673A6"}   # data stores


def d21_use_case():
    d = Diagram("d21_use_case", 590, 640, "Use case diagram")
    d.group("sys", 150, 10, 435, 620, "Research pipeline (system boundary)")
    d.node("res", 30, 70, 50, 80, "Researcher", "actor", bold=True)
    d.node("ann", 30, 320, 50, 80, "LLM annotators", "actor", bold=True)
    d.node("rdr", 30, 520, 50, 80, "Reader /\nreviewer", "actor", bold=True)
    cases = ["Configure honeypot (static or LLM)", "Run attacker batch (20 per cell)",
             "Parse and normalise real data", "Run label-free comparison", "Build blind annotation sheets",
             "Label items and adjudicate", "Compute agreement and labels", "Run transfer experiment",
             "Generate tables, figures, report", "Read results and reproduce"]
    for i, c in enumerate(cases):
        d.node(f"u{i}", 190, 40 + i * 58, 370, 44, c, "usecase", font=10.5)
    for i in (0, 1, 2, 3, 4, 6, 7, 8):
        d.edge("res", f"u{i}", exit="r", entry="l", arrow=False)
    d.edge("ann", "u5", exit="r", entry="l", arrow=False)
    d.edge("rdr", "u9", exit="r", entry="l", arrow=False)
    return d


def d22_dfd0():
    d = Diagram("d22_dfd_level0", 590, 470, "Data-flow diagram, level 0 (context)")
    d.node("p0", 190, 165, 210, 130, "0\nLLM red-team vs\nreal traffic pipeline", "usecase", bold=True)
    d.node("res", 10, 20, 170, 56, "Researcher", "plain", bold=True, **EXT)
    d.node("llm", 410, 20, 170, 56, "LLM providers\n(AWS Bedrock)", "plain", bold=True, **EXT)
    d.node("ann", 430, 205, 150, 50, "LLM annotators", "plain", bold=True, **EXT)
    d.node("rdr", 10, 205, 150, 50, "Reader / reviewer", "plain", bold=True, **EXT)
    d.node("zen", 10, 390, 170, 56, "CyberLab dataset\n(Zenodo)", "plain", bold=True, **EXT)
    d.node("cow", 410, 390, 170, 56, "Cowrie honeypot\n(own testbed)", "plain", bold=True, **EXT)
    d.edge("res", "p0", "configs, run commands", exit="b", entry="t", exit_f=0.4, entry_f=0.3)
    d.edge("p0", "res", "results, report", exit="l", entry="b", exit_f=0.2, entry_f=0.8, points=[(136, 191)])
    d.edge("p0", "llm", "prompts", exit="t", entry="b", exit_f=0.7, entry_f=0.2, points=[(337, 120), (444, 120)])
    d.edge("llm", "p0", "commands", exit="b", entry="r", entry_f=0.2, points=[(525, 191)])
    d.edge("p0", "ann", "blind items", exit="r", entry="l", exit_f=0.45, entry_f=0.3)
    d.edge("ann", "p0", "labels", exit="l", entry="r", exit_f=0.8, entry_f=0.65)
    d.edge("p0", "rdr", "documents", exit="l", entry="r", exit_f=0.5)
    d.edge("zen", "p0", "raw sessions", exit="r", entry="b", entry_f=0.3, points=[(253, 418)])
    d.edge("p0", "cow", "SSH commands", exit="b", entry="l", exit_f=0.7, entry_f=0.3, points=[(337, 407)])
    d.edge("cow", "p0", "shell output", exit="t", entry="r", exit_f=0.5, entry_f=0.8, points=[(495, 269)])
    return d


def d23_dfd1():
    d = Diagram("d23_dfd_level1", 590, 760, "Data-flow diagram, level 1")
    d.node("e1", 10, 10, 250, 50, "Cowrie + LLM APIs", "plain", bold=True, **EXT)
    d.node("p1", 330, 8, 250, 56, "1.0  Generate synthetic\nsessions")
    d.node("e2", 10, 95, 250, 50, "CyberLab (Zenodo)", "plain", bold=True, **EXT)
    d.node("d1", 330, 98, 250, 40, "D1  logs/ (raw session JSON)", "plain", **STORE)
    d.node("p2", 10, 175, 250, 56, "2.0  Parse real data")
    d.node("p3", 330, 175, 250, 56, "3.0  Convert synthetic logs")
    d.node("d2", 170, 265, 250, 40, "D2  normalized/*.jsonl", "plain", **STORE)
    d.node("p4", 10, 340, 250, 56, "4.0  Normalise and build\ntemplates")
    d.node("p5", 330, 340, 250, 56, "5.0  Label-free comparison")
    d.node("p6", 10, 430, 250, 56, "6.0  Blind annotation and\nagreement")
    d.node("d3", 330, 438, 250, 40, "D3  annotation/ (labels)", "plain", **STORE)
    d.node("p7", 10, 520, 250, 56, "7.0  Four-quadrant transfer\nexperiment")
    d.node("d4", 330, 528, 250, 40, "D4  results/ (md + json)", "plain", **STORE)
    d.node("p8", 170, 610, 250, 56, "8.0  Tables, figures,\npaper and report")
    d.node("e3", 170, 700, 250, 46, "Reader / reviewer", "plain", bold=True, **EXT)
    d.edge("p1", "e1", "commands", exit="l", entry="r", exit_f=0.3, entry_f=0.3)
    d.edge("e1", "p1", "output", exit="r", entry="l", exit_f=0.75, entry_f=0.75)
    d.edge("p1", "d1", "session logs")
    d.edge("d1", "p3")
    d.edge("e2", "p2", "raw file")
    d.edge("p2", "d2", "real sessions", exit="b", entry="t", entry_f=0.2)
    d.edge("p3", "d2", "synthetic", exit="b", entry="t", entry_f=0.8)
    d.edge("d2", "p4", exit="b", entry="t", exit_f=0.2)
    d.edge("d2", "p5", exit="b", entry="t", exit_f=0.8)
    d.edge("p4", "p5", "templates", exit="r", entry="l")
    d.edge("p4", "p6", "items")
    d.edge("p6", "d3", "labels", exit="r", entry="l")
    d.edge("d3", "p7", exit="l", entry="r", points=[(295, 458), (295, 548)])
    d.edge("p7", "d4", "metrics", exit="r", entry="l")
    d.edge("p5", "d4", exit="r", entry="r", points=[(586, 368), (586, 548)])
    d.edge("d4", "p8", exit="b", entry="t", entry_f=0.8, points=[(455, 590), (370, 590)])
    d.edge("p8", "e3", "documents")
    return d


def d24_component():
    d = Diagram("d24_component", 590, 620, "Component diagram")
    d.group("g1", 5, 5, 580, 150, "Testbed layer")
    d.node("har", 20, 40, 170, 100, "«component»\nAttacker harness\n(Python, Paramiko)")
    d.node("cow", 210, 40, 170, 100, "«component»\nCowrie honeypot\n(Docker container)", "terminal")
    d.node("llm", 400, 40, 170, 100, "«external»\nLLM APIs\n(AWS Bedrock)", "cloud")
    d.group("g2", 5, 170, 580, 250, "Analysis layer")
    d.node("par", 20, 205, 170, 90, "«component»\nCyberLab parser")
    d.node("sf", 210, 205, 170, 90, "«library»\nsession_features", "highlight")
    d.node("ds", 400, 205, 170, 90, "«component»\nLabel-free analysis")
    d.node("ann", 20, 315, 170, 90, "«component»\nAnnotation tools")
    d.node("tr", 210, 315, 170, 90, "«component»\nTransfer experiment")
    d.node("tab", 400, 315, 170, 90, "«component»\nTables and figures")
    d.group("g3", 5, 435, 580, 80, "Third-party libraries")
    for k, (nid, lab) in enumerate((("sk", "scikit-learn"), ("sp", "SciPy / NumPy"), ("mpl", "Matplotlib"),
                                    ("pk", "Paramiko"))):
        d.node(nid, 20 + k * 140, 467, 130, 38, lab, "plain")
    d.group("g4", 5, 530, 580, 80, "Outputs")
    d.node("res", 20, 562, 260, 40, "results/ (md + json)", "data")
    d.node("rep", 310, 562, 260, 40, "Report builder (python-docx)")
    d.edge("har", "cow", "SSH", exit="r", entry="l")
    d.edge("har", "llm", "HTTPS", exit="t", entry="t", points=[(105, 30), (485, 30)])
    d.edge("cow", "llm", exit="r", entry="l", dashed=True)
    d.edge("ds", "sf", "imports", exit="l", entry="r", dashed=True)
    d.edge("tr", "sf", "imports", exit="t", entry="b", dashed=True)
    d.edge("ann", "sf", exit="r", entry="l", dashed=True, entry_f=0.75, points=[(200, 360), (200, 272)])
    return d


def d25_class():
    d = Diagram("d25_class_diagram", 590, 700, "Class diagram")
    d.node("cfg", 10, 10, 280, 190, "RunConfig «dataclass»\nhost: str;  port: int\nprovider: str;  model: str\n"
           "max_turns: int = 25\nmax_session_seconds: float = 600\nresponse_wait: float = 1.5\n"
           "max_response_wait: float = 20\nmax_session_retries: int = 3\nrecovery_max_wait: float = 90", "entity")
    d.node("hp", 300, 10, 280, 150, "HoneypotSession\nclient: SSHClient;  shell: Channel\nbanner: str\n"
           "+ _drain(idle, max_wait) → str\n+ send_command(cmd) → (str, float)\n+ close()", "entity")
    d.node("run", 300, 190, 280, 140, "session runner «functions»\n+ run_session(cfg, i) → dict\n"
           "+ run_session_with_recovery(cfg, i)\n+ ensure_honeypot_healthy(cfg)\n+ save_log(log, dir) → Path", "entity")
    d.node("llm", 10, 230, 280, 140, "LLM client «functions»\n+ call_llm(provider, model, …) → str\n"
           "+ call_anthropic / call_openai\n+ call_gemini / call_bedrock\n+ call_bedrock_openai / call_local", "entity")
    d.node("sf", 10, 400, 280, 170, "session_features «module»\n+ normalize_cmd(cmd) → str\n+ segments(cmd) → list\n"
           "+ verb(segment) → str\n+ session_tactics(s) → set\n+ template_key(s) → tuple\n+ strip_chat_leak(cmd) → str", "entity")
    d.node("ds", 300, 360, 280, 130, "domain_shift «module»\n+ corpus_stats(sessions)\n+ jsd_with_ci(a, b, rng)\n"
           "+ c2st_auc(syn, real, text_fn)\n+ tactic_shares(sessions)", "entity")
    d.node("tr", 300, 520, 280, 130, "train_eval_classifier «module»\n+ fit_predict(train, test, y)\n"
           "+ rule_label(s)  (plumbing only)\n+ row(…) → metrics\n+ main(): Q1–Q4", "entity")
    d.node("ag", 10, 600, 280, 90, "agreement «module»\n+ kappa(x, y, ids)\n+ main(): final labels", "entity")
    d.edge("run", "cfg", "reads", exit="l", entry="r", dashed=True, exit_f=0.2, entry_f=0.75, points=[(295, 218), (295, 152)])
    d.edge("run", "hp", "creates", exit="t", entry="b")
    d.edge("run", "llm", "calls", exit="l", entry="r", exit_f=0.7)
    d.edge("ds", "sf", "imports", exit="l", entry="r", dashed=True, entry_f=0.2)
    d.edge("tr", "sf", "imports", exit="l", entry="r", dashed=True, exit_f=0.3, entry_f=0.75)
    d.edge("ag", "sf", "imports", exit="t", entry="b", dashed=True)
    return d


def d26_sequence():
    d = Diagram("d26_sequence", 590, 620, "Sequence diagram of one session")
    heads = [("cli", "Researcher\n(CLI)"), ("har", "Harness"), ("llm", "LLM API"), ("cow", "Cowrie"), ("log", "Log file")]
    xs = [60, 177, 295, 413, 530]
    for (hid, lab), x in zip(heads, xs):
        d.node(hid, x - 52, 10, 104, 40, lab, "plain", bold=True, font=10.5, fill="#DAE8FC", stroke="#6C8EBF")
        d.node(f"{hid}_t", x, 50, 1, 1, "", "anchor")
        d.node(f"{hid}_b", x, 600, 1, 1, "", "anchor")
        d.edge(f"{hid}_t", f"{hid}_b", exit="b", entry="t", dashed=True, arrow=False)
    d.group("loop", 125, 195, 340, 205, "loop  [until DONE, a limit or an error]")
    col = dict(zip([h for h, _ in heads], xs))
    msgs = [("cli", "har", "start batch (config)", 75, False), ("har", "cow", "probe SSH banner", 110, False),
            ("cow", "har", "SSH-2.0 banner", 140, True), ("har", "cow", "open SSH shell", 172, False),
            ("har", "llm", "prompt + transcript", 225, False), ("llm", "har", "one command", 258, True),
            ("har", "cow", "send command", 300, False), ("cow", "har", "output (1.5 s quiet)", 335, True),
            ("har", "har", "", 0, False),
            ("har", "llm", "prompt + transcript", 435, False), ("llm", "har", "DONE", 468, True),
            ("har", "log", "save session JSON", 510, False), ("har", "cli", "status line", 550, True)]
    for k, (a, b, lab, y, ret) in enumerate(msgs):
        if a == b:
            continue
        d.node(f"m{k}a", col[a], y, 1, 1, "", "anchor")
        d.node(f"m{k}b", col[b], y, 1, 1, "", "anchor")
        d.edge(f"m{k}a", f"m{k}b", lab, exit="r" if col[b] > col[a] else "l",
               entry="l" if col[b] > col[a] else "r", dashed=ret)
    d.node("rec", 182, 365, 150, 26, "record turn", "note", font=10)
    return d


def d27_state():
    d = Diagram("d27_state_machine", 590, 640, "Session state machine")
    d.node("ini", 285, 10, 20, 20, "", "initial")
    d.node("pro", 215, 50, 160, 40, "Probing honeypot", "terminal")
    d.node("con", 215, 120, 160, 40, "Connected", "terminal")
    d.node("wai", 215, 190, 160, 40, "Waiting for LLM", "terminal")
    d.node("run", 215, 260, 160, 40, "Running command", "terminal")
    d.node("rec", 215, 330, 160, 40, "Recording turn", "terminal")
    d.node("cf", 10, 50, 170, 36, "connection_failed", "io", font=10.5)
    outs = [("o1", 130, "completed"), ("o2", 175, "attacker_refused"), ("o3", 220, "llm_error"),
            ("o4", 262, "connection_lost"), ("o5", 312, "max_turns / timed_out"), ("o6", 358, "honeypot_unresponsive")]
    for oid, y, lab in outs:
        d.node(oid, 410, y, 170, 36, lab, "io", font=10.5)
    d.node("fin", 284, 590, 22, 22, "", "final")
    d.edge("ini", "pro")
    d.edge("pro", "con", "banner ok")
    d.edge("con", "wai", "send prompt")
    d.edge("wai", "run", "command")
    d.edge("run", "rec", "output")
    d.edge("rec", "wai", "next turn", exit="l", entry="l", points=[(195, 350), (195, 210)], label_pos=0.5)
    d.edge("pro", "cf", "no banner (90 s)", exit="l", entry="r")
    for oid, f, x, lab in (("o1", 0.2, 385, "DONE"), ("o2", 0.5, 393, "refusal"), ("o3", 0.8, 401, "3 failures")):
        y = 190 + 40 * f
        d.edge("wai", oid, lab, exit="r", entry="l", exit_f=f, points=[(x, y), (x, d.nodes[oid].cy)], label_pos=0.2)
    d.edge("run", "o4", "socket closed", exit="r", entry="l")
    d.edge("rec", "o5", "limit", exit="r", entry="l", exit_f=0.25)
    d.edge("rec", "o6", "2 stalls", exit="r", entry="l", exit_f=0.75)
    for oid, _, _ in outs:
        d.edge(oid, "fin", exit="r", entry="r", points=[(586, d.nodes[oid].cy), (586, 601)])
    d.edge("cf", "fin", exit="l", entry="l", points=[(5, 68), (5, 601)])
    return d




def d28_sdlc():
    d = Diagram("d28_sdlc", 590, 440, "Iterative development life cycle")
    stages = [("pl", 215, 10, "1  Plan"), ("de", 420, 110, "2  Design"), ("bu", 420, 260, "3  Build"),
              ("ru", 215, 360, "4  Run experiments"), ("an", 10, 260, "5  Analyse"), ("rv", 10, 110, "6  Review, refine")]
    for sid, x, y, lab in stages:
        d.node(sid, x, y, 160, 60, lab, "process", bold=True)
    d.edge("pl", "de", exit="r", entry="t")
    d.edge("de", "bu")
    d.edge("bu", "ru", exit="b", entry="r")
    d.edge("ru", "an", exit="l", entry="b")
    d.edge("an", "rv")
    d.edge("rv", "pl", exit="t", entry="l")
    d.node("it", 180, 120, 230, 220, "Iterations in this project\n\n1  fixed wait → idle-timeout read\n"
           "2  marker injection → removed\n3  keyword labels → dual-LLM\n4  random split → GroupKFold\n"
           "5  IEEE paper → Springer LNNS", "note", align="left", font=10.5)
    return d
