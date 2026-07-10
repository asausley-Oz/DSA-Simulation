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


def run_grid(base: EmergentConfig,
             param_x: str, values_x, param_y: str, values_y,
             seeds_per_cell: int = 8, workers: int = None,
             verbose: bool = True) -> pd.DataFrame:
    """2-D parameter grid, a small ensemble per cell. Returns one row per
    run, tagged with the cell's parameter values."""
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    jobs, tags = [], []
    for vx in values_x:
        for vy in values_y:
            cfg = dataclasses.replace(base, **{param_x: vx, param_y: vy})
            for s in range(seeds_per_cell):
                jobs.append((cfg, 1000 + s))
                tags.append((vx, vy))
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i, row in enumerate(pool.map(_run_one, jobs)):
            row[param_x], row[param_y] = tags[i]
            rows.append(row)
            if verbose and (i + 1) % 40 == 0:
                print(f"  {i + 1}/{len(jobs)} grid runs complete")
    df = pd.DataFrame(rows)
    df["outcome"] = df["ending"].str.replace(
        r"contested.*", "contested", regex=True)
    return df


def run_phase_lines(base: EmergentConfig, sweeps: dict,
                    seeds_per_value: int = 10, workers: int = None,
                    verbose: bool = True) -> pd.DataFrame:
    """1-D sweeps over several parameters — where does each tip the
    balance between renewal and consummation?"""
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    jobs, tags = [], []
    for param, values in sweeps.items():
        for v in values:
            cfg = dataclasses.replace(base, **{param: v})
            for s in range(seeds_per_value):
                jobs.append((cfg, 2000 + s))
                tags.append((param, v))
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i, row in enumerate(pool.map(_run_one, jobs)):
            row["parameter"], row["value"] = tags[i]
            rows.append(row)
            if verbose and (i + 1) % 50 == 0:
                print(f"  {i + 1}/{len(jobs)} sweep runs complete")
    df = pd.DataFrame(rows)
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
