#!/usr/bin/env python3
"""Paper figures -> figures/*.png (300 dpi) + *.pdf. No in-image titles."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

R = Path("results"); OUT = Path("figures"); OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
                     "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False,
                     "pdf.fonttype": 42, "savefig.dpi": 300, "savefig.bbox": "tight"})
# Okabe-Ito picks with distinct luminance + hatches (readable in grayscale)
C = ["#0072B2", "#E69F00", "#BBBBBB"]
H = ["", "///", "..."]
EDGE = "#222222"


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=300); fig.savefig(OUT / f"{name}.pdf"); plt.close(fig)
    print("wrote", name)


def fig_tactics():
    t = json.load(open(R / "domain_shift.json"))["tactics"]
    keys = sorted(t["synthetic"], key=lambda k: t["synthetic"][k])
    series = [("Synthetic", "synthetic"), ("Real", "real"), ("Real (template-dedup)", "real_dedup")]
    fig, ax = plt.subplots(figsize=(3.5, 3.6))
    y = np.arange(len(keys)); h = 0.26
    for i, (lab, k) in enumerate(series):
        ax.barh(y + (i - 1) * h, [100 * t[k].get(x, 0) for x in keys], h, label=lab,
                color=C[i], hatch=H[i], edgecolor=EDGE, linewidth=0.5)
    ax.set_yticks(y); ax.set_yticklabels([k.replace("_", " ").capitalize() for k in keys])
    ax.set_xlabel("Sessions exhibiting tactic (%)"); ax.set_xlim(0, 100)
    ax.xaxis.grid(True, color="#dddddd", lw=0.6); ax.set_axisbelow(True)
    ax.legend(loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.4, -0.12))
    save(fig, "fig_tactics")


def fig_condition_jsd():
    pc = json.load(open(R / "domain_shift.json"))["per_condition"]
    atts = ["DeepSeek-V3.2", "Gemma-3-4B", "GPT-OSS-120B"]
    bks = [("Static Cowrie", "Static Cowrie"), ("Dynamic Qwen-32B", "Dynamic (Qwen3-32B)")]
    fig, ax = plt.subplots(figsize=(3.5, 2.4)); w = 0.36; x = np.arange(len(atts))
    for i, (b, lab) in enumerate(bks):
        pts, err = [], [[], []]
        for a in atts:
            p, lo, hi = next(c for c in pc if c["attacker"] == a and c["backend"] == b)["jsd_vs_real_dedup"]
            pts.append(p); err[0].append(p - lo); err[1].append(hi - p)
        ax.bar(x + (i - .5) * w, pts, w, yerr=err, capsize=3, label=lab, color=C[i], hatch=H[i],
               edgecolor=EDGE, linewidth=0.5, error_kw={"lw": 1, "ecolor": EDGE})
        for xi, p in zip(x + (i - .5) * w, pts):
            ax.text(xi, 0.02, f"{p:.2f}", ha="center", va="bottom", fontsize=6.5,
                    bbox=dict(fc="white", ec="none", pad=1, alpha=.85))
    ax.set_xticks(x); ax.set_xticklabels(atts); ax.set_ylim(0, 1)
    ax.set_ylabel("JSD to real (template-dedup), lower = closer")
    ax.yaxis.grid(True, color="#dddddd", lw=0.6); ax.set_axisbelow(True)
    ax.legend(loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.12))
    save(fig, "fig_condition_jsd")


def fig_attackers():
    d = json.load(open(R / "tables_1_2.json"))
    atts = ["DeepSeek-V3.2", "Gemma-3-4B", "GPT-OSS-120B"]
    cats = [("recon", "Recon"), ("credential_hunting", "Credentials"),
            ("privilege_escalation", "Priv. esc.")]
    fig, axes = plt.subplots(1, 3, figsize=(3.5, 2.5), sharey=True)
    w = 0.38; x = np.arange(len(atts))
    for ax, (ck, cl) in zip(axes, cats):
        for i, (b, lab) in enumerate([("Static", "Static Cowrie"), ("Dynamic (Qwen-32B)", "Dynamic (Qwen3-32B)")]):
            v = [d[f"{a} | {b}"]["pct"][ck] for a in atts]
            bars = ax.bar(x + (i - .5) * w, v, w, label=lab, color=C[i], hatch=H[i], edgecolor=EDGE, linewidth=0.5)
            for r, val in zip(bars, v):
                ax.text(r.get_x() + r.get_width() / 2, val + 1, f"{val:.0f}", ha="center", fontsize=5.5)
        ax.set_xticks(x); ax.set_xticklabels(["DS", "Gemma", "GPT"], fontsize=6.5)
        ax.set_title(cl, fontsize=7.5, pad=8); ax.yaxis.grid(True, color="#dddddd", lw=0.6); ax.set_axisbelow(True)
    axes[0].set_ylabel("Share of commands (%)"); axes[0].set_ylim(0, 80)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.12))
    fig.tight_layout()
    save(fig, "fig_attackers")


def fig_transfer():
    p = R / "table3_transfer.json"
    if not p.exists():
        print("NOTICE: results/table3_transfer.json not found; skipping fig_transfer"); return
    q = json.load(open(p))["quadrants"]
    fig, ax = plt.subplots(figsize=(3.5, 2.6)); x = np.arange(len(q)); w = 0.38
    f1 = [r["macro_f1"] for r in q]; mj = [r["majority_macro_f1"] for r in q]
    for i, (v, lab) in enumerate([(f1, "Classifier"), (mj, "Majority baseline")]):
        bars = ax.bar(x + (i - .5) * w, v, w, label=lab, color=[C[0], C[2]][i], hatch=["", "..."][i],
                      edgecolor=EDGE, linewidth=0.5)
        for r, val in zip(bars, v):
            ax.text(r.get_x() + r.get_width() / 2, val + 0.015, f"{val:.2f}", ha="center", fontsize=6.5)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r['train']}\n→ {r['test']}\n(n={r['n_train']}/{r['n_test']})" for r in q], fontsize=6)
    ax.set_ylim(0, 1.1); ax.set_ylabel("Macro-F1")
    ax.yaxis.grid(True, color="#dddddd", lw=0.6); ax.set_axisbelow(True)
    ax.legend(loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.12))
    save(fig, "fig_transfer")


if __name__ == "__main__":
    fig_tactics(); fig_condition_jsd(); fig_attackers(); fig_transfer()
