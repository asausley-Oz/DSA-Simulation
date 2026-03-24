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
class CycleTracker:
    """Tracks the cyclical patterns SCC identifies across all traditions.

    SCC: 'The systems are circular and cyclical. They do not resolve.
    They repeat. They spiral without terminus.'
    """
    phase_history: List[str] = field(default_factory=list)
    cycle_count: int = 0
    current_phase: str = "creation"
    cycle_broken: bool = False

    FLOURISHING_THRESHOLD: float = 0.65
    DECLINE_THRESHOLD: float = 0.45
    COLLAPSE_THRESHOLD: float = 0.2
    RESET_THRESHOLD: float = 0.1

    def update(self, realm: RealmState, covenant_health: float) -> Optional[str]:
        """Evaluate whether a phase transition has occurred."""
        combined_health = (realm.natural_vitality + covenant_health) / 2.0
        old_phase = self.current_phase

        if self.current_phase == "creation":
            if combined_health >= self.FLOURISHING_THRESHOLD:
                self.current_phase = "flourishing"
        elif self.current_phase == "flourishing":
            if combined_health < self.DECLINE_THRESHOLD:
                self.current_phase = "decline"
        elif self.current_phase == "decline":
            if combined_health < self.COLLAPSE_THRESHOLD:
                self.current_phase = "collapse"
            elif combined_health >= self.FLOURISHING_THRESHOLD:
                self.current_phase = "flourishing"
        elif self.current_phase == "collapse":
            if combined_health < self.RESET_THRESHOLD:
                self.current_phase = "reset"
            elif combined_health >= self.DECLINE_THRESHOLD:
                self.current_phase = "decline"
        elif self.current_phase == "reset":
            self.cycle_count += 1
            self.current_phase = "creation"

        if self.current_phase != old_phase:
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

        # === Entropy Parameters ===
        # These control the fundamental rate of decay
        self.entropy_base_rate = 0.015       # corruption accumulates every tick
        self.chaos_base_rate = 0.04          # chaos always presses upward
        self.corruption_feedback = 0.15      # corruption accelerates itself (Vamphoric)
        self.life_force_base = 1.0

    def step(self, population_faithfulness: float = 0.5,
             covenant_strength: float = 0.5,
             divine_engagement: float = 0.5) -> List[dict]:
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

        # === Chaos Seepage ===
        # Underworld pressure exploits ANY gap in heavenly coverage
        heavenly_shield = self.realm.heavenly_influence * max(covenant_strength, 0.1)
        chaos_opportunity = max(0, 1.0 - heavenly_shield)
        self.realm.chaos_seepage = (self.chaos_base_rate +
                                    chaos_opportunity * 0.12 +
                                    self.realm.corruption_level * 0.08)

        # Underworld pressure builds — it ratchets up, slow to retreat
        self.realm.underworld_pressure = min(1.0,
            self.realm.underworld_pressure * 0.97 + self.realm.chaos_seepage * 0.12)

        # === ENTROPY: Corruption Accumulation ===
        # This is the heart of the system.
        # Corruption ALWAYS accumulates. The question is how fast.
        #
        # Inputs that INCREASE corruption:
        #   - Base entropy rate (always present — the curse)
        #   - Chaos seepage (underworld pressing up)
        #   - Unfaithfulness (rebellion feeds the system)
        #   - Corruption itself (Vamphoric: the system feeds on itself)
        #
        # Inputs that RESIST corruption:
        #   - Divine engagement (the only force that can truly reverse it)
        #   - Covenant strength (creates structure for resistance)
        #   - Faithfulness (slows but cannot stop)

        entropy_input = (self.entropy_base_rate +
                        self.realm.chaos_seepage * 0.15 +
                        (1.0 - population_faithfulness) * 0.1 +
                        self.realm.corruption_level * self.corruption_feedback)

        # ONLY covenant + divine engagement TOGETHER resist entropy
        # Presence alone is not protective — DSA: space as grace
        # Faithfulness slows but cannot stop
        # CDT insight: even with covenant, entropy is only SLOWED, never stopped
        # The cycle cannot be broken by human effort or covenant mechanics alone
        combined_resistance = divine_engagement * covenant_strength
        entropy_resistance = (combined_resistance * 0.06 +
                             population_faithfulness * 0.015)

        net_entropy = entropy_input - entropy_resistance
        self.realm.corruption_level = np.clip(
            self.realm.corruption_level + net_entropy * 0.05, 0.0, 1.0)

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
        phase_change = self.cycle_tracker.update(self.realm, covenant_strength)
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
        # When corruption overwhelms and natural vitality collapses
        if (r.corruption_level > 0.85 and
                r.natural_vitality < 0.2 and
                r.underworld_pressure > 0.7 and
                self._cooldown_ok("cataclysmic_reset", 80)):
            self._record_event("cataclysmic_reset")
            events.append({
                "tick": self.tick,
                "type": "cataclysmic_reset",
                "severity": r.corruption_level,
                "description": "Entropy overwhelms — cataclysmic reset",
                "parallel": "flood_pattern"
            })
            # Reset — but CDT: the curse remains, not fully pristine
            residual_curse = 0.05 + self.cycle_tracker.cycle_count * 0.03
            r.corruption_level = min(0.2, residual_curse)
            r.underworld_pressure *= 0.2
            r.natural_vitality = 0.6
            r.chaos_seepage *= 0.15
            r.heavenly_influence = min(1.0, r.heavenly_influence + 0.3)

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
                "description": "Covenant collapse — exile conditions manifest",
                "parallel": "exile_pattern"
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
        # When divine engagement enters the cycle at its worst to break it
        if (self.cycle_tracker.cycle_count >= 2 and
                divine_engagement > 0.8 and
                r.corruption_level > 0.3 and
                faithfulness > 0.3 and
                covenant > 0.5):
            if not self.cycle_tracker.cycle_broken:
                self.cycle_tracker.cycle_broken = True
                events.append({
                    "tick": self.tick,
                    "type": "cycle_breaking",
                    "description": ("The cycle breaks from within — not escape but death "
                                    "and resurrection within the cycle"),
                    "parallel": "incarnation_pattern"
                })

        return events

    def get_state_snapshot(self) -> dict:
        """Return a complete snapshot of current environmental state."""
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
        }
