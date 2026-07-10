"""Sensitivity analysis for the Emergent Covenant Engine.

One-factor-at-a-time sweeps over any numeric config parameter, with
multiple seeds per value so stochastic scatter is visible in the output.
"""

import dataclasses
import pandas as pd
from typing import Dict, List

from .config import EmergentConfig
from .simulation import EmergentSimulation


DEFAULT_SWEEP: Dict[str, List[float]] = {
    "bent": [0.004, 0.005, 0.006, 0.007, 0.008],
    "labor_efficiency": [0.05, 0.07, 0.085, 0.10, 0.12],
    "conversion_base": [0.03, 0.05, 0.06, 0.08, 0.10],
    "comfort_erosion": [0.05, 0.08, 0.10, 0.13, 0.16],
    "revival_threshold": [0.6, 0.8, 1.0, 1.2, 1.5],
}


def run_sensitivity(base: EmergentConfig,
                    sweep: Dict[str, List[float]] = None,
                    n_runs: int = 3,
                    n_ticks: int = 300,
                    verbose: bool = True) -> pd.DataFrame:
    sweep = sweep or DEFAULT_SWEEP
    rows = []
    for param, values in sweep.items():
        for value in values:
            for run in range(n_runs):
                cfg = dataclasses.replace(
                    base, n_ticks=n_ticks,
                    seed=(base.seed or 0) + run * 1000 + 7)
                setattr(cfg, param, value)
                sim = EmergentSimulation(cfg)
                hist = sim.run(verbose=False)
                summary = sim.get_summary()
                rows.append({
                    "parameter": param,
                    "value": value,
                    "run": run,
                    "ending": summary["ending"],
                    "final_entropy": summary["final_entropy"],
                    "final_remnant": summary["final_remnant_share"],
                    "n_crises": summary["events_by_type"].get("crisis", 0),
                    "n_revivals": summary["events_by_type"].get("revival", 0),
                    "n_schisms": summary["events_by_type"].get("schism", 0),
                    "total_martyrs": summary["total_martyrs"],
                })
            if verbose:
                print(f"  {param}={value}: done ({n_runs} runs)")
    return pd.DataFrame(rows)
