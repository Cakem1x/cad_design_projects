"""Project fabrication config: <project>/fabrication.toml.

A string value names a parameter of the project's `design` (.sc); a number is a fixed value.
`Config.value(x)` resolves either. Parameters are read once per process (scparams.py).
"""
import os
import sys
import tomllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scparams import load  # noqa: E402


class Config:
    def __init__(self, project_dir):
        self.root = os.path.abspath(project_dir)
        path = os.path.join(self.root, "fabrication.toml")
        with open(path, "rb") as f:
            self.data = tomllib.load(f)
        self._params = {}

    def path(self, rel):
        return os.path.join(self.root, rel)

    def params(self, design=None):
        """Evaluated parameters of a design (default: the project design), cached."""
        rel = design or self.data["design"]
        if rel not in self._params:
            self._params[rel] = load(self.path(rel))
        return self._params[rel]

    def value(self, x):
        """A number, or the value of the named parameter of the project design."""
        if isinstance(x, str):
            return self.params()[x].value
        return float(x)

    def get(self, section, key, default=None):
        return self.data.get(section, {}).get(key, default)
