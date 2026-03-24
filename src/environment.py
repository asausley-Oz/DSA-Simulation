"""
Environment Engine — SCC Three-Realm Dynamics

Models the cosmological environment from Shared Collective Cosmology (SCC):
- Heavenly influence: life force descending from above (purity, order, creative power)
- Underworld influence: chaos ascending from below (corruption, decay, entropy)
- Natural realm: the convergence zone where both forces meet

The environment is NOT date-driven. Events emerge from the dynamics:
when heavenly influence wanes and corruption peaks, flood-like resets emerge naturally.
When distance accumulates, exile conditions manifest. The simulation discovers
biblical-pattern events rather than scripting them.
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
    corruption_level: float = 0.0        # accumulated corruption in the natural realm
    life_force_flow: float = 1.0         # rate of life force descending from above
    chaos_seepage: float = 0.0           # rate of chaos ascending from below

    def convergence_tension(self) -> float:
        """The tension between heavenly and underworld forces in the natural realm.
        High tension = instability, potential for dramatic events."""
        return abs(self.heavenly_influence - self.underworld_pressure)

    def beauty_darkness_ratio(self) -> float:
        """SCC: the natural world contains both extraordinary beauty and profound darkness.
        Returns ratio of beauty to total (beauty + darkness). 0.5 = balanced."""
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

    This tracker detects when the simulation enters recognizable cycle phases
    and whether any cycle has been broken (the key SCC question).
    """
    phase_history: List[str] = field(default_factory=list)
    cycle_count: int = 0
    current_phase: str = "creation"  # creation, flourishing, decline, collapse, reset
    cycle_broken: bool = False

    # Thresholds for phase transitions
    FLOURISHING_THRESHOLD: float = 0.65
    DECLINE_THRESHOLD: float = 0.45
    COLLAPSE_THRESHOLD: float = 0.2
    RESET_THRESHOLD: float = 0.1

    def update(self, realm: RealmState, covenant_health: float) -> Optional[str]:
        """Evaluate whether a phase transition has occurred.
        Returns the new phase name if transitioned, None otherwise."""
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
                self.current_phase = "flourishing"  # partial restoration
        elif self.current_phase == "collapse":
            if combined_health < self.RESET_THRESHOLD:
                self.current_phase = "reset"
            elif combined_health >= self.DECLINE_THRESHOLD:
                self.current_phase = "decline"  # recovery without full reset
        elif self.current_phase == "reset":
            self.cycle_count += 1
            self.current_phase = "creation"

        if self.current_phase != old_phase:
            self.phase_history.append(self.current_phase)
            return self.current_phase
        return None


class Environment:
    """The cosmological environment engine.

    Models SCC's three-realm structure as a dynamic system where:
    - Heavenly influence naturally sustains life but can be blocked by rebellion
    - Underworld chaos constantly presses upward, exploiting any gap
    - The natural realm is the battleground where both forces converge
    - Corruption accumulates over time (CDT: cumulative distance)
    - Cycles emerge naturally from these dynamics
    """

    def __init__(self, seed: Optional[int] = None):
        self.realm = RealmState()
        self.cycle_tracker = CycleTracker()
        self.tick = 0
        self.rng = np.random.default_rng(seed)
        self.event_log: List[dict] = []
        self._last_event_ticks: dict = {}

        # Environmental parameters
        self.corruption_decay_rate = 0.001    # corruption slowly self-reinforces
        self.chaos_base_rate = 0.04           # baseline chaos pressure (always pressing)
        self.life_force_base = 1.0            # baseline heavenly flow
        self.natural_resilience = 0.85        # nature resists but imperfectly

    def step(self, population_faithfulness: float = 0.5,
             covenant_strength: float = 0.5,
             divine_engagement: float = 0.5) -> List[dict]:
        """Advance the environment by one tick.

        Args:
            population_faithfulness: aggregate faithfulness of agents (0-1)
            covenant_strength: strength of active covenant relationship (0-1)
            divine_engagement: DSA sovereign engagement level (0-1)

        Returns:
            List of emergent events detected this tick.
        """
        self.tick += 1
        events = []

        # === Life Force Flow ===
        # SCC: life originates from highest heaven, descends into natural order.
        # Faithfulness and covenant create channels; rebellion blocks them.
        channel_openness = (population_faithfulness * 0.4 +
                           covenant_strength * 0.3 +
                           divine_engagement * 0.3)
        self.realm.life_force_flow = self.life_force_base * channel_openness

        # Heavenly influence tracks life force flow with some inertia
        target_heavenly = min(1.0, self.realm.life_force_flow * 0.8 + divine_engagement * 0.2)
        self.realm.heavenly_influence += (target_heavenly - self.realm.heavenly_influence) * 0.1

        # === Chaos Seepage ===
        # Underworld pressure exploits gaps in heavenly coverage
        heavenly_shield = self.realm.heavenly_influence * covenant_strength
        chaos_opportunity = max(0, 1.0 - heavenly_shield)
        self.realm.chaos_seepage = (self.chaos_base_rate +
                                     chaos_opportunity * 0.1 +
                                     self.realm.corruption_level * 0.05)

        # Underworld pressure builds based on chaos seepage
        self.realm.underworld_pressure = min(1.0,
            self.realm.underworld_pressure * 0.95 + self.realm.chaos_seepage * 0.15)

        # === Corruption Accumulation ===
        # CDT: corruption is cumulative — each act adds to the distance
        # Corruption has a base rate — the curse never fully lifts on its own
        corruption_input = (self.realm.chaos_seepage * 0.3 +
                           (1.0 - population_faithfulness) * 0.25 +
                           self.realm.underworld_pressure * 0.15 +
                           0.02)  # base corruption — the post-Fall world is cursed
        corruption_resistance = (self.realm.heavenly_influence * 0.2 +
                                population_faithfulness * 0.15 +
                                divine_engagement * 0.08)
        net_corruption = corruption_input - corruption_resistance
        # CDT: corruption never fully vanishes in the cursed world — minimum floor
        corruption_floor = 0.05
        self.realm.corruption_level = np.clip(
            self.realm.corruption_level + net_corruption * 0.06,
            corruption_floor, 1.0)

        # === Natural Vitality ===
        # The health of the convergence zone
        vitality_support = (self.realm.life_force_flow * 0.4 +
                           self.realm.heavenly_influence * 0.3 +
                           population_faithfulness * 0.2 +
                           self.natural_resilience * 0.1)
        vitality_drain = (self.realm.corruption_level * 0.3 +
                         self.realm.underworld_pressure * 0.2 +
                         self.realm.chaos_seepage * 0.1)
        target_vitality = np.clip(vitality_support - vitality_drain, 0.0, 1.0)
        self.realm.natural_vitality += (target_vitality - self.realm.natural_vitality) * 0.08

        # Add small random perturbations
        noise = self.rng.normal(0, 0.01)
        self.realm.natural_vitality = np.clip(
            self.realm.natural_vitality + noise, 0.0, 1.0)

        # === Emergent Event Detection ===
        events.extend(self._detect_events(population_faithfulness, covenant_strength))

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

    def _detect_events(self, faithfulness: float, covenant: float) -> List[dict]:
        """Detect emergent events from environmental dynamics.

        Events are NOT scripted — they emerge when conditions align.
        The simulation discovers patterns that parallel biblical events.
        """
        events = []
        r = self.realm

        # --- Flood-type Reset ---
        if (r.corruption_level > 0.9 and r.underworld_pressure > 0.8 and
                r.natural_vitality < 0.15 and faithfulness < 0.1 and
                self._cooldown_ok("cataclysmic_reset", 100)):
            self._record_event("cataclysmic_reset")
            events.append({
                "tick": self.tick,
                "type": "cataclysmic_reset",
                "severity": r.corruption_level,
                "description": "Corruption overwhelms natural realm — cataclysmic reset initiated",
                "parallel": "flood_pattern"
            })
            # Reset environment but not to pristine — CDT: curse remains
            r.corruption_level *= 0.2
            r.underworld_pressure *= 0.3
            r.natural_vitality = 0.5
            r.chaos_seepage *= 0.2

        # --- Babel-type Scattering ---
        if (faithfulness < 0.2 and covenant < 0.15 and
                r.natural_vitality > 0.6 and r.corruption_level > 0.5 and
                self._cooldown_ok("scattering", 80)):
            self._record_event("scattering")
            events.append({
                "tick": self.tick,
                "type": "scattering",
                "description": "Collective ambition without covenant — scattering occurs",
                "parallel": "babel_pattern"
            })

        # --- Exile Conditions ---
        if (covenant < 0.1 and r.corruption_level > 0.7 and
                r.heavenly_influence < 0.3 and
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
        if (r.heavenly_influence > 0.8 and faithfulness > 0.7 and
                covenant > 0.6 and r.convergence_tension() > 0.5 and
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
        if (r.corruption_level > 0.6 and faithfulness > 0.3 and
                r.underworld_pressure > 0.5 and
                self._cooldown_ok("remnant_emergence", 40)):
            self._record_event("remnant_emergence")
            events.append({
                "tick": self.tick,
                "type": "remnant_emergence",
                "description": "Faithful remnant persists amid corruption",
                "parallel": "remnant_pattern"
            })

        # --- Divine Incursion ---
        if (r.heavenly_influence > 0.85 and r.life_force_flow > 0.8 and
                r.convergence_tension() > 0.6 and
                self._cooldown_ok("divine_incursion", 50)):
            self._record_event("divine_incursion")
            events.append({
                "tick": self.tick,
                "type": "divine_incursion",
                "intensity": r.heavenly_influence,
                "description": "Sovereign divine engagement — God enters the moment",
                "parallel": "theophany_pattern"
            })

        # --- Cycle Breaking (the SCC key question) ---
        # When divine engagement + incarnational pattern breaks the cycle
        if (self.cycle_tracker.cycle_count >= 2 and
                r.heavenly_influence > 0.9 and
                r.corruption_level > 0.5 and
                faithfulness > 0.5 and
                covenant > 0.7):
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
