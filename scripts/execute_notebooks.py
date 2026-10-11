"""Execute all four unchanged-on-disk notebooks for one group, preserving partial failure."""
import _bootstrap
import argparse
import os
import time
import traceback
import nbformat
from nbclient import NotebookClient
from manipulation_lab.common import ROOT, new_output, write_json

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--group", required=True, choices=[f"group_{i:02d}" for i in range(1, 7)])
    p.add_argument("--output", required=True)
    a = p.parse_args()
    output = new_output(a.output)
    os.environ["LAB_GROUP"] = a.group
    records = []
    for path in sorted((ROOT / "notebooks").glob("0[1-4]_*.ipynb")):
        notebook = nbformat.read(path, as_version=4)
        start = time.monotonic(); error = None
        try:
            client = NotebookClient(notebook, timeout=15000, kernel_name="manipulation-lab",
                                    resources={"metadata": {"path": str(ROOT)}})
            client.execute(env=os.environ.copy())
        except Exception:
            error = traceback.format_exc()
            (output / (path.stem + ".error.txt")).write_text(error)
        finally:
            nbformat.write(notebook, output / path.name)
            records.append({"notebook": path.name, "elapsed_seconds": time.monotonic() - start, "passed": error is None})
            write_json(output / "execution.json", {"group": a.group, "notebooks": records,
                       "completed": len(records) == 4 and all(x["passed"] for x in records)})
        if error:
            raise SystemExit(f"{a.group}: {path.name} failed; partial notebook and error retained")
    print(f"{a.group}: all four notebooks completed")
