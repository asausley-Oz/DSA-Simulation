"""
Validation Suite — Does the Metaphysics Hold?

Two questions:
1. POSITIVE CASE: Does the biblical arc emerge robustly across many seeds?
   (Not just seed 42 — if the metaphysics are right, they should be general.)

2. NEGATIVE CASE: Does removing the incarnation mechanic cause the system
   to fail? CDT claims the cycle cannot be broken from within. If the
   simulation reaches consummation without incarnation, CDT is wrong.

This script runs both cases and reports the evidence.
"""

import sys
import time
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Dict

sys.path.insert(0, ".")
from src.simulation import Simulation, SimulationConfig


@dataclass
class RunResult:
    """Summary of a single simulation run."""
    seed: int
    incarnation_enabled: bool
    consummated: bool
    flood_tick: Optional[int] = None
    calling_tick: Optional[int] = None
    first_temple_tick: Optional[int] = None
    incarnation_tick: Optional[int] = None
    schism_tick: Optional[int] = None
    parousia_tick: Optional[int] = None
    total_cycles: int = 0
    final_corruption: float = 0.0
    final_ticks: int = 0
    # Negative case tracking
    max_cycles_reached: int = 0
    stuck_in_entropy: bool = False


def run_single(seed: int, num_ticks: int, population_size: int,
               enable_incarnation: bool = True) -> RunResult:
    """Run one simulation and extract key events."""
    config = SimulationConfig(
        num_ticks=num_ticks,
        population_size=population_size,
        seed=seed,
        enable_incarnation=enable_incarnation,
    )
    sim = Simulation(config)
    sim.run()

    events = sim.get_events_df()
    result = RunResult(
        seed=seed,
        incarnation_enabled=enable_incarnation,
        consummated=sim._consummated,
        total_cycles=sim.environment.cycle_tracker.cycle_count,
        final_corruption=float(sim.environment.realm.corruption_level),
        final_ticks=num_ticks,
    )

    # Extract key event ticks
    event_map = {
        "cataclysmic_reset": "flood_tick",
        "calling": "calling_tick",
        "cycle_breaking": "incarnation_tick",
        "great_schism": "schism_tick",
        "parousia": "parousia_tick",
    }
    for event_type, attr in event_map.items():
        matches = events[events["type"] == event_type]
        if not matches.empty:
            setattr(result, attr, int(matches.iloc[0]["tick"]))

    # First temple
    temples = events[events["type"] == "temple_built"]
    if not temples.empty:
        result.first_temple_tick = int(temples.iloc[0]["tick"])

    result.max_cycles_reached = result.total_cycles

    return result


def print_header(title: str):
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def print_statistics(label: str, values: List[float]):
    """Print summary statistics for a list of values."""
    if not values:
        print(f"  {label}: no data")
        return
    arr = np.array(values)
    print(f"  {label}:")
    print(f"    mean={arr.mean():.0f}  median={np.median(arr):.0f}  "
          f"std={arr.std():.0f}  min={arr.min():.0f}  max={arr.max():.0f}")


def run_positive_case(seeds: range, num_ticks: int, pop_size: int) -> List[RunResult]:
    """POSITIVE CASE: Does the biblical arc emerge across seeds?"""
    print_header("POSITIVE CASE: Biblical Arc Robustness")
    print(f"  Running {len(seeds)} seeds with incarnation enabled...")
    print(f"  Ticks: {num_ticks}  Population: {pop_size}")
    print()

    results = []
    for i, seed in enumerate(seeds):
        r = run_single(seed, num_ticks, pop_size, enable_incarnation=True)
        results.append(r)
        # Progress
        if (i + 1) % 10 == 0:
            consummated = sum(1 for x in results if x.consummated)
            print(f"  ... {i+1}/{len(seeds)} complete ({consummated} consummated)")

    # === Analysis ===
    total = len(results)
    consummated = [r for r in results if r.consummated]
    floods = [r.flood_tick for r in results if r.flood_tick is not None]
    callings = [r.calling_tick for r in results if r.calling_tick is not None]
    temples = [r.first_temple_tick for r in results if r.first_temple_tick is not None]
    incarnations = [r.incarnation_tick for r in results if r.incarnation_tick is not None]
    schisms = [r.schism_tick for r in results if r.schism_tick is not None]
    parousias = [r.parousia_tick for r in results if r.parousia_tick is not None]

    print()
    print(f"  CONSUMMATION RATE: {len(consummated)}/{total} "
          f"({100*len(consummated)/total:.0f}%)")
    print()

    print_statistics("Flood tick", floods)
    print_statistics("Calling tick", callings)
    print_statistics("First Temple tick", temples)
    print_statistics("Incarnation tick", incarnations)
    print_statistics("Great Schism tick", schisms)
    print_statistics("Parousia tick", parousias)

    # Pre-flood period analysis
    if floods:
        print()
        print(f"  PRE-FLOOD PERIOD (Firmament Effect):")
        arr = np.array(floods)
        in_range = sum(1 for f in floods if 800 <= f <= 2000)
        print(f"    In target range (800-2000): {in_range}/{len(floods)} "
              f"({100*in_range/len(floods):.0f}%)")

    # Event ordering check
    if results:
        ordering_violations = 0
        for r in results:
            if r.flood_tick and r.calling_tick and r.calling_tick < r.flood_tick:
                ordering_violations += 1
            if r.calling_tick and r.incarnation_tick and r.incarnation_tick < r.calling_tick:
                ordering_violations += 1
            if r.incarnation_tick and r.parousia_tick and r.parousia_tick < r.incarnation_tick:
                ordering_violations += 1
        print()
        print(f"  THEOLOGICAL ORDERING VIOLATIONS: {ordering_violations}")
        print(f"    (flood < calling < incarnation < parousia)")

    # Failed runs
    failed = [r for r in results if not r.consummated]
    if failed:
        print()
        print(f"  FAILED RUNS ({len(failed)}):")
        for r in failed:
            print(f"    seed={r.seed}: cycles={r.total_cycles} "
                  f"corruption={r.final_corruption:.3f} "
                  f"flood={'Y' if r.flood_tick else 'N'} "
                  f"incarnation={'Y' if r.incarnation_tick else 'N'}")

    return results


def run_negative_case(seeds: range, num_ticks: int, pop_size: int) -> List[RunResult]:
    """NEGATIVE CASE: Does removing incarnation prevent consummation?

    CDT's core claim: the cycle cannot be broken from within.
    Without incarnation, the system should spiral through cycles
    indefinitely, each one worse than the last.
    """
    print_header("NEGATIVE CASE: Can the Cycle Be Broken From Within?")
    print(f"  Running {len(seeds)} seeds WITHOUT incarnation...")
    print(f"  CDT claim: consummation should be IMPOSSIBLE.")
    print(f"  Ticks: {num_ticks}  Population: {pop_size}")
    print()

    results = []
    for i, seed in enumerate(seeds):
        r = run_single(seed, num_ticks, pop_size, enable_incarnation=False)
        results.append(r)
        if (i + 1) % 10 == 0:
            consummated = sum(1 for x in results if x.consummated)
            cycles = [x.total_cycles for x in results]
            print(f"  ... {i+1}/{len(seeds)} complete "
                  f"({consummated} consummated, "
                  f"avg cycles={np.mean(cycles):.1f})")

    # === Analysis ===
    total = len(results)
    consummated = [r for r in results if r.consummated]
    cycles = [r.total_cycles for r in results]
    corruptions = [r.final_corruption for r in results]

    print()
    if not consummated:
        print(f"  CDT VALIDATED: 0/{total} runs reached consummation")
        print(f"  The cycle CANNOT be broken from within.")
    else:
        print(f"  CDT FALSIFIED: {len(consummated)}/{total} runs "
              f"reached consummation WITHOUT incarnation!")
        for r in consummated:
            print(f"    seed={r.seed}: consummated at tick {r.parousia_tick}")

    print()
    print_statistics("Cycles completed", [float(c) for c in cycles])
    print_statistics("Final corruption", corruptions)

    # Show the spiral — are later cycles harder?
    print()
    print(f"  ENTROPY SPIRAL:")
    print(f"    All runs stuck in cycles: "
          f"{sum(1 for r in results if r.total_cycles >= 3)}/{total} "
          f"reached 3+ cycles")
    print(f"    Max cycles in any run: {max(cycles)}")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Validate DSA Simulation metaphysics across seeds")
    parser.add_argument("--seeds", type=int, default=50,
                        help="Number of seeds to test (default: 50)")
    parser.add_argument("--ticks", type=int, default=10000,
                        help="Ticks per run (default: 10000)")
    parser.add_argument("--population", type=int, default=500,
                        help="Population size (default: 500)")
    parser.add_argument("--positive-only", action="store_true",
                        help="Only run positive case")
    parser.add_argument("--negative-only", action="store_true",
                        help="Only run negative case")
    args = parser.parse_args()

    seed_range = range(args.seeds)
    start = time.time()

    if not args.negative_only:
        pos_results = run_positive_case(seed_range, args.ticks, args.population)

    if not args.positive_only:
        neg_results = run_negative_case(seed_range, args.ticks, args.population)

    elapsed = time.time() - start

    print_header("SUMMARY")
    if not args.negative_only:
        consummated = sum(1 for r in pos_results if r.consummated)
        print(f"  Positive case: {consummated}/{len(pos_results)} consummated "
              f"({100*consummated/len(pos_results):.0f}%)")
    if not args.positive_only:
        consummated = sum(1 for r in neg_results if r.consummated)
        print(f"  Negative case: {consummated}/{len(neg_results)} consummated "
              f"({100*consummated/len(neg_results):.0f}%)")
    print(f"  Total time: {elapsed:.1f}s")
    print()


if __name__ == "__main__":
    main()
