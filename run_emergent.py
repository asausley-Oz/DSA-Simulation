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
from emergent.ensemble import (run_ensemble, run_grid, run_phase_lines,
                               summarize_ensemble)


def plot_run(history, events, env_names, out_dir: Path):
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))

    ax = axes[0, 0]
    ax.plot(history["tick"], history["distance"], lw=2, color="tab:red",
            label="distance (humanity's thread)")
    ax.plot(history["tick"], history["nearness"], lw=2, color="tab:blue",
            label="nearness (God's thread)")
    ax.plot(history["tick"], history["entropy"], lw=1, color="gray",
            ls="--", label="entropy (physical shadow)")
    ax.plot(history["tick"], history["rebellion"] * 0.12, lw=1,
            color="black", ls=":", label="ratchet floor (0.12 x rebellion)")
    for name in env_names:
        ax.plot(history["tick"], history[f"distance_{name}"],
                lw=0.5, alpha=0.4)
    ax.set_title("Covenant distance: the two threads")
    ax.legend(fontsize=7)
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
    ax.plot(history["tick"], history["skin"], label="skin (secular coat)",
            color="black", lw=1.5)
    ax.plot(history["tick"], history["flesh_exposed"], color="saddlebrown",
            lw=1.2, label="exposed flesh (old cosmos)")
    ax.plot(history["tick"], history["containment"], color="darkviolet",
            lw=1.5, label="containment (the trap)")
    ax.plot(history["tick"], history["unity"], label="unity")
    ax.plot(history["tick"], history["persecution"], label="persecution")
    ax.set_title("The apple: comfort, skin, exposed flesh")
    ax.legend(fontsize=7)
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
              "schism": "tab:orange", "hardening": "black",
              "scheme": "tab:purple", "incarnation": "deepskyblue",
              "deicide": "darkred", "atonement": "navy",
              "falling_away": "saddlebrown", "parousia": "cyan",
              "shaking": "magenta", "container": "darkviolet",
              "consummation": "dimgray", "fullness": "gold"}
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
    parser.add_argument("--ensemble", type=int, default=0, metavar="N",
                        help="run N seeds in parallel and map outcomes")
    parser.add_argument("--cartography", action="store_true",
                        help="map the eschatological parameter space: "
                             "grid + phase lines over theology-laden knobs")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = EmergentConfig(n_agents=args.agents, n_ticks=args.ticks,
                         seed=args.seed)

    if args.ensemble:
        print(f"Running {args.ensemble}-seed ensemble "
              f"({cfg.n_agents} agents x {cfg.n_ticks} ticks each)...")
        df = run_ensemble(cfg, n_seeds=args.ensemble)
        path = out_dir / "emergent_ensemble.csv"
        df.to_csv(path, index=False)
        print()
        print(summarize_ensemble(df))
        print(f"\nSaved: {path}")

        if not args.no_plots:
            fig, axes = plt.subplots(1, 3, figsize=(16, 5))
            colors = {"consummation": "tab:red", "fullness": "gold",
                      "contested": "tab:blue", "parousia": "cyan"}

            counts = df["outcome"].value_counts()
            axes[0].bar(counts.index, counts.values,
                        color=[colors.get(o, "gray") for o in counts.index])
            axes[0].set_title(f"Endings across {len(df)} histories")
            axes[0].set_ylabel("runs")

            for outcome, sub in df.groupby("outcome"):
                axes[1].scatter(sub["final_delusion"],
                                sub["final_remnant_share"] * 100,
                                color=colors.get(outcome, "gray"),
                                label=outcome, alpha=0.7)
            axes[1].set_xlabel("final delusion (blindness)")
            axes[1].set_ylabel("final remnant share (%)")
            axes[1].set_title("Blind worlds die, seeing worlds renew")
            axes[1].legend(fontsize=8)
            axes[1].grid(alpha=0.3)

            for outcome, sub in df.groupby("outcome"):
                axes[2].hist(sub["ticks_run"], bins=20, alpha=0.6,
                             color=colors.get(outcome, "gray"), label=outcome)
            axes[2].set_xlabel("ticks until ending")
            axes[2].set_title("When histories resolve")
            axes[2].legend(fontsize=8)
            axes[2].grid(alpha=0.3)

            fig.suptitle("DSA v7 — outcome landscape (identical rules, "
                         "different providence)", fontsize=13)
            fig.tight_layout(rect=[0, 0, 1, 0.94])
            ppath = out_dir / "emergent_ensemble.png"
            fig.savefig(ppath, dpi=130)
            plt.close(fig)
            print(f"Saved plot: {ppath}")
        return

    if args.cartography:
        print("Mapping the eschatological parameter space...\n")

        # --- 2-D grid: the race that defines the end -------------------
        # Does the witness outrun the Container?
        gx, gy = "container_growth", "witness_contact_rate"
        vx = [0.0, 0.004, 0.008, 0.012, 0.016]
        vy = [0.10, 0.19, 0.28, 0.37, 0.46]
        print(f"Grid: {gx} x {gy} ({len(vx)}x{len(vy)} cells x 8 seeds)")
        grid = run_grid(cfg, gx, vx, gy, vy, seeds_per_cell=8)
        grid.to_csv(out_dir / "eschatology_grid.csv", index=False)

        # --- phase lines over the finished cosmos's knobs --------------
        sweeps = {
            "toil": [0.0, 0.15, 0.25, 0.35, 0.50],
            "nearness_pull": [0.025, 0.035, 0.045, 0.055, 0.065],
            "container_growth": [0.0, 0.004, 0.008, 0.012, 0.016],
            "ratchet_rate": [0.10, 0.16, 0.22, 0.30, 0.40],
            "tribulation_apostasy": [0.0, 0.10, 0.20, 0.30, 0.40],
        }
        print("Phase lines: 5 parameters x 5 values x 10 seeds")
        lines = run_phase_lines(cfg, sweeps, seeds_per_value=10)
        lines.to_csv(out_dir / "eschatology_lines.csv", index=False)

        # --- render -----------------------------------------------------
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 5, height_ratios=[1.4, 1])

        ax = fig.add_subplot(gs[0, :2])
        pivot = (grid.assign(renew=(grid["outcome"] == "fullness"))
                 .groupby([gy, gx])["renew"].mean().unstack())
        im = ax.imshow(pivot.values * 100, origin="lower", cmap="RdYlGn",
                       vmin=0, vmax=100, aspect="auto")
        ax.set_xticks(range(len(vx)), [str(v) for v in vx])
        ax.set_yticks(range(len(vy)), [str(v) for v in vy])
        ax.set_xlabel("container_growth (the trap)")
        ax.set_ylabel("witness_contact_rate (the encounter)")
        ax.set_title("Fullness share (%): the witness vs the Container")
        for i in range(len(vy)):
            for j in range(len(vx)):
                ax.text(j, i, f"{pivot.values[i, j]*100:.0f}",
                        ha="center", va="center", fontsize=9)
        fig.colorbar(im, ax=ax, shrink=0.8)

        ax = fig.add_subplot(gs[0, 2:])
        med = grid.groupby([gx, gy]).agg(
            renew=("outcome", lambda s: (s == "fullness").mean()),
            revivals=("n_revivals", "mean")).reset_index()
        ax.scatter(med["revivals"], med["renew"] * 100, c=med[gy],
                   cmap="viridis", s=60)
        ax.set_xlabel("mean revivals per history (cell average)")
        ax.set_ylabel("fullness share (%)")
        ax.set_title("Revival frequency vs. final outcome "
                     "(color = witness_contact_rate)")
        ax.grid(alpha=0.3)

        for k, (param, values) in enumerate(sweeps.items()):
            ax = fig.add_subplot(gs[1, k])
            sub = lines[lines["parameter"] == param]
            stats = sub.groupby("value")["outcome"].value_counts(
                normalize=True).unstack(fill_value=0)
            for outcome, color in [("fullness", "gold"),
                                   ("consummation", "tab:red"),
                                   ("parousia", "cyan"),
                                   ("contested", "tab:blue")]:
                if outcome in stats:
                    ax.plot(stats.index, stats[outcome] * 100, "o-",
                            color=color, label=outcome)
            ax.axvline(getattr(cfg, param), color="gray", ls=":", lw=1)
            ax.set_title(param, fontsize=9)
            ax.set_ylim(-5, 105)
            ax.grid(alpha=0.3)
            if k == 0:
                ax.set_ylabel("share of histories (%)")
                ax.legend(fontsize=7)

        fig.suptitle("DSA v7 — eschatological cartography "
                     "(dotted line = current default)", fontsize=14)
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        ppath = out_dir / "eschatology_map.png"
        fig.savefig(ppath, dpi=130)
        plt.close(fig)

        print(f"\nSaved: {out_dir/'eschatology_grid.csv'}, "
              f"{out_dir/'eschatology_lines.csv'}, {ppath}")
        return

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
