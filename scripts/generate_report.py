import _bootstrap
import argparse
from manipulation_lab.common import new_output
from manipulation_lab.notebook import stage_path
from manipulation_lab.reporting import generate_report

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    output = new_output(a.output)
    print(generate_report(a.run, output, stage_path(a.run, "training"), stage_path(a.run, "evaluation"), stage_path(a.run, "analysis")))
