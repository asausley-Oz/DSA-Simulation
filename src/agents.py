"""
Agent System — Genuine Human Agency

Models individual humans as agents with:
- Genuine agency (DSA: not instruments but sovereign creatures)
- Faith as native and real (DSA: not pre-installed by God)
- Spiritual formation trajectory (CDT: born alive, dying through rebellion)
- Imaging vocation (CDT: reflecting God's character into the world)
- Susceptibility to delusion (CDT: awareness of condition can be lost)
- Capacity for divine labor (CDT: walking with God in the moment)

Agents interact with the environment and produce aggregate signals
that drive the simulation's dynamics.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class AgentTraits:
    """Innate traits of a human agent — set at creation, mostly stable."""
    faith_capacity: float = 0.5       # natural capacity for faith (DSA: native, not given)
    resilience: float = 0.5           # resistance to corruption and delusion
    awareness_sensitivity: float = 0.5  # how easily they perceive spiritual reality
    relational_capacity: float = 0.5  # capacity for covenant relationship


@dataclass
class AgentState:
    """Dynamic state of a human agent — changes each tick."""
    faith: float = 0.3                # current active faith level
    faithfulness: float = 0.3         # consistency of faithful behavior
    rebellion: float = 0.1            # current rebellion activity
    spiritual_vitality: float = 0.8   # spiritual aliveness
    delusion_level: float = 0.1       # how deluded this agent is
    awareness: float = 0.7            # awareness of spiritual condition
    imaging_quality: float = 0.3      # how well they image God into the world
    divine_labor: float = 0.0         # participation in God's work


class Agent:
    """A single human agent in the simulation."""

    def __init__(self, agent_id: int, rng: np.random.Generator,
                 traits: Optional[AgentTraits] = None):
        self.id = agent_id
        self.rng = rng

        if traits is None:
            # Generate traits with natural variation
            self.traits = AgentTraits(
                faith_capacity=np.clip(rng.normal(0.5, 0.2), 0.05, 0.95),
                resilience=np.clip(rng.normal(0.5, 0.15), 0.1, 0.9),
                awareness_sensitivity=np.clip(rng.normal(0.5, 0.2), 0.05, 0.95),
                relational_capacity=np.clip(rng.normal(0.5, 0.15), 0.1, 0.9),
            )
        else:
            self.traits = traits

        self.state = AgentState(
            faith=self.traits.faith_capacity * 0.3,
            faithfulness=self.traits.faith_capacity * 0.2,
            rebellion=np.clip(rng.normal(0.3, 0.15), 0.05, 0.7),
            spiritual_vitality=np.clip(rng.normal(0.7, 0.15), 0.3, 1.0),
            awareness=self.traits.awareness_sensitivity * 0.6,
        )
        self.is_remnant = False
        self.alive = True

    def step(self, env_corruption: float, env_heavenly: float,
             divine_engagement: float, grace_space: float,
             covenant_health: float) -> None:
        """Update agent state for one tick based on environment."""
        if not self.alive:
            return

        s = self.state
        t = self.traits
        noise = self.rng.normal(0, 0.02)

        # === Faith Dynamics ===
        # DSA: faith is native, real, and genuinely valued
        # Faith grows with divine engagement and awareness, shrinks with delusion
        faith_growth = (divine_engagement * 0.03 * t.faith_capacity +
                       s.awareness * 0.02 +
                       covenant_health * 0.01)
        faith_decay = (env_corruption * 0.02 +
                      s.delusion_level * 0.03 +
                      s.rebellion * 0.02)
        s.faith = np.clip(s.faith + faith_growth - faith_decay + noise * 0.5, 0.0, 1.0)

        # === Faithfulness ===
        # Tracks faith with behavioral lag
        target_faithfulness = s.faith * 0.7 + t.relational_capacity * 0.3
        s.faithfulness += (target_faithfulness - s.faithfulness) * 0.05
        s.faithfulness = np.clip(s.faithfulness, 0.0, 1.0)

        # === Rebellion ===
        # Rebellion is the anti-faith: driven by delusion and corruption
        # CDT: rebellion is the natural gravity — it takes effort to resist
        rebellion_pull = (env_corruption * 0.05 +
                         s.delusion_level * 0.06 +
                         (1.0 - s.awareness) * 0.04 +
                         0.01)  # base rebellion pressure — the gravity of the curse
        rebellion_resist = (s.faith * 0.03 +
                           t.resilience * 0.015 +
                           divine_engagement * 0.01)
        # Rebellion never fully vanishes — the flesh wars against the spirit
        rebellion_floor = 0.03 + (1.0 - t.faith_capacity) * 0.05
        s.rebellion = np.clip(
            s.rebellion + rebellion_pull - rebellion_resist + noise * 0.3,
            rebellion_floor, 1.0)

        # === Spiritual Vitality ===
        # CDT: born alive, dying through rebellion — a process
        vitality_nourish = (env_heavenly * 0.02 +
                           s.faith * 0.03 +
                           divine_engagement * 0.02)
        vitality_drain = (s.rebellion * 0.03 +
                         env_corruption * 0.02 +
                         s.delusion_level * 0.02)
        s.spiritual_vitality = np.clip(
            s.spiritual_vitality + vitality_nourish - vitality_drain, 0.0, 1.0)

        # === Delusion ===
        # CDT: embraced by humanity, enticed from spiritual realm
        delusion_growth = (env_corruption * 0.015 +
                          s.rebellion * 0.01 +
                          (1.0 - t.awareness_sensitivity) * 0.005)
        delusion_shrink = (divine_engagement * 0.02 +
                          s.faith * 0.015 +
                          t.resilience * 0.005)
        s.delusion_level = np.clip(
            s.delusion_level + delusion_growth - delusion_shrink, 0.0, 1.0)

        # Awareness inversely tracks delusion
        s.awareness = np.clip(
            t.awareness_sensitivity * (1.0 - s.delusion_level * 0.8), 0.05, 1.0)

        # === Imaging ===
        # CDT: reflecting God's character into the world — identity as mission
        s.imaging_quality = (s.faith * 0.3 +
                            s.faithfulness * 0.3 +
                            s.spiritual_vitality * 0.2 +
                            divine_engagement * 0.2) * (1.0 - s.rebellion * 0.5)

        # === Divine Labor ===
        # CDT: walking with God in the moment, doing what you see the Father doing
        if s.faith > 0.5 and s.faithfulness > 0.4 and divine_engagement > 0.4:
            s.divine_labor = (s.faith * 0.3 + s.faithfulness * 0.3 +
                             divine_engagement * 0.4) * grace_space
        else:
            s.divine_labor = max(0, s.divine_labor - 0.02)

        # === Remnant Status ===
        # CDT: the faithful minority — defined by faith and responsiveness
        self.is_remnant = (s.faith > 0.5 and s.faithfulness > 0.4 and
                          s.spiritual_vitality > 0.4)

        # === Death Check ===
        if s.spiritual_vitality < 0.01 and s.faith < 0.05:
            self.alive = False  # spiritual death complete


class Population:
    """Manages a population of agents and computes aggregate signals."""

    def __init__(self, size: int = 100, seed: Optional[int] = None):
        self.rng = np.random.default_rng(seed)
        self.agents: List[Agent] = [
            Agent(i, self.rng) for i in range(size)
        ]
        self.size = size

    def step(self, env_corruption: float, env_heavenly: float,
             divine_engagement: float, grace_space: float,
             covenant_health: float) -> dict:
        """Step all agents and return aggregate signals."""
        for agent in self.agents:
            agent.step(env_corruption, env_heavenly, divine_engagement,
                      grace_space, covenant_health)

        alive = [a for a in self.agents if a.alive]
        if not alive:
            return self._empty_signals()

        n = len(alive)
        return {
            "population_faithfulness": sum(a.state.faithfulness for a in alive) / n,
            "population_faith": sum(a.state.faith for a in alive) / n,
            "population_rebellion": sum(a.state.rebellion for a in alive) / n,
            "remnant_fraction": sum(1 for a in alive if a.is_remnant) / n,
            "avg_spiritual_vitality": sum(a.state.spiritual_vitality for a in alive) / n,
            "avg_delusion": sum(a.state.delusion_level for a in alive) / n,
            "avg_imaging": sum(a.state.imaging_quality for a in alive) / n,
            "avg_divine_labor": sum(a.state.divine_labor for a in alive) / n,
            "alive_count": n,
            "dead_count": self.size - n,
        }

    def _empty_signals(self) -> dict:
        return {
            "population_faithfulness": 0.0,
            "population_faith": 0.0,
            "population_rebellion": 1.0,
            "remnant_fraction": 0.0,
            "avg_spiritual_vitality": 0.0,
            "avg_delusion": 1.0,
            "avg_imaging": 0.0,
            "avg_divine_labor": 0.0,
            "alive_count": 0,
            "dead_count": self.size,
        }

    def inject_faithful_remnant(self, count: int = 5):
        """Introduce highly faithful agents — represents God calling out a people."""
        for i in range(count):
            agent_id = self.size + i
            traits = AgentTraits(
                faith_capacity=np.clip(self.rng.normal(0.8, 0.1), 0.6, 0.95),
                resilience=np.clip(self.rng.normal(0.7, 0.1), 0.5, 0.9),
                awareness_sensitivity=np.clip(self.rng.normal(0.8, 0.1), 0.6, 0.95),
                relational_capacity=np.clip(self.rng.normal(0.7, 0.1), 0.5, 0.9),
            )
            agent = Agent(agent_id, self.rng, traits)
            agent.state.faith = 0.7
            agent.state.faithfulness = 0.6
            agent.is_remnant = True
            self.agents.append(agent)
        self.size += count
