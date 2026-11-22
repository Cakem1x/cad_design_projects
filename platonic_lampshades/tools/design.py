"""Design parameters of the dodecahedron prototype, read from the SolidCraft designs.

The .sc designs are the single source of the design values. The tools import them from here
and do not copy them. Values in mm and deg (fabrication/tools/scparams.py).

  KIT         cad/dodecahedron/dodecahedron_kit.sc   the shade
  JOINT_TEST  cad/dodecahedron/joint_test.sc         the joint test coupon

Save the design in SolidCraft before you run a tool: the tools read the saved file.
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "..", "fabrication", "tools"))
from scparams import ParamError, load  # noqa: E402

KIT_SC = os.path.join(ROOT, "cad", "dodecahedron", "dodecahedron_kit.sc")
JOINT_TEST_SC = os.path.join(ROOT, "cad", "dodecahedron", "joint_test.sc")


def _values(path):
    try:
        return {n: p.value for n, p in load(path).items()}
    except ParamError as e:
        sys.exit(f"error: {e}")


KIT = _values(KIT_SC)
JOINT_TEST = _values(JOINT_TEST_SC)
