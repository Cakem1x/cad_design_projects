"""Release the laser files of a project for an order (tier 3).

Steps:
1. Require [sheet] provider and measured_thickness in <project>/fabrication.toml.
2. Run param_sync.py and dxf_check.py --strict (warnings fail) and the headless claims. All must pass.
3. Copy the BOM's laser files to <first dxf folder>/release/<YYYY-MM-DD>[-N]/ and write manifest.json:
   git commit and dirty flag, evaluated parameters of each design, fabrication.toml, per file the
   SHA-256, count and measurements, the check results.

DXFs stay untracked (.gitignore). Commit manifest.json as the record of the order.

Usage: python3 fabrication/tools/release.py <project>
"""
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import claims  # noqa: E402
import dxf_check  # noqa: E402
import param_sync  # noqa: E402
from projcfg import Config  # noqa: E402


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True).stdout.strip()


def main(argv):
    if not argv:
        sys.exit(__doc__)
    project = argv[0]
    cfg = Config(project)
    sheet = cfg.data.get("sheet", {})
    missing = [k for k in ("provider", "measured_thickness") if not sheet.get(k)]
    if missing:
        sys.exit(f"release refused: set [sheet] {', '.join(missing)} in {project}/fabrication.toml")
    # checks
    findings = param_sync.check(project)
    if param_sync.status(findings) != "OK":
        param_sync.main([project])
        sys.exit("release refused: parameter check failed")
    reports = dxf_check.run(project, strict=True)
    if dxf_check.overall(reports, True) != dxf_check.OK:
        dxf_check.main([project, "--strict"])
        sys.exit("release refused: DXF check failed (warnings count as errors here)")
    buf = io.StringIO()
    with redirect_stdout(buf):
        claims_failed = claims.main([project])
    if claims_failed:
        print(buf.getvalue())
        sys.exit("release refused: a headless claim failed")
    # copy
    bom = dxf_check.bom_entries(cfg) or {}
    folder = cfg.path(cfg.get("dxf", "folders")[0])
    base = os.path.join(folder, "release", datetime.date.today().isoformat())
    out, n = base, 1
    while os.path.exists(out):
        n += 1
        out = f"{base}-{n}"
    os.makedirs(out)
    files = []
    by_name = {r.name: r for r in reports}
    for name, count in bom.items():
        src = os.path.join(folder, name)
        shutil.copy2(src, out)
        with open(src, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        files.append({"file": name, "count": count, "sha256": digest,
                      "measurements": by_name[name].measurements if name in by_name else {}})
    root = git(cfg.root, "rev-parse", "--show-toplevel")
    designs = sorted(set(cfg.get("params", "designs", [])) | {cfg.data["design"]})
    manifest = {
        "date": datetime.datetime.now().isoformat(timespec="seconds"),
        "project": os.path.relpath(cfg.root, root) if root else project,
        "git": {"commit": git(cfg.root, "rev-parse", "HEAD"),
                "dirty": bool(git(cfg.root, "status", "--porcelain"))},
        "fabrication": cfg.data,
        "parameters": {d: {k: {"value": p.value, "unit": p.unit, "expr": p.expr} for k, p in cfg.params(d).items()}
                       for d in designs},
        "files": files,
        "checks": {"params": "OK", "dxf": "OK (strict)", "claims_headless": buf.getvalue().splitlines()},
    }
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, default=str)
    print(f"released {len(files)} file(s) to {os.path.relpath(out)}")
    if manifest["git"]["dirty"]:
        print("warning: working tree has uncommitted changes: the manifest's commit does not reproduce the files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
