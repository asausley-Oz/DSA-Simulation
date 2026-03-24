"""
Simulation Runner — Pure Entropy-Driven Dynamics

No timelines. No scripted eras. Events emerge from entropy thresholds.

The environment accumulates entropy (corruption) relentlessly.
The only forces that resist it are covenant + divine engagement.
Faithfulness alone slows but cannot stop it.

One cycle tuned correctly becomes the engine for everything:
  pristine -> entropy accumulates -> threshold crossed -> reset ->
  residual curse -> new cycle begins slightly worse

The CDT biblical arc should EMERGE from these dynamics, not be imposed.
"""

import numpy as np
import pandas as pd
from typing import List, Optional
from dataclasses import dataclass

from .environment import Environment, RealmState
from .distance import DistanceEngine
from .engagement import EngagementEngine
from .agents import Population, Agent


@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""
    num_ticks: int = 1000
    population_size: int = 100
    seed: Optional[int] = 42
    enable_atonement: bool = True
    enable_incarnation: bool = True


class Simulation:
    """Main simulation orchestrator — pure entropy-driven."""

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.seed = self.config.seed
        self.rng = np.random.default_rng(self.seed)

        # Initialize engines
        self.environment = Environment(seed=self.seed)
        self.distance = DistanceEngine(seed=self.seed)
        self.engagement = EngagementEngine(seed=self.seed)
        self.population = Population(
            size=self.config.population_size, seed=self.seed)

        # Start pristine — Eden
        self._init_pristine()

        # History tracking
        self.history: List[dict] = []
        self.all_events: List[dict] = []
        self.tick = 0

        # Tracking for emergent conditions
        self._calling_fired = False
        self._flood_count = 0

        # === Schism Mechanics ===
        # Cities amplify everything. Post-resurrection, the gospel spreads
        # fast in cities — but the accumulated fragmentation curse means
        # the multiplied faithful eventually split. Schism pressure builds
        # slowly and only fires when it crosses a HIGH threshold.
        # Not every gathering becomes a schism.
        self._schism_pressure = 0.0
        self._schism_count = 0
        self._last_schism_tick = -200

    def _init_pristine(self):
        """Set pristine Eden conditions. Everything starts perfect."""
        # Environment: pristine
        self.environment.realm = RealmState(
            heavenly_influence=1.0, underworld_pressure=0.0,
            natural_vitality=1.0, corruption_level=0.0,
            life_force_flow=1.0, chaos_seepage=0.0)

        # Distance: no distance, full nearness
        self.distance.state.cumulative_rebellion = 0.0
        self.distance.state.active_distance = 0.0
        self.distance.state.curse_weight = 0.0
        self.distance.state.blessing_flow = 1.0
        self.distance.state.spiritual_vitality = 1.0
        self.distance.state.delusion_level = 0.0
        self.distance.state.awareness_of_condition = 1.0
        self.distance.state.divine_nearness = 1.0
        self.distance.state.covenant_strength = 0.0  # no covenant yet — just presence
        self.distance.state.remnant_fraction = 1.0
        self.distance.state.population_faithfulness = 1.0

        # Engagement: present but self-limiting — DSA: space as grace
        # God is near but not controlling — genuine agency requires room
        self.engagement.state.presence_level = 0.6
        self.engagement.state.experiential_engagement = 0.5
        self.engagement.state.self_limitation_degree = 0.6  # high self-limitation
        self.engagement.state.patience = 1.0
        self.engagement.state.delight = 0.5
        self.engagement.state.grief = 0.0
        self.engagement.state.compassion = 0.5

        # Agents: high faith, low rebellion
        for agent in self.population.agents:
            agent.state.faith = np.clip(self.rng.normal(0.75, 0.1), 0.5, 1.0)
            agent.state.faithfulness = np.clip(self.rng.normal(0.65, 0.1), 0.4, 1.0)
            agent.state.rebellion = np.clip(self.rng.normal(0.05, 0.03), 0.01, 0.15)
            agent.state.spiritual_vitality = np.clip(self.rng.normal(0.95, 0.03), 0.85, 1.0)
            agent.state.delusion_level = 0.0
            agent.state.awareness = agent.traits.awareness_sensitivity * 0.9
            agent.is_remnant = True

    def run(self) -> pd.DataFrame:
        """Run the full simulation and return history as DataFrame."""
        for t in range(self.config.num_ticks):
            self.step()
        return self.get_history_df()

    def step(self) -> List[dict]:
        """Execute one simulation tick. Returns events from this tick."""
        self.tick += 1
        tick_events = []

        # === Generational Turnover ===
        # Every generation, some agents die and new ones are born.
        # CDT: the next generation must find faith anew.
        if self.tick % 80 == 0 and self.tick > 0:
            self._generational_turnover()

        # === Get Current State ===
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

        # === Emergent Calling ===
        # CDT: God calls out a people — emerges when conditions are right
        # After at least one reset, when divine engagement rises and
        # a remnant persists, God initiates covenant
        tick_events.extend(self._check_calling(pop_signals, env_state, eng_state))

        # === Sync Accumulated Curse Penalties to Distance Engine ===
        # The curse registry lives in the environment (SCC), but its structural
        # penalties affect covenant mechanics (CDT). Each tick we propagate them.
        curses = self.environment.cycle_tracker.curse_registry
        self.distance.covenant_penalty = curses.total_covenant_penalty
        self.distance.fragmentation = curses.total_fragmentation
        self.distance.foreign_pressure = curses.total_foreign_pressure

        # === Step Distance (CDT) ===
        atonement = False
        if self.config.enable_atonement:
            atonement = self._check_atonement_conditions(pop_signals, dist_state, eng_state)

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
            city_density=pop_signals["city_density"],
        )
        tick_events.extend(env_events)

        # Track flood count and cycle-breaking (incarnation)
        for e in env_events:
            if e.get("type") == "cataclysmic_reset":
                self._flood_count += 1
                # After reset, kill most agents, keep faithful remnant
                self._post_reset_population()
            elif e.get("type") == "cycle_breaking":
                # Incarnation/Resurrection: mark existing remnant as Spirit-indwelt
                # This is the hinge — the multiplication starts here
                self._activate_indwelling()
                tick_events.append({
                    "tick": self.tick,
                    "type": "spirit_indwelling",
                    "description": ("The Spirit falls — remnant agents become indwelt. "
                                    "Enhanced entropy resistance and missionary "
                                    "reproduction activated."),
                    "parallel": "pentecost_pattern"
                })

        # === Post-Incarnation: Missionary Reproduction ===
        if self.environment.cycle_tracker.cycle_broken:
            tick_events.extend(self._step_missionary_reproduction(pop_signals))

        # === City Density Effects & Schism Detection ===
        tick_events.extend(self._step_city_schism(pop_signals, env_state))

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
            "schism_pressure": round(self._schism_pressure, 4),
            "schism_count": self._schism_count,
            "event_count": len(tick_events),
        }
        self.history.append(snapshot)
        self.all_events.extend(tick_events)

        return tick_events

    def _generational_turnover(self):
        """Replace a fraction of agents with new ones.
        CDT: each generation must discover faith anew."""
        agents = self.population.agents
        alive = [a for a in agents if a.alive]
        if not alive:
            return

        n_remove = max(1, int(len(alive) * 0.15))
        for agent in alive[:n_remove]:
            agent.alive = False

        for i in range(n_remove):
            new_id = len(agents) + i
            agent = Agent(new_id, self.rng)
            # New generation starts with low faith — must discover it
            agent.state.faith = np.clip(self.rng.normal(0.15, 0.1), 0.02, 0.4)
            agent.state.rebellion = np.clip(self.rng.normal(0.35, 0.15), 0.1, 0.7)
            agent.state.delusion_level = np.clip(self.rng.normal(0.25, 0.1), 0.05, 0.5)
            agents.append(agent)

        self.population.size = len(agents)

    def _post_reset_population(self):
        """After a cataclysmic reset, most die. A remnant survives."""
        alive = [a for a in self.population.agents if a.alive]
        if not alive:
            return
        n_survive = max(8, int(len(alive) * 0.08))
        # Most faithful survive
        alive.sort(key=lambda a: a.state.faithfulness, reverse=True)
        for agent in alive[n_survive:]:
            agent.alive = False

    def _check_calling(self, pop: dict, env: dict, eng: dict) -> List[dict]:
        """Emergent calling — God calls out a people when conditions align.

        Conditions: at least one reset has occurred, a remnant persists,
        divine engagement is rising, and there's enough stability to
        build a covenant people.
        """
        if self._calling_fired:
            return []

        if (self._flood_count >= 1 and
                pop["remnant_fraction"] > 0.05 and
                eng["presence_level"] > 0.4 and
                env["corruption_level"] < 0.5 and
                env["natural_vitality"] > 0.3):
            self._calling_fired = True
            # Inject faithful remnant
            self.population.inject_faithful_remnant(10)
            # Activate covenant — this is the CDT turning point
            self.distance.covenant_active = True
            self.distance.state.covenant_strength = 0.4
            self.distance.state.divine_nearness = min(1.0,
                self.distance.state.divine_nearness + 0.2)
            return [{
                "tick": self.tick,
                "type": "calling",
                "description": "God calls out a faithful people — covenant initiated",
                "parallel": "abram_pattern"
            }]
        return []

    def _activate_indwelling(self):
        """Mark all current remnant agents as Spirit-indwelt.

        This fires once when the cycle breaks (incarnation/resurrection).
        The Spirit doesn't remove the curse — agents still face entropy,
        rebellion, delusion. But they have enhanced resistance and the
        capacity to reproduce (missionary function).
        """
        for agent in self.population.agents:
            if agent.alive and agent.is_remnant:
                agent.indwelt = True

    def _step_missionary_reproduction(self, pop: dict) -> List[dict]:
        """Post-incarnation: indwelt remnant agents reproduce.

        The missionary function — the multiplication the resurrection unlocks.
        Scales with city density (gospel spreads fast in cities).
        Works THROUGH accumulated curses, not by erasing them.
        """
        events = []
        density = pop["city_density"]

        # Any remnant agent alive post-incarnation is indwelt —
        # born into the Spirit-community, not earning it individually
        for agent in self.population.agents:
            if agent.alive and agent.is_remnant and not agent.indwelt:
                agent.indwelt = True

        converts = self.population.missionary_reproduce(density)

        if converts > 0 and (converts >= 3 or self.tick % 50 == 0):
            events.append({
                "tick": self.tick,
                "type": "missionary_reproduction",
                "converts": converts,
                "city_density": density,
                "description": (f"Gospel multiplies in the cities — {converts} new "
                                f"converts at density {density:.0%}. The multiplication "
                                f"works through the accumulated curses."),
                "parallel": "acts_pattern"
            })

        return events

    def _step_city_schism(self, pop: dict, env: dict) -> List[dict]:
        """Model city density effects on schism pressure.

        Cities never stopped being corrupting agents. Post-resurrection,
        the gospel comes to Gentile cities ripe for harvest — density
        amplifies the spread. But the church in cities becomes factions.

        Schism pressure builds when:
        - City density is high (concentrated population)
        - Remnant fraction is significant (enough believers to factionate)
        - Accumulated fragmentation curse is present (structural weakness)
        - Cycle has been broken (post-resurrection context)

        Schism only fires at a HIGH threshold — not every start is a schism.
        It takes sustained pressure building over many ticks.
        """
        events = []
        density = pop["city_density"]
        remnant = pop["remnant_fraction"]
        curses = self.environment.cycle_tracker.curse_registry
        cycle_broken = self.environment.cycle_tracker.cycle_broken

        # Post-resurrection: density amplifies remnant growth
        # (handled in distance engine via city_density in environment)

        # === Schism Pressure Accumulation ===
        # Pressure builds slowly when conditions are present.
        # All three factors must be non-trivial for pressure to grow.
        if density > 0.3 and remnant > 0.1 and curses.total_fragmentation > 0.05:
            # Pressure grows proportional to all three factors
            # All must be present but the combined effect scales naturally
            growth = density * remnant * curses.total_fragmentation * 0.02

            # Post-cycle-breaking intensifies — the gospel multiplies fast
            # in cities, which means MORE believers to factionate
            if cycle_broken:
                growth *= 2.5

            self._schism_pressure = min(1.0, self._schism_pressure + growth)
        else:
            # Slow decay when conditions aren't met — pressure doesn't vanish instantly
            self._schism_pressure = max(0.0, self._schism_pressure - 0.001)

        # === Schism Event Detection ===
        # HIGH threshold — not every gathering splits.
        # Takes sustained pressure to actually fracture.
        schism_threshold = 0.7
        cooldown = 100  # minimum ticks between schisms

        if (self._schism_pressure >= schism_threshold and
                self.tick - self._last_schism_tick >= cooldown):
            self._schism_count += 1
            self._last_schism_tick = self.tick
            # Schism partially releases pressure but doesn't reset it —
            # the structural fault lines remain
            self._schism_pressure *= 0.5

            # Schism damages covenant strength
            self.distance.state.covenant_strength *= 0.85

            events.append({
                "tick": self.tick,
                "type": "schism",
                "pressure_at_break": self._schism_pressure * 2,  # pre-release value
                "schism_number": self._schism_count,
                "city_density": density,
                "accumulated_curses": curses.curse_count,
                "description": (f"Church fractures in the cities — schism #{self._schism_count}. "
                                f"Density {density:.0%}, bearing {curses.curse_count} "
                                f"accumulated curses. The fragmentation curse "
                                f"operates through the multiplied faithful."),
                "parallel": "faction_pattern"
            })

        return events

    def _check_atonement_conditions(self, pop: dict, dist: dict, eng: dict) -> bool:
        """Atonement emerges when covenant is active and distance is significant."""
        return (pop["remnant_fraction"] > 0.1 and
                dist["covenant_health"] > 0.3 and
                eng["presence_level"] > 0.5 and
                dist["active_distance"] > 0.25 and
                dist["spiritual_vitality"] > 0.2)

    def get_history_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.history)

    def get_events_df(self) -> pd.DataFrame:
        if not self.all_events:
            return pd.DataFrame()
        return pd.DataFrame(self.all_events)

    def get_summary(self) -> dict:
        events_df = self.get_events_df()
        event_counts = {}
        if not events_df.empty and "type" in events_df.columns:
            event_counts = events_df["type"].value_counts().to_dict()

        final_env = self.environment.get_state_snapshot()
        final_dist = self.distance.get_state_snapshot()
        final_eng = self.engagement.get_state_snapshot()

        curse_summary = self.environment.cycle_tracker.curse_registry.get_summary()

        return {
            "total_ticks": self.tick,
            "total_events": len(self.all_events),
            "event_types": event_counts,
            "cycles_completed": final_env["cycle_count"],
            "cycle_broken": final_env["cycle_broken"],
            "flood_count": self._flood_count,
            "final_corruption": final_env["corruption_level"],
            "final_covenant_health": final_dist["covenant_health"],
            "final_divine_nearness": final_dist["divine_nearness"],
            "final_presence": final_eng["presence_level"],
            "final_remnant": final_dist["remnant_fraction"],
            "intimacy_milestones": final_dist["intimacy_milestones"],
            "schism_count": self._schism_count,
            "schism_pressure": round(self._schism_pressure, 4),
            "accumulated_curses": curse_summary,
            "scc_key_question": ("RESOLVED — cycle broken from within"
                                if final_env["cycle_broken"]
                                else "UNRESOLVED — cycles continue"),
        }
