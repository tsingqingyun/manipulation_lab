"""Six simultaneous group kernels, bounded shared resource queues, real runs only."""
import _bootstrap
import argparse
import csv
import os
from pathlib import Path
import subprocess
import time
import psutil
from manipulation_lab.common import ROOT, new_output, write_json
from manipulation_lab.teaching import read_json

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    p.add_argument("--checkpoint", default=str(ROOT / "checkpoints/instructor_reference.pth"))
    a = p.parse_args()
    output = new_output(a.output).resolve()
    start = time.monotonic()
    (output / "locks").mkdir()
    env = os.environ.copy()
    env.update({"LAB_OUTPUT_ROOT": str(output / "groups"), "LAB_REFERENCE_ROOT": str(output / "reference"),
                "LAB_LOCK_DIR": str(output / "locks"), "LAB_RESOURCE_AUDIT": str(output / "resource_events.jsonl")})
    python = str(ROOT / "scripts/lab_python.sh")
    write_json(output / "protocol.json", {"groups": [f"group_{i:02d}" for i in range(1, 7)],
        "student_seed": 17, "epochs": 50, "learning_rates": [.001, .0003], "test_seeds": [101, 102, 103, 104, 105],
        "same_initial_cases_per_group": True, "independent_statistical_replicates": False,
        "uid": os.getuid(), "available_ram_gib_at_start": psutil.virtual_memory().available / 2**30,
        "account_isolation_verified": False, "concurrency_scope": "six independent Jupyter kernels under one OS user"})
    with open(output / "reference.log", "x") as log:
        subprocess.run([python, str(ROOT / "scripts/prepare_reference.py"), "--checkpoint", a.checkpoint, "--output", str(output / "reference")],
                       cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    processes = []
    for i in range(1, 7):
        group = f"group_{i:02d}"
        log = open(output / f"{group}.log", "x")
        proc = subprocess.Popen([python, str(ROOT / "scripts/execute_notebooks.py"), "--group", group,
                                 "--output", str(output / "executed_notebooks" / group)],
                                cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        processes.append((group, proc, log))
    peak_process_tree_rss = 0
    peak_live_groups = 0
    while any(proc.poll() is None for _, proc, _ in processes):
        peak_live_groups = max(peak_live_groups, sum(proc.poll() is None for _, proc, _ in processes))
        total = 0
        for _, proc, _ in processes:
            try:
                parent = psutil.Process(proc.pid)
                total += sum(p.memory_info().rss for p in [parent, *parent.children(recursive=True)] if p.is_running())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        peak_process_tree_rss = max(peak_process_tree_rss, total)
        time.sleep(1)
    results = []
    selection = {}
    for group, proc, log in processes:
        log.close()
        execution = output / "executed_notebooks" / group / "execution.json"
        results.append({"group": group, "exit_code": proc.returncode,
                        "execution": read_json(execution) if execution.exists() else {"completed": False, "error": "No execution record"}})
        pointer = output / "groups" / group / "current_session.json"
        if pointer.is_file():
            selection[group] = os.path.relpath(read_json(pointer)["run"], output)
    write_json(output / "class_selection.json", selection)
    csv_status = subprocess.run([python, str(ROOT / "scripts/aggregate_results.py"), "--selection",
        str(output / "class_selection.json"), "--output", str(output / "class_results.csv")], cwd=ROOT).returncode
    events = [__import__('json').loads(line) for line in (output / "resource_events.jsonl").read_text().splitlines()]
    active, max_active, wait_starts, waits = {}, {}, {}, []
    for event in events:
        kind, pid, moment = event["kind"], event["pid"], event["monotonic"]
        active.setdefault(kind, set()); max_active.setdefault(kind, 0)
        if event["event"] == "requested":
            wait_starts[(kind, pid)] = moment
        elif event["event"] == "acquired":
            waits.append(moment - wait_starts[(kind, pid)])
            active[kind].add(pid); max_active[kind] = max(max_active[kind], len(active[kind]))
        elif event["event"] == "released":
            active[kind].remove(pid)
    passed = (peak_live_groups == 6 and all(r["exit_code"] == 0 and r["execution"]["completed"] for r in results)
              and csv_status == 0 and all(v == 1 for v in max_active.values()) and not any(active.values()))
    write_json(output / "acceptance.json", {"notebook_and_queue_acceptance_passed": passed,
        "formal_multiuser_deployment_passed": False, "account_isolation_verified": False,
        "limitation": "Same system UID; separate account permissions and JupyterHub authentication not verified",
        "elapsed_seconds": time.monotonic() - start, "groups": results, "peak_live_groups": peak_live_groups,
        "max_active_resource_slots": max_active,
        "max_queue_wait_seconds": max(waits), "peak_process_tree_rss_sum_gib": peak_process_tree_rss / 2**30,
        "rss_note": "Sum includes shared pages; not unique physical memory", "teacher_reference": read_json(output / "reference/reference_manifest.json")})
    if not passed:
        raise SystemExit("Acceptance failed; all group outputs retained")
    print("Six-group notebook and queue acceptance passed; independent-account deployment remains unverified")
