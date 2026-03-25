"""
Environment Engine — SCC Three-Realm Dynamics

Models the cosmological environment from Shared Collective Cosmology (SCC):
- Heavenly influence: life force descending from above (purity, order, creative power)
- Underworld influence: chaos ascending from below (corruption, decay, entropy)
- Natural realm: the convergence zone where both forces meet

ENTROPY IS THE DOMINANT FORCE. Corruption accumulates relentlessly.
Only active resistance (covenant + divine engagement) slows it.
Faithfulness alone cannot stop it — this is the CDT insight.

Events emerge from entropy thresholds, not timelines.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class RealmState:
    """State of the three-realm cosmological environment at a given tick."""
    heavenly_influence: float = 1.0      # 0.0 = absent, 1.0 = full presence
    underworld_pressure: float = 0.0     # 0.0 = contained, 1.0 = overwhelming
    natural_vitality: float = 1.0        # health of the convergence zone
    corruption_level: float = 0.0        # accumulated corruption (entropy)
    life_force_flow: float = 1.0         # rate of life force descending from above
    chaos_seepage: float = 0.0           # rate of chaos ascending from below

    def convergence_tension(self) -> float:
        """The tension between heavenly and underworld forces in the natural realm."""
        return abs(self.heavenly_influence - self.underworld_pressure)

    def beauty_darkness_ratio(self) -> float:
        """SCC: the natural world contains both extraordinary beauty and profound darkness."""
        beauty = self.heavenly_influence * self.life_force_flow * self.natural_vitality
        darkness = self.underworld_pressure * self.chaos_seepage * (1 + self.corruption_level)
        total = beauty + darkness
        if total == 0:
            return 0.5
        return beauty / total


@dataclass
class CycleCurse:
    """A specific structural curse imposed by a cycle's failure.

    Each curse is permanent within this age. They compound across cycles.
    Not till Heaven and Earth pass away.
    """
    cycle_imposed: int              # which cycle's failure created this curse
    curse_type: str                 # category of structural damage
    description: str                # what happened
    entropy_penalty: float = 0.0    # added to base entropy rate (permanent)
    covenant_penalty: float = 0.0   # reduces covenant effectiveness (permanent)
    threshold_tightening: float = 0.0  # how much harder collapse becomes to avoid
    resistance_penalty: float = 0.0    # reduces effectiveness of resistance
    fragmentation: float = 0.0         # population unity penalty
    foreign_pressure: float = 0.0      # constant external oppression
    resolved: bool = False             # resolved at consummation


@dataclass
class CycleCurseRegistry:
    """Tracks ALL accumulated curses across every failed cycle.

    The end of each cycle is the worst generation because it carries
    the full weight of all prior failures. The curses are cumulative
    and permanent — they transform the structural conditions, not just
    the corruption level.

    Post-resurrection works THROUGH these curses, not by erasing them.
    """
    curses: List[CycleCurse] = field(default_factory=list)

    def impose_cycle_curse(self, cycle: int) -> CycleCurse:
        """Impose the appropriate structural curse for a cycle's failure.

        Each successive cycle failure imposes tighter boundaries:
        - Cycle 0 (pre-flood): wide boundaries, catastrophic failure → corruption floor
        - Cycle 1 (post-flood): fragmentation, nations scattered, covenant capacity reduced
        - Cycle 2 (covenant era): kingdom splits, covenant effectiveness halved
        - Cycle 3+: exile, occupation, foreign pressure, compounding severity
        """
        if cycle == 0:
            curse = CycleCurse(
                cycle_imposed=cycle,
                curse_type="corruption_floor",
                description="Catastrophic corruption — the ground is cursed",
                entropy_penalty=0.003,
                threshold_tightening=0.03,
                resistance_penalty=0.005,
            )
        elif cycle == 1:
            curse = CycleCurse(
                cycle_imposed=cycle,
                curse_type="fragmentation",
                description="Scattering and fragmentation — nations divided, tongues confused",
                entropy_penalty=0.004,
                covenant_penalty=0.08,
                threshold_tightening=0.05,
                resistance_penalty=0.008,
                fragmentation=0.15,
            )
        elif cycle == 2:
            curse = CycleCurse(
                cycle_imposed=cycle,
                curse_type="kingdom_split",
                description="Kingdom divided — covenant people torn apart, mission fractured",
                entropy_penalty=0.005,
                covenant_penalty=0.15,
                threshold_tightening=0.06,
                resistance_penalty=0.01,
                fragmentation=0.1,
            )
        else:
            # Cycle 3+: exile and occupation, severity escalates but slowly
            severity = min(cycle - 2, 3)  # caps at cycle 5
            curse = CycleCurse(
                cycle_imposed=cycle,
                curse_type="exile_and_occupation",
                description=f"Exile and foreign occupation (severity {severity}) — "
                            f"loss of land, temple, agency under foreign power",
                entropy_penalty=0.003 + severity * 0.001,
                covenant_penalty=0.06 + severity * 0.03,
                threshold_tightening=0.02 + severity * 0.01,
                resistance_penalty=0.005 + severity * 0.003,
                fragmentation=0.03 * severity,
                foreign_pressure=0.05 + severity * 0.025,
            )

        self.curses.append(curse)
        return curse

    @property
    def total_entropy_penalty(self) -> float:
        """Sum of all accumulated entropy penalties."""
        return sum(c.entropy_penalty for c in self.curses)

    @property
    def total_covenant_penalty(self) -> float:
        """Sum of all accumulated covenant effectiveness penalties."""
        return sum(c.covenant_penalty for c in self.curses)

    @property
    def total_threshold_tightening(self) -> float:
        """Sum of all threshold tightening — makes collapse easier each cycle."""
        return sum(c.threshold_tightening for c in self.curses)

    @property
    def total_resistance_penalty(self) -> float:
        """Sum of all resistance effectiveness penalties."""
        return sum(c.resistance_penalty for c in self.curses)

    @property
    def total_fragmentation(self) -> float:
        """Total fragmentation — reduces population unity and covenant capacity."""
        return min(0.8, sum(c.fragmentation for c in self.curses))

    @property
    def total_foreign_pressure(self) -> float:
        """Total foreign pressure — constant external oppression."""
        return min(0.6, sum(c.foreign_pressure for c in self.curses))

    @property
    def curse_count(self) -> int:
        return len(self.curses)

    def has_curse_type(self, curse_type: str) -> bool:
        return any(c.curse_type == curse_type for c in self.curses)

    def get_summary(self) -> dict:
        return {
            "curse_count": self.curse_count,
            "curse_types": [c.curse_type for c in self.curses],
            "total_entropy_penalty": round(self.total_entropy_penalty, 4),
            "total_covenant_penalty": round(self.total_covenant_penalty, 4),
            "total_threshold_tightening": round(self.total_threshold_tightening, 4),
            "total_resistance_penalty": round(self.total_resistance_penalty, 4),
            "total_fragmentation": round(self.total_fragmentation, 4),
            "total_foreign_pressure": round(self.total_foreign_pressure, 4),
        }


@dataclass
class CycleTracker:
    """Tracks the cyclical patterns SCC identifies across all traditions.

    SCC: 'The systems are circular and cyclical. They do not resolve.
    They repeat. They spiral without terminus.'

    Each cycle's failure compounds — tighter failure boundaries, structural
    curses that persist permanently. The end of every cycle is the worst
    generation because it carries the full weight of all prior failures.
    """
    phase_history: List[str] = field(default_factory=list)
    cycle_count: int = 0
    current_phase: str = "creation"
    cycle_broken: bool = False
    curse_registry: CycleCurseRegistry = field(default_factory=CycleCurseRegistry)
    _phase_entered_tick: int = 0    # when we entered the current phase
    _tick: int = 0                  # current tick (updated each call)

    # Base thresholds — these get tightened by accumulated curses
    _BASE_FLOURISHING: float = 0.65
    _BASE_DECLINE: float = 0.45
    _BASE_COLLAPSE: float = 0.2
    _BASE_RESET: float = 0.1

    @property
    def FLOURISHING_THRESHOLD(self) -> float:
        """Flourishing gets harder to reach with accumulated curses."""
        return min(0.9, self._BASE_FLOURISHING + self.curse_registry.total_threshold_tightening)

    @property
    def DECLINE_THRESHOLD(self) -> float:
        """Decline triggers earlier with accumulated curses."""
        tightening = self.curse_registry.total_threshold_tightening
        return min(0.7, self._BASE_DECLINE + tightening * 0.8)

    @property
    def COLLAPSE_THRESHOLD(self) -> float:
        """Collapse triggers earlier with accumulated curses."""
        tightening = self.curse_registry.total_threshold_tightening
        return min(0.4, self._BASE_COLLAPSE + tightening * 0.5)

    @property
    def RESET_THRESHOLD(self) -> float:
        """Reset triggers earlier with accumulated curses."""
        tightening = self.curse_registry.total_threshold_tightening
        return min(0.25, self._BASE_RESET + tightening * 0.3)

    def update(self, realm: RealmState, covenant_health: float, tick: int = 0) -> Optional[str]:
        """Evaluate whether a phase transition has occurred."""
        self._tick = tick
        combined_health = (realm.natural_vitality + covenant_health) / 2.0
        old_phase = self.current_phase
        ticks_in_phase = tick - self._phase_entered_tick

        # Grace period scales — God's forbearance gives each cycle time to play out
        # Later cycles get shorter windows but never instant
        creation_grace = max(80, 150 - self.cycle_count * 15)
        decline_grace = max(40, 80 - self.cycle_count * 8)

        if self.current_phase == "creation":
            if combined_health >= self.FLOURISHING_THRESHOLD:
                self.current_phase = "flourishing"
            elif combined_health < self.DECLINE_THRESHOLD and ticks_in_phase >= creation_grace:
                # A cursed creation that never reaches flourishing can still decline.
                # Later cycles may never flourish — the curses prevent it.
                # But there's always a grace period — a window of possibility
                # before the accumulated curses take hold.
                self.current_phase = "decline"
        elif self.current_phase == "flourishing":
            if combined_health < self.DECLINE_THRESHOLD:
                self.current_phase = "decline"
        elif self.current_phase == "decline":
            if combined_health < self.COLLAPSE_THRESHOLD and ticks_in_phase >= decline_grace:
                self.current_phase = "collapse"
            elif combined_health >= self.FLOURISHING_THRESHOLD:
                self.current_phase = "flourishing"
        elif self.current_phase == "collapse":
            if combined_health < self.RESET_THRESHOLD:
                self.current_phase = "reset"
            elif combined_health >= self.DECLINE_THRESHOLD:
                self.current_phase = "decline"
        elif self.current_phase == "reset":
            # Impose curse for this cycle's failure BEFORE incrementing
            self.curse_registry.impose_cycle_curse(self.cycle_count)
            self.cycle_count += 1
            self.current_phase = "creation"

        if self.current_phase != old_phase:
            self._phase_entered_tick = tick
            self.phase_history.append(self.current_phase)
            return self.current_phase
        return None


class Environment:
    """The cosmological environment engine.

    CORE PRINCIPLE: Entropy is relentless.

    Without active divine engagement + covenant, corruption wins.
    Faithfulness slows it. Covenant slows it more. Divine engagement
    can reverse it. But nothing human stops it permanently.

    This is the CDT insight: the cycle cannot be broken from within
    by human effort. Only God entering the cycle breaks it.
    """

    def __init__(self, seed: Optional[int] = None):
        self.realm = RealmState()
        self.cycle_tracker = CycleTracker()
        self.tick = 0
        self.rng = np.random.default_rng(seed)
        self.event_log: List[dict] = []
        self._last_event_ticks: dict = {}
        self._flood_occurred = False  # the flood is singular — only one ever

        # === Entropy Parameters ===
        # These control the fundamental rate of decay
        self.entropy_base_rate = 0.015       # corruption accumulates every tick
        self.chaos_base_rate = 0.04          # chaos always presses upward
        self.corruption_feedback = 0.15      # corruption accelerates itself (Vamphoric)
        self.life_force_base = 1.0

    def step(self, population_faithfulness: float = 0.5,
             covenant_strength: float = 0.5,
             divine_engagement: float = 0.5,
             city_density: float = 0.5) -> List[dict]:
        """Advance the environment by one tick."""
        self.tick += 1
        events = []

        # === Life Force Flow ===
        # SCC: life originates from highest heaven, descends into natural order.
        # Without covenant and divine engagement, the channel narrows.
        # Faithfulness helps but cannot sustain the channel alone.
        channel_openness = (population_faithfulness * 0.3 +
                           covenant_strength * 0.35 +
                           divine_engagement * 0.35)
        self.realm.life_force_flow = self.life_force_base * channel_openness

        # Heavenly influence tracks life force with inertia
        target_heavenly = min(1.0, self.realm.life_force_flow * 0.7 + divine_engagement * 0.3)
        self.realm.heavenly_influence += (target_heavenly - self.realm.heavenly_influence) * 0.08

        # === Curse Registry (used in multiple sections below) ===
        curses = self.cycle_tracker.curse_registry

        # === Chaos Seepage ===
        # Underworld pressure exploits ANY gap in heavenly coverage
        heavenly_shield = self.realm.heavenly_influence * max(covenant_strength, 0.1)
        chaos_opportunity = max(0, 1.0 - heavenly_shield)
        chaos_rate = (self.chaos_base_rate +
                      chaos_opportunity * 0.12 +
                      self.realm.corruption_level * 0.08)

        # === Firmament Effect ===
        # In pristine creation, the firmament — the boundary between
        # realms — is intact. Chaos seepage is dampened because the
        # structural separation holds. After the first cycle failure,
        # the firmament is permanently compromised. The waters above
        # and below are no longer fully separated.
        if curses.curse_count == 0:
            chaos_rate *= 0.15

        self.realm.chaos_seepage = chaos_rate

        # Underworld pressure builds — it ratchets up, slow to retreat
        self.realm.underworld_pressure = min(1.0,
            self.realm.underworld_pressure * 0.97 + self.realm.chaos_seepage * 0.12)

        # === ENTROPY: Corruption Accumulation ===
        # This is the heart of the system.
        # Corruption ALWAYS accumulates. The question is how fast.
        #
        # Inputs that INCREASE corruption:
        #   - Base entropy rate (always present — the curse)
        #   - Accumulated cycle curses (each failed cycle adds permanent penalty)
        #   - Chaos seepage (underworld pressing up)
        #   - Unfaithfulness (rebellion feeds the system)
        #   - Corruption itself (Vamphoric: the system feeds on itself)
        #   - Foreign pressure (occupation from accumulated curses)
        #   - City density (cities ALWAYS amplify corruption — Cain's line,
        #     Babel, Sodom. Concentration of humanity without covenant
        #     is concentration of corruption. This never stops.)
        #
        # Inputs that RESIST corruption:
        #   - Divine engagement (the only force that can truly reverse it)
        #   - Covenant strength (creates structure for resistance)
        #   - Faithfulness (slows but cannot stop)
        #   - BUT resistance effectiveness is reduced by accumulated curses

        # City density amplifies corruption feedback — the vamphoric
        # systems scale with density. More people, faster corruption spread.
        density_amplifier = 1.0 + city_density * 0.3

        entropy_input = (self.entropy_base_rate +
                        curses.total_entropy_penalty +     # permanent curse penalty
                        curses.total_foreign_pressure * 0.02 +  # occupation pressure
                        self.realm.chaos_seepage * 0.15 +
                        (1.0 - population_faithfulness) * 0.1 +
                        self.realm.corruption_level * self.corruption_feedback * density_amplifier)

        # === Firmament Effect on Entropy ===
        # Before any cycle has failed, the firmament holds — the
        # "very good" creation has inherent resistance to entropy.
        # The ground is not yet cursed. The natural order pushes back
        # through structural integrity, not covenant. After the first
        # failure, this resilience is permanently lost.
        # "Cursed is the ground because of you."
        #
        # The firmament dampens BOTH the base entropy rate AND the
        # corruption feedback loop. In pristine creation, corruption
        # doesn't self-amplify as aggressively — the vamphoric systems
        # haven't fully formed yet. They emerge as creation degrades.
        if curses.curse_count == 0:
            firmament_strength = self.realm.natural_vitality
            # Scale down the total entropy input
            firmament_dampening = max(0.08, 1.0 - 0.8 * firmament_strength)
            entropy_input *= firmament_dampening

        # ONLY covenant + divine engagement TOGETHER resist entropy
        # Presence alone is not protective — DSA: space as grace
        # Faithfulness slows but cannot stop
        # CDT insight: even with covenant, entropy is only SLOWED, never stopped
        # The cycle cannot be broken by human effort or covenant mechanics alone
        #
        # Accumulated curses reduce resistance effectiveness —
        # the structural damage from prior failures constrains capacity
        combined_resistance = divine_engagement * covenant_strength
        resistance_factor = max(0.3, 1.0 - curses.total_resistance_penalty)
        entropy_resistance = (combined_resistance * 0.06 * resistance_factor +
                             population_faithfulness * 0.015 * resistance_factor)

        net_entropy = entropy_input - entropy_resistance

        # === Firmament Effect on Conversion Rate ===
        # In pristine creation, corruption converts from entropy more
        # slowly. The firmament absorbs entropy pressure — the structure
        # holds. The Sethite line ("they began to call on the name of
        # the LORD" — Gen 4:26) provides pre-covenant resistance.
        # Not covenant, not engagement, but worship — a proto-faithfulness
        # that slows the conversion. This gives the pre-flood world
        # its long runway: 10 generations of 900-year lifespans.
        # After the first failure, the firmament shatters and corruption
        # converts at full rate.
        if curses.curse_count == 0:
            conversion_rate = 0.01  # firmament absorbs most entropy pressure
            # As vitality drops, the firmament weakens — corruption
            # converts faster as creation degrades
            conversion_rate += (1.0 - self.realm.natural_vitality) * 0.02
        else:
            conversion_rate = 0.05  # post-curse: full conversion rate

        # CDT: pre-incarnation, entropy is only SLOWED, never stopped.
        # Even maximum covenant + divine engagement cannot reverse
        # the fundamental entropy of the cursed order. Only the
        # cycle-breaker (incarnation) can achieve true reversal.
        if not self.cycle_tracker.cycle_broken:
            net_entropy = max(0.001, net_entropy)
        self.realm.corruption_level = np.clip(
            self.realm.corruption_level + net_entropy * conversion_rate, 0.0, 1.0)

        # === Natural Vitality ===
        vitality_support = (self.realm.life_force_flow * 0.35 +
                           self.realm.heavenly_influence * 0.25 +
                           population_faithfulness * 0.15 +
                           divine_engagement * 0.15 +
                           0.1)  # base resilience of creation
        vitality_drain = (self.realm.corruption_level * 0.35 +
                         self.realm.underworld_pressure * 0.2 +
                         self.realm.chaos_seepage * 0.1)
        target_vitality = np.clip(vitality_support - vitality_drain, 0.0, 1.0)
        self.realm.natural_vitality += (target_vitality - self.realm.natural_vitality) * 0.06

        # Small random perturbation
        noise = self.rng.normal(0, 0.008)
        self.realm.natural_vitality = np.clip(
            self.realm.natural_vitality + noise, 0.0, 1.0)

        # === Emergent Event Detection ===
        events.extend(self._detect_events(population_faithfulness, covenant_strength,
                                          divine_engagement))

        # === Cycle Tracking ===
        phase_change = self.cycle_tracker.update(self.realm, covenant_strength, self.tick)
        if phase_change:
            events.append({
                "tick": self.tick,
                "type": "phase_transition",
                "phase": phase_change,
                "cycle": self.cycle_tracker.cycle_count,
                "description": f"Entered {phase_change} phase (cycle {self.cycle_tracker.cycle_count})"
            })

        self.event_log.extend(events)
        return events

    def _cooldown_ok(self, event_type: str, min_gap: int = 30) -> bool:
        last = self._last_event_ticks.get(event_type, -min_gap - 1)
        return self.tick - last >= min_gap

    def _record_event(self, event_type: str):
        self._last_event_ticks[event_type] = self.tick

    def _detect_events(self, faithfulness: float, covenant: float,
                       divine_engagement: float) -> List[dict]:
        """Detect emergent events purely from entropy thresholds.

        NO TIMELINES. Events fire when conditions are met.
        """
        events = []
        r = self.realm

        # --- Cataclysmic Reset (Flood Pattern) ---
        # The flood is SINGULAR — one catastrophic global reset in all of history.
        # After the flood, subsequent collapses manifest as exile, occupation,
        # judgment — but never another global wipe. God promised.
        if (not self._flood_occurred and
                r.corruption_level > 0.85 and
                r.natural_vitality < 0.2 and
                r.underworld_pressure > 0.7):
            self._flood_occurred = True
            self._record_event("cataclysmic_reset")
            events.append({
                "tick": self.tick,
                "type": "cataclysmic_reset",
                "severity": r.corruption_level,
                "cycle": self.cycle_tracker.cycle_count,
                "description": "Entropy overwhelms — the flood. Once. Never again.",
                "parallel": "flood_pattern"
            })
            # Reset environment — but the curse remains
            r.corruption_level = 0.05
            r.underworld_pressure *= 0.2
            r.natural_vitality = 0.7
            r.chaos_seepage *= 0.15
            r.heavenly_influence = min(1.0, r.heavenly_influence + 0.4)

        # --- Scattering (Babel Pattern) ---
        # Collective ambition without covenant in a still-viable world
        if (faithfulness < 0.2 and covenant < 0.15 and
                r.natural_vitality > 0.5 and r.corruption_level > 0.4 and
                self._cooldown_ok("scattering", 80)):
            self._record_event("scattering")
            events.append({
                "tick": self.tick,
                "type": "scattering",
                "description": "Collective ambition without covenant — scattering",
                "parallel": "babel_pattern"
            })

        # --- Kingdom Split (Covenant Fracture Under Accumulated Curse) ---
        # When covenant is weakened and fragmentation curses are active,
        # the unified covenant people split — mission capacity halved
        curses = self.cycle_tracker.curse_registry
        if (curses.total_fragmentation > 0.1 and
                covenant > 0.15 and covenant < 0.4 and
                r.corruption_level > 0.45 and
                faithfulness < 0.35 and
                self._cooldown_ok("kingdom_split", 80)):
            self._record_event("kingdom_split")
            events.append({
                "tick": self.tick,
                "type": "kingdom_split",
                "severity": curses.total_fragmentation,
                "accumulated_curses": curses.curse_count,
                "description": ("Covenant people divide — kingdom splits under weight "
                                f"of {curses.curse_count} accumulated curses"),
                "parallel": "divided_kingdom_pattern"
            })

        # --- Exile (Covenant Collapse Pattern) ---
        # When covenant breaks down completely
        if (covenant < 0.15 and r.corruption_level > 0.6 and
                r.heavenly_influence < 0.35 and
                self._cooldown_ok("exile", 60)):
            self._record_event("exile")
            events.append({
                "tick": self.tick,
                "type": "exile",
                "severity": 1.0 - covenant,
                "accumulated_curses": curses.curse_count,
                "description": (f"Covenant collapse — exile conditions manifest "
                                f"(bearing {curses.curse_count} accumulated curses)"),
                "parallel": "exile_pattern"
            })

        # --- Foreign Occupation (Accumulated Curse Pressure) ---
        # When foreign_pressure curses are active, occupation constrains agency
        # This is the structural consequence of accumulated exile curses
        if (curses.total_foreign_pressure > 0.05 and
                r.corruption_level > 0.35 and
                covenant < 0.5 and
                self._cooldown_ok("occupation", 60)):
            self._record_event("occupation")
            events.append({
                "tick": self.tick,
                "type": "occupation",
                "pressure": curses.total_foreign_pressure,
                "accumulated_curses": curses.curse_count,
                "description": (f"Foreign occupation constrains covenant people — "
                                f"agency reduced under {curses.total_foreign_pressure:.0%} "
                                f"structural pressure from accumulated curses"),
                "parallel": "occupation_pattern"
            })

        # --- Tabernacle Moment ---
        # Heaven and earth converge — requires high engagement + faithfulness
        if (r.heavenly_influence > 0.75 and faithfulness > 0.6 and
                covenant > 0.5 and r.convergence_tension() > 0.4 and
                self._cooldown_ok("tabernacle_moment", 50)):
            self._record_event("tabernacle_moment")
            events.append({
                "tick": self.tick,
                "type": "tabernacle_moment",
                "intensity": r.heavenly_influence * faithfulness,
                "description": "Heaven and earth converge — tabernacle moment",
                "parallel": "tabernacle_pattern"
            })

        # --- Remnant Emergence ---
        # Faithful minority persists amid corruption
        if (r.corruption_level > 0.5 and faithfulness > 0.25 and
                r.underworld_pressure > 0.4 and
                self._cooldown_ok("remnant_emergence", 40)):
            self._record_event("remnant_emergence")
            events.append({
                "tick": self.tick,
                "type": "remnant_emergence",
                "description": "Faithful remnant persists amid entropy",
                "parallel": "remnant_pattern"
            })

        # --- Divine Incursion ---
        # God choosing to enter and engage in a particular moment
        if (r.heavenly_influence > 0.8 and r.life_force_flow > 0.7 and
                divine_engagement > 0.7 and
                self._cooldown_ok("divine_incursion", 50)):
            self._record_event("divine_incursion")
            events.append({
                "tick": self.tick,
                "type": "divine_incursion",
                "intensity": r.heavenly_influence,
                "description": "Sovereign divine engagement — God enters the moment",
                "parallel": "theophany_pattern"
            })

        # --- Cycle Breaking (Incarnation Pattern) ---
        # Now handled by the temple mechanic in the simulation orchestrator.
        # The temple builds as heaven-earth convergence, and when it reaches
        # threshold, incarnation fires. God doesn't just visit the temple —
        # God becomes the temple.

        return events

    def get_state_snapshot(self) -> dict:
        """Return a complete snapshot of current environmental state."""
        curses = self.cycle_tracker.curse_registry
        return {
            "tick": self.tick,
            "heavenly_influence": round(self.realm.heavenly_influence, 4),
            "underworld_pressure": round(self.realm.underworld_pressure, 4),
            "natural_vitality": round(self.realm.natural_vitality, 4),
            "corruption_level": round(self.realm.corruption_level, 4),
            "life_force_flow": round(self.realm.life_force_flow, 4),
            "chaos_seepage": round(self.realm.chaos_seepage, 4),
            "beauty_darkness_ratio": round(self.realm.beauty_darkness_ratio(), 4),
            "convergence_tension": round(self.realm.convergence_tension(), 4),
            "cycle_phase": self.cycle_tracker.current_phase,
            "cycle_count": self.cycle_tracker.cycle_count,
            "cycle_broken": self.cycle_tracker.cycle_broken,
            "accumulated_curses": curses.curse_count,
            "curse_entropy_penalty": round(curses.total_entropy_penalty, 4),
            "curse_covenant_penalty": round(curses.total_covenant_penalty, 4),
            "curse_fragmentation": round(curses.total_fragmentation, 4),
            "curse_foreign_pressure": round(curses.total_foreign_pressure, 4),
        }
