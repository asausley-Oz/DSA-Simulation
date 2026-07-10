"""Ensemble mode: run the engine across many seeds and map the outcome
landscape. Identical rules, different providence — the distribution of
histories is the falsifiable object, not any single run.
"""

import dataclasses
import os
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

from .config import EmergentConfig
from .simulation import EmergentSimulation


def _run_one(args) -> dict:
    cfg, seed = args
    cfg = dataclasses.replace(cfg, seed=seed)
    sim = EmergentSimulation(cfg)
    sim.run(verbose=False)
    s = sim.get_summary()
    ev = s.pop("events_by_type")
    s.update({
        "seed": seed,
        "n_crises": ev.get("crisis", 0),
        "n_revivals": ev.get("revival", 0),
        "n_schisms": ev.get("schism", 0),
        "n_hardenings": ev.get("hardening", 0),
    })
    return s


def run_ensemble(base: EmergentConfig, n_seeds: int = 100,
                 workers: int = None, verbose: bool = True) -> pd.DataFrame:
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    jobs = [(base, seed) for seed in range(1, n_seeds + 1)]
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i, row in enumerate(pool.map(_run_one, jobs), 1):
            rows.append(row)
            if verbose and i % 20 == 0:
                print(f"  {i}/{n_seeds} histories complete")
    df = pd.DataFrame(rows)
    # Normalize the contested label for grouping.
    df["outcome"] = df["ending"].str.replace(
        r"contested.*", "contested", regex=True)
    return df


def summarize_ensemble(df: pd.DataFrame) -> str:
    lines = ["Outcome distribution:"]
    counts = df["outcome"].value_counts()
    for outcome, n in counts.items():
        pct = 100 * n / len(df)
        sub = df[df["outcome"] == outcome]
        lines.append(
            f"  {outcome:<14} {n:3d} ({pct:4.1f}%)  "
            f"median end tick {sub['ticks_run'].median():.0f}, "
            f"final delusion {sub['final_delusion'].mean():.2f}, "
            f"revivals {sub['n_revivals'].mean():.1f}")
    return "\n".join(lines)
