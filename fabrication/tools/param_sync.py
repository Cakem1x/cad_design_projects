"""Parameter consistency check (tier 1, < 1 s). Config: <project>/fabrication.toml [params].

Rules:
  designs   same-named parameters of the designs in [params] designs agree (except allow_differ)
  docs      parameter table rows "| `name` | value unit | ..." match the design's value to the
            printed decimals; a row with several names (`a`, `b`) applies to each
  sheet     [sheet] measured_thickness, when set, is within 0.05 mm of the nominal thickness

Result: OK (exit 0), FAILED (exit 1), NOT CHECKED (exit 3: a design was not readable).

Usage: python3 fabrication/tools/param_sync.py <project> [--json]
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from projcfg import Config  # noqa: E402
from scparams import ParamError  # noqa: E402

ROW = re.compile(r"^\|\s*((?:`[A-Za-z_]\w*`\s*,?\s*)+)\|\s*(-?\d+(?:\.(\d+))?)\s*(mm|°|deg)?\s*\|")
UNITS = {"mm": "mm", "°": "deg", "deg": "deg", None: None}
THICKNESS_TOL = 0.05   # mm


def doc_rows(path):
    """[(line number, [names], value, decimals, unit)] of the parameter table rows."""
    rows = []
    with open(path) as f:
        for n, line in enumerate(f, 1):
            m = ROW.match(line)
            if m:
                names = re.findall(r"`(\w+)`", m.group(1))
                rows.append((n, names, float(m.group(2)), len(m.group(3) or ""), UNITS[m.group(4)]))
    return rows


def check(project):
    cfg = Config(project)
    findings = []   # (severity, rule, message)
    sec = cfg.data.get("params", {})
    designs = sec.get("designs", [])
    try:
        values = {d: cfg.params(d) for d in designs}
        for doc in sec.get("docs", []):
            values.setdefault(doc["design"], cfg.params(doc["design"]))
    except ParamError as e:
        return [("not_checked", "designs", str(e))]
    # same-named parameters across designs
    allow = set(sec.get("allow_differ", []))
    for i, a in enumerate(designs):
        for b in designs[i + 1:]:
            for name in sorted(set(values[a]) & set(values[b]) - allow):
                va, vb = values[a][name].value, values[b][name].value
                if abs(va - vb) > 1e-9 * max(1.0, abs(va)):
                    findings.append(("error", "designs", f"`{name}`: {va:g} in {a}, {vb:g} in {b}"))
    # docs tables
    for doc in sec.get("docs", []):
        params = values[doc["design"]]
        for line, names, val, dec, unit in doc_rows(cfg.path(doc["file"])):
            for name in names:
                where = f"{doc['file']}:{line}"
                if name not in params:
                    findings.append(("warning", "docs", f"{where}: `{name}` is no parameter of {doc['design']}"))
                    continue
                p = params[name]
                if unit and p.unit != unit:
                    findings.append(("error", "docs", f"{where}: `{name}` unit {unit}, design {p.unit}"))
                elif abs(p.value - val) > 0.5 * 10 ** -dec + 1e-9:
                    findings.append(("error", "docs", f"{where}: `{name}` = {val:.{dec}f}, design "
                                     f"{p.value:.{max(dec, 3)}f} {p.unit} ({p.expr})"))
    # measured sheet thickness
    measured = cfg.get("sheet", "measured_thickness")
    if measured is not None:
        nominal = cfg.value(cfg.get("sheet", "thickness", "t"))
        if abs(measured - nominal) > THICKNESS_TOL:
            findings.append(("warning", "sheet", f"measured thickness {measured:g} mm differs from the design "
                             f"thickness {nominal:g} mm by more than {THICKNESS_TOL} mm: update the design"))
    return findings


def status(findings):
    sev = {s for s, _, _ in findings}
    return "FAILED" if "error" in sev else "NOT CHECKED" if "not_checked" in sev else "OK"


def main(argv):
    ap = argparse.ArgumentParser(description="Check parameter consistency.")
    ap.add_argument("project")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    findings = check(a.project)
    st = status(findings)
    n_err = sum(s == "error" for s, _, _ in findings)
    n_warn = sum(s == "warning" for s, _, _ in findings)
    tail = f"{st} params {a.project}: {n_err} error(s), {n_warn} warning(s)"
    if a.json:
        print(json.dumps({"status": st, "summary": tail,
                          "findings": [{"severity": s, "rule": r, "message": m} for s, r, m in findings]}, indent=1))
    else:
        for s, r, m in findings:
            print(f"    {s}: {r}: {m}")
        print(tail)
    return {"OK": 0, "FAILED": 1, "NOT CHECKED": 3}[st]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
