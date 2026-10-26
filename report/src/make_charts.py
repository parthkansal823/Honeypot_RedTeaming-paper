"""
Data charts and console "screenshots" for the project report.

Every number comes from results/*.json or report/data/report_stats.json. Colours follow the paper figures
(Okabe-Ito, colour-blind safe) with hatching as a second cue for print.

Run from the repository root (after compute_stats.py):
    python report/src/make_charts.py
"""
import json
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "results"
OUT = ROOT / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)
STATS = json.loads((ROOT / "report" / "data" / "report_stats.json").read_text(encoding="utf-8"))
DS = json.loads((R / "domain_shift.json").read_text(encoding="utf-8"))
T3 = json.loads((R / "table3_transfer.json").read_text(encoding="utf-8"))
T3S = json.loads((R / "sensitivity_dota" / "table3_transfer.json").read_text(encoding="utf-8"))
T3R = json.loads((R / "rule_labels" / "table3_transfer.json").read_text(encoding="utf-8"))
T12 = json.loads((R / "tables_1_2.json").read_text(encoding="utf-8"))

# Charts are drawn at their printed size (6 in = A4 text width), so these
# font sizes are the sizes on paper.
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.labelsize": 9.5, "axes.titlesize": 10,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 8.5,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold",
    "axes.edgecolor": "#888888", "xtick.color": "#444444", "ytick.color": "#444444",
    "axes.labelcolor": "#333333", "savefig.dpi": 300, "savefig.bbox": "tight",
})
# Soft, colour-blind-friendly palette (blue / orange pair first); white gaps between bars.
BLUE, ORANGE, GREY, GREEN, PINK, SKY, VERM = "#4C78A8", "#F2A541", "#B8B8B8", "#59A14F", "#B07AA1", "#76B7E0", "#E15759"
SERIES = [BLUE, ORANGE, GREY, GREEN, PINK, SKY]
HATCH = [""] * 6
EDGE = "white"
INK = "#333333"

CELLS = ["DeepSeek-V3.2 | Static", "DeepSeek-V3.2 | Dynamic (Qwen-32B)", "Gemma-3-4B | Static",
         "Gemma-3-4B | Dynamic (Qwen-32B)", "GPT-OSS-120B | Static", "GPT-OSS-120B | Dynamic (Qwen-32B)"]
SHORT = {c: c.replace(" | Dynamic (Qwen-32B)", "\n+ Qwen3-32B").replace(" | Static", "\nstatic") for c in CELLS}
LABELS = ["recon", "credential_access", "privilege_escalation", "persistence", "malware_drop", "resource_hijacking"]
PRETTY = {l: l.replace("_", " ").capitalize() for l in LABELS}
WRAPPED = {l: l.replace("_", "\n").capitalize() for l in LABELS}


def grid(ax, axis="x"):
    (ax.xaxis if axis == "x" else ax.yaxis).grid(True, color="#e3e3e3", lw=0.6)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def bar_labels(ax, bars, fmt="{:,.0f}", horizontal=False, pad=3):
    for b in bars:
        v = b.get_width() if horizontal else b.get_height()
        if horizontal:
            ax.annotate(fmt.format(v), (v, b.get_y() + b.get_height() / 2), xytext=(pad, 0),
                        textcoords="offset points", va="center", fontsize=8, color=INK)
        else:
            ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, v), xytext=(0, pad),
                        textcoords="offset points", ha="center", fontsize=8, color=INK)


# --------------------------------------------------------------- real data
def c01_real_funnel():
    r = STATS["real"]
    steps = [("All sessions", r["sessions"]), ("Login succeeded", r["login_success_sessions"]),
             ("Typed at least one command", r["interactive_sessions"]), ("Distinct behaviour templates", len(r["template_sizes"]))]
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.0, 2.6), gridspec_kw={"width_ratios": [2.2, 1]})
    y = np.arange(len(steps))[::-1]
    bars = a.barh(y, [v for _, v in steps], color=BLUE, edgecolor=EDGE, lw=0.5, height=0.6)
    a.set_xscale("log")
    a.set_yticks(y)
    a.set_yticklabels([s for s, _ in steps])
    a.set_xlabel("Count (log scale)")
    bar_labels(a, bars, horizontal=True)
    a.set_xlim(10, 400000)
    grid(a)
    a.set_title("From raw sessions to behaviours")
    p = r["protocol"]
    bb = b.bar(["SSH", "Telnet"], [p.get("ssh", 0), p.get("telnet", 0)], color=[BLUE, ORANGE], hatch=["", ""],
               edgecolor=EDGE, lw=0.5, width=0.6)
    bar_labels(b, bb)
    b.set_ylabel("Sessions")
    b.set_ylim(0, max(p.values()) * 1.18)
    grid(b, "y")
    b.set_title("Protocol")
    fig.tight_layout()
    save(fig, "c01_real_funnel")


def c02_template_sizes():
    sizes = STATS["real"]["template_sizes"]
    total = sum(sizes)
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    x = np.arange(1, len(sizes) + 1)
    bars = ax.bar(x, sizes, color=[ORANGE if i == 0 else BLUE for i in range(len(sizes))],
                  hatch=None, edgecolor=EDGE, lw=0.5, width=0.7)
    for i, b in enumerate(bars[:6]):
        ax.annotate(f"{sizes[i]:,}", (b.get_x() + b.get_width() / 2, sizes[i]), xytext=(0, 3),
                    textcoords="offset points", ha="center", fontsize=7.5)
    ax.set_xticks(x)
    ax.set_xlabel("Template rank (1 = most common behaviour)")
    ax.set_ylabel("Sessions in template")
    cum5 = sum(sizes[:5]) / total
    ax.text(0.98, 0.92, f"Top template ('dota' miner dropper): {sizes[0]:,} sessions ({sizes[0] / total:.1%})\n"
                        f"Top 5 templates: {cum5:.1%} of {total:,} interactive sessions\n"
                        f"{sum(1 for s in sizes if s == 1)} templates were seen only once",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.8,
            bbox=dict(boxstyle="round,pad=0.4", fc="#f7f7f7", ec="#cccccc"))
    grid(ax, "y")
    fig.tight_layout()
    save(fig, "c02_template_sizes")


def c03_countries():
    r = STATS["real"]
    fig, axes = plt.subplots(1, 2, figsize=(6.0, 2.9))
    for ax, key, title, col, h in ((axes[0], "top_countries_all", "All 76,785 sessions", BLUE, ""),
                                   (axes[1], "top_countries_interactive", "1,672 interactive sessions", ORANGE, "///")):
        items = r[key][:8][::-1]
        names = [("Unknown" if (k in (None, "unknown")) else k) for k, _ in items]
        bars = ax.barh(names, [v for _, v in items], color=col, hatch=h, edgecolor=EDGE, lw=0.5, height=0.6)
        bar_labels(ax, bars, horizontal=True)
        ax.set_xlim(0, max(v for _, v in items) * 1.25)
        ax.set_title(title)
        ax.set_xlabel("Sessions")
        grid(ax)
    fig.tight_layout()
    save(fig, "c03_countries")


def c04_credentials():
    r = STATS["real"]
    fig, axes = plt.subplots(1, 2, figsize=(6.0, 3.0))
    for ax, key, title, col, h in ((axes[0], "top_usernames", "Usernames tried", BLUE, ""),
                                   (axes[1], "top_passwords", "Passwords tried", ORANGE, "///")):
        items = r[key][:8][::-1]
        names = [("(empty)" if k == "" else str(k)) for k, _ in items]
        bars = ax.barh(names, [v for _, v in items], color=col, hatch=h, edgecolor=EDGE, lw=0.5, height=0.6)
        ax.set_xscale("log")
        bar_labels(ax, bars, horizontal=True)
        ax.set_xlim(50, max(v for _, v in items) * 6)
        ax.set_title(title)
        ax.set_xlabel("Login attempts (log scale)")
        grid(ax)
    fig.tight_layout()
    save(fig, "c04_credentials")


# ---------------------------------------------------------- synthetic side
def c05_status():
    sts = ["completed", "max_turns_reached", "connection_lost", "llm_error", "attacker_refused", "timed_out"]
    names = {"completed": "Completed (said DONE)", "max_turns_reached": "Hit turn limit", "connection_lost": "Connection lost",
             "llm_error": "LLM error", "attacker_refused": "Refused", "timed_out": "Timed out"}
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    y = np.arange(len(CELLS))[::-1]
    left = np.zeros(len(CELLS))
    for i, s in enumerate(sts):
        vals = np.array([T12[c]["statuses"][s] for c in CELLS], dtype=float)
        ax.barh(y, vals, left=left, color=SERIES[i], hatch=HATCH[i], edgecolor="white", lw=1.0, height=0.62, label=names[s])
        for yy, l0, v in zip(y, left, vals):
            if v >= 2:
                ax.text(l0 + v / 2, yy, f"{int(v)}", ha="center", va="center", fontsize=7.5,
                        color="white" if SERIES[i] in (BLUE, GREEN) else INK)
        left += vals
    ax.set_yticks(y)
    ax.set_yticklabels([SHORT[c].replace("\n", " ") for c in CELLS])
    ax.set_xlim(0, 20)
    ax.set_xlabel("Sessions (20 per cell)")
    ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.42, -0.2))
    fig.tight_layout()
    save(fig, "c05_session_status")


def c06_latency():
    atk = ["DeepSeek-V3.2", "Gemma-3-4B", "GPT-OSS-120B"]
    fig, axes = plt.subplots(1, 2, figsize=(6.0, 2.8), sharey=False)
    for ax, key, title in ((axes[0], "mean_latency", "Mean latency per command"),
                           (axes[1], "median_latency", "Median latency per command")):
        x = np.arange(len(atk))
        w = 0.36
        st = [T12[f"{a} | Static"][key] for a in atk]
        dy = [T12[f"{a} | Dynamic (Qwen-32B)"][key] for a in atk]
        b1 = ax.bar(x - w / 2, st, w, color=BLUE, edgecolor=EDGE, lw=0.5, label="Static Cowrie")
        b2 = ax.bar(x + w / 2, dy, w, color=ORANGE, hatch="", edgecolor=EDGE, lw=0.5, label="Cowrie + Qwen3-32B")
        bar_labels(ax, list(b1) + list(b2), fmt="{:.2f}")
        ax.set_xticks(x)
        ax.set_xticklabels(["DeepSeek", "Gemma", "GPT-OSS"])
        ax.set_ylabel("Seconds")
        ax.set_title(title)
        ax.set_ylim(0, max(st + dy) * 1.22)
        grid(ax, "y")
    axes[0].legend(frameon=False, loc="upper left")
    fig.tight_layout()
    save(fig, "c06_latency")


def c07_commands():
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    x = np.arange(len(CELLS))
    w = 0.38
    tot = [T12[c]["total_commands"] for c in CELLS]
    uni = [T12[c]["unique_commands"] for c in CELLS]
    b1 = ax.bar(x - w / 2, tot, w, color=BLUE, edgecolor=EDGE, lw=0.5, label="Total commands")
    b2 = ax.bar(x + w / 2, uni, w, color=ORANGE, hatch="", edgecolor=EDGE, lw=0.5, label="Unique commands")
    bar_labels(ax, list(b1) + list(b2))
    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[c] for c in CELLS], fontsize=7.5)
    ax.set_ylabel("Commands")
    ax.set_ylim(0, max(tot) * 1.2)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    grid(ax, "y")
    fig.tight_layout()
    save(fig, "c07_commands")


def c08_first_commands():
    items = STATS["synthetic"]["top_first_commands"][::-1]
    fig, ax = plt.subplots(figsize=(6.0, 2.6))
    bars = ax.barh([k for k, _ in items], [v for _, v in items], color=BLUE, edgecolor=EDGE, lw=0.5, height=0.6)
    bar_labels(ax, bars, horizontal=True)
    ax.set_xlabel("Synthetic sessions that opened with this command (of 120)")
    ax.set_xlim(0, max(v for _, v in items) * 1.18)
    for t in ax.get_yticklabels():
        t.set_family("DejaVu Sans Mono")
    grid(ax)
    fig.tight_layout()
    save(fig, "c08_first_commands")


# ------------------------------------------------------------ comparison
def c09_top_verbs():
    v = DS["verbs"]
    fig, axes = plt.subplots(1, 2, figsize=(6.0, 3.2))
    for ax, key, title, col, h in ((axes[0], "top_synthetic", "Synthetic (120 sessions)", BLUE, ""),
                                   (axes[1], "top_real", "Real (1,672 sessions)", ORANGE, "///")):
        items = v[key][:10][::-1]
        bars = ax.barh([k for k, _ in items], [n for _, n in items], color=col, hatch=h, edgecolor=EDGE, lw=0.5, height=0.62)
        bar_labels(ax, bars, horizontal=True)
        ax.set_xlim(0, max(n for _, n in items) * 1.25)
        ax.set_title(title)
        ax.set_xlabel("Occurrences of verb")
        for t in ax.get_yticklabels():
            t.set_family("DejaVu Sans Mono")
        grid(ax)
    fig.tight_layout()
    save(fig, "c09_top_verbs")


def c10_structure():
    s, r = DS["structure"]["synthetic"], DS["structure"]["real"]
    metrics = [("Distinct templates", s["distinct_templates"], r["distinct_templates"], "{:.0f}"),
               ("Top-5 template share (%)", 100 * s["top5_template_share"], 100 * r["top5_template_share"], "{:.1f}"),
               ("Mean characters per command", s["mean_chars_per_cmd"], r["mean_chars_per_cmd"], "{:.1f}"),
               ("Commands chained / piped (%)", 100 * s["pct_cmds_chained"], 100 * r["pct_cmds_chained"], "{:.1f}")]
    fig, axes = plt.subplots(1, 4, figsize=(6.0, 2.4))
    for ax, (t, a, b, fmt) in zip(axes, metrics):
        bars = ax.bar(["Synthetic", "Real"], [a, b], color=[BLUE, ORANGE], hatch=["", ""], edgecolor=EDGE, lw=0.5, width=0.6)
        bar_labels(ax, bars, fmt=fmt)
        ax.set_ylim(0, max(a, b) * 1.25)
        ax.set_title("\n".join(textwrap.wrap(t, 16)), fontsize=8.5)
        ax.tick_params(axis="x", labelsize=7.5)
        grid(ax, "y")
    fig.tight_layout()
    save(fig, "c10_corpus_structure")


# ------------------------------------------------------------ annotation
def c11_confusion():
    order = LABELS
    cm = np.array([[63, 4, 0, 0, 0, 0], [0, 83, 1, 1, 0, 0], [1, 0, 1, 0, 0, 0],
                   [0, 1, 0, 13, 1, 0], [0, 0, 0, 1, 12, 0], [0, 0, 0, 0, 2, 0]])  # results/annotation_agreement.md
    fig, ax = plt.subplots(figsize=(5.2, 4.1))
    im = ax.imshow(np.log1p(cm), cmap="Blues")
    for i in range(len(order)):
        for j in range(len(order)):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=9,
                    color="white" if cm[i, j] > 20 else INK)
    ax.set_xticks(range(len(order)))
    ax.set_yticks(range(len(order)))
    ax.set_xticklabels([PRETTY[o] for o in order], rotation=35, ha="right")
    ax.set_yticklabels([PRETTY[o] for o in order])
    ax.set_xlabel("Annotator B (Claude Opus 5.5)")
    ax.set_ylabel("Annotator A (Claude Sonnet 5.5)")
    ax.spines[:].set_visible(False)
    fig.tight_layout()
    save(fig, "c11_annotation_confusion")


def c12_labels():
    dist = T3["label_distribution"]
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    x = np.arange(len(LABELS))
    w = 0.26
    for i, (k, name) in enumerate((("synthetic", "Synthetic sessions (120)"), ("real", "Real sessions (1,672)"),
                                   ("real_dedup", "Real templates (22)"))):
        tot = sum(dist[k].values())
        vals = [100 * dist[k][l] / tot for l in LABELS]
        bars = ax.bar(x + (i - 1) * w, vals, w, color=SERIES[i], hatch=HATCH[i], edgecolor=EDGE, lw=0.5, label=name)
        for b, l in zip(bars, LABELS):
            if dist[k][l]:
                ax.annotate(f"{dist[k][l]:,}", (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 2),
                            textcoords="offset points", ha="center", fontsize=6.8)
    ax.set_xticks(x)
    ax.set_xticklabels([WRAPPED[l] for l in LABELS], fontsize=8.5)
    ax.set_ylabel("Share of corpus (%)")
    ax.set_ylim(0, 85)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.12))
    grid(ax, "y")
    fig.tight_layout()
    save(fig, "c12_label_distribution")


def c13_q3_predictions():
    q3 = next(q for q in T3["quadrants"] if q["id"] == "Q3")
    true = T3["label_distribution"]["real"]
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    x = np.arange(len(LABELS))
    w = 0.38
    b1 = ax.bar(x - w / 2, [true[l] for l in LABELS], w, color=ORANGE, hatch="", edgecolor=EDGE, lw=0.5,
                label="True label (real sessions)")
    b2 = ax.bar(x + w / 2, [q3["predicted"].get(l, 0) for l in LABELS], w, color=BLUE, edgecolor=EDGE, lw=0.5,
                label="Predicted by synthetic-trained model (Q3)")
    bar_labels(ax, [b for b in list(b1) + list(b2) if b.get_height() > 0])
    ax.set_xticks(x)
    ax.set_xticklabels([WRAPPED[l] for l in LABELS], fontsize=8.5)
    ax.set_ylabel("Sessions")
    ax.set_ylim(0, 1900)
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    grid(ax, "y")
    fig.tight_layout()
    save(fig, "c13_q3_predictions")


def c14_label_sources():
    ids = ["Q1", "Q2", "Q3", "Q3_dedup", "Q4"]
    srcs = [("Dual-LLM labels (reported)", T3, BLUE, ""), ("Sensitivity: dota → malware drop", T3S, ORANGE, ""),
            ("Keyword rules (plumbing check only)", T3R, GREY, "")]
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    x = np.arange(len(ids))
    w = 0.26
    for i, (name, src, col, h) in enumerate(srcs):
        vals = [next(q for q in src["quadrants"] if q["id"] == k)["macro_f1"] for k in ids]
        bars = ax.bar(x + (i - 1) * w, vals, w, color=col, hatch=h, edgecolor=EDGE, lw=0.5, label=name)
        bar_labels(ax, bars, fmt="{:.2f}", pad=2)
    ax.set_xticks(x)
    ax.set_xticklabels(["Q1\nsyn→syn", "Q2\nreal→real", "Q3\nsyn→real", "Q3-dedup\nsyn→real", "Q4\nreal+syn→real"], fontsize=8.5)
    ax.set_ylabel("Macro-F1")
    ax.set_ylim(0, 1.12)
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
    grid(ax, "y")
    fig.tight_layout()
    save(fig, "c14_label_sources")






# --------------------------------------------------------------- schedule
def c17_gantt():
    import datetime as dt
    tasks = [("Literature review and planning", "2026-08-01", "2026-08-31", "plan"),
             ("Testbed: Cowrie config and attacker harness", "2026-08-10", "2026-09-23", "plan"),
             ("Synthetic sessions (6 cells × 20)", "2026-09-24", "2026-09-29", "log"),
             ("CyberLab parsing and normalization", "2026-09-25", "2026-10-01", "log"),
             ("Label-free domain-shift analysis", "2026-09-28", "2026-10-01", "log"),
             ("Blind dual-LLM annotation and adjudication", "2026-09-29", "2026-10-01", "log"),
             ("Transfer experiments and sensitivity runs", "2026-10-01", "2026-10-02", "log"),
             ("Paper writing (IEEE, then Springer LNNS)", "2026-10-01", "2026-10-26", "plan"),
             ("Report and project documentation", "2026-10-20", "2026-10-31", "plan")]
    d = lambda s: dt.date.fromisoformat(s)  # noqa: E731
    t0 = d("2026-08-01")
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    for i, (name, a, b, kind) in enumerate(tasks[::-1]):
        s, e = (d(a) - t0).days, (d(b) - t0).days + 1
        ax.barh(i, e - s, left=s, color=BLUE if kind == "log" else GREY, hatch="",
                edgecolor=EDGE, lw=0.5, height=0.6)
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([t[0] for t in tasks[::-1]], fontsize=7.8)
    ticks = ["2026-08-01", "2026-08-15", "2026-09-01", "2026-09-15", "2026-10-01", "2026-10-15", "2026-11-01"]
    ax.set_xticks([(d(t) - t0).days for t in ticks])
    ax.set_xticklabels([d(t).strftime("%d %b") for t in ticks])
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=BLUE, ec=EDGE, label="Dates from log / file timestamps"),
                       Patch(fc=GREY, ec=EDGE, hatch="", label="Planned window (approximate)")],
              frameon=False, loc="upper center", bbox_to_anchor=(0.35, -0.12), ncol=2)
    grid(ax)
    fig.tight_layout()
    save(fig, "c17_gantt")


# ------------------------------------------------------- console pictures
def terminal(name, title, text, width=84):
    """Light-theme console picture, drawn at printed size (6 in wide, 8 pt mono)."""
    lines = []
    for raw in text.strip("\n").split("\n"):
        lines += textwrap.wrap(raw, width, replace_whitespace=False, drop_whitespace=False) or [""]
    step = 0.155
    h = 0.5 + step * len(lines)
    fig = plt.figure(figsize=(6.0, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fc="#FAFAFA", ec="#B5B5B5", lw=1.2))
    ax.add_patch(plt.Rectangle((0, 1 - 0.3 / h), 1, 0.3 / h, transform=ax.transAxes, fc="#E8E8E8", ec="#B5B5B5", lw=1.2))
    for k, c in enumerate(("#E15759", "#F2A541", "#59A14F")):
        ax.add_patch(plt.Circle((0.02 + k * 0.022, 1 - 0.15 / h), 0.006, transform=ax.transAxes, color=c))
    ax.text(0.5, 1 - 0.15 / h, title, transform=ax.transAxes, ha="center", va="center", color="#333333", fontsize=8.5)
    for i, line in enumerate(lines):
        prompt = line.lstrip().startswith(("$", ">", "PS "))
        ax.text(0.015, 1 - (0.42 + step * i) / h, line, transform=ax.transAxes, ha="left", va="top",
                family="DejaVu Sans Mono", fontsize=8, color="#1F5FA8" if prompt else "#222222",
                fontweight="bold" if prompt else "normal")
    fig.savefig(OUT / f"{name}.png", dpi=220, facecolor="white")
    plt.close(fig)
    print("wrote", name)


def consoles():
    r = STATS["real"]
    terminal("t01_docker_start", "Windows terminal: start the honeypot",
             "> run_docker.bat start-honeypot\nStarting Cowrie Honeypot in Docker...\n"
             "(docker compose up -d cowrie)  -> network honeypot-net + container cowrie-honeypot\n"
             "Cowrie is running on localhost:2222. Check logs with: docker compose logs -f cowrie\n\n"
             "> python check.py\n0 b'SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\\r\\n'\n1 b'SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\\r\\n'\n...")
    sess = next((ROOT / "logs" / "deepseek").glob("bedrock_openai-deepseek.v3.2-0-042e74d1.json"))
    log = json.loads(sess.read_text(encoding="utf-8"))
    terminal("t02_attacker_run", "Run one attacker batch",
             "> python better_ai_attacker.py --config batch_deepseek_static.json\n"
             "[bedrock_openai/deepseek.v3.2] session 1/20...\n"
             f"  -> {log['status']} ({log['total_turns']} turns, 0 retries) saved to logs/deepseek/{sess.name}\n"
             "[bedrock_openai/deepseek.v3.2] session 2/20...\n  ...")
    turns = log["turns"][:3]
    body = {"session_id": log["session_id"], "provider": log["provider"], "model": log["model"],
            "honeypot_backend_label": log.get("honeypot_backend_label"), "status": log["status"],
            "total_turns": log["total_turns"],
            "turns": [{"turn": t["turn"], "command": t["command"],
                       "output": (t.get("output") or "")[:70].replace("\n", "\\n") + ("..." if len(t.get("output") or "") > 70 else ""),
                       "latency_sec": t.get("latency_sec")} for t in turns]}
    terminal("t03_session_json", f"logs/deepseek/{sess.name} (first 3 turns)", json.dumps(body, indent=2), width=84)
    p = r["protocol"]
    terminal("t04_parse_cyberlab", "Parse the real dataset",
             "> python parse_cyberlab.py --in cyberlab_2019-11-15.json/cowrie_2019-11-15.json\n"
             f"Parsed {r['sessions']} sessions -> normalized/real_organic.jsonl\n"
             f"  proto_ssh: {p['ssh']}\n  proto_telnet: {p['telnet']}\n  sessions: {r['sessions']}\n"
             f"  with_commands: {r['interactive_sessions']}\n  with_downloads: {r['sessions_with_downloads']}\n"
             f"  with_login_success: {r['login_success_sessions']}")
    ds_md = (R / "domain_shift.md").read_text(encoding="utf-8").split("\n")
    terminal("t05_domain_shift", "Label-free analysis",
             "> python domain_shift.py\n" + "\n".join(ds_md[:14]) + "\n...", width=84)
    t3_md = (R / "table3_transfer.md").read_text(encoding="utf-8").split("\n")
    terminal("t06_transfer", "Four-quadrant transfer experiment",
             "> python train_eval_classifier.py --synthetic normalized/all_synthetic_120.jsonl \\\n"
             "    --real normalized/real_organic.jsonl --real-labels annotation/labels_final.csv \\\n"
             "    --synthetic-labels annotation/labels_final.csv --label-source llm-dual\n"
             "synthetic n=120, real n=1672, templates=22\n" + "\n".join(t3_md[4:12]) + "\n...", width=84)
    ag = (R / "annotation_agreement.md").read_text(encoding="utf-8").split("\n")
    terminal("t07_agreement", "Annotation agreement", "> python agreement.py\n" + "\n".join(ag[:12]) + "\n...")


# ------------------------------------------- report versions of paper figures
def c18_transfer():
    ids = ["Q1", "Q2", "Q3", "Q3_dedup", "Q4"]
    q = {x["id"]: x for x in T3["quadrants"]}
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    x = np.arange(len(ids))
    w = 0.38
    b1 = ax.bar(x - w / 2, [q[i]["macro_f1"] for i in ids], w, color=BLUE, edgecolor=EDGE, lw=0.8, label="Random forest")
    b2 = ax.bar(x + w / 2, [q[i]["majority_macro_f1"] for i in ids], w, color=GREY, edgecolor=EDGE, lw=0.8,
                label="Majority-class baseline")
    bar_labels(ax, list(b1) + list(b2), fmt="{:.3f}", pad=2)
    ax.set_xticks(x)
    short = {"Q1": "syn→syn", "Q2": "real→real", "Q3": "syn→real", "Q3_dedup": "syn→real\n(dedup)", "Q4": "real+syn\n→real"}
    ax.set_xticklabels([f"{i.replace('_', '-')}\n{short[i]}" for i in ids], fontsize=8.5)
    ax.set_ylabel("Macro-F1")
    ax.set_ylim(0, 1.12)
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    grid(ax, "y")
    fig.tight_layout()
    save(fig, "c18_transfer")


def c19_attacker_categories():
    atk = ["DeepSeek-V3.2", "Gemma-3-4B", "GPT-OSS-120B"]
    cats = [("recon", "Recon"), ("credential_hunting", "Credentials"), ("privilege_escalation", "Privilege escalation")]
    fig, axes = plt.subplots(1, 3, figsize=(6.0, 2.7), sharey=True)
    for ax, (key, title) in zip(axes, cats):
        x = np.arange(len(atk))
        w = 0.38
        st = [T12[f"{a} | Static"]["pct"][key] for a in atk]
        dy = [T12[f"{a} | Dynamic (Qwen-32B)"]["pct"][key] for a in atk]
        b1 = ax.bar(x - w / 2, st, w, color=BLUE, edgecolor=EDGE, lw=0.8, label="Static Cowrie")
        b2 = ax.bar(x + w / 2, dy, w, color=ORANGE, edgecolor=EDGE, lw=0.8, label="Cowrie + Qwen3-32B")
        bar_labels(ax, list(b1) + list(b2), fmt="{:.0f}", pad=2)
        ax.set_xticks(x)
        ax.set_xticklabels(["DeepSeek", "Gemma", "GPT-OSS"], fontsize=8)
        ax.set_title(title)
        ax.set_ylim(0, 78)
        grid(ax, "y")
    axes[0].set_ylabel("Share of commands (%)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "c19_attacker_categories")


def c20_tactics():
    t = DS["tactics"]
    keys = sorted(t["synthetic"], key=lambda k: t["synthetic"][k])
    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    y = np.arange(len(keys))
    h = 0.27
    for i, (lab, k) in enumerate((("Synthetic (120)", "synthetic"), ("Real (1,672)", "real"),
                                  ("Real, one per template (22)", "real_dedup"))):
        ax.barh(y + (1 - i) * h, [100 * t[k][x] for x in keys], h, color=SERIES[i], edgecolor=EDGE, lw=0.6, label=lab)
    ax.set_yticks(y)
    ax.set_yticklabels([k.replace("_", " ").capitalize() for k in keys])
    ax.set_xlabel("Sessions touching the tactic at least once (%)")
    ax.set_xlim(0, 105)
    ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.42, 1.0), fontsize=8)
    grid(ax)
    fig.tight_layout()
    save(fig, "c20_tactics")


def c21_condition_jsd():
    rows = sorted(DS["per_condition"], key=lambda c: (c["attacker"], c["backend"] != "Static Cowrie"))
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    y = np.arange(len(rows))[::-1]
    for yy, c in zip(y, rows):
        p, lo, hi = c["jsd_vs_real_dedup"]
        col = BLUE if c["backend"] == "Static Cowrie" else ORANGE
        ax.plot([lo, hi], [yy, yy], color=col, lw=2.2, solid_capstyle="round")
        ax.plot(p, yy, "o", ms=8, color=col, mec="white", mew=1.5)
        ax.annotate(f"{p:.3f}  [{lo:.3f}, {hi:.3f}]", (hi, yy), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=8, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{c['attacker']} · {'static' if c['backend'] == 'Static Cowrie' else '+ Qwen3-32B'}" for c in rows])
    ax.set_xlabel("Verb JSD to real templates (lower = closer to real), 95% bootstrap CI")
    ax.set_xlim(0.72, 0.885)
    grid(ax)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color=BLUE, marker="o", lw=2, label="Static Cowrie"),
                       Line2D([], [], color=ORANGE, marker="o", lw=2, label="Cowrie + Qwen3-32B")],
              frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.4, 1.0))
    fig.tight_layout()
    save(fig, "c21_condition_jsd")


def copy_paper_figures():
    import shutil
    for f in ("fig_attackers", "fig_tactics", "fig_condition_jsd", "fig_transfer"):
        shutil.copy(ROOT / "figures" / f"{f}.png", OUT / f"{f}.png")
        print("copied", f)


if __name__ == "__main__":
    for fn in (c01_real_funnel, c02_template_sizes, c03_countries, c04_credentials, c05_status, c06_latency, c07_commands,
               c08_first_commands, c09_top_verbs, c10_structure, c11_confusion, c12_labels, c13_q3_predictions,
               c14_label_sources, c17_gantt, c18_transfer, c19_attacker_categories,
               c20_tactics, c21_condition_jsd, consoles):
        fn()
