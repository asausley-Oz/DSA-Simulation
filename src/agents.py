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
        self.indwelt = False  # Spirit-indwelt post-incarnation — enhanced entropy resistance

    def step(self, env_corruption: float, env_heavenly: float,
             divine_engagement: float, grace_space: float,
             covenant_health: float) -> None:
        """Update agent state for one tick based on environment."""
        if not self.alive:
            return

        s = self.state
        t = self.traits
        noise = self.rng.normal(0, 0.02)

        # === Spirit Indwelling ===
        # Post-incarnation, agents who respond in faith can be indwelt.
        # The Spirit doesn't remove the curse — it works THROUGH it.
        # Indwelt agents have enhanced resistance to entropy, not immunity.
        # The flesh still wars against the spirit. The curses still press.
        # But there is a power source that pre-incarnation agents lacked.
        spirit_factor = 1.4 if self.indwelt else 1.0

        # === Faith Dynamics ===
        # DSA: faith is native, real, and genuinely valued
        # Faith grows with divine engagement and awareness, shrinks with delusion
        # Spirit-indwelt agents have amplified faith growth
        faith_growth = (divine_engagement * 0.03 * t.faith_capacity * spirit_factor +
                       s.awareness * 0.02 +
                       covenant_health * 0.01)
        # Vamphoric Systems: THE FORK — attention split away from the source of life
        # The fork points toward something almost right, mistaken for the real thing
        vamphoric_fork = (env_corruption * 0.02 +
                         s.delusion_level * 0.03 +
                         s.rebellion * 0.02)
        s.faith = np.clip(s.faith + faith_growth - vamphoric_fork + noise * 0.5, 0.0, 1.0)

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
        rebellion_resist = (s.faith * 0.03 * spirit_factor +
                           t.resilience * 0.015 +
                           divine_engagement * 0.01 * spirit_factor)
        # Rebellion never fully vanishes — the flesh wars against the spirit
        # Even indwelt agents have a rebellion floor — the curse persists
        rebellion_floor = 0.03 + (1.0 - t.faith_capacity) * 0.05
        s.rebellion = np.clip(
            s.rebellion + rebellion_pull - rebellion_resist + noise * 0.3,
            rebellion_floor, 1.0)

        # === Spiritual Vitality ===
        # Anti-Life Delusion: spiritual death is an active, ongoing process
        # Vamphoric Systems: THE DRAIN — life extracted while appearing beneficial
        vitality_nourish = (env_heavenly * 0.02 +
                           s.faith * 0.03 * spirit_factor +
                           divine_engagement * 0.02 * spirit_factor)
        # The drain operates through corruption, rebellion, and delusion
        # It is built into the structure — not announced, not visible from within
        vamphoric_drain = (s.rebellion * 0.03 +
                          env_corruption * 0.025 +
                          s.delusion_level * 0.02)
        s.spiritual_vitality = np.clip(
            s.spiritual_vitality + vitality_nourish - vamphoric_drain, 0.0, 1.0)

        # === Delusion ===
        # Anti-Life Delusion: embraced by humanity, enticed from spiritual realm
        # Delusion keeps the drain running undetected — awareness is the precondition of turning
        delusion_growth = (env_corruption * 0.015 +
                          s.rebellion * 0.01 +
                          (1.0 - t.awareness_sensitivity) * 0.005)
        # Exposure breaks delusion — divine engagement is the greater glory
        # Spirit-indwelt agents have enhanced capacity to see through delusion
        delusion_shrink = (divine_engagement * 0.02 * spirit_factor +
                          s.faith * 0.015 * spirit_factor +
                          t.resilience * 0.005)

        # === Pharisee Hardening ===
        # "They saw the Light and chose the darkness" (John 3:19)
        # Agents exposed to high divine engagement who persist in
        # high rebellion HARDEN — exposure without response produces
        # not softening but calcification. The greater the light
        # rejected, the deeper the darkness. This is the Pharisee
        # dynamic: proximity to God's work + refusal = hardening.
        if divine_engagement > 0.5 and s.rebellion > 0.6 and s.faith < 0.3:
            # Exposure without response — delusion deepens, not breaks
            hardening = divine_engagement * s.rebellion * 0.02
            delusion_growth += hardening
            delusion_shrink *= 0.3  # exposure loses its power to break through

        s.delusion_level = np.clip(
            s.delusion_level + delusion_growth - delusion_shrink, 0.0, 1.0)

        # Awareness inversely tracks delusion
        # A person who clearly sees they are dying is halfway toward the gospel
        # Anti-Life Delusion: delusion can achieve COMPLETE blindness.
        # Awareness is the precondition of turning — without it,
        # repentance is not possible. This is the Pharisee condition:
        # "having eyes but not seeing" (Mark 8:18).
        s.awareness = np.clip(
            t.awareness_sensitivity * (1.0 - s.delusion_level * 0.95), 0.0, 1.0)

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
        self._initial_size = size  # baseline for density calculation

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
        remnant_fraction = sum(1 for a in alive if a.is_remnant) / n

        # === City Density ===
        # Density is a function of living population concentration.
        # As population grows/concentrates, density rises.
        # Density amplifies EVERYTHING — corruption spreads faster,
        # but so does gospel (post-resurrection). Cities never stop
        # being corrupting agents, but they also become harvest fields.
        #
        # Normalized: density approaches 1.0 as population fills capacity.
        # The initial population size is the baseline — growth beyond it
        # increases density, death below it decreases it.
        density = min(1.0, n / max(1, self._initial_size))

        return {
            "population_faithfulness": sum(a.state.faithfulness for a in alive) / n,
            "population_faith": sum(a.state.faith for a in alive) / n,
            "population_rebellion": sum(a.state.rebellion for a in alive) / n,
            "remnant_fraction": remnant_fraction,
            "avg_spiritual_vitality": sum(a.state.spiritual_vitality for a in alive) / n,
            "avg_delusion": sum(a.state.delusion_level for a in alive) / n,
            "avg_imaging": sum(a.state.imaging_quality for a in alive) / n,
            "avg_divine_labor": sum(a.state.divine_labor for a in alive) / n,
            "alive_count": n,
            "dead_count": self.size - n,
            "city_density": density,
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
            "city_density": 0.0,
        }

    def missionary_reproduce(self, city_density: float) -> int:
        """Remnant agents who are Spirit-indwelt reproduce — missionary function.

        This is the multiplication that the resurrection unlocks.
        Indwelt remnant agents in cities can convert non-remnant agents
        or spawn new believers. The rate scales with city density —
        the gospel spreads faster where people are concentrated.

        The curses don't lift. The corruption doesn't stop. But the
        multiplication works THROUGH the accumulated structural damage.

        Returns:
            Number of new converts this tick.
        """
        alive = [a for a in self.agents if a.alive]
        if not alive:
            return 0

        # Count indwelt missionaries (remnant + indwelt + high divine labor)
        missionaries = [a for a in alive
                       if a.indwelt and a.is_remnant and a.state.divine_labor > 0.3]
        if not missionaries:
            return 0

        # Conversion rate scales with density and missionary count
        # More missionaries in denser cities = faster gospel spread
        # But it's not automatic — each missionary has a probability
        missionary_fraction = len(missionaries) / len(alive)
        conversion_chance = missionary_fraction * city_density * 0.08

        converts = 0

        # First: try to convert existing non-remnant, non-indwelt agents
        # (the harvest — people already present in the cities)
        unconverted = [a for a in alive if not a.indwelt and not a.is_remnant]
        for agent in unconverted:
            # Agents with higher awareness are more reachable
            # Agents deep in delusion are harder to reach
            reachability = agent.state.awareness * (1.0 - agent.state.delusion_level * 0.5)
            if self.rng.random() < conversion_chance * reachability:
                # Convert: boost faith, mark as indwelt
                agent.state.faith = max(agent.state.faith,
                                       np.clip(self.rng.normal(0.55, 0.15), 0.35, 0.8))
                agent.state.faithfulness = max(agent.state.faithfulness,
                                              agent.state.faith * 0.5)
                agent.state.delusion_level *= 0.5  # scales broken, not erased
                agent.indwelt = True
                converts += 1

        # Second: if missionary density is high enough, spawn new agents
        # (the church planting function — new communities of faith)
        if missionary_fraction > 0.15 and city_density > 0.5:
            spawn_chance = missionary_fraction * city_density * 0.03
            if self.rng.random() < spawn_chance:
                agent_id = self.size
                traits = AgentTraits(
                    faith_capacity=np.clip(self.rng.normal(0.65, 0.15), 0.4, 0.9),
                    resilience=np.clip(self.rng.normal(0.6, 0.15), 0.3, 0.85),
                    awareness_sensitivity=np.clip(self.rng.normal(0.65, 0.15), 0.4, 0.9),
                    relational_capacity=np.clip(self.rng.normal(0.6, 0.15), 0.3, 0.85),
                )
                agent = Agent(agent_id, self.rng, traits)
                agent.state.faith = np.clip(self.rng.normal(0.5, 0.15), 0.3, 0.75)
                agent.state.faithfulness = agent.state.faith * 0.5
                agent.state.delusion_level = np.clip(self.rng.normal(0.1, 0.05), 0.0, 0.3)
                agent.indwelt = True
                agent.is_remnant = True
                self.agents.append(agent)
                self.size += 1
                converts += 1

        return converts

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
