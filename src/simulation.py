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
from .agents import Population, Agent, AgentTraits


@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""
    num_ticks: int = 1000
    population_size: int = 500
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
        self._flood_occurred = False
        self._flood_tick = 0  # when the flood happened (for repopulation timing)

        # === Sojourn Mechanics ===
        # The 400-year pause: after calling, the covenant people are
        # displaced (Egypt). God deliberately waits for the Amorites'
        # iniquity to fill up. Temple cannot be built during sojourn.
        # The sojourn ends when the land's corruption reaches the
        # judgment threshold — the iniquity of the Amorites is complete.
        self._sojourn_active = False
        self._sojourn_start_tick = 0
        self._sojourn_ended = False
        self._amorite_iniquity = 0.0  # accumulates toward judgment

        # === Temple Mechanics ===
        # The temple is the heaven-earth convergence point — a localized
        # entropy drain in the city. It sustains the remnant against
        # maximum corruption. When temple presence builds high enough
        # it triggers incarnation — God fully entering the convergence.
        self._temple_presence = 0.0
        self._temple_number = 0       # which temple we're on (0 = none yet)
        self._temple_standing = False  # is a temple currently standing?
        self._exile_start_tick = 0    # when first temple destroyed (for Cyrus decree)

        # === Grace Period (the Millennium) ===
        # After incarnation, the Spirit reduces "the bent" — the
        # gravitational pull toward corruption across the whole system.
        # The curse doesn't lift, but its grip loosens. For ~1000 years
        # the church operates under reduced entropy pressure.
        # When grace fades, the Great Schism fractures the church.
        self._grace_period_active = False
        self._grace_start_tick = 0
        self._grace_duration = 1000  # ticks of reduced bent
        self._great_schism_fired = False

        # === Schism Mechanics ===
        # Cities amplify everything. Post-resurrection, the gospel spreads
        # fast in cities — but the accumulated fragmentation curse means
        # the multiplied faithful eventually split. Schism pressure builds
        # slowly and only fires when it crosses a HIGH threshold.
        # Not every gathering becomes a schism.
        self._schism_pressure = 0.0
        self._schism_count = 0
        self._last_schism_tick = -200

        # === Eschatological State ===
        # After the Great Schism, entropy overwhelms the post-grace church.
        # The final apostasy builds as corruption returns to maximum.
        # When conditions reach their darkest — yet the remnant persists —
        # the cycle-breaker returns. Not escape but consummation.
        # The parousia resolves what the flood could only reset.
        self._consummated = False
        self._apostasy_level = 0.0   # builds after grace ends
        self._parousia_tick = 0
        self._settlement_tick = 0    # when settlement/conquest began
        self._wrath_event_fired = False  # cup of wrath event (once)

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

        # === Post-Consummation: New Creation State ===
        # After the parousia, the simulation continues but in a
        # qualitatively different state. No entropy, no decay, no cycles.
        # We record the stable state without running the full engine.
        if self._consummated:
            snapshot = {
                "tick": self.tick,
                "env_corruption_level": 0.0,
                "env_heavenly_influence": 1.0,
                "env_underworld_pressure": 0.0,
                "env_natural_vitality": 1.0,
                "env_cycle_count": self.environment.cycle_tracker.cycle_count,
                "env_cycle_broken": True,
                "env_current_phase": "new_creation",
                "cdt_covenant_health": 1.0,
                "cdt_divine_nearness": 1.0,
                "cdt_active_distance": 0.0,
                "cdt_spiritual_vitality": 1.0,
                "cdt_incremental_intimacy": 1.0,
                "cdt_remnant_fraction": 1.0,
                "dsa_presence_level": 1.0,
                "dsa_grace_space": 1.0,
                "pop_alive_count": len(self.population.agents),
                "pop_remnant_fraction": 1.0,
                "pop_population_faithfulness": 1.0,
                "pop_population_rebellion": 0.0,
                "pop_avg_spiritual_vitality": 1.0,
                "pop_city_density": 1.0,
                "grace_period_active": False,
                "sojourn_active": False,
                "amorite_iniquity": 0.0,
                "temple_presence": 1.0,
                "schism_pressure": 0.0,
                "schism_count": self._schism_count,
                "apostasy_level": 0.0,
                "consummated": True,
                "event_count": 0,
            }
            self.history.append(snapshot)
            return []

        # === Generational Turnover ===
        # Every generation, some agents die and new ones are born.
        # CDT: the next generation must find faith anew.
        if self.tick % 80 == 0 and self.tick > 0:
            self._generational_turnover()

        # === Post-Flood Repopulation ===
        # "Be fruitful and multiply" — after the flood, population grows
        # rapidly under divine mandate. This fires frequently until the
        # population is viable again, independent of generational turnover.
        if self._flood_occurred:
            self._repopulate_post_flood()

        # === Settlement Repopulation ===
        # After sojourn ends, the covenant people take the land and multiply.
        # Conquest → Judges → Kingdom era. Population grows to fill the land.
        if self._sojourn_ended:
            self._repopulate_settlement()

        # === Minimum Remnant Preservation ===
        # CDT: God always preserves a remnant — sovereign, not natural
        self._preserve_minimum_remnant()

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

        # Track flood
        for e in env_events:
            if e.get("type") == "cataclysmic_reset":
                self._flood_occurred = True
                self._flood_tick = self.tick
                # After the flood, kill most agents, keep faithful remnant
                self._post_reset_population()
                # The flood IS cycle 0's failure — impose the first curse
                # directly. The ground is cursed from here forward.
                curses = self.environment.cycle_tracker.curse_registry
                if curses.curse_count == 0:
                    curse = curses.impose_cycle_curse(0)
                    self.environment.cycle_tracker.cycle_count = 1
                    tick_events.append({
                        "tick": self.tick,
                        "type": "curse_imposed",
                        "curse_type": curse.curse_type,
                        "description": (f"Curse imposed: {curse.description}. "
                                        "The ground bears the weight of the first failure."),
                        "parallel": "curse_pattern"
                    })

        # === Kingdom Collapse Destroys Temple ===
        # When the kingdom era population collapses, the temple falls.
        # Babylon didn't attack a thriving kingdom — they burned the
        # temple of a people already in decline. The exile IS the
        # population collapse — a FALL from kingdom to remnant.
        # Only triggers once per temple: when population drops below
        # threshold AND the temple was built with a larger population.
        # Kingdom collapse scales with population size — exile threshold
        # is when the kingdom shrinks to a small fraction of capacity
        exile_threshold = max(8, int(self.config.population_size * 0.08))
        if (self._temple_standing and
                self._sojourn_ended and
                pop_signals["alive_count"] <= exile_threshold and
                pop_signals["city_density"] < 0.15 and
                self._temple_presence > 0.15):  # only destroys a real temple
            # Check this temple hasn't already survived a collapse
            # (the second temple is built BY the remnant, so it's immune)
            if self._temple_number == 1:
                self._temple_presence = 0.08  # foundations remain
                self._temple_standing = False
                self._exile_start_tick = self.tick  # track for Cyrus decree
                tick_events.append({
                    "tick": self.tick,
                    "type": "temple_destroyed",
                    "temple_number": self._temple_number,
                    "description": ("First temple destroyed — the kingdom "
                                    "collapsed, the city fell, the sacred space "
                                    "is consumed. Exile."),
                    "parallel": "exile_destruction_pattern"
                })
        # Exile events also damage temple
        for e in env_events:
            if e.get("type") == "exile" and self._temple_standing:
                self._temple_presence *= 0.4

        # === Sojourn Mechanics ===
        # During the sojourn, covenant people are displaced.
        # The Amorites' iniquity accumulates toward judgment.
        # Temple cannot be built until the sojourn ends.
        if self._sojourn_active:
            tick_events.extend(self._step_sojourn(
                self.environment.get_state_snapshot()))

        # === Temple Mechanics ===
        # Temple builds as heaven-earth convergence in the city.
        # When it reaches threshold, triggers incarnation.
        # BLOCKED during sojourn — can't build in a land not yet given.
        if not self._sojourn_active:
            tick_events.extend(self._step_temple(
                pop_signals,
                self.environment.get_state_snapshot(),
                self.engagement.get_state_snapshot(),
                self.distance.get_state_snapshot(),
            ))

        # === Post-Incarnation: Missionary Reproduction ===
        if self.environment.cycle_tracker.cycle_broken:
            tick_events.extend(self._step_missionary_reproduction(pop_signals))

        # === Grace Period (the Millennium) ===
        # During grace: reduced bent, church grows under protection.
        # When grace fades: the Great Schism fires.
        if self._grace_period_active:
            tick_events.extend(self._step_grace_period(pop_signals))

        # === City Density Effects & Schism Detection ===
        tick_events.extend(self._step_city_schism(pop_signals, env_state))

        # === Eschatological Consummation ===
        # After the Great Schism, apostasy builds toward final darkness.
        # When the remnant is nearly overwhelmed — the return.
        if self._consummated:
            # Post-consummation: maintain new creation state
            self._step_new_creation()
        else:
            tick_events.extend(self._step_consummation(
                pop_signals,
                self.environment.get_state_snapshot(),
                self.engagement.get_state_snapshot(),
            ))

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
            "grace_period_active": self._grace_period_active,
            "sojourn_active": self._sojourn_active,
            "amorite_iniquity": round(self._amorite_iniquity, 4),
            "temple_presence": round(self._temple_presence, 4),
            "schism_pressure": round(self._schism_pressure, 4),
            "schism_count": self._schism_count,
            "apostasy_level": round(self._apostasy_level, 4),
            "consummated": self._consummated,
            "event_count": len(tick_events),
        }
        self.history.append(snapshot)
        self.all_events.extend(tick_events)

        return tick_events

    def _generational_turnover(self):
        """Replace a fraction of agents with new ones.
        CDT: each generation must discover faith anew.

        Post-flood: population grows faster — "be fruitful and multiply."
        The repopulation window gives the covenant era a viable population.
        """
        agents = self.population.agents
        alive = [a for a in agents if a.alive]
        if not alive:
            return

        n_remove = max(1, int(len(alive) * 0.15))
        for agent in alive[:n_remove]:
            agent.alive = False

        # Post-flood repopulation: if population is below initial size
        # and the flood has occurred, spawn extra agents to rebuild.
        # "Be fruitful and multiply" — rapid growth after the reset.
        n_spawn = n_remove
        if self._flood_occurred and len(alive) < self.config.population_size:
            ticks_since_flood = self.tick - self._flood_tick
            if ticks_since_flood < 400:
                # Strong repopulation in the first ~400 ticks after flood
                deficit = self.config.population_size - len(alive)
                extra = max(2, int(deficit * 0.12))
                n_spawn = n_remove + extra

        for i in range(n_spawn):
            new_id = len(agents) + i
            agent = Agent(new_id, self.rng)
            # New generation starts with low faith — must discover it
            agent.state.faith = np.clip(self.rng.normal(0.15, 0.1), 0.02, 0.4)
            agent.state.rebellion = np.clip(self.rng.normal(0.35, 0.15), 0.1, 0.7)
            agent.state.delusion_level = np.clip(self.rng.normal(0.25, 0.1), 0.05, 0.5)
            agents.append(agent)

        self.population.size = len(agents)

    def _repopulate_post_flood(self):
        """Be fruitful and multiply — rapid population growth after the flood.

        Fires every few ticks until population recovers to target size.
        Children of the remnant are raised in covenant community —
        they start with moderate faith, not the zero-baseline of random
        generational turnover. Each generation still must find faith anew,
        but the starting point is better than a godless generation.
        """
        alive = [a for a in self.population.agents if a.alive]
        n_alive = len(alive)

        # Stop repopulating once population is restored
        if n_alive >= self.config.population_size:
            return

        # Repopulation rate: every 10 ticks, spawn agents proportional to deficit
        if self.tick % 10 != 0:
            return

        ticks_since_flood = self.tick - self._flood_tick
        if ticks_since_flood > 500:
            return  # repopulation mandate fades after extended period

        # Spawn rate scales with how depleted the population is
        deficit = self.config.population_size - n_alive
        n_spawn = max(1, int(deficit * 0.08))

        agents = self.population.agents
        for i in range(n_spawn):
            new_id = len(agents) + i
            agent = Agent(new_id, self.rng)
            # Children of the remnant — raised in covenant community
            # Better starting faith than random generation, but still
            # must discover it for themselves (CDT)
            agent.state.faith = np.clip(self.rng.normal(0.35, 0.15), 0.1, 0.6)
            agent.state.faithfulness = np.clip(self.rng.normal(0.3, 0.1), 0.1, 0.5)
            agent.state.rebellion = np.clip(self.rng.normal(0.2, 0.1), 0.05, 0.45)
            agent.state.delusion_level = np.clip(self.rng.normal(0.1, 0.08), 0.0, 0.3)
            agent.state.spiritual_vitality = np.clip(self.rng.normal(0.7, 0.1), 0.4, 0.9)
            agents.append(agent)

        self.population.size = len(agents)

    def _repopulate_settlement(self):
        """Settlement repopulation — covenant people fill the promised land.

        After the sojourn, the people multiply in the land God gave them.
        This creates the kingdom era: judges, united kingdom, temple building.
        The repopulation gives the first temple a viable population base.
        """
        alive = [a for a in self.population.agents if a.alive]
        n_alive = len(alive)
        if n_alive >= self.config.population_size:
            return
        if self.tick % 8 != 0:
            return

        ticks_since_settlement = self.tick - self._settlement_tick
        if ticks_since_settlement > 800:
            return  # settlement/kingdom growth phase ends

        deficit = self.config.population_size - n_alive
        n_spawn = max(1, int(deficit * 0.08))

        agents = self.population.agents
        for i in range(n_spawn):
            new_id = len(agents) + i
            agent = Agent(new_id, self.rng)
            # Children of the covenant in the promised land —
            # raised with knowledge of God's acts (exodus, conquest)
            agent.state.faith = np.clip(self.rng.normal(0.4, 0.15), 0.15, 0.65)
            agent.state.faithfulness = np.clip(self.rng.normal(0.35, 0.1), 0.15, 0.55)
            agent.state.rebellion = np.clip(self.rng.normal(0.2, 0.1), 0.05, 0.4)
            agent.state.delusion_level = np.clip(self.rng.normal(0.1, 0.08), 0.0, 0.3)
            agent.state.spiritual_vitality = np.clip(self.rng.normal(0.7, 0.1), 0.4, 0.9)
            agents.append(agent)
        self.population.size = len(agents)

    def _post_reset_population(self):
        """After a cataclysmic reset, most die. A remnant survives."""
        alive = [a for a in self.population.agents if a.alive]
        if not alive:
            return
        n_survive = max(40, int(len(alive) * 0.08))
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

        if (self._flood_occurred and
                pop["remnant_fraction"] > 0.03 and
                eng["presence_level"] > 0.3 and
                env["corruption_level"] < 0.6 and
                env["natural_vitality"] > 0.25):
            self._calling_fired = True
            # Inject faithful remnant
            self.population.inject_faithful_remnant(50)
            # Activate covenant — this is the CDT turning point
            self.distance.covenant_active = True
            self.distance.state.covenant_strength = 0.4
            self.distance.state.divine_nearness = min(1.0,
                self.distance.state.divine_nearness + 0.2)
            # Begin the sojourn — covenant people exist but are displaced.
            # Temple cannot be built until the Amorites' iniquity is full.
            self._sojourn_active = True
            self._sojourn_start_tick = self.tick
            return [{
                "tick": self.tick,
                "type": "calling",
                "description": "God calls out a faithful people — covenant initiated. "
                               "The sojourn begins — displaced among the nations, "
                               "waiting for the fullness of time.",
                "parallel": "abram_pattern"
            }]
        return []

    def _preserve_minimum_remnant(self):
        """CDT: God always preserves a remnant — even in maximum corruption.

        If the living population drops dangerously low, divine preservation
        sustains a handful of agents. This is not natural survival — it's
        sovereign preservation of the covenant line. Abraham's family in
        Ur, the faithful during exile, the hidden remnant in occupation.
        """
        alive = [a for a in self.population.agents if a.alive]
        if len(alive) >= 20:
            return

        # Preserve: boost the few remaining or spawn preserved remnant
        n_needed = 20 - len(alive)

        # First: boost any living agents to survive
        for agent in alive:
            agent.state.spiritual_vitality = max(agent.state.spiritual_vitality, 0.3)
            agent.state.faith = max(agent.state.faith, 0.2)

        # Then: spawn divinely preserved agents if needed
        if n_needed > 0:
            agents = self.population.agents
            for i in range(n_needed):
                new_id = len(agents) + i
                traits = AgentTraits(
                    faith_capacity=np.clip(self.rng.normal(0.75, 0.1), 0.6, 0.9),
                    resilience=np.clip(self.rng.normal(0.7, 0.1), 0.5, 0.85),
                    awareness_sensitivity=np.clip(self.rng.normal(0.75, 0.1), 0.6, 0.9),
                    relational_capacity=np.clip(self.rng.normal(0.65, 0.1), 0.5, 0.8),
                )
                agent = Agent(new_id, self.rng, traits)
                # Preserved remnant — hidden, small, but sustained by God.
                # These are remnant-quality: faithful enough to qualify.
                # God preserves the faithful, not random survivors.
                agent.state.faith = np.clip(self.rng.normal(0.6, 0.1), 0.5, 0.8)
                agent.state.faithfulness = np.clip(self.rng.normal(0.5, 0.1), 0.4, 0.7)
                agent.state.rebellion = np.clip(self.rng.normal(0.1, 0.05), 0.03, 0.2)
                agent.state.delusion_level = np.clip(self.rng.normal(0.05, 0.03), 0.0, 0.15)
                agent.state.spiritual_vitality = np.clip(self.rng.normal(0.7, 0.1), 0.5, 0.9)
                agent.is_remnant = True
                agents.append(agent)
            self.population.size = len(agents)

    def _step_sojourn(self, env: dict) -> List[dict]:
        """The 400-year sojourn — God waits for the Amorites' iniquity.

        Genesis 15:13-16: 'your offspring will be strangers in a land
        not their own... for the iniquity of the Amorites is not yet
        complete.'

        The covenant people exist and are preserved, but they are
        displaced — unable to build the temple. Meanwhile, the land's
        corruption accumulates. God is deliberately waiting (DSA:
        patience as sovereign choice). The sojourn ends when the
        Amorites' iniquity crosses the judgment threshold.

        During the sojourn:
        - Temple growth is blocked
        - Amorite iniquity accumulates from environmental corruption
        - God's patience is active (not absent)
        - The covenant people are refined in displacement
        """
        events = []
        corruption = env["corruption_level"]

        # Amorite iniquity accumulates — driven by environmental
        # corruption but at its own pace. This is the judgment clock.
        # Not every tick of corruption counts equally — the iniquity
        # builds slowly, then accelerates as it approaches fullness.
        self._amorite_iniquity += (corruption * 0.0004 +
                                   self._amorite_iniquity * 0.00005)
        self._amorite_iniquity = min(1.0, self._amorite_iniquity)

        # Minimum sojourn duration — God's timing is not rushed.
        # 400 years of displacement, forging a people.
        ticks_in_sojourn = self.tick - self._sojourn_start_tick
        min_sojourn = 800  # 400 years of displacement, forging a people

        # The sojourn ends when the Amorites' iniquity is complete
        # AND enough time has passed for the covenant people to be
        # forged in displacement.
        if (self._amorite_iniquity > 0.7 and
                ticks_in_sojourn >= min_sojourn):
            self._sojourn_active = False
            self._sojourn_ended = True
            self._settlement_tick = self.tick

            # === Settlement / Conquest ===
            # The covenant people enter the land and multiply.
            # God gives the land — the Amorites' judgment is complete.
            # The land is cleansed by divine judgment — a significant
            # corruption reset. This gives a flourishing window for
            # the kingdom era: judges, united monarchy, temple building.
            # Think Solomon's reign — prosperity, peace, construction.
            # The judgment doesn't just suppress corruption — it
            # dismantles the corrupt infrastructure. The Amorites' cities
            # are destroyed. It takes generations for new corruption
            # to rebuild. This gives the kingdom era its flourishing window.
            self.environment.realm.corruption_level = 0.02
            self.environment.realm.underworld_pressure = 0.05
            self.environment.realm.chaos_seepage = 0.02
            self.environment.realm.natural_vitality = 0.85
            self.environment.realm.heavenly_influence = min(1.0,
                self.environment.realm.heavenly_influence + 0.4)

            # Inject a wave of covenant settlers — the people who
            # crossed the Jordan, the tribes taking the land
            self.population.inject_faithful_remnant(75)

            events.append({
                "tick": self.tick,
                "type": "sojourn_ends",
                "duration": ticks_in_sojourn,
                "amorite_iniquity": round(self._amorite_iniquity, 3),
                "description": (f"The iniquity of the Amorites is complete — "
                                f"sojourn ends after {ticks_in_sojourn} ticks. "
                                f"The covenant people enter the land. "
                                f"Settlement and conquest begin."),
                "parallel": "exodus_conquest_pattern"
            })

        return events

    def _step_temple(self, pop: dict, env: dict, eng: dict, dist: dict) -> List[dict]:
        """Temple mechanic — heaven-earth convergence point in the city.

        The temple is a localized entropy drain. It sustains the remnant
        against maximum corruption by providing a pocket of sanctified space.
        Temple presence builds when:
        - Covenant is active and has some strength
        - Faithfulness and divine engagement are present
        - City density provides the critical mass for worship

        When temple presence reaches a HIGH threshold, it triggers
        incarnation — God fully entering the convergence point.
        The temple builds up slowly, like schism builds up slowly.
        Not every act of worship builds a temple; sustained, faithful,
        covenant worship in a city over generations does.
        """
        events = []

        # Temple can only exist after covenant is activated
        if not self.distance.covenant_active:
            return events

        density = pop["city_density"]
        faithfulness = pop["population_faithfulness"]
        covenant = dist["covenant_strength"]
        engagement = eng["presence_level"]
        remnant = pop["remnant_fraction"]

        # === City Corruption Drain on Temple ===
        # The city never stops corroding the temple. Like a long-term
        # relationship gone sour — the surrounding culture pulls toward
        # compromise. Corruption and density together erode sacred space.
        # This is ALWAYS active, even when worship is growing the temple.
        # The temple has to OUTPACE the city's corrosive drag.
        corruption = env["corruption_level"]
        city_drag = corruption * density * 0.002 + corruption * 0.0003
        # Accumulated curses intensify the drag — structural damage
        # from prior failures makes the city even more hostile to
        # the sacred. Each curse deepens the hostility.
        curses = self.environment.cycle_tracker.curse_registry
        curse_drag = curses.total_fragmentation * 0.0003 + curses.total_foreign_pressure * 0.0002

        # As the temple grows stronger, the city pushes back harder.
        # The sacred presence threatens the corrupt order — the closer
        # to incarnation, the more intense the resistance. This creates
        # fast initial rebuilding (exile is short — Cyrus decree) but
        # a long grind as temple approaches fullness (centuries of
        # occupation, Hellenization, Roman pressure on covenant worship).
        temple_threat = self._temple_presence * corruption * 0.0005

        total_drag = city_drag + curse_drag + temple_threat

        # === Temple Building ===
        # Temple presence grows with sustained covenant worship.
        # Even a tiny remnant can sustain a temple — 5 faithful families
        # worshipping in exile is enough. Density amplifies but isn't required.
        # But it must outpace the city's corrosive drag to actually grow.
        # Worship requires minimal faithfulness and covenant, not
        # necessarily a large remnant fraction. Even 5 families
        # worshipping faithfully sustains the temple.
        alive_count = pop.get("alive_count", 0)
        if (faithfulness > 0.2 and covenant > 0.15 and
                engagement > 0.2 and alive_count >= 3):
            # Population size amplifies temple growth — more worshippers
            # means faster construction. Solomon had thousands of workers.
            # A city of 50 builds faster than 5 families in exile.
            # But temple building is generational work, not instant.
            pop_factor = 1.0 + density * 1.0  # density=0.5 → 1.5x, density=1.0 → 2.0x

            growth = (faithfulness * 0.3 +
                     covenant * 0.3 +
                     engagement * 0.2 +
                     density * 0.1 +
                     remnant * 0.1) * 0.003 * pop_factor

            # Cyrus decree: after first temple destruction, a divine
            # mandate accelerates rebuilding. The exile is short because
            # God sends the people back. This boost fades over time.
            if (self._temple_number >= 1 and not self._temple_standing and
                    self._exile_start_tick > 0):
                ticks_since_exile = self.tick - self._exile_start_tick
                if ticks_since_exile < 300:
                    decree_boost = 3.0 * max(0, 1.0 - ticks_since_exile / 300.0)
                    growth *= (1.0 + decree_boost)

            # Net change: worship growth minus city corruption drag
            net = growth - total_drag
            self._temple_presence = np.clip(
                self._temple_presence + net, 0.0, 1.0)

            # Temple built event — fires when presence crosses 0.2
            # A modest temple is still a real convergence point.
            if not self._temple_standing and self._temple_presence > 0.2:
                self._temple_number += 1
                self._temple_standing = True
                ordinal = {1: "First", 2: "Second", 3: "Third"}.get(
                    self._temple_number, f"Temple #{self._temple_number}")
                events.append({
                    "tick": self.tick,
                    "type": "temple_built",
                    "temple_number": self._temple_number,
                    "presence": self._temple_presence,
                    "description": (f"{ordinal} temple established — heaven-earth "
                                    f"convergence point. Localized entropy drain "
                                    f"active in the city."),
                    "parallel": "temple_pattern"
                })
        else:
            # No worship AND city drag — temple erodes faster
            self._temple_presence = max(0.0,
                self._temple_presence - 0.002 - total_drag)

            # Temple destruction — standing temple collapses
            if self._temple_standing and self._temple_presence < 0.1:
                self._temple_standing = False
                if self._temple_number == 1:
                    self._exile_start_tick = self.tick  # Cyrus decree clock starts
                ordinal = {1: "First", 2: "Second", 3: "Third"}.get(
                    self._temple_number, f"Temple #{self._temple_number}")
                events.append({
                    "tick": self.tick,
                    "type": "temple_destroyed",
                    "temple_number": self._temple_number,
                    "description": (f"{ordinal} temple destroyed — convergence point "
                                    f"lost. The city's corruption consumed the "
                                    f"sacred space."),
                    "parallel": "exile_destruction_pattern"
                })

        # === Temple as Entropy Drain ===
        # When temple is present, it creates a localized pocket that
        # resists corruption. This sustains the remnant, but it cannot
        # purify the world. The drain is modest — enough to keep the
        # faithful alive, not enough to reverse the curse.
        # The temple pushes back against corruption but can't push it
        # below a floor — the curse of the ground remains.
        if self._temple_presence > 0.2:
            corruption = self.environment.realm.corruption_level
            # Drain scales with temple presence but is modest
            drain = self._temple_presence * 0.004
            # Corruption floor: the temple can slow entropy but the
            # curse persists. Higher corruption means less effective drain.
            floor = 0.15 + self.environment.cycle_tracker.curse_registry.total_entropy_penalty
            self.environment.realm.corruption_level = max(
                floor, corruption - drain)

        # === Incarnation Trigger ===
        # When temple presence reaches a very high threshold AND
        # accumulated curses have built to the fullness of time,
        # the incarnation fires. God doesn't just visit the temple —
        # God becomes the temple. The convergence point becomes a person.
        curses = self.environment.cycle_tracker.curse_registry
        if (not self.environment.cycle_tracker.cycle_broken and
                self._temple_presence > 0.55 and
                curses.curse_count >= 1 and
                engagement > 0.25):
            self.environment.cycle_tracker.cycle_broken = True
            events.append({
                "tick": self.tick,
                "type": "cycle_breaking",
                "temple_presence": self._temple_presence,
                "accumulated_curses": curses.curse_count,
                "description": ("The temple's fullness overflows — God enters the cycle "
                                f"as participant. Incarnation. Bearing {curses.curse_count} "
                                "accumulated curses. Not escape but death and resurrection "
                                "within the cycle."),
                "parallel": "incarnation_pattern"
            })
            # Incarnation activates indwelling and grace period
            self._activate_indwelling()
            self._grace_period_active = True
            self._grace_start_tick = self.tick

            # Pentecost: inject a wave of new believers — the 3000
            # of Acts 2. The church explodes in the cities.
            self.population.inject_faithful_remnant(100)
            for agent in self.population.agents[-100:]:
                agent.indwelt = True

            events.append({
                "tick": self.tick,
                "type": "spirit_indwelling",
                "description": ("The Spirit falls — remnant agents become indwelt. "
                                "Grace period begins: the bent is reduced. "
                                "Pentecost — thousands added to the church."),
                "parallel": "pentecost_pattern"
            })

        return events

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

    def _step_grace_period(self, pop: dict) -> List[dict]:
        """The 1000-year grace period — the bent is reduced.

        After incarnation, the Spirit's presence reduces the gravitational
        pull toward corruption across the whole system. The curse persists
        but its grip loosens. Entropy still accumulates, but slower.
        The church grows under this reduced pressure.

        When the grace period expires, the bent returns to full force
        and the Great Schism fires — the accumulated fragmentation
        curse fractures the church at its first full exposure to
        unreduced entropy.
        """
        events = []
        ticks_in_grace = self.tick - self._grace_start_tick

        if ticks_in_grace <= self._grace_duration:
            # === The Bent is Reduced ===
            # During grace, corruption pressure is dampened system-wide.
            # The Spirit works through the church to slow entropy.
            # This isn't immunity — it's resistance. The curse still
            # operates, but at reduced intensity.
            grace_strength = 1.0 - (ticks_in_grace / self._grace_duration) * 0.3
            # grace_strength fades from 1.0 to 0.7 over the period

            # Reduce corruption directly — the Spirit pushing back.
            # The bent is reduced enough for cities to become viable
            # for the church. People can survive and multiply.
            # During grace, corruption is CAPPED — the Spirit doesn't
            # just push back against entropy, it holds a ceiling.
            # The ceiling rises as grace fades (0.3 → 0.7 over 1000 ticks).
            grace_ceiling = 0.3 + (1.0 - grace_strength) * 0.6
            if self.environment.realm.corruption_level > grace_ceiling:
                self.environment.realm.corruption_level = grace_ceiling

            # Boost agent resilience during grace — indwelt agents
            # are sustained, and even non-indwelt agents benefit
            # from the reduced bent (common grace)
            for agent in self.population.agents:
                if agent.alive:
                    boost = 0.008 if agent.indwelt else 0.003
                    agent.state.spiritual_vitality = min(1.0,
                        agent.state.spiritual_vitality + boost * grace_strength)
                    # Reduce rebellion pressure — the bent loosens
                    agent.state.rebellion = max(
                        agent.state.rebellion - 0.002 * grace_strength,
                        0.03)

        elif not self._great_schism_fired:
            # === Grace Period Expires — the Great Schism ===
            # The reduced bent snaps back. The church, having grown
            # under protection, now faces the full weight of accumulated
            # curses for the first time. The fragmentation curse —
            # carried from Babel through every cycle — fractures the
            # church along fault lines that were masked by grace.
            self._great_schism_fired = True
            self._grace_period_active = False

            # The schism damages covenant strength significantly
            self.distance.state.covenant_strength *= 0.6

            # Fragmentation intensifies
            curses = self.environment.cycle_tracker.curse_registry
            events.append({
                "tick": self.tick,
                "type": "great_schism",
                "grace_duration": self._grace_duration,
                "accumulated_curses": curses.curse_count,
                "description": (f"The Great Schism — grace period ends after "
                                f"{self._grace_duration} ticks. The bent returns "
                                f"to full force. The church fractures under "
                                f"{curses.curse_count} accumulated curses. "
                                f"East and West divide."),
                "parallel": "great_schism_pattern"
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
        if density > 0.1 and remnant > 0.1 and curses.total_fragmentation > 0.05:
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

    def _step_consummation(self, pop: dict, env: dict, eng: dict) -> List[dict]:
        """Model the eschatological ending — the cup of wrath, parousia, new creation.

        The end comes at an entropy point. The cup of wrath is not a
        metaphor — it's accumulated entropy that reaches a terminal
        threshold. Every cycle's curses compound. Every failed generation
        adds weight. The cup fills.

        After the Great Schism, the bent returns to full force. Corruption
        climbs back to maximum. The post-grace church faces the full
        weight of every accumulated curse without the Spirit's restraining
        hand. The cup of wrath fills as entropy accumulates beyond what
        any prior cycle endured.

        When the cup overflows — the parousia fires.

        The parousia is NOT a reset. The flood was a reset — entropy
        cleared but curses remain, cycle continues. The parousia is
        RESOLUTION — every curse resolved, entropy permanently defeated,
        heaven-earth convergence made permanent. What the flood couldn't
        do, what the temple could only localize, what incarnation could
        only initiate — consummation completes.
        """
        events = []
        cycle_broken = self.environment.cycle_tracker.cycle_broken
        corruption = env["corruption_level"]
        curses = self.environment.cycle_tracker.curse_registry

        # === The Cup of Wrath Fills ===
        # After grace ends, entropy accumulates without restraint.
        # The cup of wrath is the total accumulated entropy burden —
        # corruption level PLUS the structural weight of every curse.
        # Each tick at maximum corruption adds to the cup.
        if (self._great_schism_fired and
                cycle_broken and
                not self._grace_period_active):

            # The cup fills from the STRUCTURAL weight of accumulated
            # curses — not just the corruption level. The post-grace
            # church can hold corruption down through sheer remnant
            # strength, but the structural damage is still there.
            # The cup fills slowly but inevitably as curse weight
            # grinds against the church's foundations.
            #
            # Two pathways fill the cup:
            # 1. High corruption (>0.7) — the classic entropy overwhelm
            # 2. Accumulated curse weight — structural damage from every
            #    failed cycle, grinding even when corruption is controlled
            curse_structural_weight = (curses.total_entropy_penalty +
                                       curses.total_fragmentation * 0.5)

            if corruption >= 0.7 or curse_structural_weight > 0.1:
                # Base rate from corruption
                wrath_rate = 0.001 * max(corruption, 0.3)
                # Curse weight accelerates — every failed cycle presses
                wrath_rate *= (1.0 + curse_structural_weight * 3.0)
                wrath_rate *= (1.0 + curses.curse_count * 0.05)
                # Time since grace ended — the longer without protection,
                # the faster the cup fills
                ticks_post_grace = self.tick - (self._grace_start_tick + self._grace_duration)
                time_factor = min(2.0, 1.0 + ticks_post_grace / 2000.0)
                wrath_rate *= time_factor
                self._apostasy_level = min(1.0, self._apostasy_level + wrath_rate)

            # The cup of wrath event — when it crosses the visible threshold
            if (self._apostasy_level >= 0.3 and
                    not self._wrath_event_fired):
                self._wrath_event_fired = True
                events.append({
                    "tick": self.tick,
                    "type": "cup_of_wrath",
                    "wrath_level": round(self._apostasy_level, 4),
                    "corruption": round(corruption, 4),
                    "accumulated_curses": curses.curse_count,
                    "total_entropy_penalty": round(curses.total_entropy_penalty, 4),
                    "description": (
                        f"The cup of wrath fills — {self._apostasy_level:.0%} full. "
                        f"Corruption at {corruption:.0%} under {curses.curse_count} "
                        f"accumulated curses (entropy penalty "
                        f"{curses.total_entropy_penalty:.3f}). "
                        f"The post-grace church bears the full weight of "
                        f"every cycle's failure. The cup that the flood could "
                        f"only empty now fills to overflowing."),
                    "parallel": "wrath_pattern"
                })

        # === The Parousia — The Cup Overflows ===
        # When the cup of wrath is full AND the remnant still persists.
        # The end comes at an entropy point, not a calendar date.
        # "As in the days of Noah" — but this time, not a reset.
        # The parousia fires when the cup overflows — not when
        # corruption is at absolute maximum, but when the accumulated
        # weight of every cycle's failure reaches its terminus.
        # The remnant still persists — that's the point. They endure.
        if (self._apostasy_level >= 0.85 and
                cycle_broken and
                pop["remnant_fraction"] > 0 and
                pop["alive_count"] > 0):

            self._consummated = True
            self._parousia_tick = self.tick

            events.append({
                "tick": self.tick,
                "type": "parousia",
                "apostasy_at_return": round(self._apostasy_level, 4),
                "corruption_at_return": round(corruption, 4),
                "remnant_at_return": pop["alive_count"],
                "accumulated_curses": curses.curse_count,
                "schisms_endured": self._schism_count,
                "description": (
                    f"The cycle-breaker returns — parousia. Not escape but "
                    f"consummation. Apostasy at {self._apostasy_level:.0%}, "
                    f"corruption at {corruption:.0%}, bearing "
                    f"{curses.curse_count} accumulated curses from every "
                    f"cycle. {pop['alive_count']} faithful remain. "
                    f"What the flood could only reset, the return resolves."),
                "parallel": "parousia_pattern"
            })

            # === Phase 3: Curse Resolution ===
            # Every accumulated curse — from every failed cycle —
            # is resolved. Not reversed (as if they never happened)
            # but fulfilled and overcome. The structural damage heals.
            resolved_curses = curses.curse_count
            for curse in curses.curses:
                curse.resolved = True
            events.append({
                "tick": self.tick,
                "type": "curse_resolution",
                "curses_resolved": resolved_curses,
                "description": (
                    f"All {resolved_curses} accumulated curses resolved. "
                    f"The structural damage from every cycle — fragmentation, "
                    f"foreign pressure, covenant penalties, entropy penalties "
                    f"— fulfilled and overcome. Not reversed but completed."),
                "parallel": "resolution_pattern"
            })

            # === Phase 4: New Creation ===
            # Entropy permanently defeated. Heaven-earth convergence
            # made permanent. All agents restored.
            # This is categorically different from a reset:
            # - Reset: corruption cleared, curses remain, cycle continues
            # - New creation: curses resolved, entropy source sealed,
            #   convergence permanent, no more cycles
            realm = self.environment.realm
            realm.corruption_level = 0.0
            realm.heavenly_influence = 1.0
            realm.underworld_pressure = 0.0
            realm.natural_vitality = 1.0
            realm.life_force_flow = 1.0
            realm.chaos_seepage = 0.0

            # Restore all agents — resurrection of the dead
            for agent in self.population.agents:
                agent.alive = True
                agent.state.faith = 1.0
                agent.state.faithfulness = 1.0
                agent.state.rebellion = 0.0
                agent.state.spiritual_vitality = 1.0
                agent.state.delusion_level = 0.0
                agent.state.awareness = 1.0
                agent.is_remnant = True
                agent.indwelt = True

            # Covenant perfected — distance eliminated
            self.distance.state.covenant_strength = 1.0
            self.distance.state.divine_nearness = 1.0
            self.distance.state.incremental_intimacy = 1.0
            self.distance.state.active_distance = 0.0
            self.distance.covenant_penalty = 0.0
            self.distance.fragmentation = 0.0
            self.distance.foreign_pressure = 0.0

            # Divine engagement permanent
            self.engagement.state.presence_level = 1.0
            self.engagement.state.grace_space = 1.0

            events.append({
                "tick": self.tick,
                "type": "new_creation",
                "agents_restored": len(self.population.agents),
                "curses_resolved": resolved_curses,
                "description": (
                    f"New creation — heaven and earth converge permanently. "
                    f"{len(self.population.agents)} agents restored. "
                    f"Entropy source sealed. Corruption cannot return. "
                    f"What the flood reset, the temple localized, and "
                    f"incarnation initiated — consummation completes. "
                    f"The cycle ends not by escape but by fulfillment."),
                "parallel": "new_creation_pattern"
            })

        return events

    def _step_new_creation(self):
        """Maintain new creation state — entropy permanently defeated.

        After consummation, the simulation continues ticking but in a
        qualitatively different state. No entropy, no corruption, no decay.
        The convergence is permanent.
        """
        realm = self.environment.realm
        realm.corruption_level = 0.0
        realm.heavenly_influence = 1.0
        realm.underworld_pressure = 0.0
        realm.natural_vitality = 1.0
        realm.chaos_seepage = 0.0

        # All agents remain fully alive and vital
        for agent in self.population.agents:
            if not agent.alive:
                agent.alive = True
            agent.state.spiritual_vitality = 1.0
            agent.state.rebellion = 0.0

        # Covenant and engagement remain perfect
        self.distance.state.covenant_strength = 1.0
        self.distance.state.active_distance = 0.0
        self.engagement.state.presence_level = 1.0

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
            "flood_occurred": self._flood_occurred,
            "final_corruption": final_env["corruption_level"],
            "final_covenant_health": final_dist["covenant_health"],
            "final_divine_nearness": final_dist["divine_nearness"],
            "final_presence": final_eng["presence_level"],
            "final_remnant": final_dist["remnant_fraction"],
            "intimacy_milestones": final_dist["intimacy_milestones"],
            "schism_count": self._schism_count,
            "schism_pressure": round(self._schism_pressure, 4),
            "accumulated_curses": curse_summary,
            "consummated": self._consummated,
            "parousia_tick": self._parousia_tick if self._consummated else None,
            "cup_of_wrath": round(self._apostasy_level, 4),
            "scc_key_question": (
                "CONSUMMATED — curses resolved, entropy defeated, "
                "heaven-earth convergence permanent"
                if self._consummated
                else ("RESOLVED — cycle broken from within"
                      if final_env["cycle_broken"]
                      else "UNRESOLVED — cycles continue")),
        }
