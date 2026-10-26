"""
Builds every flowchart / block diagram used in the report.

Each diagram is written twice from one spec:
  report/diagrams/<name>.drawio   editable source (open in draw.io / diagrams.net)
  report/images/<name>.png        picture embedded in the Word report

Run from the repository root:
    python report/src/make_diagrams.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagram_lib import Diagram  # noqa: E402
from diagrams_a4 import (  # noqa: E402  A4-portrait layouts of the wide diagrams
    d01_architecture, d02_graphical_abstract, d06_normalization, d07_label_free, d08_annotation, d09_quadrants, d10_deployment, d11_designs, d12_timeline, d13_data_model, d14_method_overview, d16_concepts, d17_wbs, d18_harness_modules, d20_validation)
from session_features import normalize_cmd, segments, session_tactics, verb  # noqa: E402

DRAWIO = ROOT / "report" / "diagrams"
PNG = ROOT / "report" / "images"






def d03_session_flow():
    d = Diagram("d03_attacker_session_flowchart", 780, 1520, "Attacker session loop")
    d.node("start", 290, 20, 200, 50, "Start session i", "terminal")
    d.node("probe", 300, 100, 180, 90, "SSH banner\nanswers?", "decision")
    d.node("rec", 20, 110, 230, 70, "Recovery: remote restart\nor wait for watchdog\n(≤ recovery_max_wait)")
    d.node("recok", 45, 215, 180, 90, "Honeypot\nback?", "decision")
    d.node("cf", 25, 340, 220, 50, "status = connection_failed", "io")
    d.node("conn", 290, 235, 200, 60, "Open SSH shell (Paramiko)\nread banner")
    d.node("lim", 300, 330, 180, 90, "Turn limit or\nsession time\nreached?", "decision")
    d.node("ask", 290, 460, 200, 64, "Send system prompt +\ntranscript to attacker LLM")
    d.node("err", 300, 560, 180, 90, "LLM call failed\n3 times?", "decision")
    d.node("done", 300, 690, 180, 80, "Reply is\nDONE?", "decision")
    d.node("ref", 300, 810, 180, 80, "Looks like\na refusal?", "decision")
    d.node("send", 290, 930, 200, 64, "Type command into honeypot,\nread until 1.5 s of silence")
    d.node("lost", 300, 1030, 180, 80, "Socket\ndied?", "decision")
    d.node("log", 290, 1150, 200, 64, "Append turn (command,\noutput, latency);\nnext context = output")
    d.node("stall", 300, 1250, 180, 96, "2 empty replies\nat the time\nceiling in a row?", "decision")
    d.node("s1", 540, 350, 210, 50, "status = max_turns_reached\nor timed_out", "io")
    d.node("s2", 540, 580, 210, 50, "status = llm_error", "io")
    d.node("s3", 540, 705, 210, 50, "status = completed", "io")
    d.node("s4", 540, 825, 210, 50, "status = attacker_refused", "io")
    d.node("s5", 540, 1045, 210, 50, "status = connection_lost", "io")
    d.node("s6", 540, 1273, 210, 50, "status = honeypot_unresponsive", "io")
    d.node("save", 540, 1380, 210, 54, "Save session JSON\n(+ infra_events.log)")
    d.node("end", 545, 1460, 200, 46, "End session", "terminal")
    d.edge("start", "probe")
    d.edge("probe", "conn", "yes")
    d.edge("probe", "rec", "no", exit="l", entry="r")
    d.edge("rec", "recok")
    d.edge("recok", "conn", "yes", exit="r", entry="l")
    d.edge("recok", "cf", "no")
    d.edge("cf", "save", exit="b", entry="l", points=[(135, 1407)])
    d.edge("conn", "lim")
    d.edge("lim", "ask", "no")
    d.edge("ask", "err")
    d.edge("err", "done", "no")
    d.edge("done", "ref", "no")
    d.edge("ref", "send", "no")
    d.edge("send", "lost")
    d.edge("lost", "log", "no")
    d.edge("log", "stall")
    d.edge("stall", "lim", "no", exit="l", entry="l", points=[(265, 1298), (265, 375)], label_pos=0.05)
    for dec, st in (("lim", "s1"), ("err", "s2"), ("done", "s3"), ("ref", "s4"), ("lost", "s5"), ("stall", "s6")):
        d.edge(dec, st, "yes", exit="r", entry="l")
        y = d.nodes[st].cy
        d.edge(st, "save", exit="r", entry="r", points=[(765, y), (765, 1407)])
    d.edge("save", "end")
    return d


def d04_recovery():
    d = Diagram("d04_recovery_flowchart", 760, 900, "Session retry and recovery")
    d.node("st", 260, 20, 240, 50, "Next session requested", "terminal")
    d.node("probe", 250, 100, 260, 60, "ensure_honeypot_healthy():\nraw-socket SSH banner probe")
    d.node("ok", 290, 195, 180, 90, "Banner\nreceived?", "decision")
    d.node("fix", 520, 200, 220, 80, "Remote restart over admin\nSSH (if --vm-host set),\nelse wait for watchdog")
    d.node("back", 540, 320, 180, 90, "Back within\n90 s?", "decision")
    d.node("give", 520, 450, 220, 54, "Log connection_failed;\ngive up on this session", "io")
    d.node("run", 250, 330, 260, 60, "run_session(): drive the\nattacker loop")
    d.node("infra", 280, 430, 200, 110, "Status is an infra\nfailure? (failed /\nunresponsive / lost)", "decision")
    d.node("keep", 20, 455, 200, 60, "Keep log as real data\n(completed, refused, ...)", "io")
    d.node("left", 290, 580, 180, 90, "Retries left?\n(max 3)", "decision")
    d.node("retry", 20, 595, 210, 60, "Save failed attempt,\nwait 3 s, retry")
    d.node("ex", 270, 720, 220, 54, "Save last log\n(retries exhausted)", "io")
    d.node("end", 280, 820, 200, 46, "Session finished", "terminal")
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
    d.edge("left", "retry", "yes", exit="l", entry="r")
    d.edge("retry", "probe", exit="t", entry="l", points=[(125, 130)])
    d.edge("left", "ex", "no")
    d.edge("ex", "end")
    d.edge("keep", "end", exit="b", entry="l", points=[(120, 843)])
    d.edge("give", "end", exit="b", entry="r", points=[(630, 843)])
    return d


def d05_parser():
    d = Diagram("d05_cyberlab_parser_flowchart", 720, 1060, "CyberLab parser")
    d.node("in", 210, 20, 300, 60, "cowrie_2019-11-15.json\n(one big JSON array, ~600 MB)", "data")
    d.node("rd", 210, 115, 300, 60, "Read ONE line at a time\nstrip '[' ',' ']' around it")
    d.node("js", 270, 210, 180, 90, "Valid JSON\nobject?", "decision")
    d.node("skip", 520, 225, 170, 60, "Skip the line", "io")
    d.node("blk", 210, 335, 300, 60, "For every {session_id: [events]}\nin the object")
    d.node("mrg", 210, 430, 300, 60, "Get or create the session record\n(a session can appear twice)")
    d.node("srt", 210, 525, 300, 50, "Sort its events by timestamp")
    d.node("map", 140, 610, 440, 170,
           "Map each event into the record\n"
           "session.connect → protocol (ssh / telnet)\n"
           "login.success / login.failed → login_attempts[]\n"
           "command.input → commands[] (drop the 'CMD: ' prefix)\n"
           "session.file_download / upload → downloads[]\n"
           "client.version → client_version\n"
           "session.closed → duration_s", "plain")
    d.node("more", 270, 815, 180, 80, "More lines?", "decision")
    d.node("out", 160, 930, 400, 64, "Add findings + counts, write one JSON line per session\n→ normalized/real_organic.jsonl (76,785 sessions)", "data")
    d.edge("in", "rd")
    d.edge("rd", "js")
    d.edge("js", "skip", "no", exit="r", entry="l")
    d.edge("skip", "more", exit="b", entry="r", points=[(605, 855)])
    d.edge("js", "blk", "yes")
    d.edge("blk", "mrg")
    d.edge("mrg", "srt")
    d.edge("srt", "map")
    d.edge("map", "more")
    d.edge("more", "rd", "yes", exit="l", entry="l", points=[(110, 855), (110, 145)])
    d.edge("more", "out", "no")
    return d




















def d15_tiebreak():
    d = Diagram("d15_label_tiebreak", 760, 1000, "Rubric tie-break")
    qs = [("Miner, dota kit, xmrig or\nmining pool seen?", "resource_hijacking"),
          ("Payload downloaded\nor run?", "malware_drop"),
          ("Cron/rc entry, SSH key,\nnew user or password change?", "persistence"),
          ("sudo / su / SUID used to\ngain more rights?", "privilege_escalation"),
          ("Secrets, keys, shadow file\nor password hunting?", "credential_access"),
          ("Logs/history cleared,\ndefences disabled?", "defense_evasion"),
          ("Only looking around\n(uname, ls, ps, cpuinfo)?", "recon")]
    d.node("st", 230, 20, 260, 50, "Read the WHOLE session", "terminal")
    prev = "st"
    y = 100
    for i, (q, lab) in enumerate(qs):
        d.node(f"q{i}", 220, y, 280, 100, q, "decision", font=10)
        d.node(f"l{i}", 560, y + 25, 180, 50, lab, "io", bold=True)
        d.edge(prev, f"q{i}", "no" if i else "")
        d.edge(f"q{i}", f"l{i}", "yes", exit="r", entry="l")
        prev = f"q{i}"
        y += 120
    d.node("oth", 270, y, 180, 50, "other", "io", bold=True)
    d.edge(prev, "oth", "no")
    return d








def d19_drain():
    d = Diagram("d19_drain_algorithm", 700, 900, "Idle-timeout read")
    d.node("st", 230, 20, 240, 50, "send_command(cmd)", "terminal")
    d.node("s", 210, 100, 280, 56, "write cmd + newline;\nstart clock")
    d.node("rr", 260, 190, 180, 90, "Bytes\nwaiting?", "decision")
    d.node("rd", 500, 205, 180, 60, "read up to 64 KB;\nlast_data_at = now")
    d.node("idle", 250, 320, 200, 100, "Quiet for 1.5 s\nsince last data?", "decision")
    d.node("cap", 250, 460, 200, 100, "Total wait ≥\nmax_response_wait?", "decision")
    d.node("sl", 30, 485, 170, 50, "sleep 0.15 s")
    d.node("cl", 210, 600, 280, 60, "strip ANSI codes,\nnormalize line endings")
    d.node("out", 210, 700, 280, 60, "return (output, latency)", "io")
    d.node("end", 230, 800, 240, 50, "next turn", "terminal")
    d.edge("st", "s")
    d.edge("s", "rr")
    d.edge("rr", "rd", "yes", exit="r", entry="l")
    d.edge("rd", "idle", exit="b", entry="r", points=[(590, 370)])
    d.edge("rr", "idle", "no")
    d.edge("idle", "cl", "yes", exit="r", entry="r", points=[(520, 370), (520, 630)], label_pos=0.15)
    d.edge("idle", "cap", "no")
    d.edge("cap", "cl", "yes")
    d.edge("cap", "sl", "no", exit="l", entry="r")
    d.edge("sl", "rr", exit="t", entry="l", points=[(115, 235)])
    d.edge("cl", "out")
    d.edge("out", "end")
    return d




ALL = [d01_architecture, d02_graphical_abstract, d03_session_flow, d04_recovery, d05_parser, d06_normalization,
       d07_label_free, d08_annotation, d09_quadrants, d10_deployment, d11_designs, d12_timeline, d13_data_model,
       d14_method_overview, d15_tiebreak, d16_concepts, d17_wbs, d18_harness_modules, d19_drain, d20_validation]


def main():
    for fn in ALL:
        dg = fn().save(DRAWIO, PNG)
        print("wrote", dg.name)


if __name__ == "__main__":
    main()
