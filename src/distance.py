"""
Distance Mechanics — Covenant Distance Theology (CDT)

Models the cumulative distance between God and humanity:
- Rebellion accumulates — each act adds to the distance
- Spiritual death is a process, not an instantaneous state
- The curse structure: natural consequences of moving from the Source
- God's counter-movement: incremental intimacy drawing near
- The remnant: faithful minority persisting in a cursed world
- Delusion: accelerates spiritual death, obscures awareness

CDT reads the biblical story as dynamic, unfolding accumulation of distance
and a sovereign reversal in Christ.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class CovenantState:
    """The state of the covenant relationship between God and a population."""

    # === Distance Metrics ===
    cumulative_rebellion: float = 0.0      # total accumulated rebellion (never fully resets)
    active_distance: float = 0.0           # current relational distance (can decrease)
    curse_weight: float = 0.0              # weight of accumulated curses
    blessing_flow: float = 1.0             # flow of covenant blessings

    # === Spiritual State (Anti-Life Delusion) ===
    spiritual_vitality: float = 1.0        # 0 = spiritually dead, 1 = fully alive
    delusion_level: float = 0.0            # Anti-Life Delusion: conceals and accelerates dying
    awareness_of_condition: float = 1.0    # awareness is the precondition of turning

    # === God's Counter-Movement ===
    divine_nearness: float = 0.5           # CDT: God's movement toward humanity
    covenant_strength: float = 0.5         # strength of formal covenant relationship
    incremental_intimacy: float = 0.0      # accumulated intimacy milestones

    # === Population Dynamics ===
    remnant_fraction: float = 0.1          # fraction of population that is faithful
    population_faithfulness: float = 0.5   # aggregate faithfulness

    def effective_distance(self) -> float:
        """Net distance accounting for God's counter-movement."""
        return max(0.0, self.active_distance - self.divine_nearness * 0.3)

    def covenant_health(self) -> float:
        """Overall health of the covenant relationship."""
        return (self.covenant_strength * 0.3 +
                self.blessing_flow * 0.2 +
                self.spiritual_vitality * 0.3 +
                (1.0 - self.effective_distance()) * 0.2)


class DistanceEngine:
    """Models CDT's cumulative distance mechanics.

    Core dynamics:
    1. Rebellion accumulates — never fully erased, but can be covered/atoned
    2. Spiritual death is progressive — born alive, dying through rebellion
    3. Curse deepens with distance — natural consequence, not arbitrary punishment
    4. God moves counter — incremental intimacy, drawing nearer over time
    5. Delusion accelerates the process — obscures awareness of condition
    6. The remnant persists — faithful minority in every generation
    """

    def __init__(self, seed: Optional[int] = None):
        self.state = CovenantState()
        self.rng = np.random.default_rng(seed)
        self.tick = 0
        self.intimacy_milestones: List[dict] = []
        self._last_event_ticks: dict = {}
        self.covenant_active = False  # covenant requires explicit calling to activate

        # Parameters
        self.rebellion_decay = 0.001       # very slow natural decay of rebellion
        self.curse_growth_rate = 0.02      # how fast curse builds with rebellion
        self.blessing_base = 0.8           # baseline blessing in covenant
        self.delusion_growth = 0.02        # how fast delusion spreads (increased)
        self.counter_movement_rate = 0.01  # how fast God draws near

        # Accumulated cycle curse penalties — set by simulation from environment
        self.covenant_penalty = 0.0        # reduces covenant effectiveness
        self.fragmentation = 0.0           # reduces population unity
        self.foreign_pressure = 0.0        # constant external oppression

    def step(self, rebellion_input: float = 0.0,
             faithfulness_input: float = 0.5,
             divine_initiative: float = 0.5,
             atonement_event: bool = False) -> List[dict]:
        """Advance distance mechanics by one tick.

        Args:
            rebellion_input: new rebellion this tick (0-1)
            faithfulness_input: population faithfulness this tick (0-1)
            divine_initiative: DSA engagement level (0-1)
            atonement_event: whether an atonement/sacrifice occurs this tick

        Returns:
            List of emergent covenant events.
        """
        self.tick += 1
        events = []
        s = self.state

        # === Cumulative Rebellion ===
        # CDT: each act adds to the weight — never fully erased by human effort
        s.cumulative_rebellion = min(10.0,
            s.cumulative_rebellion + rebellion_input * 0.1 - self.rebellion_decay)
        s.cumulative_rebellion = max(0.0, s.cumulative_rebellion)

        # === Active Distance ===
        # Moves based on net rebellion vs faithfulness and divine movement
        # Foreign pressure from accumulated curses adds constant distance push
        distance_push = (rebellion_input * 0.15 +
                        s.delusion_level * 0.05 +
                        self.foreign_pressure * 0.03)  # occupation pushes distance
        distance_pull = (faithfulness_input * 0.08 +
                        divine_initiative * 0.06 +
                        s.remnant_fraction * 0.03)
        if atonement_event:
            distance_pull += 0.2  # atonement creates significant pull

        s.active_distance = np.clip(
            s.active_distance + distance_push - distance_pull, 0.0, 1.0)

        # === Curse Weight ===
        # CDT: curses are natural consequences of distance from the Source
        # Accumulated cycle curses add a permanent floor to curse weight
        target_curse = (s.cumulative_rebellion * 0.1 +
                       s.active_distance * 0.3 +
                       self.foreign_pressure * 0.2)  # occupation adds curse weight
        s.curse_weight += (target_curse - s.curse_weight) * self.curse_growth_rate
        s.curse_weight = np.clip(s.curse_weight, 0.0, 1.0)

        # === Blessing Flow ===
        # Blessings flow through covenant — blocked by distance, curse, AND
        # accumulated structural damage (covenant penalty from cycle failures)
        covenant_effectiveness = max(0.2, 1.0 - self.covenant_penalty)
        covenant_channel = (s.covenant_strength * covenant_effectiveness *
                          (1.0 - s.active_distance * 0.5))
        s.blessing_flow = (self.blessing_base * covenant_channel *
                          (1.0 - s.curse_weight * 0.4) *
                          (1.0 - self.fragmentation * 0.3))  # fragmentation blocks blessing
        s.blessing_flow = np.clip(s.blessing_flow, 0.0, 1.0)

        # === Spiritual Vitality ===
        # CDT: spiritual death is a process — born alive, dying through rebellion
        vitality_drain = (s.active_distance * 0.05 +
                         s.curse_weight * 0.03 +
                         s.delusion_level * 0.04 +
                         rebellion_input * 0.08)
        vitality_restore = (faithfulness_input * 0.06 +
                           divine_initiative * 0.05 +
                           s.blessing_flow * 0.04)
        if atonement_event:
            vitality_restore += 0.15

        s.spiritual_vitality = np.clip(
            s.spiritual_vitality + vitality_restore - vitality_drain, 0.0, 1.0)

        # === Delusion ===
        # CDT: delusion accelerates spiritual death, obscures awareness
        # Delusion grows in distance from God, shrinks with divine engagement
        delusion_growth = ((1.0 - faithfulness_input) * self.delusion_growth +
                          s.active_distance * 0.01)
        delusion_shrink = (divine_initiative * 0.02 +
                          faithfulness_input * 0.01)
        s.delusion_level = np.clip(
            s.delusion_level + delusion_growth - delusion_shrink, 0.0, 1.0)

        # Awareness inversely tracks delusion
        # Anti-Life Delusion: complete blindness is possible
        s.awareness_of_condition = max(0.0, 1.0 - s.delusion_level * 0.95)

        # === God's Counter-Movement ===
        # CDT: incremental intimacy — God draws nearer over the long arc
        # DSA: this is sovereign and chosen, not mechanical
        nearness_drive = (divine_initiative * 0.4 +
                         s.remnant_fraction * 0.2 +
                         faithfulness_input * 0.2)
        # God moves toward even in rebellion — but more dramatically with faith
        s.divine_nearness = np.clip(
            s.divine_nearness + nearness_drive * self.counter_movement_rate, 0.0, 1.0)

        # === Covenant Strength ===
        # Covenant requires explicit activation (calling event)
        # Pre-covenant: only basic relational connection, not formal covenant
        # Accumulated curses (fragmentation, occupation) reduce covenant ceiling
        if self.covenant_active:
            raw_strength = (faithfulness_input * 0.3 +
                           divine_initiative * 0.3 +
                           s.divine_nearness * 0.2 +
                           s.remnant_fraction * 0.2) - s.active_distance * 0.2
            # Fragmentation caps covenant strength — split kingdom can't unite fully
            covenant_ceiling = max(0.3, 1.0 - self.fragmentation * 0.6)
            s.covenant_strength = np.clip(raw_strength, 0.0, covenant_ceiling)
        else:
            # Pre-covenant: minimal relational structure
            s.covenant_strength = np.clip(
                faithfulness_input * 0.1 - s.active_distance * 0.3,
                0.0, 0.15)

        # === Remnant Dynamics ===
        # The remnant grows with divine engagement, shrinks with delusion
        remnant_growth = divine_initiative * 0.005 + faithfulness_input * 0.003
        remnant_loss = s.delusion_level * 0.004 + s.curse_weight * 0.002
        s.remnant_fraction = np.clip(
            s.remnant_fraction + remnant_growth - remnant_loss, 0.01, 0.5)

        # Aggregate faithfulness is weighted by remnant
        s.population_faithfulness = (s.remnant_fraction * 0.8 +
                                    (1.0 - s.remnant_fraction) * 0.1 * faithfulness_input)

        # === Emergent Event Detection ===
        events.extend(self._detect_events(rebellion_input, faithfulness_input,
                                          divine_initiative, atonement_event))

        return events

    def _cooldown_ok(self, event_type: str, min_gap: int = 25) -> bool:
        last = self._last_event_ticks.get(event_type, -min_gap - 1)
        return self.tick - last >= min_gap

    def _record_event(self, event_type: str):
        self._last_event_ticks[event_type] = self.tick

    def _detect_events(self, rebellion: float, faithfulness: float,
                       divine_initiative: float, atonement: bool) -> List[dict]:
        """Detect emergent covenant events from CDT dynamics."""
        events = []
        s = self.state

        # --- Covenant Formation ---
        if (s.divine_nearness > 0.7 and faithfulness > 0.6 and
                s.covenant_strength > 0.6):
            milestone = len(self.intimacy_milestones)
            if milestone == 0 or self.tick - self.intimacy_milestones[-1]["tick"] > 50:
                entry = {
                    "tick": self.tick,
                    "type": "covenant_formation",
                    "nearness": s.divine_nearness,
                    "description": f"Covenant deepens — intimacy milestone {milestone + 1}",
                    "parallel": "covenant_pattern"
                }
                self.intimacy_milestones.append(entry)
                events.append(entry)

        # --- Covenant Fracture ---
        if (s.covenant_strength < 0.2 and s.active_distance > 0.7 and
                rebellion > 0.6 and self._cooldown_ok("covenant_fracture", 40)):
            self._record_event("covenant_fracture")
            events.append({
                "tick": self.tick,
                "type": "covenant_fracture",
                "severity": s.active_distance,
                "description": "Covenant fractures under weight of rebellion",
                "parallel": "divided_kingdom_pattern"
            })

        # --- Spiritual Death Threshold ---
        if s.spiritual_vitality < 0.1 and self._cooldown_ok("spiritual_death", 50):
            self._record_event("spiritual_death")
            events.append({
                "tick": self.tick,
                "type": "spiritual_death",
                "description": "Spiritual death reaches critical threshold",
                "parallel": "death_pattern"
            })

        # --- Vamphoric Dominance (Anti-Life Delusion) ---
        # The drain runs undetected, the fork has split attention completely
        if (s.delusion_level > 0.8 and s.awareness_of_condition < 0.15 and
                self._cooldown_ok("delusion_dominance", 50)):
            self._record_event("delusion_dominance")
            events.append({
                "tick": self.tick,
                "type": "delusion_dominance",
                "description": "Vamphoric systems dominate — awareness of condition nearly lost",
                "parallel": "hardening_pattern"
            })

        # --- Curse Paradox (Beatitudes) ---
        if (s.curse_weight > 0.6 and faithfulness > 0.5 and
                s.remnant_fraction > 0.15 and self._cooldown_ok("curse_paradox", 40)):
            self._record_event("curse_paradox")
            events.append({
                "tick": self.tick,
                "type": "curse_paradox",
                "description": "The cursed prove blessed — paradox of the kingdom",
                "parallel": "beatitudes_pattern"
            })

        # --- Atonement Breakthrough ---
        if atonement and s.active_distance > 0.5 and self._cooldown_ok("atonement", 30):
            self._record_event("atonement")
            events.append({
                "tick": self.tick,
                "type": "atonement",
                "distance_before": s.active_distance,
                "description": "Atonement event — distance temporarily bridged",
                "parallel": "sacrifice_pattern"
            })

        # --- Incremental Intimacy Milestone ---
        intimacy_score = s.divine_nearness * s.covenant_strength * (1.0 - s.active_distance)
        if (intimacy_score > 0.6 and divine_initiative > 0.7 and
                self._cooldown_ok("intimacy_advance", 40)):
            self._record_event("intimacy_advance")
            events.append({
                "tick": self.tick,
                "type": "intimacy_advance",
                "score": intimacy_score,
                "description": "God draws measurably nearer — intimacy advances",
                "parallel": "tabernacle_to_temple_pattern"
            })

        return events

    def get_state_snapshot(self) -> dict:
        """Return complete snapshot of covenant distance state."""
        s = self.state
        return {
            "tick": self.tick,
            "cumulative_rebellion": round(s.cumulative_rebellion, 4),
            "active_distance": round(s.active_distance, 4),
            "effective_distance": round(s.effective_distance(), 4),
            "curse_weight": round(s.curse_weight, 4),
            "blessing_flow": round(s.blessing_flow, 4),
            "spiritual_vitality": round(s.spiritual_vitality, 4),
            "delusion_level": round(s.delusion_level, 4),
            "awareness_of_condition": round(s.awareness_of_condition, 4),
            "divine_nearness": round(s.divine_nearness, 4),
            "covenant_strength": round(s.covenant_strength, 4),
            "covenant_health": round(s.covenant_health(), 4),
            "remnant_fraction": round(s.remnant_fraction, 4),
            "population_faithfulness": round(s.population_faithfulness, 4),
            "intimacy_milestones": len(self.intimacy_milestones),
        }
