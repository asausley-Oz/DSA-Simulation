"""
Engagement Mechanics — Divine Sovereign Agency (DSA)

Models God's sovereign, chosen engagement with creation:
- Sovereign self-limitation: God chooses to experience creation as it unfolds
- Space as grace: distance given for genuine discovery and faith
- The God who prefers: faith is real, native, genuinely valued
- God as gardener: dynamic world with genuinely sovereign creatures
- The God of the Moment: entering particular moments experientially

DSA preserves full sovereignty while creating space for genuine
relational encounter, human faith, and divine delight.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class DivineEngagementState:
    """State of God's sovereign engagement with the simulation."""

    # === Sovereign Presence ===
    presence_level: float = 0.5           # how present God is choosing to be
    experiential_engagement: float = 0.5  # how much God is "in the moment"
    self_limitation_degree: float = 0.3   # how much sovereign power is held back

    # === Grace Space ===
    grace_space: float = 0.5             # room given for genuine discovery
    faith_opportunity: float = 0.5       # how much room exists for faith to matter

    # === Response to Humanity ===
    delight: float = 0.5                 # divine delight in faithful response
    grief: float = 0.0                   # divine grief at rebellion
    patience: float = 1.0               # sovereign patience before judgment
    compassion: float = 0.7             # active compassion toward creation

    # === Gardener Dynamics ===
    cultivation_intensity: float = 0.5   # how actively God tends the garden
    harvest_readiness: float = 0.0       # how close the harvest is


class EngagementEngine:
    """Models DSA's divine sovereign engagement.

    Core dynamics:
    1. God is sovereign — fully omniscient but chooses experiential engagement
    2. Space is grace — distance creates room for genuine faith
    3. Faith is valued — God responds to and delights in faith
    4. God is a gardener — cultivating, not controlling
    5. The Moment matters — God enters particular moments with particular intensity
    6. Incarnational trajectory — engagement deepens toward full entry
    """

    def __init__(self, seed: Optional[int] = None):
        self.state = DivineEngagementState()
        self.rng = np.random.default_rng(seed)
        self.tick = 0
        self.intervention_log: List[dict] = []

        # Parameters
        self.patience_drain_rate = 0.01
        self.patience_restore_rate = 0.008
        self.delight_sensitivity = 0.3
        self.grief_sensitivity = 0.25
        self.incarnation_threshold = 0.85
        self._last_event_ticks: dict = {}  # cooldown tracking

    def step(self, population_faithfulness: float = 0.5,
             remnant_fraction: float = 0.1,
             covenant_health: float = 0.5,
             corruption_level: float = 0.0,
             spiritual_vitality: float = 0.5,
             cycle_count: int = 0) -> Tuple[float, List[dict]]:
        """Advance divine engagement by one tick.

        Args:
            population_faithfulness: aggregate faithfulness of agents
            remnant_fraction: fraction of faithful remnant
            covenant_health: health of covenant relationship
            corruption_level: environmental corruption
            spiritual_vitality: population spiritual health
            cycle_count: how many cosmological cycles have occurred

        Returns:
            Tuple of (engagement_level, list of divine events)
        """
        self.tick += 1
        events = []
        s = self.state

        # === Sovereign Presence ===
        # DSA: God chooses how present to be — this is sovereign, not mechanical
        # Higher faithfulness and remnant draw more presence (but it's chosen, not forced)
        presence_draw = (population_faithfulness * 0.3 +
                        remnant_fraction * 0.3 +
                        covenant_health * 0.2)
        # God also moves toward need — compassion drives presence in darkness
        need_draw = corruption_level * 0.15 + (1.0 - spiritual_vitality) * 0.1

        target_presence = np.clip(presence_draw + need_draw, 0.1, 1.0)
        # Presence moves with inertia — God is not reactive but deliberate
        s.presence_level += (target_presence - s.presence_level) * 0.05
        s.presence_level = np.clip(s.presence_level, 0.1, 1.0)

        # === Experiential Engagement ===
        # DSA: the God of the Moment — choosing to experience creation in real time
        # Engagement intensifies with covenant health and remnant faithfulness
        moment_intensity = (covenant_health * 0.4 +
                           population_faithfulness * 0.3 +
                           s.presence_level * 0.3)
        s.experiential_engagement = np.clip(moment_intensity, 0.1, 1.0)

        # === Self-Limitation ===
        # DSA: sovereign self-limitation creates space for genuine agency
        # More limitation = more room for faith to matter
        # God limits more when humanity is capable, less when intervention is needed
        capability = spiritual_vitality * covenant_health
        s.self_limitation_degree = np.clip(
            capability * 0.5 + 0.1, 0.1, 0.7)

        # === Grace Space ===
        # The room given for genuine discovery — inversely related to direct control
        s.grace_space = s.self_limitation_degree * 0.8 + 0.2
        s.faith_opportunity = s.grace_space * (1.0 - corruption_level * 0.3)

        # === Divine Emotions (anthropopathic but theologically significant) ===

        # Delight: God delights in faith and faithfulness
        # Requires genuinely high faithfulness — not triggered by mediocrity
        faith_delight = max(0, population_faithfulness - 0.4) * remnant_fraction * 5.0
        s.delight = np.clip(faith_delight * self.delight_sensitivity, 0.0, 1.0)

        # Grief: God grieves rebellion and corruption
        rebellion_grief = corruption_level * (1.0 - population_faithfulness)
        s.grief = np.clip(rebellion_grief * self.grief_sensitivity, 0.0, 1.0)

        # Patience: sovereign patience — drains with persistent rebellion, restores with faith
        if population_faithfulness < 0.2 and corruption_level > 0.7:
            s.patience -= self.patience_drain_rate
        elif population_faithfulness > 0.5:
            s.patience += self.patience_restore_rate
        s.patience = np.clip(s.patience, 0.0, 1.0)

        # Compassion: driven by need, amplified by remnant faithfulness
        s.compassion = np.clip(
            0.5 + (1.0 - spiritual_vitality) * 0.3 + remnant_fraction * 0.2,
            0.3, 1.0)

        # === Cultivation (Gardener) ===
        # DSA: God as gardener tending a dynamic world
        s.cultivation_intensity = (s.presence_level * 0.3 +
                                  s.experiential_engagement * 0.3 +
                                  s.compassion * 0.2 +
                                  covenant_health * 0.2)

        # Harvest readiness builds over time with sustained cultivation
        if s.cultivation_intensity > 0.6:
            s.harvest_readiness = min(1.0, s.harvest_readiness + 0.002)
        else:
            s.harvest_readiness = max(0.0, s.harvest_readiness - 0.001)

        # === Emergent Events ===
        events.extend(self._detect_events(population_faithfulness, remnant_fraction,
                                          covenant_health, corruption_level,
                                          cycle_count))

        # Compute overall engagement level for other engines
        engagement_level = (s.presence_level * 0.3 +
                           s.experiential_engagement * 0.3 +
                           s.cultivation_intensity * 0.2 +
                           (1.0 - s.self_limitation_degree) * 0.2)

        return engagement_level, events

    def _cooldown_ok(self, event_type: str, min_gap: int = 20) -> bool:
        """Check if enough ticks have passed since last event of this type."""
        last = self._last_event_ticks.get(event_type, -min_gap - 1)
        return self.tick - last >= min_gap

    def _record_event(self, event_type: str):
        self._last_event_ticks[event_type] = self.tick

    def _detect_events(self, faithfulness: float, remnant: float,
                       covenant: float, corruption: float,
                       cycle_count: int) -> List[dict]:
        """Detect emergent divine engagement events."""
        events = []
        s = self.state

        # --- Sovereign Intervention ---
        if s.patience < 0.1 and corruption > 0.8 and self._cooldown_ok("sovereign_intervention", 50):
            self._record_event("sovereign_intervention")
            events.append({
                "tick": self.tick,
                "type": "sovereign_intervention",
                "patience_remaining": s.patience,
                "description": "Divine patience exhausts — sovereign intervention",
                "parallel": "judgment_pattern"
            })
            s.patience = 0.5

        # --- God Draws Near ---
        if (s.presence_level > 0.8 and faithfulness > 0.6 and
                self._cooldown_ok("divine_drawing_near", 40)):
            self._record_event("divine_drawing_near")
            events.append({
                "tick": self.tick,
                "type": "divine_drawing_near",
                "presence": s.presence_level,
                "description": "God draws near — presence intensifies with faithfulness",
                "parallel": "revival_pattern"
            })

        # --- Divine Delight ---
        if s.delight > 0.85 and self._cooldown_ok("divine_delight", 30):
            self._record_event("divine_delight")
            events.append({
                "tick": self.tick,
                "type": "divine_delight",
                "delight": s.delight,
                "description": "God delights in the faithfulness of His people",
                "parallel": "approval_pattern"
            })

        # --- Divine Grief ---
        if s.grief > 0.7 and s.patience > 0.3 and self._cooldown_ok("divine_grief", 30):
            self._record_event("divine_grief")
            events.append({
                "tick": self.tick,
                "type": "divine_grief",
                "grief": s.grief,
                "description": "God grieves the rebellion and corruption",
                "parallel": "grief_pattern"
            })

        # --- Incarnational Trajectory ---
        engagement = (s.presence_level * 0.3 + s.experiential_engagement * 0.3 +
                     s.compassion * 0.2 + s.cultivation_intensity * 0.2)
        if (engagement > self.incarnation_threshold and
                cycle_count >= 2 and corruption > 0.4 and
                self._cooldown_ok("incarnational_entry", 100)):
            self._record_event("incarnational_entry")
            events.append({
                "tick": self.tick,
                "type": "incarnational_entry",
                "engagement": engagement,
                "description": ("Engagement reaches incarnational threshold — "
                                "God enters the cycle as participant"),
                "parallel": "incarnation_pattern"
            })

        # --- Harvest Time ---
        if s.harvest_readiness > 0.8 and self._cooldown_ok("harvest_ready", 50):
            self._record_event("harvest_ready")
            events.append({
                "tick": self.tick,
                "type": "harvest_ready",
                "readiness": s.harvest_readiness,
                "description": "The harvest is ready — long cultivation bears fruit",
                "parallel": "harvest_pattern"
            })

        return events

    def get_state_snapshot(self) -> dict:
        """Return complete snapshot of divine engagement state."""
        s = self.state
        return {
            "tick": self.tick,
            "presence_level": round(s.presence_level, 4),
            "experiential_engagement": round(s.experiential_engagement, 4),
            "self_limitation_degree": round(s.self_limitation_degree, 4),
            "grace_space": round(s.grace_space, 4),
            "faith_opportunity": round(s.faith_opportunity, 4),
            "delight": round(s.delight, 4),
            "grief": round(s.grief, 4),
            "patience": round(s.patience, 4),
            "compassion": round(s.compassion, 4),
            "cultivation_intensity": round(s.cultivation_intensity, 4),
            "harvest_readiness": round(s.harvest_readiness, 4),
        }
