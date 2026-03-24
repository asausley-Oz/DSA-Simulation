"""
Simulation Runner — Integrates all three frameworks

Connects the Environment (SCC), Distance (CDT), and Engagement (DSA) engines
with a Population of agents. Events emerge from dynamics, not scripts.

The simulation answers SCC's key question: What breaks the cycle?
"""

import numpy as np
import pandas as pd
from typing import List, Optional
from dataclasses import dataclass

from .environment import Environment
from .distance import DistanceEngine
from .engagement import EngagementEngine
from .agents import Population


@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""
    num_ticks: int = 500
    population_size: int = 100
    seed: Optional[int] = 42
    enable_atonement: bool = True        # allow atonement events to emerge
    enable_incarnation: bool = True      # allow incarnational cycle-breaking
    remnant_injection_tick: int = 100     # when God "calls out" a faithful people
    remnant_size: int = 8


class Simulation:
    """Main simulation orchestrator."""

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.seed = self.config.seed

        # Initialize engines
        self.environment = Environment(seed=self.seed)
        self.distance = DistanceEngine(seed=self.seed)
        self.engagement = EngagementEngine(seed=self.seed)
        self.population = Population(
            size=self.config.population_size, seed=self.seed)

        # History tracking
        self.history: List[dict] = []
        self.all_events: List[dict] = []
        self.tick = 0

    def run(self) -> pd.DataFrame:
        """Run the full simulation and return history as DataFrame."""
        for t in range(self.config.num_ticks):
            self.step()
        return self.get_history_df()

    def step(self) -> List[dict]:
        """Execute one simulation tick. Returns events from this tick."""
        self.tick += 1
        tick_events = []

        # === Generational Corruption Waves ===
        # SCC: cyclical patterns — each generation forgets and rebels
        # CDT: the judges cycle — faithfulness -> complacency -> rebellion -> crisis
        # === Generational Turnover ===
        # CDT: each generation must find faith anew — the judges cycle
        # New agents born with low faith replace dying ones
        if self.tick % 100 == 0 and self.tick > 0:
            cycle_num = self.tick // 100
            turnover_rate = 0.15 + 0.02 * min(cycle_num, 5)
            self._generational_turnover(turnover_rate)

        # === Remnant Injection ===
        # CDT: God calls out a people — this emerges at a configured point
        if self.tick == self.config.remnant_injection_tick:
            self.population.inject_faithful_remnant(self.config.remnant_size)
            tick_events.append({
                "tick": self.tick,
                "type": "calling",
                "description": "God calls out a faithful people from the nations",
                "parallel": "abram_pattern"
            })

        # === Get Current Aggregate Signals ===
        env_state = self.environment.get_state_snapshot()
        dist_state = self.distance.get_state_snapshot()
        eng_state = self.engagement.get_state_snapshot()

        # === Step Population ===
        pop_signals = self.population.step(
            env_corruption=env_state["corruption_level"],
            env_heavenly=env_state["heavenly_influence"],
            divine_engagement=eng_state["presence_level"],
            grace_space=eng_state["grace_space"],
            covenant_health=dist_state["covenant_health"],
        )

        # === Step Engagement (DSA) ===
        divine_engagement, eng_events = self.engagement.step(
            population_faithfulness=pop_signals["population_faithfulness"],
            remnant_fraction=pop_signals["remnant_fraction"],
            covenant_health=dist_state["covenant_health"],
            corruption_level=env_state["corruption_level"],
            spiritual_vitality=pop_signals["avg_spiritual_vitality"],
            cycle_count=env_state["cycle_count"],
        )
        tick_events.extend(eng_events)

        # === Step Distance (CDT) ===
        # Determine if atonement conditions have emerged
        atonement = False
        if self.config.enable_atonement:
            atonement = self._check_atonement_conditions(
                pop_signals, dist_state, eng_state)

        dist_events = self.distance.step(
            rebellion_input=pop_signals["population_rebellion"],
            faithfulness_input=pop_signals["population_faithfulness"],
            divine_initiative=divine_engagement,
            atonement_event=atonement,
        )
        tick_events.extend(dist_events)

        # === Step Environment (SCC) ===
        env_events = self.environment.step(
            population_faithfulness=pop_signals["population_faithfulness"],
            covenant_strength=self.distance.state.covenant_strength,
            divine_engagement=divine_engagement,
        )
        tick_events.extend(env_events)

        # === Record History ===
        snapshot = {
            "tick": self.tick,
            **{f"env_{k}": v for k, v in self.environment.get_state_snapshot().items()
               if k != "tick"},
            **{f"cdt_{k}": v for k, v in self.distance.get_state_snapshot().items()
               if k != "tick"},
            **{f"dsa_{k}": v for k, v in self.engagement.get_state_snapshot().items()
               if k != "tick"},
            **{f"pop_{k}": v for k, v in pop_signals.items()},
            "event_count": len(tick_events),
        }
        self.history.append(snapshot)
        self.all_events.extend(tick_events)

        return tick_events

    def _generational_turnover(self, strength: float):
        """Model generational change: old agents die, new ones born.

        CDT: the next generation doesn't inherit the faith of the previous one.
        They must discover it anew — and many don't.
        """
        rng = np.random.default_rng(self.tick)
        agents = self.population.agents
        alive = [a for a in agents if a.alive]
        if not alive:
            return

        # Remove a fraction of agents (death/aging)
        n_remove = max(1, int(len(alive) * strength * 0.3))
        # Preferentially remove oldest (first in list)
        for agent in alive[:n_remove]:
            agent.alive = False

        # Birth new agents — start with LOW faith (must discover it)
        from .agents import Agent, AgentTraits
        n_birth = n_remove
        for i in range(n_birth):
            new_id = len(agents) + i
            agent = Agent(new_id, rng)
            # New generation starts skeptical — CDT: each generation must find faith anew
            agent.state.faith = np.clip(rng.normal(0.15, 0.1), 0.02, 0.4)
            agent.state.rebellion = np.clip(rng.normal(0.4, 0.15), 0.1, 0.8)
            agent.state.delusion_level = np.clip(rng.normal(0.3, 0.1), 0.05, 0.6)
            agents.append(agent)

        self.population.size = len(agents)

    def _check_atonement_conditions(self, pop: dict, dist: dict, eng: dict) -> bool:
        """Atonement events emerge when conditions align — not scripted.

        Conditions: faithful remnant exists, covenant is active,
        divine engagement is high, and distance is significant.
        """
        return (pop["remnant_fraction"] > 0.1 and
                dist["covenant_health"] > 0.4 and
                eng["presence_level"] > 0.6 and
                dist["active_distance"] > 0.3 and
                dist["spiritual_vitality"] > 0.3)

    def get_history_df(self) -> pd.DataFrame:
        """Return simulation history as a pandas DataFrame."""
        return pd.DataFrame(self.history)

    def get_events_df(self) -> pd.DataFrame:
        """Return all events as a pandas DataFrame."""
        if not self.all_events:
            return pd.DataFrame()
        return pd.DataFrame(self.all_events)

    def get_summary(self) -> dict:
        """Return a summary of the simulation run."""
        events_df = self.get_events_df()
        event_counts = {}
        if not events_df.empty and "type" in events_df.columns:
            event_counts = events_df["type"].value_counts().to_dict()

        final_env = self.environment.get_state_snapshot()
        final_dist = self.distance.get_state_snapshot()
        final_eng = self.engagement.get_state_snapshot()

        return {
            "total_ticks": self.tick,
            "total_events": len(self.all_events),
            "event_types": event_counts,
            "cycles_completed": final_env["cycle_count"],
            "cycle_broken": final_env["cycle_broken"],
            "final_corruption": final_env["corruption_level"],
            "final_covenant_health": final_dist["covenant_health"],
            "final_divine_nearness": final_dist["divine_nearness"],
            "final_presence": final_eng["presence_level"],
            "final_remnant": final_dist["remnant_fraction"],
            "intimacy_milestones": final_dist["intimacy_milestones"],
            "scc_key_question": ("RESOLVED — cycle broken from within"
                                if final_env["cycle_broken"]
                                else "UNRESOLVED — cycles continue"),
        }
