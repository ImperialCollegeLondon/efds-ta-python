#!/usr/bin/env python3
"""
Generate completed/ and root / notebooks from completed/solutions/ notebooks.

Cell tag conventions in solution notebooks:
  (none) → keep source in both completed/ and root /
  hide   → keep source in completed/, clear source in root /
  todo   → clear source in both completed/ and root /
  Markdown cells are always preserved as-is; all outputs cleared everywhere.
"""

import copy
import glob
import json
import os
import sys

SOLUTIONS_DIR = "completed/solutions"
COMPLETED_DIR = "completed"
ROOT_DIR = "."

DRY_RUN = "--dry-run" in sys.argv


def cleared(cell):
    c = copy.deepcopy(cell)
    c["outputs"] = []
    c["execution_count"] = None
    c.get("metadata", {}).pop("tags", None)
    return c


def make_completed(nb):
    out = copy.deepcopy(nb)
    cells = []
    for cell in out["cells"]:
        if cell["cell_type"] == "markdown":
            cells.append(cell)
        elif cell["cell_type"] == "code":
            tags = cell.get("metadata", {}).get("tags", [])
            if "todo" in tags:
                c = cleared(cell)
                c["source"] = []
                cells.append(c)
            else:
                cells.append(cleared(cell))
    out["cells"] = cells
    return out


def make_root(nb):
    out = copy.deepcopy(nb)
    cells = []
    for cell in out["cells"]:
        if cell["cell_type"] == "markdown":
            cells.append(cell)
        elif cell["cell_type"] == "code":
            tags = cell.get("metadata", {}).get("tags", [])
            if "hide" in tags or "todo" in tags:
                c = cleared(cell)
                c["source"] = []
                cells.append(c)
            else:
                cells.append(cleared(cell))
    out["cells"] = cells
    return out


def write(path, nb):
    if DRY_RUN:
        print(f"  [dry-run] would write {path}")
        return
    with open(path, "w") as f:
        json.dump(nb, f, indent=1)
    print(f"  wrote {path}")


for sol_path in sorted(glob.glob(os.path.join(SOLUTIONS_DIR, "*.ipynb"))):
    name = os.path.basename(sol_path)
    print(name)

    with open(sol_path) as f:
        nb = json.load(f)

    write(os.path.join(COMPLETED_DIR, name), make_completed(nb))
    write(os.path.join(ROOT_DIR, name), make_root(nb))
