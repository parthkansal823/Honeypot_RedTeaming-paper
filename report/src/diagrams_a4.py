"""
A4-portrait layouts for the report's block diagrams.

Every canvas here is at most 590 px wide, i.e. 15.5 cm (the A4 text width) at
96 px per inch, so each diagram is placed upright at its natural size and its
labels print at about 9.5 pt. make_diagrams.py uses these functions in place
of its wide originals.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagram_lib import Diagram  # noqa: E402
from session_features import normalize_cmd, segments, session_tactics, verb  # noqa: E402


def d03_session_flow():
    d = Diagram("d03_attacker_session_flowchart", 596, 822, "Attacker session loop")
    d.node("start", 205, 8, 170, 30, "Start session", "terminal")
    d.node("probe", 205, 50, 170, 56, "SSH banner\nanswers?", "decision")
    d.node("rec", 8, 50, 165, 46, "Restart or wait\nfor watchdog")
    d.node("recok", 16, 110, 150, 56, "Back in\n90 s?", "decision")
    d.node("cf", 8, 182, 165, 34, "connection_failed", "io")
    d.node("conn", 195, 118, 190, 38, "Open SSH shell,\nread banner")
    d.node("lim", 205, 168, 170, 56, "Turn or time\nlimit hit?", "decision")
    d.node("ask", 195, 236, 190, 38, "Ask the attacker LLM\nfor one command")
    d.node("err", 205, 286, 170, 56, "LLM failed\n3 times?", "decision")
    d.node("done", 205, 354, 170, 56, "Reply is\nDONE?", "decision")
    d.node("ref", 205, 422, 170, 56, "Looks like\na refusal?", "decision")
    d.node("send", 195, 490, 190, 38, "Send command, read\nuntil 1.5 s quiet")
    d.node("lost", 205, 540, 170, 56, "Socket\nclosed?", "decision")
    d.node("log", 195, 608, 190, 38, "Record turn; output\nis the next context")
    d.node("stall", 205, 658, 170, 56, "2 empty replies\nin a row?", "decision")
    statuses = [("s1", "lim", "max_turns / timed_out"), ("s2", "err", "llm_error"), ("s3", "done", "completed"),
                ("s4", "ref", "attacker_refused"), ("s5", "lost", "connection_lost"),
                ("s6", "stall", "honeypot_unresponsive")]
    for sid, dec, lab in statuses:
        d.node(sid, 400, d.nodes[dec].cy - 16, 180, 32, lab, "io", font=10.5)
    d.node("save", 400, 736, 180, 34, "Save session JSON")
    d.node("end", 410, 784, 160, 30, "End", "terminal")
    d.edge("start", "probe")
    d.edge("probe", "conn", "yes")
    d.edge("probe", "rec", "no", exit="l", entry="r", entry_f=0.45)
    d.edge("rec", "recok")
    d.edge("recok", "conn", "yes", exit="r", entry="l")
    d.edge("recok", "cf", "no")
    d.edge("cf", "save", exit="b", entry="l", points=[(90, 753)])
    for a, b, lab in (("conn", "lim", ""), ("lim", "ask", "no"), ("ask", "err", ""), ("err", "done", "no"),
                      ("done", "ref", "no"), ("ref", "send", "no"), ("send", "lost", ""), ("lost", "log", "no"),
                      ("log", "stall", "")):
        d.edge(a, b, lab)
    d.edge("stall", "lim", "no", exit="l", entry="l", points=[(182, 686), (182, 196)], label_pos=0.03)
    for sid, dec, _ in statuses:
        d.edge(dec, sid, "yes", exit="r", entry="l")
        d.edge(sid, "save", exit="r", entry="r", points=[(590, d.nodes[sid].cy), (590, 753)])
    d.edge("save", "end")
    return d


def d04_recovery():
    d = Diagram("d04_recovery_flowchart", 590, 550, "Session retry and recovery")
    d.node("st", 195, 8, 200, 32, "Next session", "terminal")
    d.node("probe", 175, 54, 240, 44, "Probe SSH banner\n(raw socket, 5 s)")
    d.node("ok", 210, 112, 170, 58, "Banner\nreceived?", "decision")
    d.node("fix", 410, 104, 172, 74, "Restart over admin\nSSH (--vm-host), else\nwait for watchdog")
    d.node("back", 426, 196, 140, 58, "Back in\n90 s?", "decision")
    d.node("give", 410, 276, 172, 44, "Give up:\nconnection_failed", "io")
    d.node("run", 175, 198, 240, 44, "run_session():\nthe turn loop")
    d.node("infra", 200, 258, 190, 64, "Infrastructure\nfailure?", "decision")
    d.node("why", 8, 196, 160, 52, "infrastructure = failed,\nunresponsive, lost", "note", font=10)
    d.node("keep", 8, 266, 160, 52, "Keep log as data\n(completed, refused)", "io", font=10.5)
    d.node("left", 210, 344, 170, 58, "Retries left?\n(max 3)", "decision")
    d.node("retry", 420, 350, 160, 48, "Save attempt,\nwait 3 s, retry")
    d.node("ex", 185, 426, 210, 44, "Save last log\n(retries used up)", "io")
    d.node("end", 195, 500, 200, 32, "Session finished", "terminal")
    d.edge("st", "probe")
    d.edge("probe", "ok")
    d.edge("ok", "run", "yes")
    d.edge("ok", "fix", "no", exit="r", entry="l")
    d.edge("fix", "back")
    d.edge("back", "run", "yes", exit="l", entry="r")
    d.edge("back", "give", "no")
    d.edge("run", "infra")
    d.edge("infra", "keep", "no", exit="l", entry="r")
    d.edge("infra", "left", "yes")
    d.edge("left", "retry", "yes", exit="r", entry="l")
    d.edge("retry", "probe", exit="r", entry="r", points=[(586, 374), (586, 76)])
    d.edge("left", "ex", "no")
    d.edge("ex", "end")
    d.edge("keep", "end", exit="b", entry="l", exit_f=0.19, points=[(38, 516)])
    d.edge("give", "end", exit="l", entry="r", points=[(402, 298), (402, 516)])
    return d


def d05_parser():
    d = Diagram("d05_cyberlab_parser_flowchart", 590, 700, "CyberLab parser")
    d.node("in", 145, 8, 300, 50, "cowrie_2019-11-15.json\n(one JSON array, about 600 MB)", "data")
    d.node("rd", 145, 76, 300, 40, "Read ONE line; strip '[' ',' ']'")
    d.node("js", 210, 130, 170, 58, "Valid JSON?", "decision")
    d.node("skip", 420, 140, 140, 38, "Skip the line", "io")
    d.node("blk", 145, 204, 300, 40, "For each {session_id: [events]}")
    d.node("mrg", 145, 258, 300, 44, "Get or create the session record\n(one session can repeat)")
    d.node("srt", 145, 316, 300, 36, "Sort its events by timestamp")
    d.node("map", 35, 368, 520, 150,
           "Map every event into the record\n"
           "session.connect → protocol (ssh or telnet)\n"
           "login.success / login.failed → login_attempts[ ]\n"
           "command.input → commands[ ] (drop the 'CMD: ' prefix)\n"
           "file_download / file_upload → downloads[ ]\n"
           "client.version → client_version;  session.closed → duration_s", "plain", font=11)
    d.node("more", 210, 534, 170, 56, "More lines?", "decision")
    d.node("out", 95, 616, 400, 56, "Write one JSON line per session\n→ real_organic.jsonl (76,785 sessions)", "data")
    d.edge("in", "rd")
    d.edge("rd", "js")
    d.edge("js", "skip", "no", exit="r", entry="l")
    d.edge("skip", "more", exit="r", entry="r", points=[(578, 159), (578, 562)])
    d.edge("js", "blk", "yes")
    d.edge("blk", "mrg")
    d.edge("mrg", "srt")
    d.edge("srt", "map")
    d.edge("map", "more")
    d.edge("more", "rd", "yes", exit="l", entry="l", points=[(16, 562), (16, 96)])
    d.edge("more", "out", "no")
    return d


def d15_tiebreak():
    d = Diagram("d15_label_tiebreak", 590, 780, "Rubric tie-break")
    questions = [("Miner, dota kit or\nmining pool seen?", "resource_hijacking"),
                 ("Payload downloaded\nor run?", "malware_drop"),
                 ("Cron entry, SSH key, new\nuser or password change?", "persistence"),
                 ("sudo / su / SUID used\nto gain rights?", "privilege_escalation"),
                 ("Secrets, keys or\npassword hunting?", "credential_access"),
                 ("Logs or history cleared,\ndefences disabled?", "defense_evasion"),
                 ("Only looking around\n(uname, ls, ps, cpuinfo)?", "recon")]
    d.node("st", 160, 10, 250, 40, "Read the WHOLE session", "terminal", bold=True)
    prev = "st"
    for i, (q, lab) in enumerate(questions):
        y = 70 + i * 92
        d.node(f"q{i}", 145, y, 280, 76, q, "decision", font=10.5)
        d.node(f"l{i}", 445, y + 20, 140, 36, lab, "io", bold=True, font=10)
        d.edge(prev, f"q{i}", "no" if i else "")
        d.edge(f"q{i}", f"l{i}", "yes", exit="r", entry="l")
        prev = f"q{i}"
    d.node("oth", 215, 728, 140, 36, "other", "io", bold=True)
    d.edge(prev, "oth", "no")
    return d


def d19_drain():
    d = Diagram("d19_drain_algorithm", 590, 560, "Idle-timeout read")
    d.node("st", 195, 10, 200, 34, "send_command(cmd)", "terminal")
    d.node("s", 170, 60, 250, 44, "Write cmd + newline;\nstart the clock")
    d.node("rr", 210, 122, 170, 58, "Bytes\nwaiting?", "decision")
    d.node("rd", 412, 127, 170, 48, "Read up to 64 KB;\nmark the time")
    d.node("idle", 200, 205, 190, 64, "Quiet 1.5 s\nsince data?", "decision")
    d.node("cap", 200, 295, 190, 64, "Waited the\nmaximum?", "decision")
    d.node("sl", 10, 305, 150, 44, "Sleep 0.15 s")
    d.node("cl", 170, 385, 250, 44, "Strip ANSI codes,\nfix line endings")
    d.node("out", 170, 450, 250, 40, "Return output and latency", "io")
    d.node("end", 195, 510, 200, 34, "Next turn", "terminal")
    d.edge("st", "s")
    d.edge("s", "rr")
    d.edge("rr", "rd", "yes", exit="r", entry="l")
    d.edge("rd", "idle", exit="b", entry="t", entry_f=0.75, points=[(497, 190), (342, 190)])
    d.edge("rr", "idle", "no")
    d.edge("idle", "cl", "yes", exit="r", entry="r", points=[(560, 237), (560, 407)], label_pos=0.12)
    d.edge("idle", "cap", "no")
    d.edge("cap", "cl", "yes")
    d.edge("cap", "sl", "no", exit="l", entry="r")
    d.edge("sl", "rr", exit="t", entry="l", points=[(85, 151)])
    d.edge("cl", "out")
    d.edge("out", "end")
    return d


def d01_architecture():
    d = Diagram("d01_system_architecture", 590, 800, "System architecture")
    d.group("g1", 5, 5, 580, 265, "1  Synthetic data generation (own testbed)")
    d.node("harness", 20, 45, 250, 58, "Attacker harness\nbetter_ai_attacker.py")
    d.node("llm", 320, 45, 250, 58, "Attacker LLMs (AWS Bedrock)\nDeepSeek · Gemma · GPT-OSS", "cloud")
    d.node("cs", 20, 130, 120, 56, "Cowrie\nstatic shell", "terminal")
    d.node("cl", 150, 130, 120, 56, "Cowrie\nLLM shell", "terminal")
    d.node("qwen", 320, 130, 250, 56, "Qwen3-32B writes\nthe shell replies", "cloud")
    d.node("logs", 320, 205, 250, 50, "120 session logs (JSON)", "data")
    d.edge("harness", "llm", "prompt", exit="r", entry="l", exit_f=0.3, entry_f=0.3)
    d.edge("llm", "harness", "command", exit="l", entry="r", exit_f=0.75, entry_f=0.75)
    d.edge("harness", "cs", exit="b", entry="t", exit_f=0.25)
    d.edge("harness", "cl", exit="b", entry="t", exit_f=0.75)
    d.edge("cl", "qwen", exit="r", entry="l")
    d.edge("harness", "logs", "save", exit="l", entry="l", points=[(12, 74), (12, 230)], label_pos=0.7)

    d.group("g2", 5, 280, 580, 250, "2  Data preparation")
    d.node("raw", 20, 320, 250, 56, "CyberLab honeynet (Zenodo)\n76,785 sessions", "data")
    d.node("parse", 20, 395, 250, 50, "parse_cyberlab.py")
    d.node("realj", 20, 465, 250, 50, "real_organic.jsonl", "data")
    d.node("synj", 320, 320, 250, 56, "all_synthetic_120.jsonl", "data")
    d.node("feats", 320, 420, 250, 95, "session_features.py\nmask · split · verbs\ntactics · templates")
    d.edge("logs", "synj", "convert")
    d.edge("raw", "parse")
    d.edge("parse", "realj")
    d.edge("synj", "feats")
    d.edge("realj", "feats", exit="r", entry="l", entry_f=0.75)

    d.group("g3", 5, 545, 580, 250, "3  Analysis and outputs")
    d.node("ds", 20, 590, 175, 64, "domain_shift.py\nlabel-free tests")
    d.node("ann", 205, 590, 175, 64, "Dual-LLM\nannotation")
    d.node("tr", 390, 590, 180, 64, "train_eval_\nclassifier.py")
    d.node("res", 120, 700, 350, 64, "results/ → tables, figures,\npaper, report, docs", "data")
    for t, x in (("ds", 107), ("ann", 292), ("tr", 480)):
        d.edge("feats", t, exit="b", entry="t", points=[(445, 572), (x, 572)])
    d.edge("ann", "tr", "labels", exit="r", entry="l")
    d.edge("ds", "res", exit="b", entry="l", points=[(107, 732)])
    d.edge("ann", "res", exit="b", entry="t", entry_f=0.49)
    d.edge("tr", "res", exit="b", entry="r", points=[(480, 732)])
    return d


def d02_graphical_abstract():
    d = Diagram("d02_graphical_abstract", 590, 550, "Graphical abstract")
    d.node("att", 10, 10, 280, 72, "3 LLM attackers\nDeepSeek-V3.2 · Gemma-3-4B\nGPT-OSS-120B", "cloud")
    d.node("be", 300, 10, 280, 72, "2 Cowrie backends\nstatic shell\nQwen3-32B LLM shell", "terminal")
    d.node("syn", 10, 115, 280, 60, "120 synthetic sessions\n('explore the system' persona)", "data")
    d.node("real", 300, 115, 280, 60, "1,672 real sessions (CyberLab)\n= 22 behaviour templates", "data")
    d.node("join", 10, 205, 570, 34, "Same normalization, templates and features for both", "plain", fill="#F5F5F5")
    d.node("lf", 10, 270, 280, 100, "Label-free comparison\nverb JSD = 0.700\nclassifier AUC = 1.000")
    d.node("tf", 300, 270, 280, 100, "Transfer test (κ = 0.898)\nsyn → real F1 = 0.205\nreal → real F1 = 0.983\nreal + syn F1 = 0.981")
    d.node("out", 10, 400, 570, 140, "Finding\nLLM-agent traffic does not look like real bot traffic.\n"
           "Agents explore and hunt credentials; most real sessions\nrun one cryptominer dropper. "
           "Synthetic data adds no gain.", "highlight")
    d.edge("att", "syn")
    d.edge("be", "syn", exit="b", entry="t", entry_f=0.75, points=[(440, 98), (220, 98)])
    d.edge("syn", "join")
    d.edge("real", "join")
    d.edge("join", "lf", exit="b", entry="t", exit_f=0.25)
    d.edge("join", "tf", exit="b", entry="t", exit_f=0.76)
    d.edge("lf", "out", exit="b", entry="t", entry_f=0.25)
    d.edge("tf", "out", exit="b", entry="t", entry_f=0.76)
    return d


def d06_normalization():
    d = Diagram("d06_normalization_pipeline", 590, 560, "Command normalization")
    steps = [("n1", 10, 10, "1  Raw command\nfrom a session", "terminal"),
             ("n2", 310, 10, "2  Lower-case; cut leaked\nchat tokens (<|...)", "process"),
             ("n3", 310, 95, "3  Mask URLs, IPs, quoted\ntext, hex, numbers", "process"),
             ("n4", 10, 95, "4  Mask the random\nbusybox tag", "process"),
             ("n5", 10, 180, "5  Split on ; | && || $( `\n→ segments", "process"),
             ("n6", 310, 180, "6  Verbs, tactic tags,\ntemplate key", "terminal")]
    for nid, x, y, lab, kind in steps:
        d.node(nid, x, y, 270, 60, lab, kind)
    d.edge("n1", "n2", exit="r", entry="l")
    d.edge("n2", "n3", exit="b", entry="t")
    d.edge("n3", "n4", exit="l", entry="r")
    d.edge("n4", "n5", exit="b", entry="t")
    d.edge("n5", "n6", exit="r", entry="l")
    examples = ['echo "root:Xk29qPa7mz"|chpasswd|bash', "/bin/busybox QWERT", "cat /proc/cpuinfo | grep name | wc -l"]
    for k, c in enumerate(examples):
        segs = segments(c)
        tac = sorted(session_tactics({"commands": [c]})) or ["none"]
        d.node(f"x{k}", 10, 270 + k * 95, 570, 85,
               f"Raw:  {c}\nNormalized:  {normalize_cmd(c)}\nVerbs:  {', '.join(verb(s) for s in segs)}\n"
               f"Tactics:  {', '.join(t.replace('_', ' ') for t in tac)}", "note", align="left", font=11)
    return d


def d07_label_free():
    d = Diagram("d07_label_free_analysis", 590, 460, "Label-free domain-shift analysis")
    d.node("syn", 10, 20, 180, 52, "Synthetic sessions\n120 (all unique)", "data")
    d.node("real", 10, 150, 180, 52, "Real sessions\n1,672 interactive", "data")
    d.node("dedup", 10, 280, 180, 52, "Dedup by template\n→ 22 templates")
    measures = [("m1", "M1  Corpus structure: templates,\ntop-5 share, length, chaining"),
                ("m2", "M2  Tactic profile: 9 regex\ncategories, share of sessions"),
                ("m3", "M3  Verb JSD (base 2), bootstrap\nCI, Jaccard, coverage"),
                ("m4", "M4  Classifier two-sample test:\nTF-IDF + logistic regression"),
                ("m5", "M5  Per attacker × backend:\nJSD to real templates")]
    for i, (mid, lab) in enumerate(measures):
        d.node(mid, 230, 10 + i * 72, 345, 60, lab, font=11)
    d.node("out", 230, 390, 345, 56, "results/domain_shift.md + .json", "data")
    d.edge("real", "dedup")
    d.edge("syn", "m1", exit="r", entry="l", points=[(210, 46), (210, 40)])
    d.edge("syn", "m2", exit="r", entry="l", points=[(210, 46), (210, 112)])
    d.edge("real", "m3", exit="r", entry="l", points=[(210, 176), (210, 184)])
    d.edge("dedup", "m4", exit="r", entry="l", points=[(210, 306), (210, 256)])
    d.edge("dedup", "m5", exit="r", entry="l", points=[(210, 306), (210, 328)])
    for mid, _ in measures:
        d.edge(mid, "out", exit="r", entry="r", points=[(584, d.nodes[mid].cy), (584, 418)])
    return d


def d08_annotation():
    d = Diagram("d08_annotation_workflow", 590, 690, "Blind dual-LLM annotation")
    d.node("rt", 10, 10, 280, 50, "64 distinct real sequences\n(22 templates)", "data")
    d.node("st", 300, 10, 280, 50, "120 synthetic sessions", "data")
    d.node("mk", 55, 85, 480, 56, "make_annotation_sheet.py: shuffle (seed 42),\nhide source, drop DONE, cut to 30 commands")
    d.node("rub", 10, 165, 170, 66, "RUBRIC.md: 8 labels,\nwhole sequence,\ntie-break order", "note", font=10.5)
    d.node("items", 205, 172, 230, 50, "184 blind items\n+ hidden key.csv", "data")
    d.node("a", 10, 255, 280, 46, "Annotator A: Claude Sonnet 5.5", "cloud")
    d.node("b", 300, 255, 280, 46, "Annotator B: Claude Opus 5.5", "cloud")
    d.node("ag", 165, 325, 260, 46, "agreement.py: Cohen's κ = 0.898")
    d.node("same", 210, 390, 170, 58, "Same label?", "decision")
    d.node("adj", 405, 384, 175, 70, "Adjudicator\n(Opus 5.5, blind)\ndecides 12 items", font=11)
    d.node("fin", 165, 475, 260, 50, "184 final item labels\n(172 agreed + 12 adjudicated)")
    d.node("ver", 165, 545, 260, 46, "Authors cross-verify\n(dota template checked)")
    d.node("bc", 95, 615, 400, 64, "Broadcast template labels to sessions\n→ labels_final.csv (1,672 + 120)", "data")
    d.edge("rt", "mk", exit="b", entry="t", entry_f=0.2)
    d.edge("st", "mk", exit="b", entry="t", entry_f=0.8)
    d.edge("mk", "items")
    d.edge("rub", "items", dashed=True, exit="r", entry="l")
    d.edge("items", "a", exit="b", entry="t", exit_f=0.3)
    d.edge("items", "b", exit="b", entry="t", exit_f=0.7)
    d.edge("a", "ag", exit="b", entry="t", entry_f=0.2)
    d.edge("b", "ag", exit="b", entry="t", entry_f=0.8)
    d.edge("ag", "same")
    d.edge("same", "fin", "yes (172)")
    d.edge("same", "adj", "no (12)", exit="r", entry="l")
    d.edge("adj", "fin", exit="b", entry="r", points=[(492, 500)])
    d.edge("fin", "ver")
    d.edge("ver", "bc")
    return d


def d09_quadrants():
    d = Diagram("d09_transfer_quadrants", 590, 470, "Four-quadrant transfer design")
    d.node("hdr", 170, 10, 410, 30, "TEST ON", "plain", bold=True, fill="#EEEEEE")
    d.node("ts", 170, 40, 200, 30, "Synthetic", "plain", bold=True, fill="#F7F7F7")
    d.node("tr_", 380, 40, 200, 30, "Real", "plain", bold=True, fill="#F7F7F7")
    d.node("vh", 10, 80, 50, 290, "TRAIN\nON", "plain", bold=True, fill="#EEEEEE", font=10)
    d.node("rs", 65, 80, 100, 140, "Synthetic\n(120)", "plain", bold=True, fill="#F7F7F7")
    d.node("rr", 65, 230, 100, 140, "Real\n(1,672)", "plain", bold=True, fill="#F7F7F7")
    d.node("q1", 170, 80, 200, 140, "Q1  syn → syn\nstratified 2-fold\nmacro-F1 0.493\naccuracy 0.758")
    d.node("q3", 380, 80, 200, 140, "Q3  syn → real\ntrain 120, test 1,672\nmacro-F1 0.205\ndedup (22): 0.071", "highlight")
    d.node("na", 170, 230, 200, 140, "not studied\n(real → synthetic is\nnot the practical case)", "note")
    d.node("q2", 380, 230, 200, 140, "Q2  real → real\nGroupKFold(5)\nby template\nmacro-F1 0.983", "terminal")
    d.node("q4", 65, 385, 515, 74, "Q4  real + synthetic → real (same folds as Q2)\nmacro-F1 0.981 · accuracy 0.992 → no gain")
    return d


def d10_deployment():
    d = Diagram("d10_deployment_docker", 590, 550, "Docker deployment")
    d.group("host", 8, 8, 574, 405, "Researcher machine (Docker Engine)")
    d.group("net", 24, 45, 542, 248, "bridge network: honeypot-net")
    d.node("cow", 40, 82, 240, 140, "cowrie/cowrie:latest\nlistens on port 2222\ncowrie.cfg (read-only)\n"
           "var/ → named volume\nlogs → ./var/log/cowrie", font=11)
    d.node("att", 310, 82, 240, 140, "attacker container\npython:3.11-slim\nmounts logs/, normalized/,\n"
           "results/, repo at /app\nruns analysis scripts", font=11)
    d.node("port", 40, 236, 240, 44, "host 2222 → container 2222", "io", font=11)
    d.node("env", 310, 236, 240, 44, "API keys from environment", "note", font=11)
    d.node("bat", 24, 308, 542, 90, "run_docker.bat:  start-honeypot · stop-honeypot\n"
           "tables · attack · eval  (each wraps docker compose)", "note", font=11)
    d.node("bed2", 40, 445, 240, 90, "AWS Bedrock\nqwen.qwen3-32b\n(Cowrie LLM backend)", "cloud")
    d.node("bed", 310, 445, 240, 90, "AWS Bedrock\nattacker models\n(OpenAI-compatible)", "cloud")
    d.edge("att", "cow", "SSH :2222", exit="l", entry="r")
    d.edge("cow", "bed2", "backend = llm", exit="l", entry="l", points=[(16, 152), (16, 490)], dashed=True, label_pos=0.6)
    d.edge("att", "bed", "HTTPS", exit="r", entry="r", points=[(578, 152), (578, 490)], label_pos=0.6)
    return d


def d11_designs():
    d = Diagram("d11_alternative_designs", 590, 470, "Alternative designs")
    rows = [("A", "Design A · keyword-rule labels (rejected)",
             ["Synthetic +\nreal sessions", "weak_label():\nkeyword rules", "TF-IDF from\nthe SAME\nkeywords",
              "Random\nforest", "High score,\nbut circular"]),
            ("B", "Design B · label-free tests + blind dual-LLM labels (selected)",
             ["Synthetic +\nreal sessions", "Label-free:\nJSD, C2ST", "Blind dual-\nLLM labels +\nadjudication",
              "Grouped CV,\ndedup,\nsensitivity", "Honest\ntransfer\nnumbers"]),
            ("C", "Design C · human-only expert annotation",
             ["Synthetic +\nreal sessions", "Recruit and\ntrain 2–3\nexperts", "Weeks of\npaid labelling",
              "Same test\nas Design B", "Best labels,\nover budget"])]
    y = 8
    for key, title, boxes in rows:
        d.group(f"g{key}", 5, y, 580, 145, title)
        for i, lab in enumerate(boxes):
            kind = "data" if i == 0 else "process"
            if i == 4:
                kind = {"A": "highlight", "B": "terminal", "C": "note"}[key]
            d.node(f"{key}{i}", 16 + i * 114, y + 42, 100, 88, lab, kind, font=10.5)
            if i:
                d.edge(f"{key}{i - 1}", f"{key}{i}")
        y += 155
    return d


def d12_timeline():
    events = [("1989", "Stoll: The Cuckoo's Egg"), ("1992", "Cheswick: Berferd"), ("2003", "Spitzner: Honeynets"),
              ("2004", "Provos: Honeyd"), ("2009", "Kippo SSH honeypot"), ("2015", "Cowrie; IoTPOT"),
              ("2017", "Mirai botnet study"), ("2018", "Outlaw miner; honeypot\nfingerprinting"),
              ("2019", "CyberLab capture;\nHoneyCloud"), ("2023", "shelLM, chatbot honeypots;\nLLM pentesting"),
              ("2024", "HoneyGPT, PentestGPT;\nweb-hacking agents"), ("2025", "Cybench; open\nfrontier models"),
              ("2026", "This work: synthetic →\nreal transfer test")]
    d = Diagram("d12_literature_timeline", 590, 50 + 60 * len(events), "Timeline of the problem")
    d.node("axis", 291, 20, 8, 30 + 60 * (len(events) - 1), "", "plain", fill="#888888", stroke="#888888")
    for i, (yr, lab) in enumerate(events):
        cy = 35 + i * 60
        d.node(f"y{i}", 255, cy - 14, 80, 28, yr, "terminal", bold=True)
        kind = "highlight" if yr == "2026" else ("cloud" if yr >= "2023" else "process")
        if i % 2 == 0:
            d.node(f"e{i}", 10, cy - 24, 225, 48, lab, kind, font=11)
            d.edge(f"e{i}", f"y{i}", exit="r", entry="l")
        else:
            d.node(f"e{i}", 355, cy - 24, 225, 48, lab, kind, font=11)
            d.edge(f"y{i}", f"e{i}", exit="r", entry="l")
    return d


def d13_data_model():
    d = Diagram("d13_data_model", 590, 680, "Data model")
    d.node("raw", 10, 10, 280, 180, "Synthetic session log (JSON)\nsession_id\nprovider, model\nhoneypot_backend_label\n"
           "status, start and end time\ntotal_turns, recovery_attempts\nturns[ ]: turn, timestamp,\n"
           "   command, output, latency_sec", "entity")
    d.node("syn", 10, 225, 280, 170, "Normalized synthetic session\nsession_id\nattacker_model\nhoneypot_backend\n"
           "status, total_turns\ncommand_count\ncommands[ ]\nstarted_at, ended_at", "entity")
    d.node("item", 10, 430, 280, 150, "Annotation item (sheet)\nitem_id (A001…)\nn_commands\ncommands (joined by ;;)\n"
           "label\nconfidence (1–3)\nnotes", "entity")
    d.node("real", 300, 10, 280, 240, "Normalized real session\nsession_id, source\nsrc_ip (hashed id)\n"
           "country, protocol\nstart, end, duration_s\nlogin_attempts[ ]\nlogin_success\ncommands[ ]\n"
           "downloads[ ]\nclient_version\nfindings, counts", "entity")
    d.node("tpl", 300, 275, 280, 80, "Template key\ntuple of normalized commands\n(same sequence = same template)", "entity")
    d.node("key", 300, 380, 280, 150, "Key row (key.csv, hidden)\nitem_id\nsession_id\nsource (real / synthetic)\n"
           "attacker_model\nhoneypot_backend\ntemplate_size", "entity")
    d.node("lab", 300, 560, 280, 100, "Final label (labels_final.csv)\nsession_id\nlabel (8 classes)\nsource", "entity")
    d.edge("raw", "syn", "convert")
    d.edge("syn", "item", "1 : 1 item")
    d.edge("real", "tpl", "many : 1")
    d.edge("tpl", "key", "1 representative")
    d.edge("item", "key", "item_id", exit="r", entry="l", entry_f=0.5)
    d.edge("key", "lab", "broadcast")
    d.edge("item", "lab", "agreed / adjudicated", exit="b", entry="l", points=[(150, 610)], label_pos=0.65)
    return d


def d14_method_overview():
    d = Diagram("d14_methodology_overview", 590, 355, "Research methodology")
    stages = ["1  Problem and\nliterature", "2  Build testbed\n(Cowrie + harness)", "3  Collect data\n(120 synthetic +\nCyberLab real)",
              "4  Normalize and\ntemplate", "5  Label-free\ncomparison", "6  Blind dual-LLM\nannotation",
              "7  Four-quadrant\ntransfer test", "8  Sensitivity and\nvalidation", "9  Paper, report,\nopen code"]
    pos = [(10, 10), (207, 10), (404, 10), (404, 140), (207, 140), (10, 140), (10, 270), (207, 270), (404, 270)]
    for i, (s, (x, y)) in enumerate(zip(stages, pos)):
        kind = "terminal" if i in (0, 8) else ("highlight" if i == 6 else "process")
        d.node(f"s{i}", x, y, 175, 72, s, kind, font=11)
    for a, b, ex, en in ((0, 1, "r", "l"), (1, 2, "r", "l"), (2, 3, "b", "t"), (3, 4, "l", "r"), (4, 5, "l", "r"),
                         (5, 6, "b", "t"), (6, 7, "r", "l"), (7, 8, "r", "l")):
        d.edge(f"s{a}", f"s{b}", exit=ex, entry=en)
    return d


def d16_concepts():
    d = Diagram("d16_concept_generation", 590, 490, "Concept generation")
    d.node("root", 120, 10, 350, 56, "How can a defender get enough\nlabelled attack sessions?", "terminal", bold=True)
    left = [("c2", "C2  Scripted synthetic generator\n(fixed archetypes)"), ("c3", "C3  Generative models\n(GANs over traffic)"),
            ("c1", "C1  Collect more real data\n(own internet honeypots)")]
    right = [("c4", "C4  LLM agent vs\nstatic Cowrie"), ("c5", "C5  LLM agent vs\nLLM-backed Cowrie"),
             ("c6", "C6  Replay or mutate\nreal sessions")]
    for k, ((lid, ltxt), (rid, rtxt)) in enumerate(zip(left, right)):
        y = 110 + k * 80
        d.node(lid, 10, y, 260, 64, ltxt, "process", font=11)
        d.node(rid, 320, y, 260, 64, rtxt, "terminal" if rid in ("c4", "c5") else "process", font=11)
        d.edge("root", lid, exit="b", entry="r", points=[(295, y + 32)])
        d.edge("root", rid, exit="b", entry="l", points=[(295, y + 32)])
    d.node("out", 10, 365, 570, 110, "Selected: C4 + C5 (two honeypot conditions), compared with public\n"
           "real data (the C1 side, without waiting for our own deployment).\n"
           "Kept for future work: C1 (own deployment) and C6 (replay).\n"
           "Rejected now: C2 (no realism) and C3 (needs a lot of real data).", "note", align="left", font=11)
    return d


def d17_wbs():
    d = Diagram("d17_work_breakdown", 590, 580, "Work breakdown structure")
    d.node("root", 145, 10, 300, 52, "LLM red-team vs real honeypot\ntraffic project", "terminal", bold=True)
    wps = [("WP1  Literature\nand planning", "survey, project plan,\nresearch questions"),
           ("WP2  Testbed", "Cowrie configuration, harness,\nrecovery logic"),
           ("WP3  Data", "120 synthetic sessions,\nCyberLab parser"),
           ("WP4  Analysis", "normalization, templates,\nlabel-free comparison"),
           ("WP5  Labels", "rubric, dual-LLM annotation,\nadjudication, author check"),
           ("WP6  Experiments", "transfer matrix,\nsensitivity runs"),
           ("WP7  Dissemination", "LNNS paper, report,\ndocumentation, GitHub")]
    for i, (t, sub) in enumerate(wps):
        y = 85 + i * 70
        d.node(f"w{i}", 50, y, 210, 56, t, "process", bold=True, font=11)
        d.node(f"s{i}", 285, y, 295, 56, sub, "note", font=10.5)
        d.edge("root", f"w{i}", exit="l", entry="l", points=[(28, 36), (28, y + 28)])
        d.edge(f"w{i}", f"s{i}", exit="r", entry="l")
    return d


def d18_harness_modules():
    d = Diagram("d18_harness_modules", 590, 540, "Harness module structure")
    d.node("cli", 10, 10, 270, 60, "main() / argparse or\nbatch config file")
    d.node("rec", 310, 10, 270, 60, "run_session_with_recovery()\nhealth check + retries")
    d.node("cfg", 10, 100, 270, 150, "RunConfig (dataclass)\nhost, port, provider, model\nmax_turns, response_wait\n"
           "retries, recovery_max_wait\noptional admin settings", "entity")
    d.node("rs", 310, 100, 270, 50, "run_session(): turn loop")
    d.node("hp", 310, 180, 270, 90, "HoneypotSession\nconnect (Paramiko)\n_drain(): read until idle\nsend_command()")
    d.node("save", 310, 300, 270, 50, "save_log() → <session_id>.json", "data")
    d.node("health", 10, 290, 270, 100, "probe_banner()\nwait_for_honeypot()\nrestart_honeypot_remote()\nlog_infra_event()")
    d.node("guard", 10, 420, 270, 60, "looks_like_refusal()\nclean_output()")
    d.node("llm", 310, 380, 270, 140, "call_llm() dispatcher\n+ 3 retries with back-off\nanthropic · openai · gemini\n"
           "bedrock · bedrock_openai · local", "cloud")
    d.edge("cli", "cfg")
    d.edge("cli", "rec", exit="r", entry="l")
    d.edge("rec", "rs")
    d.edge("rs", "hp")
    d.edge("hp", "save")
    d.edge("rec", "health", exit="l", entry="r", exit_f=0.67, points=[(292, 50), (292, 340)])
    d.edge("rs", "guard", exit="l", entry="r", exit_f=0.8, points=[(300, 140), (300, 450)])
    d.edge("rs", "llm", exit="r", entry="r", points=[(586, 125), (586, 450)])
    return d


def d20_validation():
    d = Diagram("d20_validation_checks", 590, 480, "Validation checks")
    d.node("c", 145, 10, 300, 56, "How do we know the numbers\nare trustworthy?", "terminal", bold=True)
    checks = [("Data checks", "parser count = 76,785; CMD prefix\nhandled; leaked chat tokens stripped"),
              ("Leakage checks", "GroupKFold by template; Q3-dedup (22);\nDONE token removed from sheets"),
              ("Label checks", "κ = 0.898 between annotators;\n12 adjudicated; authors cross-verify"),
              ("Robustness", "dota relabel run; keyword-rule\nplumbing check; verb-only C2ST"),
              ("Reproducibility", "fixed seed 42; scripts write\nresults/; open repository")]
    for i, (t, s) in enumerate(checks):
        y = 92 + i * 76
        d.node(f"k{i}", 50, y, 190, 56, t, "process", bold=True)
        d.node(f"v{i}", 260, y, 320, 56, s, "note", font=10.5)
        d.edge("c", f"k{i}", exit="l", entry="l", points=[(28, 38), (28, y + 28)])
        d.edge(f"k{i}", f"v{i}", exit="r", entry="l")
    return d
