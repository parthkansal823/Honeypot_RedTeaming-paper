"""
Tiny diagram toolkit: one spec -> an editable draw.io file AND a PNG.

A diagram is a list of nodes and edges in draw.io pixel coordinates
(x to the right, y downwards). save() writes <name>.drawio (open it at
https://app.diagrams.net or in draw.io desktop) and renders the same
geometry with matplotlib to <name>.png for the Word report, so the picture
in the report and the editable source never drift apart.
"""
from __future__ import annotations

import html
import math
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

FONT = "Arial"
# Render-time text scale (labels are enlarged slightly so they stay legible on A4).
FONT_SCALE = float(__import__("os").environ.get("DIAGRAM_FONT_SCALE", "1.3"))

# draw.io's default palette, so the .drawio files look native when opened.
KIND_COLORS = {
    "process": ("#DAE8FC", "#6C8EBF"),
    "decision": ("#FFF2CC", "#D6B656"),
    "terminal": ("#D5E8D4", "#82B366"),
    "data": ("#E1D5E7", "#9673A6"),
    "io": ("#F8CECC", "#B85450"),
    "cloud": ("#FFE6CC", "#D79B00"),
    "note": ("#FFFFFF", "#999999"),
    "entity": ("#FFFFFF", "#6C8EBF"),
    "highlight": ("#F8CECC", "#B85450"),
    "plain": ("#FFFFFF", "#666666"),
    "group": ("#F7F7F7", "#888888"),
}


@dataclass
class Node:
    id: str
    x: float
    y: float
    w: float
    h: float
    label: str
    kind: str = "process"
    fill: str | None = None
    stroke: str | None = None
    font: float = 11
    bold: bool = False
    align: str = "center"

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    def colors(self):
        f, s = KIND_COLORS.get(self.kind, KIND_COLORS["process"])
        return self.fill or f, self.stroke or s

    def port(self, side, frac=0.5):
        if side == "t":
            return (self.x + self.w * frac, self.y)
        if side == "b":
            return (self.x + self.w * frac, self.y + self.h)
        if side == "l":
            return (self.x, self.y + self.h * frac)
        return (self.x + self.w, self.y + self.h * frac)


@dataclass
class Edge:
    src: str
    dst: str
    label: str = ""
    exit: str | None = None      # side letter t/b/l/r
    entry: str | None = None
    exit_f: float = 0.5
    entry_f: float = 0.5
    points: list = field(default_factory=list)  # explicit waypoints
    dashed: bool = False
    label_pos: float = 0.5       # where on the route the label sits (0..1 of length)


class Diagram:
    def __init__(self, name, width, height, title=""):
        self.name, self.W, self.H, self.title = name, width, height, title
        self.nodes: dict[str, Node] = {}
        self.order: list[str] = []
        self.edges: list[Edge] = []

    # ------------------------------------------------------------------ build
    def node(self, id, x, y, w, h, label, kind="process", **kw):
        n = Node(id, x, y, w, h, label, kind, **kw)
        self.nodes[id] = n
        self.order.append(id)
        return n

    def group(self, id, x, y, w, h, label, **kw):
        kw.setdefault("bold", True)
        kw.setdefault("align", "left")
        return self.node(id, x, y, w, h, label, "group", **kw)

    def edge(self, src, dst, label="", **kw):
        self.edges.append(Edge(src, dst, label, **kw))

    # ---------------------------------------------------------------- routing
    def _sides(self, e):
        a, b = self.nodes[e.src], self.nodes[e.dst]
        if e.exit and e.entry:
            return e.exit, e.entry
        dx, dy = b.cx - a.cx, b.cy - a.cy
        if abs(dy) >= abs(dx):
            s, t = ("b", "t") if dy > 0 else ("t", "b")
        else:
            s, t = ("r", "l") if dx > 0 else ("l", "r")
        return e.exit or s, e.entry or t

    def route(self, e):
        a, b = self.nodes[e.src], self.nodes[e.dst]
        s, t = self._sides(e)
        p0, p1 = a.port(s, e.exit_f), b.port(t, e.entry_f)
        if e.points:
            return [p0, *e.points, p1], s, t
        pts = [p0]
        vert = {"t", "b"}
        if s in vert and t in vert:
            if abs(p0[0] - p1[0]) > 0.5:
                my = (p0[1] + p1[1]) / 2
                pts += [(p0[0], my), (p1[0], my)]
        elif s not in vert and t not in vert:
            if abs(p0[1] - p1[1]) > 0.5:
                mx = (p0[0] + p1[0]) / 2
                pts += [(mx, p0[1]), (mx, p1[1])]
        elif s in vert:
            pts.append((p0[0], p1[1]))
        else:
            pts.append((p1[0], p0[1]))
        pts.append(p1)
        return pts, s, t

    # ------------------------------------------------------------- draw.io
    def _style(self, n):
        fill, stroke = n.colors()
        base = f"whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontFamily={FONT};fontSize={round(n.font * FONT_SCALE)};"
        if n.bold:
            base += "fontStyle=1;"
        if n.align != "center":
            base += f"align={n.align};spacingLeft=8;"
        shape = {
            "process": "rounded=1;arcSize=12;",
            "decision": "rhombus;",
            "terminal": "rounded=1;arcSize=50;",
            "data": "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;",
            "io": "shape=parallelogram;perimeter=parallelogramPerimeter;fixedSize=1;size=16;",
            "cloud": "rounded=1;arcSize=30;",
            "note": "rounded=0;dashed=1;",
            "entity": "rounded=0;verticalAlign=top;align=left;spacingLeft=6;",
            "highlight": "rounded=1;arcSize=12;strokeWidth=2;",
            "plain": "rounded=0;",
            "group": "rounded=1;arcSize=3;verticalAlign=top;dashed=0;container=0;",
        }.get(n.kind, "rounded=1;")
        return shape + base

    @staticmethod
    def _label_html(n):
        if n.kind == "entity":
            title, *fields = n.label.split("\n")
            return f"<b>{html.escape(title)}</b><hr>" + "<br>".join(html.escape(f) for f in fields)
        lines = [html.escape(x) for x in n.label.split("\n")]
        return "<br>".join(lines)

    def to_drawio(self):
        cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
        groups = [i for i in self.order if self.nodes[i].kind == "group"]
        others = [i for i in self.order if self.nodes[i].kind != "group"]
        for i in groups + others:
            n = self.nodes[i]
            cells.append(
                f'<mxCell id="{i}" value="{html.escape(self._label_html(n), quote=True)}" '
                f'style="{self._style(n)}" vertex="1" parent="1">'
                f'<mxGeometry x="{n.x:.0f}" y="{n.y:.0f}" width="{n.w:.0f}" height="{n.h:.0f}" as="geometry"/></mxCell>')
        for k, e in enumerate(self.edges):
            pts, s, t = self.route(e)
            a, b = self.nodes[e.src], self.nodes[e.dst]
            ex = {"t": (e.exit_f, 0), "b": (e.exit_f, 1), "l": (0, e.exit_f), "r": (1, e.exit_f)}[s]
            en = {"t": (e.entry_f, 0), "b": (e.entry_f, 1), "l": (0, e.entry_f), "r": (1, e.entry_f)}[t]
            style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;"
                     f"exitX={ex[0]};exitY={ex[1]};exitDx=0;exitDy=0;entryX={en[0]};entryY={en[1]};entryDx=0;entryDy=0;"
                     f"fontFamily={FONT};fontSize=11;labelBackgroundColor=#FFFFFF;")
            if e.dashed:
                style += "dashed=1;"
            inner = "".join(f'<mxPoint x="{x:.0f}" y="{y:.0f}"/>' for x, y in pts[1:-1])
            arr = f'<Array as="points">{inner}</Array>' if inner else ""
            cells.append(
                f'<mxCell id="e{k}" value="{html.escape(e.label, quote=True)}" style="{style}" edge="1" parent="1" '
                f'source="{e.src}" target="{e.dst}"><mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')
        body = "".join(cells)
        return (f'<mxfile host="app.diagrams.net" type="device"><diagram id="{self.name}" name="{html.escape(self.title or self.name)}">'
                f'<mxGraphModel dx="{self.W}" dy="{self.H}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
                f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.W}" pageHeight="{self.H}" math="0" shadow="0">'
                f'<root>{body}</root></mxGraphModel></diagram></mxfile>')

    # ------------------------------------------------------------ matplotlib
    def _text(self, ax, n):
        fs = n.font * 0.75 * FONT_SCALE
        weight = "bold" if n.bold else "normal"
        if n.kind == "group":
            ax.text(n.x + 10, n.y + 8, n.label, ha="left", va="top", fontsize=fs + 0.5, fontweight="bold",
                    family=FONT, color="#333333")
            return
        if n.kind == "entity":
            title, *fields = n.label.split("\n")
            ax.text(n.x + 8, n.y + 6, title, ha="left", va="top", fontsize=fs, fontweight="bold", family=FONT)
            ax.plot([n.x, n.x + n.w], [n.y + 24, n.y + 24], color=n.colors()[1], lw=0.8)
            ax.text(n.x + 8, n.y + 30, "\n".join(fields), ha="left", va="top", fontsize=fs - 0.5, family=FONT,
                    linespacing=1.35)
            return
        ha = "left" if n.align == "left" else "center"
        tx = n.x + 10 if ha == "left" else n.cx
        t = ax.text(tx, n.cy, n.label, ha=ha, va="center", fontsize=fs, fontweight=weight, family=FONT,
                    linespacing=1.3, color="#1A1A1A")
        self._texts.append((n, t))

    def _shape(self, ax, n):
        fill, stroke = n.colors()
        lw = 1.6 if n.kind == "highlight" else 1.0
        if n.kind in ("process", "cloud", "highlight"):
            r = 10 if n.kind != "cloud" else 18
            ax.add_patch(FancyBboxPatch((n.x, n.y), n.w, n.h, boxstyle=f"round,pad=0,rounding_size={r}",
                                        fc=fill, ec=stroke, lw=lw))
        elif n.kind == "terminal":
            ax.add_patch(FancyBboxPatch((n.x, n.y), n.w, n.h, boxstyle=f"round,pad=0,rounding_size={n.h / 2}",
                                        fc=fill, ec=stroke, lw=lw))
        elif n.kind == "decision":
            ax.add_patch(Polygon([(n.cx, n.y), (n.x + n.w, n.cy), (n.cx, n.y + n.h), (n.x, n.cy)],
                                 closed=True, fc=fill, ec=stroke, lw=lw))
        elif n.kind == "io":
            s = 16
            ax.add_patch(Polygon([(n.x + s, n.y), (n.x + n.w, n.y), (n.x + n.w - s, n.y + n.h), (n.x, n.y + n.h)],
                                 closed=True, fc=fill, ec=stroke, lw=lw))
        elif n.kind == "data":
            e = 10
            ax.add_patch(Rectangle((n.x, n.y + e / 2), n.w, n.h - e, fc=fill, ec="none"))
            ax.add_patch(Ellipse((n.cx, n.y + n.h - e / 2), n.w, e, fc=fill, ec=stroke, lw=lw))
            ax.add_patch(Rectangle((n.x, n.y + e / 2), n.w, n.h - e, fc=fill, ec="none"))
            ax.plot([n.x, n.x], [n.y + e / 2, n.y + n.h - e / 2], color=stroke, lw=lw)
            ax.plot([n.x + n.w, n.x + n.w], [n.y + e / 2, n.y + n.h - e / 2], color=stroke, lw=lw)
            ax.add_patch(Ellipse((n.cx, n.y + e / 2), n.w, e, fc=fill, ec=stroke, lw=lw))
        elif n.kind == "note":
            ax.add_patch(Rectangle((n.x, n.y), n.w, n.h, fc=fill, ec=stroke, lw=lw, ls="--"))
        elif n.kind == "group":
            ax.add_patch(FancyBboxPatch((n.x, n.y), n.w, n.h, boxstyle="round,pad=0,rounding_size=8",
                                        fc=fill, ec=stroke, lw=0.9))
        else:  # plain / entity
            ax.add_patch(Rectangle((n.x, n.y), n.w, n.h, fc=fill, ec=stroke, lw=lw))

    def _edge(self, ax, e):
        pts, _, _ = self.route(e)
        xs, ys = zip(*pts)
        ls = "--" if e.dashed else "-"
        ax.plot(xs[:-1] + (xs[-1],), ys[:-1] + (ys[-1],), color="#444444", lw=1.0, ls=ls,
                solid_capstyle="butt", zorder=3)
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        L = math.hypot(x1 - x0, y1 - y0) or 1
        back = min(9, L)
        ax.annotate("", xy=(x1, y1), xytext=(x1 - (x1 - x0) / L * back, y1 - (y1 - y0) / L * back),
                    arrowprops=dict(arrowstyle="-|>", color="#444444", lw=1.0, mutation_scale=9,
                                    shrinkA=0, shrinkB=0), zorder=4)
        if e.label:
            segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
            lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs]
            target = sum(lens) * e.label_pos
            acc = 0
            for (a, b), l in zip(segs, lens):
                if acc + l >= target:
                    f = (target - acc) / (l or 1)
                    lx, ly = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
                    break
                acc += l
            ax.text(lx, ly, e.label, ha="center", va="center", fontsize=8.5, family=FONT, color="#222222",
                    bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none"), zorder=5)

    def _check_fit(self, fig, ax):
        """Shrink any label that is wider/taller than its shape (at most to 80% of its size),
        and warn if it still does not fit, so overflow is caught without eyeballing."""
        r = fig.canvas.get_renderer()
        inv = ax.transData.inverted()
        for n, t in self._texts:
            room_w = n.w * (0.62 if n.kind == "decision" else 1) - (6 if n.kind != "decision" else 0)
            room_h = n.h * (0.62 if n.kind == "decision" else 1) - 4
            base = t.get_fontsize()
            for _ in range(10):
                (x0, y0), (x1, y1) = inv.transform(t.get_window_extent(r).get_points())
                tw, th = abs(x1 - x0), abs(y1 - y0)
                if (tw <= room_w and th <= room_h) or t.get_fontsize() <= base * 0.8:
                    break
                t.set_fontsize(t.get_fontsize() * 0.96)
            if tw > room_w or th > room_h:
                print(f"  ! {self.name}:{n.id} text {tw:.0f}x{th:.0f} > box {room_w:.0f}x{room_h:.0f}")

    def to_png(self, path, dpi=220):
        self._texts = []
        fig = plt.figure(figsize=(self.W / 96, self.H / 96))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, self.W)
        ax.set_ylim(self.H, 0)
        ax.axis("off")
        for i in self.order:
            if self.nodes[i].kind == "group":
                self._shape(ax, self.nodes[i])
                self._text(ax, self.nodes[i])
        for e in self.edges:
            self._edge(ax, e)
        for i in self.order:
            n = self.nodes[i]
            if n.kind != "group":
                self._shape(ax, n)
                self._text(ax, n)
        self._check_fit(fig, ax)
        fig.savefig(path, dpi=dpi, facecolor="white")
        plt.close(fig)

    def save(self, drawio_dir, png_dir):
        Path(drawio_dir).mkdir(parents=True, exist_ok=True)
        Path(png_dir).mkdir(parents=True, exist_ok=True)
        (Path(drawio_dir) / f"{self.name}.drawio").write_text(self.to_drawio(), encoding="utf-8")
        self.to_png(Path(png_dir) / f"{self.name}.png")
        return self
