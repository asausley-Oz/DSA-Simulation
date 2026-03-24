#!/usr/bin/env python3
"""
DSA Simulation Runner

Run the Divine Sovereign Agency simulation and generate output.

Usage:
    python run_simulation.py                    # default run
    python run_simulation.py --ticks 1000       # longer run
    python run_simulation.py --seed 123         # different seed
    python run_simulation.py --no-plots         # text output only
"""

import argparse
import sys
from pathlib import Path

from src.simulation import Simulation, SimulationConfig
from src.visualization import (
    plot_simulation, print_event_timeline, print_summary
)


def main():
    parser = argparse.ArgumentParser(description="DSA Simulation Runner")
    parser.add_argument("--ticks", type=int, default=500,
                        help="Number of simulation ticks (default: 500)")
    parser.add_argument("--population", type=int, default=100,
                        help="Population size (default: 100)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--no-plots", action="store_true",
                        help="Skip plot generation")
    parser.add_argument("--output-dir", type=str, default="output",
                        help="Output directory for plots (default: output)")
    parser.add_argument("--no-incarnation", action="store_true",
                        help="Disable incarnational cycle-breaking")
    parser.add_argument("--remnant-tick", type=int, default=100,
                        help="Tick at which remnant is called out (default: 100)")
    args = parser.parse_args()

    config = SimulationConfig(
        num_ticks=args.ticks,
        population_size=args.population,
        seed=args.seed,
        enable_incarnation=not args.no_incarnation,
        remnant_injection_tick=args.remnant_tick,
    )

    print(f"Running DSA Simulation: {config.num_ticks} ticks, "
          f"{config.population_size} agents, seed={config.seed}")
    print()

    sim = Simulation(config)
    history_df = sim.run()
    events_df = sim.get_events_df()
    summary = sim.get_summary()

    # Print results
    print_summary(summary)
    print_event_timeline(events_df)

    # Generate plots
    if not args.no_plots:
        print(f"\nGenerating plots to {args.output_dir}/...")
        saved = plot_simulation(history_df, events_df, args.output_dir)
        for path in saved:
            print(f"  Saved: {path}")

    # Save data
    csv_path = Path(args.output_dir) / "history.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    history_df.to_csv(csv_path, index=False)
    print(f"\n  History saved: {csv_path}")

    if not events_df.empty:
        events_path = Path(args.output_dir) / "events.csv"
        events_df.to_csv(events_path, index=False)
        print(f"  Events saved: {events_path}")


if __name__ == "__main__":
    main()
