"""Light on the table through the bottom panel: projection of the panel holes with a finite source.

Model:
- The bulb is a disc light source of diameter SOURCE_D at the centre of the solid (frosted A60
  bulb: 60 mm; clear LED filament bulb: about 25 mm).
- A table point receives light from the source centre if the ray passes a hole on the outer and
  on the inner face of the bottom panel (point-source mask).
- The finite source blurs the mask: convolution with a disc of diameter
  SOURCE_D * (L - d) / d, with L the distance from the source to the table and d the distance to
  the panel (docs/light_patterns.md, Projection sharpness).
- Illuminance falls with cos^3 of the angle from the axis.
- Result: relative illuminance, 1 = no bottom panel, on the axis. Light through the lower ring
  panels is not included.

Room values: docs/light_patterns.md (Room and lamp height). Keep them in sync with
tools/plot_sight_lines.py.

Usage as a library: table_light(holes) and draw_table(ax, ...); tools/bottom_pattern.py and
prototypes/bottom_pattern_study.py use it.
Usage as a script: python3 platonic_lampshades/tools/table_light.py PATTERN.dxf OUT.svg
  PATTERN.dxf: nominal cutouts of a bottom panel in the base panel frame (for example
  cad/dodecahedron/bottom_pattern.dxf).
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel_pattern as pp  # noqa: E402
from panel_pattern import plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.path import Path  # noqa: E402

SHADE_BOTTOM = 1000.0          # shade bottom above the table, mm
TABLE = (1600.0, 900.0)        # table length, width, mm
L_TABLE = pp.RI + SHADE_BOTTOM # source (centre of the solid) to the table, mm
D_OUT, D_IN = pp.RI, pp.RI - pp.T   # source to the outer / inner face of the bottom panel, mm
SOURCES = {"clear filament bulb (Ø 25 mm)": 25.0, "frosted A60 bulb (Ø 60 mm)": 60.0}
HALF = 1300.0                  # half size of the table window, mm
STEP = 4.0                     # table grid, mm


def blur_width(source_d):
    """Blur width on the table (mm) for a source of diameter source_d."""
    d = (D_OUT + D_IN) / 2
    return source_d * (L_TABLE - d) / d


def table_light(holes, source_d):
    """Relative illuminance on the table grid. holes: CCW polylines in the base panel frame, mm.
    Returns (t, E): t the grid coordinates (mm from the axis), E[y, x]."""
    t = np.arange(-HALF, HALF + STEP, STEP)
    TX, TY = np.meshgrid(t, t)
    paths = [Path(p) for p in holes]

    def open_at(d):
        pts = np.stack([TX.ravel() * d / L_TABLE, TY.ravel() * d / L_TABLE], axis=1)
        m = np.zeros(len(pts), bool)
        for path in paths:
            m |= path.contains_points(pts)
        return m.reshape(TX.shape)

    mask = (open_at(D_OUT) & open_at(D_IN)).astype(float)
    r = blur_width(source_d) / 2
    k = (TX ** 2 + TY ** 2 <= r * r).astype(float)
    k /= k.sum()
    conv = np.real(np.fft.ifft2(np.fft.fft2(mask) * np.fft.fft2(np.fft.ifftshift(k))))
    cos = L_TABLE / np.sqrt(L_TABLE ** 2 + TX ** 2 + TY ** 2)
    return t, np.clip(conv, 0, 1) * cos ** 3


def draw_table(ax, t, E, label, ticks=True):
    """Illuminance map with the table outline (blue) and the 50 % contour (dashed)."""
    im = ax.imshow(E, origin="lower", extent=[t[0], t[-1], t[0], t[-1]], cmap="magma", vmin=0, vmax=1)
    ax.add_patch(Rectangle((-TABLE[0] / 2, -TABLE[1] / 2), *TABLE, fill=False, edgecolor="#7fd1ff", linewidth=1))
    ax.contour(t, t, E, levels=[0.5], colors="#ffffff", linewidths=0.6, linestyles=[(0, (2, 2))])
    ax.set_aspect("equal")
    if ticks:
        ax.set_xticks([-1000, -500, 0, 500, 1000])
        ax.set_yticks([-1000, -500, 0, 500, 1000])
        ax.tick_params(labelsize=6)
    else:
        ax.set_xticks([])
        ax.set_yticks([])
    ax.set_title(label, fontsize=7, loc="left")
    return im


def figure(holes, panel_title, path):
    """Panel and the table light for each source in SOURCES, side by side."""
    fig, axes = plt.subplots(1, 1 + len(SOURCES), figsize=(4 * (1 + len(SOURCES)), 4))
    fig.patch.set_facecolor("#fcfcfb")
    pp.draw_panel(axes[0], holes, {i: "#2b2a28" for i in range(len(holes))})
    axes[0].set_aspect("equal")
    axes[0].set_xlim(-pp.RP - 4, pp.RV + 4)
    axes[0].set_ylim(-pp.RV - 4, pp.RV + 4)
    axes[0].axis("off")
    axes[0].set_title(panel_title, fontsize=7, loc="left")
    for ax, (label, src) in zip(axes[1:], SOURCES.items()):
        t, E = table_light(holes, src)
        im = draw_table(ax, t, E, f"{label}, blur {blur_width(src):.0f} mm")
    fig.colorbar(im, ax=list(axes[1:]), shrink=0.8, label="relative illuminance")
    fig.text(0.01, 0.01, f"Table {TABLE[0]:.0f} mm × {TABLE[1]:.0f} mm (blue), {SHADE_BOTTOM:.0f} mm below the "
             "shade. Dashed: 50 %. Bottom panel only; light through the lower ring not included.",
             fontsize=6.5, color="#52514e")
    fig.savefig(path, facecolor="#fcfcfb")
    plt.close(fig)


def read_dxf(path):
    """Closed polylines from a DXF of LINE entities (as written by panel_pattern.dxf)."""
    v = [s.strip() for s in open(path).read().split("\n")]
    segs = []
    for i in range(len(v) - 1):
        if v[i] == "0" and v[i + 1] == "LINE":
            g = dict(zip(v[i + 2:i + 20:2], v[i + 3:i + 21:2]))
            segs.append(((float(g["10"]), float(g["20"])), (float(g["11"]), float(g["21"]))))
    loops, cur = [], []
    for a, b in segs:
        cur.append(a)
        if cur and math.dist(b, cur[0]) < 1e-6:
            p = np.array(cur)
            loops.append(p if pp.polygon_area(p) > 0 else p[::-1])
            cur = []
    return loops


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: table_light.py PATTERN.dxf OUT.svg")
    src, out = sys.argv[1], sys.argv[2]
    holes = read_dxf(src)
    area = sum(pp.polygon_area(p) for p in holes)
    figure(holes, f"{os.path.basename(src)}: {len(holes)} holes, open {100 * area / pp.PANEL_AREA:.0f} %", out)
    print(f"written: {os.path.relpath(out)}")


if __name__ == "__main__":
    main()
