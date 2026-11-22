"""Manufacturing check of laser DXF files (tier 1, < 2 s). Rules: fabrication/laser_cutting.md.

Laser files are `*_x<N>.dxf` in the folders of <project>/fabrication.toml ([dxf] folders).
Other DXFs (for example pattern inputs) are not checked.

Result per file and for the run:
  OK           every rule was evaluated, no error. Warnings may remain. Exit 0.
  FAILED       at least one error: the file cannot be cut as drawn. Exit 1.
  NOT CHECKED  a rule could not be evaluated (for example an unsupported entity). Never a pass. Exit 3.
  With --strict, warnings fail too (used by release.py).

Rules (error unless noted):
  entities      LINE, ARC, CIRCLE, LWPOLYLINE only; others: NOT CHECKED
  units         $INSUNITS = 4 (mm) when present; drawing 1 mm ... 2000 mm
  open          every contour closed (endpoint tolerance 0.001 mm)
  duplicate     no duplicate or overlapping segments
  branch        no point shared by more than 2 segments
  self_cross    no self-intersecting contour, no crossing contours
  island        no contour inside a hole (falls out), unless allowed in [dxf] allow_islands
  layers        with role layers: outlines on OUTLINE, holes on CUT
  web           cut web (drawn distance - kerf) >= web_min: hole to hole, hole to outline
  hole          narrowest hole (inscribed circle diameter + kerf) >= hole_min
  sheet         each part fits the sheet minus the margins (rotation allowed)
  part_size     warning: part smaller than part_min
  part_gap      warning: parts closer than part_gap in one file
  bom           warning: file not in the BOM or [dxf.sources]; count in the file name differs from the BOM
  stale         warning: file older than one of its sources ([dxf.sources])

Usage: python3 fabrication/tools/dxf_check.py <project> [file.dxf ...] [--json] [--strict]
"""
import argparse
import json
import math
import os
import re
import sys

from shapely import STRtree, maximum_inscribed_circle, shortest_line
from shapely.geometry import Polygon
from shapely.validation import explain_validity

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from projcfg import Config  # noqa: E402
from scparams import ParamError  # noqa: E402

OK, FAILED, NOT_CHECKED = "OK", "FAILED", "NOT CHECKED"
TOL = 1e-3          # endpoint snap, mm
CHORD = 0.005       # arc discretisation sag, mm
MAX_LOC = 8         # locations listed per rule
LASER = re.compile(r".+_x(\d+)\.dxf$")
ROLE_LAYERS = {"OUTLINE", "CUT"}
SUPPORTED = {"LINE", "ARC", "CIRCLE", "LWPOLYLINE"}


# ---------- findings ----------
class Report:
    def __init__(self, name):
        self.name = name
        self.findings = []      # dict(rule, severity, message, at)
        self.measurements = {}

    def add(self, rule, severity, message, at=()):
        self.findings.append({"rule": rule, "severity": severity, "message": message,
                              "at": [[round(x, 3), round(y, 3)] for x, y in at]})

    def status(self, strict=False):
        sev = {f["severity"] for f in self.findings}
        if "error" in sev or (strict and "warning" in sev):
            return FAILED
        if "not_checked" in sev:
            return NOT_CHECKED
        return OK


# ---------- DXF reading ----------
def read_dxf(path):
    """Units ($INSUNITS or None) and entities [(type, [(code, value), ...])] of the ENTITIES section."""
    with open(path, errors="replace") as f:
        lines = [ln.strip() for ln in f.read().splitlines()]
    pairs = [(int(lines[i]), lines[i + 1]) for i in range(0, len(lines) - 1, 2) if lines[i].lstrip("-").isdigit()]
    units, section, entities, i = None, None, [], 0
    while i < len(pairs):
        code, val = pairs[i]
        if code == 0 and val == "SECTION" and i + 1 < len(pairs):
            section = pairs[i + 1][1]
            i += 2
            continue
        if code == 0 and val == "ENDSEC":
            section = None
        elif section == "HEADER" and code == 9 and val == "$INSUNITS" and i + 1 < len(pairs):
            units = int(pairs[i + 1][1])
        elif section == "ENTITIES" and code == 0:
            entities.append((val, []))
        elif section == "ENTITIES" and entities:
            entities[-1][1].append((code, val))
        i += 1
    return units, entities


def _arc_points(c, r, a0, a1):
    sweep = (a1 - a0) % 360.0 or 360.0
    step = 2 * math.degrees(math.acos(max(-1.0, 1 - CHORD / r))) if r > CHORD else sweep
    n = max(2, math.ceil(sweep / step) + 1)
    return [(c[0] + r * math.cos(math.radians(a0 + sweep * k / (n - 1))),
             c[1] + r * math.sin(math.radians(a0 + sweep * k / (n - 1)))) for k in range(n)]


def _bulge_arc(p, q, bulge):
    """Arc from p to q with DXF bulge: (centre, radius, a0, a1) counter-clockwise."""
    theta = 4 * math.atan(bulge)
    chord = math.dist(p, q)
    r = abs(chord / (2 * math.sin(theta / 2)))
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    h = r * math.cos(theta / 2) * (1 if bulge > 0 else -1)
    ux, uy = (q[0] - p[0]) / chord, (q[1] - p[1]) / chord
    c = (mx - uy * h, my + ux * h)
    a_p = math.degrees(math.atan2(p[1] - c[1], p[0] - c[0]))
    a_q = math.degrees(math.atan2(q[1] - c[1], q[0] - c[0]))
    return (c, r, a_p, a_q) if bulge > 0 else (c, r, a_q, a_p)


def segments(entities, rep):
    """Segments: dict(kind L|A|C, layer, a, b, pts, key for duplicates)."""
    segs, unsupported = [], {}
    for typ, codes in entities:
        if typ not in SUPPORTED:
            unsupported[typ] = unsupported.get(typ, 0) + 1
            continue
        d = {}
        for code, val in codes:
            d.setdefault(code, val)
        layer = d.get(8, "0")
        if typ == "LINE":
            a = (float(d[10]), float(d[20]))
            b = (float(d[11]), float(d[21]))
            if math.dist(a, b) > TOL:
                segs.append(dict(kind="L", layer=layer, a=a, b=b, pts=[a, b]))
        elif typ in ("ARC", "CIRCLE"):
            c, r = (float(d[10]), float(d[20])), float(d[40])
            if typ == "CIRCLE":
                segs.append(dict(kind="C", layer=layer, c=c, r=r, pts=_arc_points(c, r, 0, 360)))
            else:
                a0, a1 = float(d[50]), float(d[51])
                pts = _arc_points(c, r, a0, a1)
                segs.append(dict(kind="A", layer=layer, c=c, r=r, a0=a0, a1=a1, a=pts[0], b=pts[-1], pts=pts))
        else:  # LWPOLYLINE
            verts, closed = [], int(d.get(70, "0")) & 1
            for code, val in codes:
                if code == 10:
                    verts.append([float(val), None, 0.0])
                elif code == 20 and verts:
                    verts[-1][1] = float(val)
                elif code == 42 and verts:
                    verts[-1][2] = float(val)
            n = len(verts) if closed else len(verts) - 1
            for k in range(n):
                p, q, bulge = tuple(verts[k][:2]), tuple(verts[(k + 1) % len(verts)][:2]), verts[k][2]
                if math.dist(p, q) <= TOL:
                    continue
                if abs(bulge) < 1e-9:
                    segs.append(dict(kind="L", layer=layer, a=p, b=q, pts=[p, q]))
                else:
                    c, r, a0, a1 = _bulge_arc(p, q, bulge)
                    pts = _arc_points(c, r, a0, a1)
                    if bulge < 0:
                        pts = pts[::-1]
                    segs.append(dict(kind="A", layer=layer, c=c, r=r, a0=a0, a1=a1, a=p, b=q, pts=pts))
    for typ, n in unsupported.items():
        rep.add("entities", "not_checked", f"{n} {typ} entit{'y' if n == 1 else 'ies'} not supported (convert to lines and arcs)")
    return segs


# ---------- topology ----------
class Snapper:
    def __init__(self):
        self.cells, self.points = {}, []

    def node(self, p):
        cx, cy = math.floor(p[0] / TOL), math.floor(p[1] / TOL)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for n in self.cells.get((cx + dx, cy + dy), ()):
                    if math.dist(self.points[n], p) <= TOL:
                        return n
        self.points.append(p)
        self.cells.setdefault((cx, cy), []).append(len(self.points) - 1)
        return len(self.points) - 1


def check_duplicates(segs, nodes, rep):
    seen, dups = {}, []
    for i, s in enumerate(segs):
        if s["kind"] == "C":
            key = ("C", round(s["c"][0], 3), round(s["c"][1], 3), round(s["r"], 3))
        else:
            key = (s["kind"],) + tuple(sorted((nodes[i][0], nodes[i][1])))
            if s["kind"] == "A":
                key += (round(s["r"], 3),)
        if key in seen:
            dups.append(s["pts"][0])
        seen[key] = i
    # collinear overlap of lines with different end points
    groups = {}
    for s in segs:
        if s["kind"] != "L":
            continue
        (x0, y0), (x1, y1) = s["a"], s["b"]
        th = math.atan2(y1 - y0, x1 - x0) % math.pi
        if th > math.pi - 1e-7:
            th = 0.0
        off = -math.sin(th) * x0 + math.cos(th) * y0
        t0, t1 = sorted((math.cos(th) * x0 + math.sin(th) * y0, math.cos(th) * x1 + math.sin(th) * y1))
        groups.setdefault((round(th, 6), round(off, 3)), []).append((t0, t1, s["a"]))
    overlaps = []
    for ivs in groups.values():
        ivs.sort()
        end = -math.inf
        for t0, t1, p in ivs:
            if t0 < end - TOL:
                overlaps.append(p)
            end = max(end, t1)
    found = dups + [p for p in overlaps if p not in dups]
    if found:
        rep.add("duplicate", "error", f"{len(found)} duplicate or overlapping segment(s)", found[:MAX_LOC])


def loops(segs, rep):
    """Closed loops [(points, layers)] from the segments; reports open ends and branches."""
    snap = Snapper()
    nodes = {}
    adj = {}
    result = []
    for i, s in enumerate(segs):
        if s["kind"] == "C":
            result.append((s["pts"], {s["layer"]}))
            continue
        na, nb = snap.node(s["a"]), snap.node(s["b"])
        nodes[i] = (na, nb)
        adj.setdefault(na, []).append(i)
        adj.setdefault(nb, []).append(i)
    check_duplicates(segs, {i: nodes.get(i, (None, None)) for i in range(len(segs))}, rep)
    open_ends = [snap.points[n] for n, e in adj.items() if len(e) == 1]
    branches = [snap.points[n] for n, e in adj.items() if len(e) > 2]
    if open_ends:
        rep.add("open", "error", f"{len(open_ends)} open end(s): contour not closed", open_ends[:MAX_LOC])
    if branches:
        rep.add("branch", "error", f"{len(branches)} point(s) shared by more than 2 segments", branches[:MAX_LOC])
    used = set()
    for start in nodes:
        if start in used:
            continue
        pts, layers, seg, node, ok = [], set(), start, nodes[start][0], True
        while True:
            used.add(seg)
            layers.add(segs[seg]["layer"])
            na, nb = nodes[seg]
            p = segs[seg]["pts"] if na == node else segs[seg]["pts"][::-1]
            pts.extend(p[:-1])
            node = nb if na == node else na
            nxt = [e for e in adj[node] if e != seg]
            if len(adj[node]) != 2 or not nxt:
                ok = False
                break
            seg = nxt[0]
            if seg == start:
                break
            if seg in used:
                ok = False
                break
        if ok and len(pts) >= 3:
            result.append((pts, layers))
    return result


# ---------- geometry checks ----------
def _rect_sides(poly):
    r = poly.minimum_rotated_rectangle
    c = list(r.exterior.coords)
    return sorted((math.dist(c[0], c[1]), math.dist(c[1], c[2])), reverse=True)


def _mid(line):
    (x0, y0), (x1, y1) = line.coords[0], line.coords[-1]
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def check_geometry(loop_list, rep, cfg, name):
    polys = []
    for pts, layers in loop_list:
        poly = Polygon(pts)
        if not poly.is_valid:
            rep.add("self_cross", "error", f"self-intersecting contour: {explain_validity(poly)}", [pts[0]])
            poly = poly.buffer(0)
            if poly.geom_type != "Polygon" or poly.is_empty:
                continue
        polys.append((poly, layers))
    if not polys:
        rep.add("open", "not_checked" if not rep.findings else "error", "no closed contour")
        return
    polys.sort(key=lambda pl: -pl[0].area)
    tree = STRtree([p for p, _ in polys])
    # crossing contours
    crossings = []
    for i, (p, _) in enumerate(polys):
        for j in tree.query(p):
            if j > i and p.exterior.intersects(polys[j][0].exterior):
                crossings.append(_mid(shortest_line(p.exterior, polys[j][0].exterior)))
    if crossings:
        rep.add("self_cross", "error", f"{len(crossings)} pair(s) of crossing contours", crossings[:MAX_LOC])
    # containment depth and parent
    depth, parent = [0] * len(polys), [None] * len(polys)
    for i, (p, _) in enumerate(polys):
        rp = p.representative_point()
        for j in tree.query(rp):
            if j < i and polys[j][0].contains(rp):
                depth[i] += 1
                if parent[i] is None or polys[j][0].area < polys[parent[i]][0].area:
                    parent[i] = j
    parts = [i for i in range(len(polys)) if depth[i] == 0]
    holes = [i for i in range(len(polys)) if depth[i] == 1]
    islands = [i for i in range(len(polys)) if depth[i] >= 2]
    rep.measurements.update(parts=len(parts), holes=len(holes))
    if islands and name not in cfg.get("dxf", "allow_islands", []):
        rep.add("island", "error", f"{len(islands)} contour(s) inside a hole: they fall out",
                [polys[i][0].representative_point().coords[0] for i in islands[:MAX_LOC]])
    # layers
    all_layers = set().union(*(lay for _, lay in polys))
    if all_layers & ROLE_LAYERS:
        wrong = [i for i in range(len(polys))
                 if polys[i][1] != ({"OUTLINE"} if depth[i] == 0 else {"CUT"})]
        if wrong:
            rep.add("layers", "error", f"{len(wrong)} contour(s) on the wrong layer (outline: OUTLINE, hole: CUT)",
                    [polys[i][0].exterior.coords[0] for i in wrong[:MAX_LOC]])
    else:
        rep.add("layers", "info", "no role layers (OUTLINE, CUT): layer rule not applicable")
    # units and size
    minx, miny, maxx, maxy = (min(p.bounds[k] for p, _ in polys) if k < 2 else max(p.bounds[k] for p, _ in polys)
                              for k in range(4))
    span = max(maxx - minx, maxy - miny)
    rep.measurements["bbox_mm"] = [round(maxx - minx, 2), round(maxy - miny, 2)]
    if span < 1 or span > 2000:
        rep.add("units", "error", f"drawing spans {span:.3g}: not in mm?")
    kerf = cfg.value(cfg.get("dxf", "kerf", 0.0))
    web_min = cfg.value(cfg.get("dxf", "web_min", 3.0))
    hole_min = cfg.value(cfg.get("dxf", "hole_min", 1.5))
    sheet = sorted(cfg.get("sheet", "size", [1200, 600]), reverse=True)
    margin = cfg.value(cfg.get("sheet", "margin", 5.0))
    part_min = cfg.value(cfg.get("dxf", "part_min", 20.0))
    part_gap = cfg.value(cfg.get("dxf", "part_gap", 2.0))
    # parts: sheet fit, size
    for i in parts:
        L, W = _rect_sides(polys[i][0])
        at = [polys[i][0].exterior.coords[0]]
        if L > sheet[0] - 2 * margin or W > sheet[1] - 2 * margin:
            rep.add("sheet", "error", f"part {L:.1f} x {W:.1f} mm exceeds the sheet {sheet[0]} x {sheet[1]} mm "
                    f"minus {margin:g} mm margins", at)
        if L < part_min:
            rep.add("part_size", "warning", f"part {L:.1f} x {W:.1f} mm is smaller than {part_min:g} mm", at)
    # gap between parts
    close = []
    ptree = STRtree([polys[i][0] for i in parts])
    for a, i in enumerate(parts):
        for b in ptree.query(polys[i][0], predicate="dwithin", distance=part_gap):
            if b > a:
                close.append(_mid(shortest_line(polys[i][0].exterior, polys[parts[b]][0].exterior)))
    if close:
        rep.add("part_gap", "warning", f"{len(close)} pair(s) of parts closer than {part_gap:g} mm", close[:MAX_LOC])
    # webs: hole to hole and hole to its part outline
    search = web_min + kerf + 1.0
    hole_geoms = [polys[i][0] for i in holes]
    htree = STRtree(hole_geoms)
    webs = []          # (cut web, location)
    for a, i in enumerate(holes):
        h = polys[i][0]
        for b in htree.query(h, predicate="dwithin", distance=search):
            if b > a:
                line = shortest_line(h.exterior, hole_geoms[b].exterior)
                webs.append((line.length - kerf, _mid(line)))
        outline = polys[parent[i]][0].exterior
        line = shortest_line(h.exterior, outline)
        if line.length <= search:
            webs.append((line.length - kerf, _mid(line)))
    if webs:
        wmin = min(w for w, _ in webs)
        rep.measurements["min_web_mm"] = round(wmin, 3)
        thin = sorted((w, p) for w, p in webs if w < web_min - 1e-6)
        if thin:
            rep.add("web", "error", f"{len(thin)} web(s) under {web_min:g} mm (min {thin[0][0]:.2f} mm, cut width)",
                    [p for _, p in thin[:MAX_LOC]])
    # narrowest hole
    narrow, hmin = [], math.inf
    for i in holes:
        line = maximum_inscribed_circle(polys[i][0], 0.005)
        width = 2 * line.length + kerf
        hmin = min(hmin, width)
        if width < hole_min - 1e-6:
            narrow.append((width, line.coords[0]))
    if holes:
        rep.measurements["min_hole_mm"] = round(hmin, 3)
    if narrow:
        narrow.sort()
        rep.add("hole", "error", f"{len(narrow)} hole(s) narrower than {hole_min:g} mm (min {narrow[0][0]:.2f} mm)",
                [p for _, p in narrow[:MAX_LOC]])


# ---------- project checks ----------
def bom_entries(cfg):
    """{file: count} from the BOM table: rows with a count cell and a `*_x<N>.dxf` cell."""
    path = cfg.path(cfg.data.get("bom", ""))
    if not os.path.isfile(path):
        return None
    entries = {}
    with open(path) as f:
        for line in f:
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            files = [m for c in cells for m in re.findall(r"[\w.-]+_x\d+\.dxf", c)]
            counts = [int(c) for c in cells if c.isdigit()]
            for fn in files:
                entries[fn] = counts[0] if counts else None
    return entries


def check_project(rep, path, cfg, bom):
    name = os.path.basename(path)
    m = LASER.match(name)
    sources = cfg.get("dxf", "sources", {})
    if bom is not None and name not in bom and name not in sources:
        rep.add("bom", "warning", f"not in the BOM ({cfg.data.get('bom')}) or [dxf.sources]: stale export?")
    if bom and name in bom and bom[name] is not None and m and int(m.group(1)) != bom[name]:
        rep.add("bom", "warning", f"file name count x{m.group(1)} differs from the BOM count {bom[name]}")
    mtime = os.path.getmtime(path)
    for src in sources.get(name, []):
        sp = cfg.path(src)
        if os.path.exists(sp) and os.path.getmtime(sp) > mtime + 1:
            rep.add("stale", "warning", f"older than {src}: export or regenerate it")


def check_file(path, cfg, bom):
    rep = Report(os.path.basename(path))
    try:
        units, entities = read_dxf(path)
    except (OSError, ValueError) as e:
        rep.add("entities", "not_checked", f"unreadable: {e}")
        return rep
    if units is not None and units != 4:
        rep.add("units", "error", f"$INSUNITS = {units}, expected 4 (mm)")
    segs = segments(entities, rep)
    if not segs:
        rep.add("entities", "not_checked", "no cut geometry")
        return rep
    loop_list = loops(segs, rep)
    if any(f["rule"] in ("open", "branch", "duplicate") for f in rep.findings):
        # broken contours change which loop is a part and which a hole: the figures would mislead
        rep.add("geometry", "not_checked", "web, hole, layer, island and sheet rules skipped: fix the contours first")
    else:
        check_geometry(loop_list, rep, cfg, rep.name)
    check_project(rep, path, cfg, bom)
    return rep


def laser_files(cfg):
    out = []
    for folder in cfg.get("dxf", "folders", []) or [cfg.data.get("dxf", {}).get("folders", [])]:
        d = cfg.path(folder)
        if os.path.isdir(d):
            out += sorted(os.path.join(d, f) for f in os.listdir(d) if LASER.match(f))
    return out


def summary_line(rep, strict):
    st = rep.status(strict)
    meas = rep.measurements
    bits = []
    if "parts" in meas:
        bits.append(f"{meas['parts']} part(s), {meas['holes']} hole(s)")
    if "bbox_mm" in meas:
        bits.append(f"{meas['bbox_mm'][0]:.1f} x {meas['bbox_mm'][1]:.1f} mm")
    if "min_web_mm" in meas:
        bits.append(f"web >= {meas['min_web_mm']:.2f} mm")
    if "min_hole_mm" in meas:
        bits.append(f"hole >= {meas['min_hole_mm']:.2f} mm")
    return f"{st:<12}{rep.name}: " + ", ".join(bits)


def run(project, files=(), strict=False):
    cfg = Config(project)
    paths = [os.path.abspath(f) for f in files] if files else laser_files(cfg)
    bom = bom_entries(cfg)
    reports = []
    try:
        cfg.value(cfg.get("dxf", "kerf", 0.0))
    except (ParamError, KeyError) as e:
        rep = Report("parameters")
        rep.add("parameters", "not_checked", f"design parameters not readable: {e}")
        return [rep]
    for p in paths:
        if not LASER.match(os.path.basename(p)):
            continue
        reports.append(check_file(p, cfg, bom))
    if bom:
        present = {r.name for r in reports}
        for fn in bom:
            if not files and fn not in present:
                rep = Report(fn)
                rep.add("bom", "warning", "in the BOM, but no file: export it")
                reports.append(rep)
    return reports


def overall(reports, strict):
    sts = [r.status(strict) for r in reports]
    if FAILED in sts:
        return FAILED
    if NOT_CHECKED in sts or not reports:
        return NOT_CHECKED
    return OK


def main(argv):
    ap = argparse.ArgumentParser(description="Check laser DXF files.")
    ap.add_argument("project")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="warnings fail")
    a = ap.parse_args(argv)
    reports = run(a.project, a.files, a.strict)
    st = overall(reports, a.strict)
    n_warn = sum(f["severity"] == "warning" for r in reports for f in r.findings)
    counts = {s: sum(r.status(a.strict) == s for r in reports) for s in (FAILED, NOT_CHECKED)}
    tail = (f"{st} dxf {a.project}: {len(reports)} file(s), {counts[FAILED]} failed, "
            f"{counts[NOT_CHECKED]} not checked, {n_warn} warning(s)")
    if a.json:
        print(json.dumps({"status": st, "summary": tail,
                          "files": [{"file": r.name, "status": r.status(a.strict), "findings": r.findings,
                                     "measurements": r.measurements} for r in reports]}, indent=1))
    else:
        for r in reports:
            print(summary_line(r, a.strict))
            for f in r.findings:
                if f["severity"] == "info":
                    continue
                loc = "; at " + ", ".join(f"({x:.2f}, {y:.2f})" for x, y in f["at"]) if f["at"] else ""
                print(f"    {f['severity']}: {f['rule']}: {f['message']}{loc}")
        print(tail)
    return {OK: 0, FAILED: 1, NOT_CHECKED: 3}[st]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
