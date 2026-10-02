"""Build blind annotation sheets: all distinct real templates (>=1 command) + all synthetic sessions."""
import argparse, csv, os, random
from collections import defaultdict
from session_features import load_jsonl, strip_chat_leak, template_key

MAXCMD, MAXLEN = 30, 200


def render(cmds):
    # Drop the synthetic attackers' "DONE" stop token: it is not a shell command and would identify the source.
    cmds = [strip_chat_leak(c).strip().replace("\r", " ").replace("\n", " ") for c in cmds]
    while cmds and cmds[-1] == "DONE":
        cmds.pop()
    cmds = [c for c in cmds if c]
    shown = [c if len(c) <= MAXLEN else c[:MAXLEN] + "..." for c in cmds[:MAXCMD]]
    s = " ;; ".join(shown)
    if len(cmds) > MAXCMD:
        s += f" ;; [+{len(cmds) - MAXCMD} more]"
    return len(cmds), s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", default="normalized/real_organic.jsonl")
    ap.add_argument("--synthetic", default="normalized/all_synthetic_120.jsonl")
    ap.add_argument("--out", default="annotation")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    groups = defaultdict(list)
    for s in load_jsonl(a.real):
        if s.get("commands"):
            groups[template_key(s)].append(s)
    items = []
    for k, ss in groups.items():
        rep = min(ss, key=lambda s: s["session_id"])
        items.append((rep, "real", "", "", len(ss)))
    for s in load_jsonl(a.synthetic):
        items.append((s, "synthetic", s.get("attacker_model", ""), s.get("honeypot_backend", ""), 1))
    items.sort(key=lambda t: t[0]["session_id"])
    random.Random(a.seed).shuffle(items)

    os.makedirs(a.out, exist_ok=True)
    rows, key = [], []
    for i, (s, src, model, be, n) in enumerate(items, 1):
        iid = f"A{i:03d}"
        nc, cmds = render(s["commands"])
        rows.append((iid, nc, cmds))
        key.append((iid, s["session_id"], src, model, be, n))
    for name in ("sheet_annotator1.csv", "sheet_annotator2.csv"):
        with open(os.path.join(a.out, name), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["item_id", "n_commands", "commands", "label", "confidence", "notes"])
            for r in rows:
                w.writerow([*r, "", "", ""])
    with open(os.path.join(a.out, "annotation_sheet.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "commands"])
        for r in rows:
            w.writerow([r[0], r[2]])
    with open(os.path.join(a.out, "key.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "session_id", "source", "attacker_model", "honeypot_backend", "template_size"])
        w.writerows(key)
    nr = sum(k[2] == "real" for k in key)
    print(f"{len(key)} items: {nr} real, {len(key) - nr} synthetic -> {a.out}/")


if __name__ == "__main__":
    main()
