"""Design claims (tier 2). Config: <project>/claims.toml.

Runs the headless claims with solidcraft-cli and compares the last result with `expect`.
Lists the app and manual claims with what to do. Exit: 1 when a headless claim fails, else 0.

Usage: python3 fabrication/tools/claims.py <project> [id ...]
"""
import json
import os
import subprocess
import sys
import tempfile
import tomllib


def run_headless(root, claim):
    design = os.path.join(root, claim["design"])
    with tempfile.TemporaryDirectory(prefix="claims-") as tmp:
        script, out = os.path.join(tmp, "claim.json"), os.path.join(tmp, "out.json")
        with open(script, "w") as f:
            json.dump({"commands": claim["commands"]}, f)
        r = subprocess.run(["solidcraft-cli", "run", script, "--in", design, "--results", "--quiet",
                            "--json-out", out], capture_output=True, text=True, timeout=600)
        if r.returncode != 0 or not os.path.exists(out):
            return False, f"run failed: {(r.stderr or r.stdout).strip()}"
        with open(out) as f:
            result = json.load(f)[-1]
    bad = [f"{k} = {result.get(k)!r}, expected {v!r}" for k, v in claim["expect"].items() if result.get(k) != v]
    return not bad, "; ".join(bad) or ", ".join(f"{k} = {result.get(k)!r}" for k in claim["expect"])


def main(argv):
    if not argv:
        sys.exit(__doc__)
    root = os.path.abspath(argv[0])
    with open(os.path.join(root, "claims.toml"), "rb") as f:
        claims = tomllib.load(f)["claim"]
    ids = set(argv[1:])
    failed = 0
    for c in claims:
        if ids and c["id"] not in ids:
            continue
        if c["where"] == "headless":
            ok, msg = run_headless(root, c)
            failed += not ok
            print(f"{'OK' if ok else 'FAILED':<8}{c['id']}  {c['title']}: {msg}")
        elif c["where"] == "app":
            call = c.get("how") or (f"execute {c['command']} {json.dumps(c.get('params', {}))}, bodies {c['bodies']}"
                                    f"; expect {json.dumps(c['expect'])}")
            print(f"{'APP':<8}{c['id']}  {c['title']}: {call}")
        else:
            print(f"{'MANUAL':<8}{c['id']}  {c['title']}: {c['how']}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
