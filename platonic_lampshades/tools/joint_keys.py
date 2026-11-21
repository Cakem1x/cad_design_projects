"""Wooden cross-section keys for the dodecahedron edges. Writes a figure and laser DXFs.

Concept: a key is a flat plywood part in the plane perpendicular to an edge. That plane contains
both panel normals, so the key passes through both panels square to the sheet, and its outline
carries the dihedral angle exactly. Each key has two arms that lie on the inner faces of the two
panels; a tab on each arm passes through a slot in its panel. The key sets the dihedral angle.

Frame of the key (cross-section plane): origin at the inner corner P where the two panels touch,
y along the bisector into the solid, arm A to +x, arm B to -x.

Outputs (relative to platonic_lampshades/):
  docs/img/joint_key.svg                    cross-section, flat key, flat panel detail
  cad/dodecahedron/joint_test_x1.dxf        test coupon: 2 plates and 2 keys, kerf-compensated

The shade's keys come from the SolidCraft design (sketches KeySection, KeyLaser); keep the key
parameters here in sync with it.

Usage: python3 platonic_lampshades/tools/joint_keys.py
"""
import math
import os
import sys

import matplotlib

matplotlib.use("svg")
matplotlib.rcParams["svg.hashsalt"] = "platonic_lampshades"
matplotlib.rcParams["svg.fonttype"] = "path"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MplPolygon  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CAD_DIR = os.path.join(ROOT, "cad", "dodecahedron")
IMG_DIR = os.path.join(ROOT, "docs", "img")

# Design values (docs/overview.md), mm
T = 3.0                       # panel thickness
TK = 3.0                      # key thickness (same plywood)
KERF = 0.15
DELTA = 180.0 - math.degrees(math.atan(2.0))      # dihedral angle, 116.565 deg
RP = 71.074                   # panel inradius (outer face)
EDGE = 2 * RP * math.tan(math.radians(36))        # panel edge length

# Key parameters, mm
L_ARM = 18.0      # arm length on the inner face, from the inner corner P
D_KEY = 9.0       # key depth, normal to the inner face
H_TAB = 10.0      # tab centre distance from P (= slot centre distance from the panel edge)
W_TAB = 6.0       # tab width along the arm
TAB_OUT = 0.3     # tab length beyond the outer face (sand flush after gluing)
R_REL = 1.2       # relief at P: the key does not touch the panel inner corners
E_KEY = 50.0      # key spacing along the edge (2 keys per edge, centred)

# Fit parameters, mm (tune with the test coupon; slot = nominal + fit)
FIT_T = 0.0       # slot along the edge: key thickness + FIT_T
FIT_W = 0.0       # slot across the edge: tab width + FIT_W

# Test coupon
PLATE_W = 60.0    # along the edge
PLATE_L = 40.0    # from the edge
KEY_GAP = 3.0     # nesting gap on the sheet

ALPHA = math.radians(90.0 - DELTA / 2)            # arm A angle from +x
UA = (math.cos(ALPHA), math.sin(ALPHA))
NA = (-math.sin(ALPHA), math.cos(ALPHA))          # interior normal of panel A
UB = (-math.cos(ALPHA), math.sin(ALPHA))
NB = (math.sin(ALPHA), math.cos(ALPHA))


def pt(u, a, n, b):
    return (u[0] * a + n[0] * b, u[1] * a + n[1] * b)


def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def key_outline():
    """Key polygon (CCW) in the cross-section frame."""
    q_depth = D_KEY / math.sin(math.radians(DELTA / 2))         # inner body corner on the bisector
    out = T + TAB_OUT
    arm_a = [pt(UA, R_REL, NA, 0), pt(UA, H_TAB - W_TAB / 2, NA, 0), pt(UA, H_TAB - W_TAB / 2, NA, -out),
             pt(UA, H_TAB + W_TAB / 2, NA, -out), pt(UA, H_TAB + W_TAB / 2, NA, 0), pt(UA, L_ARM, NA, 0),
             pt(UA, L_ARM, NA, D_KEY)]
    arm_b = [pt(UB, L_ARM, NB, D_KEY), pt(UB, L_ARM, NB, 0), pt(UB, H_TAB + W_TAB / 2, NB, 0),
             pt(UB, H_TAB + W_TAB / 2, NB, -out), pt(UB, H_TAB - W_TAB / 2, NB, -out),
             pt(UB, H_TAB - W_TAB / 2, NB, 0), pt(UB, R_REL, NB, 0)]
    relief = [(0.0, R_REL * 1.2)]
    poly = arm_a + [(0.0, q_depth)] + arm_b + relief
    return poly if area(poly) > 0 else poly[::-1]


def panel_section(u, n, length):
    """Panel cross-section: band between the inner face (through P) and the outer face."""
    return [(0.0, 0.0), pt(u, length, n, 0), pt(u, length, n, -T), pt(n, -T, u, 0)]


def area(p):
    return 0.5 * sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))


def offset(poly, d):
    """Offset a simple CCW polygon outward by d (mitred corners)."""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % n]
        e1 = (p1[0] - p0[0], p1[1] - p0[1])
        e2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*e1), math.hypot(*e2)
        n1 = (e1[1] / l1, -e1[0] / l1)
        n2 = (e2[1] / l2, -e2[0] / l2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by)
        cosh = (n1[0] * n2[0] + n1[1] * n2[1] + 1) / 2
        m = d / math.sqrt(max(cosh, 1e-6))
        out.append((p1[0] + bx / bl * m, p1[1] + by / bl * m))
    return out


def rect(cx, cy, w, h):
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]


def check():
    """Geometric checks in the cross-section: returns a list of (name, value, ok)."""
    res = []
    q_depth = D_KEY / math.sin(math.radians(DELTA / 2))
    res.append(("tab to arm end (mm)", L_ARM - H_TAB - W_TAB / 2, L_ARM - H_TAB - W_TAB / 2 >= 3.0))
    res.append(("tab to relief (mm)", H_TAB - W_TAB / 2 - R_REL, H_TAB - W_TAB / 2 - R_REL >= 3.0))
    res.append(("key depth above relief (mm)", q_depth - 1.2 * R_REL, q_depth - 1.2 * R_REL >= 3.0))
    res.append(("slot web to panel edge (mm)", H_TAB - W_TAB / 2, H_TAB - W_TAB / 2 >= 3.0))
    # the tab of arm A must not enter panel B; panel B lies at x <= 0 in this frame
    c = pt(UA, H_TAB - W_TAB / 2, NA, -(T + TAB_OUT))
    res.append(("tab A clear of panel B (mm)", c[0], c[0] > 1.0))
    # keys of adjacent edges meet near the vertex: distance from key to the edge end
    res.append(("key to edge end (mm)", EDGE / 2 - E_KEY / 2 - TK / 2, EDGE / 2 - E_KEY / 2 - TK / 2 >= 15.0))
    return res


def dxf(polys, path):
    out = ["0", "SECTION", "2", "ENTITIES"]
    for p in polys:
        for i in range(len(p)):
            (x0, y0), (x1, y1) = p[i], p[(i + 1) % len(p)]
            out += ["0", "LINE", "8", "0", "10", f"{x0:.4f}", "20", f"{y0:.4f}", "30", "0",
                    "11", f"{x1:.4f}", "21", f"{y1:.4f}", "31", "0"]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


def laser_key(dx=0.0, dy=0.0):
    k = offset(key_outline(), KERF / 2)
    return [(x + dx, y + dy) for x, y in k]


def laser_plate(dx=0.0, dy=0.0):
    """Test plate, flat: x along the edge, y from the joining edge (y = 0) into the plate."""
    outline = offset([(0, 0), (PLATE_W, 0), (PLATE_W, PLATE_L), (0, PLATE_L)], KERF / 2)
    slots = []
    for sx in (PLATE_W / 2 - E_KEY_TEST / 2, PLATE_W / 2 + E_KEY_TEST / 2):
        s = rect(sx, H_TAB, TK + FIT_T, W_TAB + FIT_W)
        slots.append(offset(s, -KERF / 2) if area(s) > 0 else s)
    return [[(x + dx, y + dy) for x, y in p] for p in [outline] + slots]


E_KEY_TEST = 30.0   # key spacing on the 60 mm test plates


def figure(path):
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1.3, 1, 1]})
    fig.patch.set_facecolor("#fcfcfb")
    wood, key_c, ink, sec = "#d8b07a", "#2a78d6", "#3d3c39", "#52514e"
    # cross-section
    ax = axs[0]
    ax.add_patch(MplPolygon(panel_section(UA, NA, 32), closed=True, facecolor=wood, edgecolor=ink, lw=1))
    ax.add_patch(MplPolygon(panel_section(UB, NB, 32), closed=True, facecolor=wood, edgecolor=ink, lw=1))
    ax.add_patch(MplPolygon(key_outline(), closed=True, facecolor=key_c, alpha=0.75, edgecolor=ink, lw=1))
    ax.text(-31, 22, f"dihedral {DELTA:.2f}° (between the inner faces)", fontsize=8, color=sec)
    ax.text(22, 4, "panel A", fontsize=8, color=ink, rotation=math.degrees(ALPHA))
    ax.text(-30, 18, "panel B", fontsize=8, color=ink, rotation=-math.degrees(ALPHA))
    ax.text(-6, 13, "key", fontsize=8, color="#0b0b0b")
    ax.text(5, -9, "tabs pass through\nslots, end flush\nwith the outer face", fontsize=7, color=sec)
    ax.set_title("Cross-section perpendicular to the edge (inside up)", fontsize=9, loc="left")
    ax.set_aspect("equal")
    ax.set_xlim(-32, 32)
    ax.set_ylim(-12, 24)
    ax.axis("off")
    # flat key
    ax = axs[1]
    k = key_outline()
    ax.add_patch(MplPolygon(k, closed=True, facecolor=key_c, alpha=0.75, edgecolor=ink, lw=1))
    xs, ys = [p[0] for p in k], [p[1] for p in k]
    ax.set_xlim(min(xs) - 3, max(xs) + 3)
    ax.set_ylim(min(ys) - 3, max(ys) + 3)
    ax.set_aspect("equal")
    ax.set_title(f"Key, flat ({max(xs) - min(xs):.1f} mm x {max(ys) - min(ys):.1f} mm, {TK:.0f} mm plywood)",
                 fontsize=9, loc="left")
    ax.tick_params(labelsize=7, colors=sec, length=0)
    for s in ax.spines:
        ax.spines[s].set_visible(False)
    # flat panel detail
    ax = axs[2]
    half = EDGE / 2
    ax.add_patch(MplPolygon([(-half - 5, 0), (half + 5, 0), (half + 5, 30), (-half - 5, 30)], closed=True,
                            facecolor=wood, edgecolor="none"))
    ax.plot([-half, half], [0, 0], color=ink, lw=1.2)
    for sx in (-E_KEY / 2, E_KEY / 2):
        ax.add_patch(MplPolygon(rect(sx, H_TAB, TK, W_TAB), closed=True, facecolor="#fcfcfb", edgecolor=ink, lw=0.8))
        ax.plot([sx, sx], [0, L_ARM], color=key_c, lw=TK * 1.2, alpha=0.5, solid_capstyle="butt")
    ax.text(-half, -5, f"panel edge {EDGE:.1f} mm", fontsize=7, color=sec)
    ax.text(-12, 18, f"2 slots {TK:.0f} x {W_TAB:.0f} mm\nat {H_TAB:.0f} mm from the edge,\n{E_KEY:.0f} mm apart",
            fontsize=7, color=sec)
    ax.set_aspect("equal")
    ax.set_xlim(-half - 6, half + 6)
    ax.set_ylim(-9, 32)
    ax.axis("off")
    ax.set_title("Panel edge, inner face (blue: key arm footprint)", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(path, facecolor="#fcfcfb")
    plt.close(fig)


def main():
    ok = True
    for name, val, good in check():
        print(f"{name}: {val:.2f} {'OK' if good else 'FAIL'}")
        ok &= good
    k = key_outline()
    xs, ys = [p[0] for p in k], [p[1] for p in k]
    print(f"key bbox {max(xs) - min(xs):.2f} x {max(ys) - min(ys):.2f} mm, area {area(k):.1f} mm^2")
    figure(os.path.join(IMG_DIR, "joint_key.svg"))
    if not ok:
        print("CHECK FAILED: no DXF written")
        sys.exit(1)
    kw = max(xs) - min(xs)
    kh = max(ys) - min(ys)
    polys = laser_plate(0, 0) + laser_plate(PLATE_W + KEY_GAP, 0)
    for i in range(2):
        polys.append(laser_key(-min(xs) + i * (kw + KEY_GAP), PLATE_L + KEY_GAP - min(ys)))
    dxf(polys, os.path.join(CAD_DIR, "joint_test_x1.dxf"))
    print(f"test coupon sheet: {2 * PLATE_W + KEY_GAP:.0f} x {PLATE_L + KEY_GAP + kh:.0f} mm")


if __name__ == "__main__":
    main()
