"""Plot the reflector shape options to docs/img/.

Usage: python3 tools/plot_reflector_options.py
"""
import math
import os
import sys

import matplotlib

matplotlib.use("svg")
# Deterministic SVG output: fixed element IDs, no date stamp.
matplotlib.rcParams["svg.hashsalt"] = "solar_cad"
matplotlib.rcParams["svg.fonttype"] = "path"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpc  # noqa: E402
import adjustment  # noqa: E402

ABSORBER_R = 55.0
GLASS_R = 62.5
CLEARANCE = 2.5
ANGLES = (20, 25, 30, 35)
TRUNC_HEIGHTS = (350, 450, 600)
DEFAULT_HEIGHT = 600
OUT_DIR = "docs/img"

# Reference palette, categorical slots 1-4 (fixed order).
COLORS = {20: "#2a78d6", 25: "#eb6834", 30: "#1baf7a", 35: "#eda100"}
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
TUBE_FILL = "#3d3c39"
GLASS = "#a9a8a2"


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.set_aspect("equal")
    ax.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for side in ax.spines:
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=TEXT_SECONDARY, length=0, labelsize=8)


def draw_tube(ax, labels=False):
    ax.add_patch(Circle((0, 0), GLASS_R, facecolor="none", edgecolor=GLASS, linewidth=1.5, zorder=4))
    ax.add_patch(Circle((0, 0), ABSORBER_R, facecolor=TUBE_FILL, edgecolor="none", zorder=4))
    if labels:
        ax.annotate(f"glass Ø {2 * GLASS_R:.0f}", (GLASS_R * 0.71, GLASS_R * 0.71), (90, 95),
                    color=TEXT_SECONDARY, fontsize=8, arrowprops=dict(arrowstyle="-", color=GLASS, linewidth=1))


def both(points):
    return [-p[0] for p in reversed(points)], [p[1] for p in reversed(points)], [p[0] for p in points], [p[1] for p in points]


def new_fig(w, h, ncols=1):
    fig, axes = plt.subplots(1, ncols, figsize=(w, h), dpi=100)
    fig.patch.set_facecolor(SURFACE)
    return fig, axes


def plot_acceptance_angles():
    fig = plt.figure(figsize=(9, 9), dpi=100)
    fig.patch.set_facecolor(SURFACE)
    grid = fig.add_gridspec(2, 1, height_ratios=(4, 1))
    ax = fig.add_subplot(grid[0])
    style(ax)
    draw_tube(ax, labels=True)
    rows = []
    for angle in ANGLES:
        pts = cpc.truncate(cpc.full_profile(ABSORBER_R, angle), DEFAULT_HEIGHT)
        xl, yl, xr, yr = both(pts)
        color = COLORS[angle]
        ax.plot(xl, yl, color=color, linewidth=2, solid_capstyle="round", label=f"θa = {angle}°", zorder=2)
        ax.plot(xr, yr, color=color, linewidth=2, solid_capstyle="round", zorder=2)
        # Ladder of labels above the right branch ends: wider profiles get lower labels.
        label_y = yr[-1] + 20 + 30 * ANGLES.index(angle)
        ax.plot([xr[-1], xr[-1]], [yr[-1] + 4, label_y - 3], color=color, linewidth=1, zorder=1)
        ax.text(xr[-1], label_y, f"θa = {angle}°: W = {cpc.aperture_width(pts):.0f} mm, C = {cpc.concentration(pts, ABSORBER_R):.2f}",
                color=TEXT_PRIMARY, fontsize=8, va="bottom", ha="left")
        settings = [len(adjustment.schedule(angle, decl)) for _, decl in adjustment.SEASONS]
        rows.append([f"{angle}°", f"{cpc.aperture_width(pts):.0f} mm", f"{cpc.concentration(pts, ABSORBER_R):.2f}"]
                    + [str(n) for n in settings])
    ax.set_xlim(-560, 760)
    ax.set_ylim(-120, 650)
    ax.set_xlabel("x (mm)", color=TEXT_SECONDARY)
    ax.set_ylabel("y (mm)", color=TEXT_SECONDARY)
    ax.set_title(f"Truncated CPC profiles, height {DEFAULT_HEIGHT} mm, absorber r = {ABSORBER_R:.0f} mm",
                 loc="left", color=TEXT_PRIMARY, fontsize=11)
    leg = ax.legend(loc="lower left", frameon=False, fontsize=8)
    for t in leg.get_texts():
        t.set_color(TEXT_PRIMARY)

    tab_ax = fig.add_subplot(grid[1])
    tab_ax.axis("off")
    header = ["θa", "Aperture W", "C"] + [f"Settings/day {name.lower()}" for name, _ in adjustment.SEASONS]
    table = tab_ax.table(cellText=rows, colLabels=header, loc="upper center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 1.3)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_facecolor(SURFACE)
        cell.get_text().set_color(TEXT_SECONDARY if row == 0 else TEXT_PRIMARY)
        if row > 0 and col == 0:
            cell.get_text().set_color(TEXT_PRIMARY)
    tab_ax.text(0, -0.08, f"Settings/day: reflector settings per day at {adjustment.LATITUDE_DEG:.0f}° N, sun elevation ≥ "
                f"{adjustment.MIN_ELEVATION_DEG:.0f}°, unit turned to face the sun azimuth. Rough estimate:\n"
                "the acceptance edge of a truncated CPC is gradual. Turning the unit for the azimuth (approx. every 30–60 min) is separate.",
                transform=tab_ax.transAxes, color=TEXT_SECONDARY, fontsize=7.5, va="top")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "cpc_acceptance_angles.svg"), facecolor=SURFACE, metadata={"Date": None})
    plt.close(fig)


def plot_truncation():
    fig, axes = new_fig(14, 7.5, ncols=len(ANGLES))
    full = {a: cpc.full_profile(ABSORBER_R, a) for a in ANGLES}
    ymax = max(p[-1][1] for p in full.values()) + 40
    xmax = max(cpc.aperture_width(p) for p in full.values()) / 2 + 20
    for ax, angle in zip(axes, ANGLES):
        style(ax)
        draw_tube(ax)
        pts = full[angle]
        y0 = cpc.bottom_y(pts)
        xl, yl, xr, yr = both(pts)
        ax.plot(xl, yl, color=GLASS, linewidth=1.5, zorder=1)
        ax.plot(xr, yr, color=GLASS, linewidth=1.5, zorder=1)
        cut = cpc.truncate(pts, DEFAULT_HEIGHT)
        cxl, cyl, cxr, cyr = both(cut)
        ax.plot(cxl, cyl, color=COLORS[angle], linewidth=2, solid_capstyle="round", zorder=2)
        ax.plot(cxr, cyr, color=COLORS[angle], linewidth=2, solid_capstyle="round", zorder=2)
        for h in TRUNC_HEIGHTS:
            t = cpc.truncate(pts, h)
            ax.axhline(y0 + h, color=TEXT_SECONDARY, linewidth=1, zorder=0)
            ax.text(0, y0 + h + 10, f"H {h}: C {cpc.concentration(t, ABSORBER_R):.2f}",
                    ha="center", color=TEXT_SECONDARY, fontsize=7.5,
                    bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1))
        top = pts[-1][1]
        ax.set_xlim(-xmax, xmax)
        ax.set_ylim(y0 - 30, ymax + 60)
        ax.set_title(f"θa = {angle}°\nfull CPC: H {top - y0:.0f}, C {cpc.concentration(pts, ABSORBER_R):.2f}",
                     color=TEXT_PRIMARY, fontsize=10)
    fig.suptitle(f"Full CPC (gray) and truncation heights H (mm); colored: H = {DEFAULT_HEIGHT}, same scale",
                 x=0.01, ha="left", color=TEXT_PRIMARY, fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "cpc_truncation.svg"), facecolor=SURFACE, metadata={"Date": None})
    plt.close(fig)


def plot_cusp_gap():
    angle = 30
    fig, ax = new_fig(9, 5.6)
    style(ax)
    draw_tube(ax)
    pts = cpc.full_profile(ABSORBER_R, angle, n=6000)
    xl, yl, xr, yr = both(pts)
    ax.plot(xl, yl, color=GLASS, linewidth=1.5, zorder=1, label="Ideal involute (intersects the glass)")
    ax.plot(xr, yr, color=GLASS, linewidth=1.5, zorder=1)
    r_cut = GLASS_R + CLEARANCE
    cut = cpc.cut_at_radius(pts, r_cut)
    cxl, cyl, cxr, cyr = both(cut)
    c1 = COLORS[20]
    ax.plot(cxl, cyl, color=c1, linewidth=2, zorder=3, label=f"G1: cut at r = {r_cut:.1f}, bridge arc")
    ax.plot(cxr, cyr, color=c1, linewidth=2, zorder=3)
    a0 = math.atan2(cut[0][1], cut[0][0])
    a1 = math.pi - a0 if a0 > 0 else -math.pi - a0
    arc = [a0 + (a1 - a0) * i / 50 for i in range(51)]
    ax.plot([r_cut * math.cos(a) for a in arc], [r_cut * math.sin(a) for a in arc], color=c1, linewidth=2, zorder=3)
    r_virt = r_cut
    virt = cpc.full_profile(r_virt, angle, n=6000)
    vxl, vyl, vxr, vyr = both(virt)
    c2 = COLORS[25]
    ax.plot(vxl, vyl, color=c2, linewidth=2, zorder=2, label=f"G2: CPC for virtual absorber r = {r_virt:.1f}")
    ax.plot(vxr, vyr, color=c2, linewidth=2, zorder=2)
    ax.annotate(f"G1 bridge arc: {2 * cut[0][0]:.1f} mm wide", (4, -r_cut + 1), (75, -58), color=TEXT_PRIMARY, fontsize=8,
                va="center", arrowprops=dict(arrowstyle="-", color=TEXT_SECONDARY, linewidth=1))
    ax.text(-ABSORBER_R + 8, 0, "absorber", color=SURFACE, fontsize=8, va="center", zorder=5)
    ax.text(GLASS_R + 4, 20, "glass", color=TEXT_SECONDARY, fontsize=8)
    ax.set_xlim(-200, 200)
    ax.set_ylim(-170, 60)
    ax.set_xlabel("x (mm)", color=TEXT_SECONDARY)
    ax.set_ylabel("y (mm)", color=TEXT_SECONDARY)
    ax.set_title(f"Cusp region, θa = {angle}°, absorber r = {ABSORBER_R:.0f} mm, clearance {CLEARANCE} mm",
                 loc="left", color=TEXT_PRIMARY, fontsize=11)
    leg = ax.legend(loc="upper left", frameon=False, fontsize=8)
    for t in leg.get_texts():
        t.set_color(TEXT_PRIMARY)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "cpc_cusp_gap.svg"), facecolor=SURFACE, metadata={"Date": None})
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    plot_acceptance_angles()
    plot_truncation()
    plot_cusp_gap()
