"""Run the whole pipeline top to bottom on the raw files.

Order: PMS cleaning, CRM cleaning, merge, describe, analysis.
Each notebook runs in its own folder (so its relative paths work) with a fresh
namespace, exactly as "Restart & Run All" would. The notebooks themselves are
not modified: only the files in data/processed/ are rewritten.

Usage, from the Project folder:
    python run_all.py            # quiet: one line per notebook
    python run_all.py --verbose  # also prints every notebook's output
"""

import contextlib
import io
import json
import os
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # charts are drawn but not opened in windows

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent
NOTEBOOKS = [
    "cleaning/pms_cleaning.ipynb",
    "cleaning/crm_cleaning.ipynb",
    "merge/merge.ipynb",
    "describe/describe.ipynb",
    "analysis/analysis.ipynb",
]
OUTPUTS = [
    "data/processed/pms_clean.csv",
    "data/processed/crm_clean.csv",
    "data/processed/merged_clean.csv",
]


def run_notebook(path: Path, verbose: bool) -> int:
    """Execute the code cells of one notebook in order; return how many ran."""
    cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
    code_cells = [c for c in cells if c["cell_type"] == "code"]
    namespace = {"__name__": "__main__"}
    old_cwd = os.getcwd()
    os.chdir(path.parent)
    try:
        for i, cell in enumerate(code_cells, start=1):
            source = "".join(cell["source"])
            # IPython magics (%...) and shell commands (!...) are not Python
            source = "\n".join(
                line for line in source.splitlines()
                if not line.lstrip().startswith(("%", "!"))
            )
            out = sys.stdout if verbose else io.StringIO()
            with contextlib.redirect_stdout(out):
                try:
                    exec(compile(source, f"{path.name} [cell {i}]", "exec"), namespace)
                except Exception:
                    print(f"\nFAILED in {path.name}, code cell {i}:\n{source}\n", file=sys.stderr)
                    raise
            plt.close("all")
    finally:
        os.chdir(old_cwd)
    return len(code_cells)


def main() -> None:
    verbose = "--verbose" in sys.argv
    start = time.time()
    for nb in NOTEBOOKS:
        t0 = time.time()
        n = run_notebook(ROOT / nb, verbose)
        print(f"OK  {nb:<32} {n:>3} code cells  {time.time() - t0:5.1f}s")

    print("\nClean tables written:")
    for out in OUTPUTS:
        df = pd.read_csv(ROOT / out)
        print(f"    {out:<34} {len(df):>6,} rows x {df.shape[1]} columns")
    print(f"\nPipeline finished in {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
