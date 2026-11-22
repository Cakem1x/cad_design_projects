"""Read the parameter values of a SolidCraft design (.sc) without rebuilding it.

Responsibility: get parameter values out of a .sc file. Nothing else.

Method:
1. Read the user parameters (expression, unit) from document.json inside the .sc zip.
2. Sort them by reference (SolidCraft refuses forward references).
3. Evaluate them with SolidCraft's own evaluator: `solidcraft-cli run` on a script of only
   `parameters.add` steps and one `parameters.list`, without `--in`. No geometry is built.

Cost: < 1 s for the dodecahedron kit (a full headless rebuild takes > 5 min).
The file is read, not opened: it works while the app has the design open. It reads the saved
state, so save the design first.

Units: values are in mm and deg, as SolidCraft reports them.

Usage:
  python3 fabrication/tools/scparams.py <design.sc> [name ...] [--json]
  from scparams import load; p = load("design.sc"); p["t"].value
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass

IDENT = re.compile(r"[A-Za-z_]\w*")


@dataclass(frozen=True)
class Param:
    name: str
    value: float
    unit: str
    expr: str


class ParamError(Exception):
    pass


def read_expressions(path):
    """User parameters of the design: {name: (expression, unit)}, in file order."""
    try:
        with zipfile.ZipFile(path) as z:
            doc = json.loads(z.read("document.json"))
    except (OSError, KeyError, zipfile.BadZipFile, json.JSONDecodeError) as e:
        raise ParamError(f"{path}: not a readable SolidCraft design ({e})") from e
    return {p["name"]: (p["expr"], p["unit"]) for p in doc.get("params", []) if not p.get("model")}


def dependency_order(exprs, model_names=()):
    """Names sorted so that each parameter follows the parameters it references."""
    order, state = [], {}

    def visit(name, chain):
        if state.get(name) == "done":
            return
        if state.get(name) == "busy":
            raise ParamError(f"cyclic reference: {' -> '.join(chain + [name])}")
        state[name] = "busy"
        for tok in IDENT.findall(exprs[name][0]):
            if tok in exprs:
                visit(tok, chain + [name])
            elif tok in model_names:
                raise ParamError(f"parameter {name!r} references the model parameter {tok!r}")
        state[name] = "done"
        order.append(name)

    for n in exprs:
        visit(n, [])
    return order


def _model_names(path):
    with zipfile.ZipFile(path) as z:
        doc = json.loads(z.read("document.json"))
    return {p["name"] for p in doc.get("params", []) if p.get("model")}


def load(path, names=None, cli="solidcraft-cli"):
    """Evaluated user parameters of a .sc file: {name: Param}. `names` limits the result."""
    exprs = read_expressions(path)
    order = dependency_order(exprs, _model_names(path))
    steps = [{"command": "parameters.add",
              "params": {"name": n, "expression": exprs[n][0], "unit": exprs[n][1]}} for n in order]
    steps.append({"command": "parameters.list", "params": {"filter": "user"}})
    with tempfile.TemporaryDirectory(prefix="scparams-") as tmp:
        script, out = os.path.join(tmp, "params.json"), os.path.join(tmp, "out.json")
        with open(script, "w") as f:
            json.dump({"commands": steps}, f)
        try:
            run = subprocess.run([cli, "run", script, "--results", "--quiet", "--json-out", out],
                                 capture_output=True, text=True, timeout=60)
        except FileNotFoundError as e:
            raise ParamError(f"{cli} not found: run inside the Nix dev shell") from e
        if run.returncode != 0 or not os.path.exists(out):
            raise ParamError(f"{path}: SolidCraft evaluation failed: {(run.stderr or run.stdout).strip()}")
        with open(out) as f:
            listing = json.load(f)[-1]
    result = {}
    for p in listing["parameters"]:
        if p.get("error"):
            raise ParamError(f"{path}: parameter {p['name']!r}: {p['error']}")
        result[p["name"]] = Param(p["name"], float(p["value"]), p["unit"], p["expression"])
    if names:
        missing = [n for n in names if n not in result]
        if missing:
            raise ParamError(f"{path}: no parameter {', '.join(missing)}")
        result = {n: result[n] for n in names}
    return result


def main(argv):
    args = [a for a in argv if a != "--json"]
    if not args:
        sys.exit(__doc__)
    try:
        params = load(args[0], args[1:] or None)
    except ParamError as e:
        sys.exit(f"error: {e}")
    if "--json" in argv:
        print(json.dumps({n: {"value": p.value, "unit": p.unit, "expr": p.expr} for n, p in params.items()},
                         indent=1))
    else:
        for p in params.values():
            print(f"{p.name}\t{p.value:.6g}\t{p.unit}\t{p.expr}")


if __name__ == "__main__":
    main(sys.argv[1:])
