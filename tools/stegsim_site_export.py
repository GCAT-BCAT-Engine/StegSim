"""
StegSim site export tool.
Reads run summaries and exports to site_data/stegsim_summary.json
for rendering on StegVerse transition pages.
Invoked as a declared task — no workflow file.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
def now():
return datetime.now(timezone.utc).isoformat()
def export_stegsim_data(runs_dir: str, output_dir: str):
runs_path = Path(runs_dir)
out_path = Path(output_dir)
out_path.mkdir(parents=True, exist_ok=True)
summaries = []
for summary_file in sorted(runs_path.glob("*/summary.json")):
try:
with open(summary_file) as f:
s = json.load(f)
summaries.append({
"run_id": s.get("run_id"),
"scenario": s.get("scenario"),
"seed": s.get("seed"),
"agents": s.get("agents"),
"steps": s.get("steps"),
"initial_v": s.get("initial_viability"),
"final_v": s.get("final_viability"),
"min_v": s.get("min_viability"),
"status": s.get("final_viability_status"),
"first_warning": s.get("first_warning_step"),
"first_inadmiss": s.get("first_inadmissible_step"),
"peak_lg_disagree": s.get("peak_local_global_disagreement_rate"),
"total_proposals": s.get("total_proposals"),
"accepted": s.get("accepted_count"),
"denied": s.get("denied_count"),
"total_receipts": s.get("total_receipts"),
"generated_at": s.get("generated_at"),
})
except Exception as e:
print(f"Warning: could not read {summary_file}: {e}")
export = {
"schema": "stegsim_site_export.v1",
"generated_at": now(),
"run_count": len(summaries),
"runs": summaries,
"headline": (
"All dashboards green. System already lost."
if any(s["peak_lg_disagree"] and s["peak_lg_disagree"] > 0.1 for s in summaries)
else "Simulation results available."
),
}
out_file = out_path / "stegsim_summary.json"
with open(out_file, "w") as f:
json.dump(export, f, indent=2)
print(f"Exported {len(summaries)} run summaries to {out_file}")
return export
if __name__ == "__main__":
runs_dir = sys.argv[1] if len(sys.argv) > 1 else "runs"
output_dir = sys.argv[2] if len(sys.argv) > 2 else "site_data"
export_stegsim_data(runs_dir, output_dir)
