#!/usr/bin/env python3
"""DSA v7 — Emergent Covenant Engine runner.

Nothing in this engine reads a date. Wars, revivals, schisms, persecution
waves, secular drift, and the ending itself all emerge from coupled
feedback between agents and their regional environments. Different seeds
produce genuinely different histories from identical rules.

Usage:
    python run_emergent.py                   # default 600-tick run
    python run_emergent.py --ticks 1000 --agents 20000
    python run_emergent.py --seed 7          # a different history
    python run_emergent.py --sensitivity     # parameter sweeps
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from emergent import EmergentConfig, EmergentSimulation
from emergent.analysis import run_sensitivity


def plot_run(history, events, env_names, out_dir: Path):
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))

    ax = axes[0, 0]
    ax.plot(history["tick"], history["entropy"], lw=2, label="global")
    for name in env_names:
        ax.plot(history["tick"], history[f"entropy_{name}"],
                lw=0.7, alpha=0.6, label=name)
    ax.set_title("Entropy (global + regional)")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.plot(history["tick"], history["remnant_share"] * 100, lw=2,
            color="tab:green", label="global")
    for name in env_names:
        ax.plot(history["tick"], history[f"remnant_{name}"] * 100,
                lw=0.7, alpha=0.6, label=name)
    ax.set_title("Remnant share (%)")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(alpha=0.3)

    ax = axes[1, 0]
    ax.plot(history["tick"], history["comfort"], label="comfort")
    ax.plot(history["tick"], history["receptivity"], label="receptivity")
    ax.plot(history["tick"], history["unity"], label="unity")
    ax.plot(history["tick"], history["persecution"], label="persecution")
    ax.set_title("The secular cycle: comfort vs. receptivity")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = axes[1, 1]
    ax.plot(history["tick"], history["strain"], color="tab:red",
            label="strain")
    ax.plot(history["tick"], history["vamphoric"], color="tab:purple",
            label="vamphoric")
    ax2 = ax.twinx()
    ax2.fill_between(history["tick"], history["crises_active"],
                     alpha=0.25, color="tab:red", step="mid")
    ax2.set_ylabel("active crises", fontsize=8)
    ax.set_title("Strain -> crisis ignition")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = axes[2, 0]
    ax.plot(history["tick"], history["conversions"], lw=0.8,
            label="conversions")
    ax.plot(history["tick"], history["apostasies"], lw=0.8,
            label="apostasies")
    ax.plot(history["tick"], history["martyrs"], lw=0.8, label="martyrs")
    ax.set_title("Flows per tick")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Event raster: when and where things happened.
    ax = axes[2, 1]
    colors = {"crisis": "tab:red", "revival": "tab:green",
              "schism": "tab:orange", "consummation": "black",
              "renewal": "gold"}
    if not events.empty:
        region_order = list(env_names) + ["GLOBAL"]
        for _, ev in events.iterrows():
            y = region_order.index(ev["region"])
            ax.scatter(ev["tick"], y, s=28,
                       color=colors.get(ev["type"], "gray"), alpha=0.8)
        ax.set_yticks(range(len(region_order)))
        ax.set_yticklabels(region_order, fontsize=8)
        handles = [plt.Line2D([0], [0], marker="o", ls="", color=c, label=t)
                   for t, c in colors.items()
                   if t in set(events["type"])]
        ax.legend(handles=handles, fontsize=7)
    ax.set_title("Emergent event timeline")
    ax.grid(alpha=0.3, axis="x")

    for ax_row in axes:
        for a in ax_row:
            a.set_xlabel("tick")

    fig.suptitle("DSA v7 — Emergent Covenant Engine", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    path = out_dir / "emergent_run.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def main():
    parser = argparse.ArgumentParser(description="DSA v7 Emergent Engine")
    parser.add_argument("--ticks", type=int, default=600)
    parser.add_argument("--agents", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default="output")
    parser.add_argument("--sensitivity", action="store_true",
                        help="run one-factor-at-a-time parameter sweeps")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = EmergentConfig(n_agents=args.agents, n_ticks=args.ticks,
                         seed=args.seed)

    if args.sensitivity:
        print("Running sensitivity analysis (this launches many runs)...")
        results = run_sensitivity(cfg)
        path = out_dir / "emergent_sensitivity.csv"
        results.to_csv(path, index=False)
        print(f"\nSaved: {path}")
        print(results.groupby(["parameter", "value"])
              [["final_entropy", "final_remnant", "n_crises", "n_revivals"]]
              .mean().round(3).to_string())
        return

    print(f"DSA v7 Emergent Engine: {cfg.n_agents} agents, "
          f"{cfg.n_ticks} ticks, seed={cfg.seed}\n")
    sim = EmergentSimulation(cfg)
    history = sim.run()
    events = sim.get_events_df()
    summary = sim.get_summary()

    print("\n=== Summary ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    if not events.empty:
        print("\n=== Emergent event timeline (first 30) ===")
        for _, ev in events.head(30).iterrows():
            print(f"  tick {ev['tick']:4d}  {ev['region']:<10} "
                  f"{ev['type']:<12} {ev['detail']}")
        if len(events) > 30:
            print(f"  ... and {len(events) - 30} more")

    history.to_csv(out_dir / "emergent_history.csv", index=False)
    if not events.empty:
        events.to_csv(out_dir / "emergent_events.csv", index=False)
    print(f"\nSaved history/events CSVs to {out_dir}/")

    if not args.no_plots:
        path = plot_run(history, events, sim.env.names, out_dir)
        print(f"Saved plot: {path}")


if __name__ == "__main__":
    main()
