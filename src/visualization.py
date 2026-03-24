"""
Visualization — Simulation output and plotting

Generates plots showing the interplay of SCC, CDT, and DSA dynamics
over the course of a simulation run.
"""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List


def plot_simulation(history_df: pd.DataFrame, events_df: pd.DataFrame,
                    output_dir: str = "output", title_prefix: str = "") -> List[str]:
    """Generate all simulation plots and save to output directory.

    Returns list of saved file paths.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved = []

    saved.append(_plot_three_realms(history_df, events_df, out, title_prefix))
    saved.append(_plot_covenant_distance(history_df, events_df, out, title_prefix))
    saved.append(_plot_divine_engagement(history_df, events_df, out, title_prefix))
    saved.append(_plot_population(history_df, events_df, out, title_prefix))
    saved.append(_plot_dashboard(history_df, events_df, out, title_prefix))

    return saved


def _plot_three_realms(df: pd.DataFrame, events: pd.DataFrame,
                       out: Path, prefix: str) -> str:
    """SCC three-realm dynamics over time."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle(f"{prefix}SCC: Three-Realm Cosmological Dynamics", fontsize=14, fontweight="bold")

    ax1 = axes[0]
    ax1.fill_between(df["tick"], df["env_heavenly_influence"], alpha=0.3, color="gold", label="Heavenly Influence")
    ax1.fill_between(df["tick"], df["env_underworld_pressure"], alpha=0.3, color="darkred", label="Underworld Pressure")
    ax1.plot(df["tick"], df["env_natural_vitality"], color="green", linewidth=1.5, label="Natural Vitality")
    ax1.plot(df["tick"], df["env_corruption_level"], color="purple", linewidth=1.5, linestyle="--", label="Corruption")
    ax1.set_ylabel("Level")
    ax1.set_ylim(0, 1.05)
    ax1.legend(loc="upper right", fontsize=8)
    ax1.set_title("Realm Forces")

    # Mark major events
    _mark_events(ax1, events, ["cataclysmic_reset", "scattering", "cycle_breaking"])

    ax2 = axes[1]
    ax2.plot(df["tick"], df["env_life_force_flow"], color="gold", linewidth=1.5, label="Life Force Flow")
    ax2.plot(df["tick"], df["env_chaos_seepage"], color="darkred", linewidth=1.5, label="Chaos Seepage")
    ax2.plot(df["tick"], df["env_beauty_darkness_ratio"], color="blue", linewidth=1, linestyle=":", label="Beauty/Darkness Ratio")
    ax2.set_ylabel("Level")
    ax2.set_xlabel("Tick")
    ax2.set_ylim(0, 1.05)
    ax2.legend(loc="upper right", fontsize=8)
    ax2.set_title("Life Force vs Chaos")

    plt.tight_layout()
    path = str(out / "scc_three_realms.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def _plot_covenant_distance(df: pd.DataFrame, events: pd.DataFrame,
                            out: Path, prefix: str) -> str:
    """CDT covenant distance dynamics over time."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle(f"{prefix}CDT: Covenant Distance Dynamics", fontsize=14, fontweight="bold")

    ax1 = axes[0]
    ax1.plot(df["tick"], df["cdt_active_distance"], color="red", linewidth=1.5, label="Active Distance")
    ax1.plot(df["tick"], df["cdt_divine_nearness"], color="gold", linewidth=1.5, label="Divine Nearness")
    ax1.plot(df["tick"], df["cdt_covenant_strength"], color="blue", linewidth=1.5, label="Covenant Strength")
    ax1.fill_between(df["tick"], df["cdt_curse_weight"], alpha=0.2, color="darkred", label="Curse Weight")
    ax1.set_ylabel("Level")
    ax1.set_ylim(0, 1.05)
    ax1.legend(loc="upper right", fontsize=8)
    ax1.set_title("Distance vs Counter-Movement")

    _mark_events(ax1, events, ["covenant_formation", "covenant_fracture", "exile", "atonement"])

    ax2 = axes[1]
    ax2.plot(df["tick"], df["cdt_spiritual_vitality"], color="green", linewidth=1.5, label="Spiritual Vitality")
    ax2.plot(df["tick"], df["cdt_delusion_level"], color="purple", linewidth=1.5, linestyle="--", label="Delusion")
    ax2.plot(df["tick"], df["cdt_blessing_flow"], color="gold", linewidth=1, label="Blessing Flow")
    ax2.plot(df["tick"], df["cdt_awareness_of_condition"], color="cyan", linewidth=1, linestyle=":", label="Awareness")
    ax2.set_ylabel("Level")
    ax2.set_xlabel("Tick")
    ax2.set_ylim(0, 1.05)
    ax2.legend(loc="upper right", fontsize=8)
    ax2.set_title("Spiritual State")

    plt.tight_layout()
    path = str(out / "cdt_covenant_distance.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def _plot_divine_engagement(df: pd.DataFrame, events: pd.DataFrame,
                            out: Path, prefix: str) -> str:
    """DSA divine engagement dynamics over time."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle(f"{prefix}DSA: Divine Sovereign Engagement", fontsize=14, fontweight="bold")

    ax1 = axes[0]
    ax1.plot(df["tick"], df["dsa_presence_level"], color="gold", linewidth=2, label="Presence Level")
    ax1.plot(df["tick"], df["dsa_experiential_engagement"], color="orange", linewidth=1.5, label="Experiential Engagement")
    ax1.plot(df["tick"], df["dsa_cultivation_intensity"], color="green", linewidth=1, label="Cultivation Intensity")
    ax1.fill_between(df["tick"], df["dsa_grace_space"], alpha=0.15, color="blue", label="Grace Space")
    ax1.set_ylabel("Level")
    ax1.set_ylim(0, 1.05)
    ax1.legend(loc="upper right", fontsize=8)
    ax1.set_title("Sovereign Presence & Space")

    _mark_events(ax1, events, ["divine_drawing_near", "incarnational_entry", "sovereign_intervention"])

    ax2 = axes[1]
    ax2.plot(df["tick"], df["dsa_delight"], color="gold", linewidth=1.5, label="Delight")
    ax2.plot(df["tick"], df["dsa_grief"], color="blue", linewidth=1.5, label="Grief")
    ax2.plot(df["tick"], df["dsa_patience"], color="green", linewidth=1.5, label="Patience")
    ax2.plot(df["tick"], df["dsa_compassion"], color="red", linewidth=1, linestyle=":", label="Compassion")
    ax2.set_ylabel("Level")
    ax2.set_xlabel("Tick")
    ax2.set_ylim(0, 1.05)
    ax2.legend(loc="upper right", fontsize=8)
    ax2.set_title("Divine Response")

    plt.tight_layout()
    path = str(out / "dsa_engagement.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def _plot_population(df: pd.DataFrame, events: pd.DataFrame,
                     out: Path, prefix: str) -> str:
    """Population dynamics over time."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 5))
    fig.suptitle(f"{prefix}Population Dynamics", fontsize=14, fontweight="bold")

    ax.plot(df["tick"], df["pop_population_faithfulness"], color="blue", linewidth=1.5, label="Faithfulness")
    ax.plot(df["tick"], df["pop_population_rebellion"], color="red", linewidth=1.5, label="Rebellion")
    ax.plot(df["tick"], df["pop_remnant_fraction"], color="gold", linewidth=1.5, label="Remnant Fraction")
    ax.plot(df["tick"], df["pop_avg_delusion"], color="purple", linewidth=1, linestyle="--", label="Avg Delusion")
    ax.plot(df["tick"], df["pop_avg_imaging"], color="green", linewidth=1, linestyle=":", label="Avg Imaging Quality")
    ax.set_ylabel("Level")
    ax.set_xlabel("Tick")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper right", fontsize=8)

    _mark_events(ax, events, ["calling", "remnant_emergence"])

    plt.tight_layout()
    path = str(out / "population_dynamics.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def _plot_dashboard(df: pd.DataFrame, events: pd.DataFrame,
                    out: Path, prefix: str) -> str:
    """Combined dashboard with all key metrics."""
    fig, axes = plt.subplots(4, 1, figsize=(16, 14), sharex=True)
    fig.suptitle(f"{prefix}DSA Simulation — CDT Biblical Arc", fontsize=16, fontweight="bold")

    # Mark era boundaries on all axes
    _mark_era_boundaries(axes, events)

    # Row 1: SCC Environment
    ax = axes[0]
    ax.fill_between(df["tick"], df["env_heavenly_influence"], alpha=0.3, color="gold")
    ax.fill_between(df["tick"], df["env_underworld_pressure"], alpha=0.3, color="darkred")
    ax.plot(df["tick"], df["env_natural_vitality"], color="green", linewidth=1.5)
    ax.plot(df["tick"], df["env_corruption_level"], color="purple", linewidth=1.5, linestyle="--")
    ax.set_ylabel("SCC")
    ax.set_ylim(0, 1.05)
    _mark_events(ax, events, ["cataclysmic_reset", "cycle_breaking", "phase_transition"])

    # Row 2: CDT Distance
    ax = axes[1]
    ax.plot(df["tick"], df["cdt_active_distance"], color="red", linewidth=1.5)
    ax.plot(df["tick"], df["cdt_divine_nearness"], color="gold", linewidth=1.5)
    ax.plot(df["tick"], df["cdt_covenant_health"], color="blue", linewidth=1.5)
    ax.set_ylabel("CDT")
    ax.set_ylim(0, 1.05)
    _mark_events(ax, events, ["covenant_formation", "covenant_fracture", "atonement"])

    # Row 3: DSA Engagement
    ax = axes[2]
    ax.plot(df["tick"], df["dsa_presence_level"], color="gold", linewidth=2)
    ax.plot(df["tick"], df["dsa_delight"], color="green", linewidth=1)
    ax.plot(df["tick"], df["dsa_grief"], color="blue", linewidth=1)
    ax.plot(df["tick"], df["dsa_patience"], color="orange", linewidth=1)
    ax.set_ylabel("DSA")
    ax.set_ylim(0, 1.05)
    _mark_events(ax, events, ["divine_drawing_near", "incarnational_entry"])

    # Row 4: Population
    ax = axes[3]
    ax.plot(df["tick"], df["pop_population_faithfulness"], color="blue", linewidth=1.5)
    ax.plot(df["tick"], df["pop_population_rebellion"], color="red", linewidth=1.5)
    ax.plot(df["tick"], df["pop_remnant_fraction"], color="gold", linewidth=1.5)
    ax.set_ylabel("Pop")
    ax.set_xlabel("Tick")
    ax.set_ylim(0, 1.05)
    _mark_events(ax, events, ["calling", "remnant_emergence"])

    plt.tight_layout()
    path = str(out / "dashboard.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def _mark_era_boundaries(axes, events_df: pd.DataFrame):
    """Mark era transitions on all axes with labeled vertical lines."""
    if events_df.empty or "type" not in events_df.columns:
        return
    era_events = events_df[events_df["type"] == "era_transition"]
    for _, row in era_events.iterrows():
        era_name = row.get("era", "")
        for ax in axes:
            ax.axvline(x=row["tick"], color="black", alpha=0.25, linewidth=0.6, linestyle="-")
        # Label on top axis only
        if len(axes) > 0 and era_name:
            short = era_name[:12]
            axes[0].text(row["tick"] + 2, 1.0, short, fontsize=5,
                        rotation=45, va="top", alpha=0.6)


def _mark_events(ax, events_df: pd.DataFrame, event_types: List[str]):
    """Mark specific event types on an axis with vertical lines."""
    if events_df.empty or "type" not in events_df.columns:
        return

    colors = {
        "cataclysmic_reset": "darkred",
        "scattering": "orange",
        "cycle_breaking": "gold",
        "phase_transition": "gray",
        "covenant_formation": "blue",
        "covenant_fracture": "red",
        "exile": "brown",
        "atonement": "purple",
        "divine_drawing_near": "gold",
        "incarnational_entry": "gold",
        "sovereign_intervention": "red",
        "calling": "green",
        "remnant_emergence": "teal",
    }

    for etype in event_types:
        subset = events_df[events_df["type"] == etype]
        for _, row in subset.iterrows():
            color = colors.get(etype, "gray")
            ax.axvline(x=row["tick"], color=color, alpha=0.4, linewidth=0.8, linestyle="--")


def print_event_timeline(events_df: pd.DataFrame):
    """Print a readable timeline of simulation events."""
    if events_df.empty:
        print("No events occurred.")
        return

    print("\n" + "=" * 70)
    print("SIMULATION EVENT TIMELINE")
    print("=" * 70)

    for _, event in events_df.iterrows():
        tick = event.get("tick", "?")
        etype = event.get("type", "unknown")
        desc = event.get("description", "")
        parallel = event.get("parallel", "")

        marker = _event_marker(etype)
        print(f"  [{tick:>4}] {marker} {desc}")
        if parallel:
            print(f"         -> Biblical parallel: {parallel}")

    print("=" * 70)


def _event_marker(etype: str) -> str:
    """Return a text marker for event types."""
    markers = {
        "cataclysmic_reset": "[RESET]",
        "scattering": "[SCATTER]",
        "cycle_breaking": "[BREAK]",
        "phase_transition": "[PHASE]",
        "covenant_formation": "[COVENANT]",
        "covenant_fracture": "[FRACTURE]",
        "exile": "[EXILE]",
        "atonement": "[ATONE]",
        "divine_drawing_near": "[NEAR]",
        "incarnational_entry": "[INCARNATION]",
        "sovereign_intervention": "[JUDGMENT]",
        "calling": "[CALL]",
        "remnant_emergence": "[REMNANT]",
        "spiritual_death": "[DEATH]",
        "delusion_dominance": "[VAMPHORIC]",
        "curse_paradox": "[PARADOX]",
        "tabernacle_moment": "[TABERNACLE]",
        "divine_incursion": "[THEOPHANY]",
        "divine_delight": "[DELIGHT]",
        "divine_grief": "[GRIEF]",
        "intimacy_advance": "[INTIMACY]",
        "harvest_ready": "[HARVEST]",
        "era_transition": "[ERA]",
        "judges_phase": "[JUDGES]",
        "spirit_indwelling": "[SPIRIT]",
    }
    return markers.get(etype, f"[{etype.upper()}]")


def print_summary(summary: dict):
    """Print a formatted simulation summary."""
    print("\n" + "=" * 70)
    print("SIMULATION SUMMARY")
    print("=" * 70)
    print(f"  Total ticks:          {summary['total_ticks']}")
    print(f"  Total events:         {summary['total_events']}")
    print(f"  Final era:            {summary.get('final_era', 'N/A')}")
    print(f"  Judges cycles:        {summary.get('judges_cycles', 0)}")
    print(f"  SCC cycles completed: {summary['cycles_completed']}")
    print(f"  Intimacy milestones:  {summary['intimacy_milestones']}")
    print()
    print(f"  Final corruption:     {summary['final_corruption']:.4f}")
    print(f"  Final covenant health:{summary['final_covenant_health']:.4f}")
    print(f"  Final divine nearness:{summary['final_divine_nearness']:.4f}")
    print(f"  Final presence:       {summary['final_presence']:.4f}")
    print(f"  Final remnant:        {summary['final_remnant']:.4f}")
    print()
    print(f"  SCC Key Question:     {summary['scc_key_question']}")
    print()

    if summary["event_types"]:
        print("  Event breakdown:")
        for etype, count in sorted(summary["event_types"].items()):
            print(f"    {etype:30s} {count:>4}")
    print("=" * 70)
