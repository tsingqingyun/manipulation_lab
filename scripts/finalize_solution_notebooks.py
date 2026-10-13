"""Execute answer edits on an existing complete run; never repeat training or evaluation.

The source notebook outputs are retained. A separate kernel executes the edited
answer cells for 01--03; 04 is executed in full to regenerate annotated evidence.
"""
import _bootstrap
import argparse
import json
import os
from pathlib import Path
import time

import nbformat
from nbclient import NotebookClient

from manipulation_lab.common import ROOT, new_output, sha256, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executed", type=Path, required=True)
    parser.add_argument("--answers", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    execution = json.loads((args.executed / "execution.json").read_text())
    if not execution["completed"]:
        raise ValueError("All four original notebooks must have completed first")
    answers = json.loads(args.answers.read_text())
    required = ["Q1", "TRAJECTORY_REFLECTION", "Q2", "Q3", "Q4", "FAILURE_STAGE",
                "FIRST_OBSERVABLE_ERROR", "HYPOTHESIZED_CAUSE", "IMPROVEMENT"]
    if any(not answers.get(k, "").strip() for k in required):
        raise ValueError("All solution answers must be nonempty")
    if type(answers["FIRST_ERROR_STEP"]) is not int or len(set(answers["KEYFRAME_STEPS"])) < 3:
        raise ValueError("Supply an evidence-based error marker and at least three steps")
    output = new_output(args.output)
    records = []
    for number, path in enumerate(sorted(args.executed.glob("0[1-4]_*.ipynb")), 1):
        notebook = nbformat.read(path, as_version=4)
        start = time.monotonic()
        if number < 4:
            answer_index = {1: 7, 2: 9, 3: 9}[number]
            fields = {1: ["Q1", "TRAJECTORY_REFLECTION"], 2: ["Q2", "Q3"], 3: ["Q4"]}[number]
            cell = notebook.cells[answer_index]
            for key in fields:
                cell.source = cell.source.replace(f'{key} = ""', f'{key} = {answers[key]!r}')
            cell.source += '\n' + '\n'.join(
                f'display(Markdown("**{key} — Instructor solution**\\n\\n" + {key}))' for key in fields)
            setup = notebook.cells[1].source.replace("workspace(GROUP, fresh=True)", "workspace(GROUP)")
            if number == 1:
                setup += '\nfrom manipulation_lab.dataset import inspect\nimport h5py\ninfo = inspect(DATA)\nEPISODE = "demo_0"\nwith h5py.File(DATA, "r") as f:\n    expert_actions = f["data"][EPISODE]["actions"][:]'
            edits = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(setup),
                                                   nbformat.v4.new_code_cell(cell.source)])
            client = NotebookClient(edits, timeout=300, kernel_name="manipulation-lab",
                                    resources={"metadata": {"path": str(ROOT)}})
            client.execute(env=os.environ.copy())
            notebook.cells[answer_index] = edits.cells[1]
            scope = "original computation retained; setup and edited answer cell executed in a fresh kernel"
        else:
            for i in [4, 7]:
                lines = notebook.cells[i].source.splitlines()
                for j, line in enumerate(lines):
                    key = line.split(" = ", 1)[0]
                    if key in answers:
                        lines[j] = f"{key} = {answers[key]!r}"
                notebook.cells[i].source = "\n".join(lines)
            notebook.cells[2].source = notebook.cells[2].source.replace(
                'EPISODE = failures[0]["episode_id"]', f'EPISODE = {answers["EPISODE"]!r}')
            notebook.cells[7].source += '\ndisplay(Markdown("**Q5 — Instructor solution**\\n\\n" + FIRST_OBSERVABLE_ERROR + "\\n\\n**Hypothesis:** " + HYPOTHESIZED_CAUSE + "\\n\\n**Proposed test:** " + IMPROVEMENT))'
            client = NotebookClient(notebook, timeout=600, kernel_name="manipulation-lab",
                                    resources={"metadata": {"path": str(ROOT)}})
            client.execute(env=os.environ.copy())
            scope = "all cells executed; analysis/report/export only; no training or evaluation repeated"
        for cell in notebook.cells:
            if cell.cell_type == "markdown":
                cell.source = cell.source.replace("- [ ]", "- [x]")
        notebook.cells[0].source += (
            "\n\n> **Executed instructor solution — 2026-10-13.** "
            "Original student templates are preserved. Computation and answer-edit sessions are "
            "recorded in solution_execution.json. These answers interpret this particular run. "
            "Training and policy evaluation were each performed once in the completed run.")
        notebook.metadata["solution_execution"] = {"source_sha256": sha256(path), "scope": scope,
                                                   "answers_sha256": sha256(args.answers)}
        nbformat.validate(notebook)
        assert all(c.execution_count is not None and not any(o.output_type == "error" for o in c.outputs)
                   for c in notebook.cells if c.cell_type == "code")
        nbformat.write(notebook, output / path.name)
        records.append({"notebook": path.name, "scope": scope, "elapsed_seconds": time.monotonic() - start,
                        "sha256": sha256(output / path.name)})
        write_json(output / "solution_execution.json", {"original_execution": execution,
                   "answer_edits": records, "completed": len(records) == 4})
        print(f"Completed solution: {path.name}", flush=True)


if __name__ == "__main__":
    main()
