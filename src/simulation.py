"""
Simulation Runner — CDT Biblical Arc

Maps the simulation to the CDT reading of the biblical narrative:
  Eden -> Fall -> Antediluvian Slide -> Flood -> Babel -> Abraham Calling ->
  Patriarchs -> Egypt/Exodus -> Sinai/Tabernacle -> Judges Cycles ->
  United Monarchy -> Divided Kingdom -> Exile -> Return ->
  Intertestamental -> Incarnation -> Cross/Resurrection -> Church Age

The engines (SCC environment, CDT distance, DSA engagement) are unchanged.
What changes is the CONDITIONS each era creates for the agents —
environmental pressures, divine engagement patterns, and covenant dynamics
that produce the CDT narrative arc.

Events still emerge from dynamics — eras set the conditions, events emerge
when thresholds are crossed.
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from .environment import Environment
from .distance import DistanceEngine
from .engagement import EngagementEngine
from .agents import Population, Agent, AgentTraits


# ============================================================
# Era Definitions — CDT Biblical Timeline
# ============================================================

@dataclass
class Era:
    """A named period in the CDT biblical arc with environmental conditions."""
    name: str
    start_tick: int
    end_tick: int
    description: str
    parallel: str

    # Environmental pressures this era applies
    corruption_pressure: float = 0.0     # additional corruption input
    rebellion_pressure: float = 0.0      # additional rebellion on agents
    divine_engagement_mod: float = 0.0   # modifier to divine engagement
    covenant_boost: float = 0.0          # boost to covenant mechanics
    generational_turnover: float = 0.0   # rate of population replacement


def build_cdt_timeline(total_ticks: int = 1000) -> List[Era]:
    """Build the CDT biblical arc as a sequence of eras.

    Proportioned roughly to the biblical narrative's weight in CDT:
    - Pre-Abrahamic history is compressed (CDT: the problem is established)
    - Covenant history gets the most space (CDT: the two narratives intertwine)
    - Post-incarnation gets meaningful space (CDT: the resolution unfolds)
    """
    t = total_ticks
    return [
        Era("Eden", 0, int(t * 0.03), "Pristine creation — God walks with humanity",
            "genesis_1-2", divine_engagement_mod=0.4, covenant_boost=0.3),

        Era("Fall", int(t * 0.03), int(t * 0.06), "First rebellion — distance initiated",
            "genesis_3", corruption_pressure=0.3, rebellion_pressure=0.4),

        Era("Antediluvian Slide", int(t * 0.06), int(t * 0.13),
            "Cumulative rebellion — Cain, Lamech, technological arrogance",
            "genesis_4-6", corruption_pressure=0.5, rebellion_pressure=0.5,
            generational_turnover=0.2),

        Era("Flood", int(t * 0.13), int(t * 0.16), "Cataclysmic reset — but curse remains",
            "genesis_6-9", corruption_pressure=-0.3, divine_engagement_mod=0.2),

        Era("Post-Flood / Babel", int(t * 0.16), int(t * 0.22),
            "Renewed mandate, repeated failure, scattering",
            "genesis_9-11", corruption_pressure=0.2, rebellion_pressure=0.3,
            generational_turnover=0.15),

        Era("Abrahamic Calling", int(t * 0.22), int(t * 0.30),
            "God calls out one man — covenant initiated",
            "genesis_12-25", divine_engagement_mod=0.3, covenant_boost=0.4),

        Era("Patriarchs", int(t * 0.30), int(t * 0.36),
            "Covenant deepens through generations — wrestling, promise, exile in Egypt",
            "genesis_25-50", divine_engagement_mod=0.2, covenant_boost=0.2,
            corruption_pressure=0.1, generational_turnover=0.1),

        Era("Egypt / Exodus", int(t * 0.36), int(t * 0.42),
            "Slavery then liberation — God draws dramatically near",
            "exodus", divine_engagement_mod=0.4, covenant_boost=0.3,
            corruption_pressure=0.15),

        Era("Sinai / Tabernacle", int(t * 0.42), int(t * 0.48),
            "Law given, tabernacle built — God dwells among them",
            "exodus-leviticus", divine_engagement_mod=0.5, covenant_boost=0.5),

        Era("Judges Cycle", int(t * 0.48), int(t * 0.60),
            "Repeated cycle: flourishing -> complacency -> rebellion -> cry out -> deliverance",
            "judges", corruption_pressure=0.2, rebellion_pressure=0.25,
            generational_turnover=0.25),

        Era("United Monarchy", int(t * 0.60), int(t * 0.66),
            "Peak of Israel — temple built, but seeds of decline",
            "samuel-kings", divine_engagement_mod=0.3, covenant_boost=0.3,
            corruption_pressure=0.1),

        Era("Divided Kingdom", int(t * 0.66), int(t * 0.74),
            "Covenant fractures — northern kingdom falls, prophets warn",
            "kings-chronicles", corruption_pressure=0.6, rebellion_pressure=0.5,
            divine_engagement_mod=-0.1, generational_turnover=0.25),

        Era("Exile", int(t * 0.74), int(t * 0.80),
            "God's glory departs — temple destroyed, covenant at lowest",
            "jeremiah-ezekiel", corruption_pressure=0.7, rebellion_pressure=0.4,
            divine_engagement_mod=-0.3),

        Era("Return / Second Temple", int(t * 0.80), int(t * 0.85),
            "Partial restoration — return but not renewal",
            "ezra-nehemiah", corruption_pressure=0.1, divine_engagement_mod=0.1,
            covenant_boost=0.15),

        Era("Intertestamental", int(t * 0.85), int(t * 0.88),
            "Silence — waiting, occupation, the cycle grinds",
            "intertestamental", corruption_pressure=0.2, rebellion_pressure=0.15),

        Era("Incarnation", int(t * 0.88), int(t * 0.92),
            "God enters the cycle as a human being — the Second Adam",
            "gospels", divine_engagement_mod=0.8, covenant_boost=0.5,
            corruption_pressure=0.1),

        Era("Cross / Resurrection", int(t * 0.92), int(t * 0.95),
            "Death within the cycle, rising out of it — new creation inaugurated",
            "passion-resurrection", divine_engagement_mod=1.0, covenant_boost=0.8),

        Era("Church Age", int(t * 0.95), t,
            "Spirit indwelling — the fullest descent of life force into humanity",
            "acts-revelation", divine_engagement_mod=0.6, covenant_boost=0.4,
            corruption_pressure=0.1, generational_turnover=0.1),
    ]


# ============================================================
# Configuration
# ============================================================

@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""
    num_ticks: int = 1000
    population_size: int = 100
    seed: Optional[int] = 42
    enable_atonement: bool = True
    enable_incarnation: bool = True


# ============================================================
# Simulation
# ============================================================

class Simulation:
    """Main simulation orchestrator — CDT biblical arc."""

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

        # Build CDT timeline
        self.eras = build_cdt_timeline(self.config.num_ticks)
        self.current_era_idx = 0
        self.era_events_fired: set = set()

        # Initialize Eden state — pristine
        self._init_eden()

        # History tracking
        self.history: List[dict] = []
        self.all_events: List[dict] = []
        self.tick = 0

        # Judges cycle sub-tracker
        self._judges_sub_cycle = 0
        self._judges_phase = "flourishing"  # flourishing/complacency/rebellion/crying_out/deliverance

    def _init_eden(self):
        """Set pristine Eden conditions.

        CDT: humanity starts in full presence of God.
        No corruption, no distance, full vitality.
        """
        # Environment: pristine
        self.environment.realm.heavenly_influence = 1.0
        self.environment.realm.underworld_pressure = 0.0
        self.environment.realm.natural_vitality = 1.0
        self.environment.realm.corruption_level = 0.0
        self.environment.realm.life_force_flow = 1.0
        self.environment.realm.chaos_seepage = 0.0

        # Distance: no distance, full nearness
        self.distance.state.cumulative_rebellion = 0.0
        self.distance.state.active_distance = 0.0
        self.distance.state.curse_weight = 0.0
        self.distance.state.blessing_flow = 1.0
        self.distance.state.spiritual_vitality = 1.0
        self.distance.state.delusion_level = 0.0
        self.distance.state.awareness_of_condition = 1.0
        self.distance.state.divine_nearness = 1.0
        self.distance.state.covenant_strength = 0.8
        self.distance.state.remnant_fraction = 1.0
        self.distance.state.population_faithfulness = 1.0

        # Engagement: full presence, walking in the garden
        self.engagement.state.presence_level = 1.0
        self.engagement.state.experiential_engagement = 1.0
        self.engagement.state.self_limitation_degree = 0.1
        self.engagement.state.grace_space = 0.3
        self.engagement.state.delight = 0.8
        self.engagement.state.grief = 0.0
        self.engagement.state.patience = 1.0
        self.engagement.state.compassion = 0.7

        # Agents: high faith, low rebellion, full vitality
        for agent in self.population.agents:
            agent.state.faith = np.clip(self.rng.normal(0.8, 0.1), 0.5, 1.0)
            agent.state.faithfulness = np.clip(self.rng.normal(0.7, 0.1), 0.4, 1.0)
            agent.state.rebellion = np.clip(self.rng.normal(0.05, 0.03), 0.01, 0.15)
            agent.state.spiritual_vitality = np.clip(self.rng.normal(0.95, 0.03), 0.85, 1.0)
            agent.state.delusion_level = 0.0
            agent.state.awareness = agent.traits.awareness_sensitivity * 0.95
            agent.is_remnant = True

    def _get_current_era(self) -> Era:
        """Get the era for the current tick."""
        while (self.current_era_idx < len(self.eras) - 1 and
               self.tick >= self.eras[self.current_era_idx].end_tick):
            self.current_era_idx += 1
        return self.eras[self.current_era_idx]

    def run(self) -> pd.DataFrame:
        """Run the full simulation and return history as DataFrame."""
        for t in range(self.config.num_ticks):
            self.step()
        return self.get_history_df()

    def step(self) -> List[dict]:
        """Execute one simulation tick. Returns events from this tick."""
        self.tick += 1
        tick_events = []

        era = self._get_current_era()

        # === Era Transition Events ===
        if era.name not in self.era_events_fired:
            self.era_events_fired.add(era.name)
            tick_events.append({
                "tick": self.tick,
                "type": "era_transition",
                "era": era.name,
                "description": era.description,
                "parallel": era.parallel,
            })
            # Special era-entry actions
            tick_events.extend(self._on_era_enter(era))

        # === Era-specific Dynamics ===
        tick_events.extend(self._apply_era_dynamics(era))

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
        base_engagement, eng_events = self.engagement.step(
            population_faithfulness=pop_signals["population_faithfulness"],
            remnant_fraction=pop_signals["remnant_fraction"],
            covenant_health=dist_state["covenant_health"],
            corruption_level=env_state["corruption_level"],
            spiritual_vitality=pop_signals["avg_spiritual_vitality"],
            cycle_count=env_state["cycle_count"],
        )
        # Apply era modifier to engagement
        divine_engagement = np.clip(
            base_engagement + era.divine_engagement_mod * 0.3, 0.0, 1.0)
        tick_events.extend(eng_events)

        # === Step Distance (CDT) ===
        atonement = False
        if self.config.enable_atonement:
            atonement = self._check_atonement_conditions(
                pop_signals, dist_state, eng_state, era)

        dist_events = self.distance.step(
            rebellion_input=pop_signals["population_rebellion"] + era.rebellion_pressure * 0.1,
            faithfulness_input=pop_signals["population_faithfulness"] + era.covenant_boost * 0.1,
            divine_initiative=divine_engagement,
            atonement_event=atonement,
        )
        tick_events.extend(dist_events)

        # === Step Environment (SCC) ===
        env_events = self.environment.step(
            population_faithfulness=pop_signals["population_faithfulness"],
            covenant_strength=self.distance.state.covenant_strength + era.covenant_boost * 0.15,
            divine_engagement=divine_engagement,
        )
        tick_events.extend(env_events)

        # === Record History ===
        snapshot = {
            "tick": self.tick,
            "era": era.name,
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

    def _on_era_enter(self, era: Era) -> List[dict]:
        """Actions triggered when entering a new era."""
        events = []

        if era.name == "Fall":
            # The first rebellion — agents experience the pull
            for agent in self.population.agents:
                if agent.alive:
                    # Appetite and ego — the fruit was pleasing
                    agent.state.rebellion = min(1.0, agent.state.rebellion + 0.4)
                    agent.state.faith -= 0.3
                    agent.state.faith = max(0.0, agent.state.faith)
                    agent.state.delusion_level += 0.2

            # Environment shifts — corruption enters
            self.environment.realm.corruption_level = 0.15
            self.environment.realm.chaos_seepage = 0.1
            self.environment.realm.underworld_pressure = 0.1
            # CDT: humans hide first; God comes looking
            self.distance.state.active_distance = 0.2

        elif era.name == "Flood":
            # Cataclysmic reset — but curse remains (CDT)
            self.environment.realm.corruption_level *= 0.15
            self.environment.realm.underworld_pressure *= 0.2
            self.environment.realm.natural_vitality = 0.6
            self.environment.realm.chaos_seepage *= 0.2
            # Kill most agents, keep a remnant
            alive = [a for a in self.population.agents if a.alive]
            n_survive = max(8, int(len(alive) * 0.08))
            # Sort by faithfulness — the most faithful survive
            alive.sort(key=lambda a: a.state.faithfulness, reverse=True)
            for agent in alive[n_survive:]:
                agent.alive = False
            events.append({
                "tick": self.tick,
                "type": "cataclysmic_reset",
                "survivors": n_survive,
                "description": f"Flood reset — {n_survive} survive, curse remains",
                "parallel": "genesis_6-9"
            })

        elif era.name == "Abrahamic Calling":
            # God calls out a faithful people
            self.population.inject_faithful_remnant(10)
            events.append({
                "tick": self.tick,
                "type": "calling",
                "description": "God calls Abram — covenant people initiated",
                "parallel": "genesis_12"
            })

        elif era.name == "Egypt / Exodus":
            # Slavery conditions — corruption pressure on agents
            for agent in self.population.agents:
                if agent.alive:
                    agent.state.rebellion = min(1.0, agent.state.rebellion + 0.15)
                    agent.state.spiritual_vitality = max(0.1,
                        agent.state.spiritual_vitality - 0.1)

        elif era.name == "Sinai / Tabernacle":
            # Law given — exposes Anti-Way (CDT)
            # Tabernacle moment — God dwells among them
            events.append({
                "tick": self.tick,
                "type": "tabernacle_moment",
                "description": "God dwells among His people — tabernacle built",
                "parallel": "exodus_25-40"
            })

        elif era.name == "Divided Kingdom":
            # Covenant fractures — kingdom splits
            self.distance.state.covenant_strength *= 0.5
            for agent in self.population.agents:
                if agent.alive:
                    agent.state.rebellion = min(1.0, agent.state.rebellion + 0.25)
                    agent.state.faith = max(0.0, agent.state.faith - 0.15)
            events.append({
                "tick": self.tick,
                "type": "covenant_fracture",
                "description": "Kingdom divides — covenant fractures under rebellion",
                "parallel": "1_kings_12"
            })

        elif era.name == "Exile":
            # God's glory departs — the most devastating moment in covenant history
            self.distance.state.covenant_strength *= 0.2
            self.distance.state.divine_nearness *= 0.4
            self.distance.state.active_distance = min(1.0,
                self.distance.state.active_distance + 0.5)
            self.distance.state.curse_weight = min(1.0,
                self.distance.state.curse_weight + 0.3)
            # Environment devastated
            self.environment.realm.corruption_level = min(1.0,
                self.environment.realm.corruption_level + 0.4)
            self.environment.realm.heavenly_influence *= 0.4
            # Population shattered
            alive = [a for a in self.population.agents if a.alive]
            for agent in alive:
                agent.state.faith = max(0.0, agent.state.faith - 0.35)
                agent.state.rebellion = min(1.0, agent.state.rebellion + 0.3)
                agent.state.spiritual_vitality = max(0.1,
                    agent.state.spiritual_vitality - 0.2)
                agent.state.delusion_level = min(1.0, agent.state.delusion_level + 0.15)
            events.append({
                "tick": self.tick,
                "type": "exile",
                "description": "Glory departs — temple destroyed, people scattered",
                "parallel": "ezekiel_10"
            })

        elif era.name == "Incarnation":
            # God enters the cycle as human — the Second Adam
            self.engagement.state.presence_level = 0.95
            self.engagement.state.experiential_engagement = 1.0
            self.engagement.state.compassion = 1.0
            events.append({
                "tick": self.tick,
                "type": "incarnational_entry",
                "description": "The Word becomes flesh — God enters the cycle as participant",
                "parallel": "john_1"
            })

        elif era.name == "Cross / Resurrection":
            # Death within the cycle, rising out of it
            # CDT: the trap is sprung — curse borne, death conquered
            self.distance.state.active_distance *= 0.2
            self.distance.state.curse_weight *= 0.3
            self.distance.state.spiritual_vitality = min(1.0,
                self.distance.state.spiritual_vitality + 0.4)
            self.distance.state.blessing_flow = 0.9
            self.environment.cycle_tracker.cycle_broken = True
            # Agents receive the breakthrough
            for agent in self.population.agents:
                if agent.alive and agent.state.faith > 0.2:
                    agent.state.spiritual_vitality = min(1.0,
                        agent.state.spiritual_vitality + 0.3)
                    agent.state.delusion_level *= 0.5
                    agent.state.awareness = min(1.0, agent.state.awareness + 0.3)
            events.append({
                "tick": self.tick,
                "type": "cycle_breaking",
                "description": "Death and resurrection within the cycle — new creation inaugurated",
                "parallel": "passion_resurrection"
            })

        elif era.name == "Church Age":
            # Spirit indwelling — fullest descent of life force
            events.append({
                "tick": self.tick,
                "type": "spirit_indwelling",
                "description": "The Spirit indwells believers — fullest descent of the life force",
                "parallel": "acts_2"
            })

        return events

    def _apply_era_dynamics(self, era: Era) -> List[dict]:
        """Apply ongoing era-specific dynamics each tick."""
        events = []

        # Generational turnover
        if era.generational_turnover > 0 and self.tick % 30 == 0:
            self._generational_turnover(era.generational_turnover)

        # Era-specific corruption pressure on environment
        if era.corruption_pressure != 0:
            self.environment.realm.corruption_level = np.clip(
                self.environment.realm.corruption_level + era.corruption_pressure * 0.003,
                0.0, 1.0)

        # === Judges Cycle Sub-dynamics ===
        if era.name == "Judges Cycle":
            events.extend(self._judges_cycle_dynamics())

        return events

    def _judges_cycle_dynamics(self) -> List[dict]:
        """Model the judges cycle within its era.

        CDT: flourishing -> complacency -> rebellion -> crying out -> deliverance
        This should repeat 3-4 times within the Judges era.

        The key: these pressures must OVERWHELM the normal recovery rate,
        creating genuine oscillation rather than gentle drift.
        """
        events = []
        alive = [a for a in self.population.agents if a.alive]
        if not alive:
            return events

        avg_faith = sum(a.state.faith for a in alive) / len(alive)
        avg_rebellion = sum(a.state.rebellion for a in alive) / len(alive)

        if self._judges_phase == "flourishing":
            # Aggressive complacency — prosperity breeds forgetfulness FAST
            for agent in alive:
                agent.state.rebellion = min(1.0, agent.state.rebellion + 0.025)
                agent.state.faith = max(0.0, agent.state.faith - 0.02)
                agent.state.delusion_level = min(1.0, agent.state.delusion_level + 0.01)
            if avg_rebellion > 0.35 or avg_faith < 0.6:
                self._judges_phase = "complacency"
                events.append({
                    "tick": self.tick,
                    "type": "judges_phase",
                    "phase": "complacency",
                    "description": "Complacency sets in — the generation forgets",
                    "parallel": "judges_cycle"
                })

        elif self._judges_phase == "complacency":
            # Rebellion accelerates hard
            for agent in alive:
                agent.state.rebellion = min(1.0, agent.state.rebellion + 0.04)
                agent.state.faith = max(0.0, agent.state.faith - 0.03)
                agent.state.delusion_level = min(1.0, agent.state.delusion_level + 0.02)
            if avg_rebellion > 0.55:
                self._judges_phase = "rebellion"
                events.append({
                    "tick": self.tick,
                    "type": "judges_phase",
                    "phase": "rebellion",
                    "description": "Israel does evil in the eyes of the Lord",
                    "parallel": "judges_cycle"
                })

        elif self._judges_phase == "rebellion":
            # Oppression / crisis — everything degrades
            for agent in alive:
                agent.state.spiritual_vitality = max(0.0,
                    agent.state.spiritual_vitality - 0.03)
                agent.state.rebellion = min(1.0, agent.state.rebellion + 0.03)
                agent.state.faith = max(0.0, agent.state.faith - 0.03)
                agent.state.delusion_level = min(1.0, agent.state.delusion_level + 0.02)
            avg_vit = sum(a.state.spiritual_vitality for a in alive) / len(alive)
            if avg_rebellion > 0.6 or avg_vit < 0.4:
                self._judges_phase = "crying_out"
                events.append({
                    "tick": self.tick,
                    "type": "judges_phase",
                    "phase": "crying_out",
                    "description": "Israel cries out to the Lord in distress",
                    "parallel": "judges_cycle"
                })

        elif self._judges_phase == "crying_out":
            # God hears — rapid turning begins
            for agent in alive:
                if agent.traits.faith_capacity > 0.3:
                    agent.state.faith = min(1.0, agent.state.faith + 0.04)
                    agent.state.rebellion = max(0.0, agent.state.rebellion - 0.03)
            if avg_faith > 0.2 or avg_rebellion < 0.5:
                self._judges_phase = "deliverance"
                self._judges_sub_cycle += 1
                events.append({
                    "tick": self.tick,
                    "type": "judges_phase",
                    "phase": "deliverance",
                    "cycle": self._judges_sub_cycle,
                    "description": f"God raises a deliverer — judges cycle {self._judges_sub_cycle}",
                    "parallel": "judges_cycle"
                })
                # Dramatic deliverance
                for agent in alive:
                    agent.state.rebellion = max(0.0, agent.state.rebellion - 0.4)
                    agent.state.faith = min(1.0, agent.state.faith + 0.3)
                    agent.state.spiritual_vitality = min(1.0,
                        agent.state.spiritual_vitality + 0.2)
                    agent.state.delusion_level = max(0.0, agent.state.delusion_level - 0.25)

        elif self._judges_phase == "deliverance":
            # Brief flourishing before the cycle repeats
            if avg_faith > 0.45:
                self._judges_phase = "flourishing"

        return events

    def _generational_turnover(self, strength: float):
        """Model generational change: old agents die, new ones born.

        CDT: the next generation doesn't inherit the faith of the previous one.
        They must discover it anew — and many don't.
        """
        agents = self.population.agents
        alive = [a for a in agents if a.alive]
        if not alive:
            return

        rng = np.random.default_rng(self.tick)
        n_remove = max(1, int(len(alive) * strength * 0.25))
        # Remove oldest
        for agent in alive[:n_remove]:
            agent.alive = False

        # Birth new agents with low faith
        n_birth = n_remove
        for i in range(n_birth):
            new_id = len(agents) + i
            agent = Agent(new_id, rng)
            agent.state.faith = np.clip(rng.normal(0.15, 0.1), 0.02, 0.4)
            agent.state.rebellion = np.clip(rng.normal(0.4, 0.15), 0.1, 0.8)
            agent.state.delusion_level = np.clip(rng.normal(0.3, 0.1), 0.05, 0.6)
            agents.append(agent)

        self.population.size = len(agents)

    def _check_atonement_conditions(self, pop: dict, dist: dict,
                                     eng: dict, era: Era) -> bool:
        """Atonement emerges when conditions align within covenant eras."""
        # Atonement is meaningful only in covenant context
        covenant_eras = {"Sinai / Tabernacle", "Judges Cycle", "United Monarchy",
                        "Divided Kingdom", "Return / Second Temple"}
        if era.name not in covenant_eras:
            return False
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

        return {
            "total_ticks": self.tick,
            "total_events": len(self.all_events),
            "event_types": event_counts,
            "cycles_completed": final_env["cycle_count"],
            "cycle_broken": final_env["cycle_broken"],
            "judges_cycles": self._judges_sub_cycle,
            "final_era": self.eras[self.current_era_idx].name,
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
