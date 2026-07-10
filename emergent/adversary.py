"""The Adversary — the prince of the power of the air (Eph 2:2).

NOT a rival god. Per Anti-Life Delusion, the powers that entice delusion
are themselves expressions of the disorder rebellion introduced: the
adversary's power is PARASITIC — derived entirely from the breach (the
accumulated weight of rebellion, the open distance, the captured agents).
He creates nothing; he schemes within the space rebellion opens.

Three structural limits bind him:
  1. He works in the dark — exposure (being named) drains his power.
  2. His sharpest weapon backfires: violence against the faithful
     produces martyrs, and martyr-seed grows the very thing he strikes.
  3. At the atonement he is disarmed (Col 2:15) — not annihilated, but
     stripped: the record of debt that empowered him is cancelled.

He schemes with intelligence, not randomness — each move targets where
God's counter-movement is gaining ground:
  QUENCH — snatch the seed: crush revival tension where it nears ignition
  GILD   — the subtlest scheme: reward a strong church into softness
  SCHISM — sow division where accusation has inflated pride: load the
           church's own fracture pressure until it splits itself
  ACCUSE — sift the deep remnant: drain agency, inflate pride
  INCITE — stir war where the remnant is absent, so ruin cannot seed

Every movement carries a DISTANCE LOAD: a scheme is rebellion enacted,
so it widens the breach directly and part of it sticks to the record —
the parasite feeding the very disorder it feeds on. This is his engine
of escalation, and also his leash: the more he works, the heavier the
record grows toward the fullness of time.
"""

import numpy as np
from typing import List, Optional, Tuple

from .config import EmergentConfig


class Adversary:
    def __init__(self, cfg: EmergentConfig, rng: np.random.Generator):
        self.cfg = cfg
        self.rng = rng
        self.power = 0.20
        self.exposure = 0.0     # how thoroughly he has been named
        self.disarmed = False   # set by the atonement
        self.released = False   # loosed for a little while (Rev 20:3)
        self.deicide_urge = 0.0  # the compulsion he cannot resist
        self.cooldowns = {"quench": 0, "gild": 0, "schism": 0,
                          "accuse": 0, "incite": 0}
        self.schemes_run = {"quench": 0, "gild": 0, "schism": 0,
                            "accuse": 0, "incite": 0}

    # ------------------------------------------------------------------
    def step(self, env, agg: dict, tick: int,
             incarnate_region: Optional[int] = None
             ) -> Tuple[List[dict], Optional[int], bool]:
        """Update power, whisper passively, and possibly run one scheme.

        Returns (events, accuse_region, deicide) — agent-level accusation
        effects are applied by the simulation layer. While the presence is
        embodied (incarnate_region set), a compulsion grows in him that
        he cannot resist and cannot survive: deicide=True is his final
        scheme, and the simulation springs the atonement from it.
        """
        cfg = self.cfg
        events: List[dict] = []
        accuse_region: Optional[int] = None

        pop_w = agg["pop"] / max(agg["pop"].sum(), 1.0)

        # --- power: parasitic on the breach --------------------------
        breach = (cfg.adversary_from_rebellion * float(env.rebellion @ pop_w)
                  + cfg.adversary_from_distance * float(env.distance @ pop_w)
                  + cfg.adversary_from_empire
                  * float(agg["empire_share"] @ pop_w))
        target = np.clip(breach, 0.0, 1.0) \
            * (1.0 - cfg.adversary_exposure_damp * self.exposure)
        if self.released:
            target *= cfg.adversary_release_factor  # his short, final rage
        elif self.disarmed:
            target *= cfg.adversary_disarmed_factor
        self.power += cfg.adversary_power_relax * (target - self.power)
        self.power = float(np.clip(self.power, 0.0, 1.0))
        self.exposure = max(0.0, self.exposure - 0.004)  # the world forgets

        # --- passive influence: the spirit now at work ----------------
        # A constant whisper feeding the vamphoric systems everywhere.
        env.vamphoric = np.clip(
            env.vamphoric + cfg.adversary_vamphoric_gain * self.power,
            0.0, 1.0)
        # Released, he makes war on the saints directly (Rev 13:7) —
        # the minority damper no longer shields a large remnant.
        if self.released:
            env.persecution = np.clip(
                env.persecution + 0.03 * self.power, 0.0, 1.0)

        # --- the embodied presence: the compulsion he cannot resist ----
        if incarnate_region is not None:
            self.deicide_urge += (cfg.deicide_urge_base
                                  + cfg.deicide_urge_power * self.power)
            if self.rng.random() < self.deicide_urge:
                return events, accuse_region, True
            # While the Light stands in one region, his scheming
            # concentrates there — accusation aimed at the vessel.
            if self.cooldowns["accuse"] == 0:
                self.cooldowns["accuse"] = 6
                self.schemes_run["accuse"] += 1
                events.append({
                    "tick": tick, "region": env.names[incarnate_region],
                    "type": "scheme",
                    "detail": ("accuse: every scheme bent toward the "
                               f"vessel (urge {self.deicide_urge:.2f})")})
                return events, incarnate_region, False
            return events, accuse_region, False

        # --- cooldowns -------------------------------------------------
        for k in self.cooldowns:
            self.cooldowns[k] = max(0, self.cooldowns[k] - 1)

        # --- scheme selection: targeted, prioritized -------------------
        # Released, he rages at a faster cadence — he knows his time is
        # short (Rev 12:12).
        scheme_p = cfg.adversary_scheme_prob * self.power \
            * (cfg.tribulation_scheme_boost if self.released else 1.0)
        if self.rng.random() >= scheme_p:
            return events, accuse_region, False

        scheme = None
        # 1. QUENCH the wick nearest ignition — oppose the visitation.
        r = int(np.argmax(env.revival_tension))
        if (self.cooldowns["quench"] == 0
                and env.revival_tension[r] > 0.6 * cfg.revival_threshold):
            scheme = ("quench", r)
        # 2. GILD the strongest church — golden chains.
        if scheme is None:
            candidates = np.where(env.comfort < 0.75,
                                  agg["remnant_share"], -1.0)
            r = int(np.argmax(candidates))
            if self.cooldowns["gild"] == 0 and candidates[r] > 0.10:
                scheme = ("gild", r)
        # 3. SCHISM — divide the church against itself. Easiest where a
        #    sizable remnant already carries weakened unity.
        if scheme is None:
            candidates = np.where(env.unity < 0.65,
                                  agg["remnant_share"], -1.0)
            r = int(np.argmax(candidates))
            if self.cooldowns["schism"] == 0 and candidates[r] > 0.15:
                scheme = ("schism", r)
        # 4. ACCUSE the deep remnant — sift them like wheat.
        if scheme is None:
            r = int(np.argmax(agg["deep_share"]))
            if self.cooldowns["accuse"] == 0 and agg["deep_share"][r] > 0.02:
                scheme = ("accuse", r)
        # 5. INCITE ruin where the remnant is absent — wreckage no seed
        #    can grow in.
        if scheme is None:
            score = env.strain * (1.0 - agg["remnant_share"])
            r = int(np.argmax(score))
            if self.cooldowns["incite"] == 0 and env.strain[r] > 0.5:
                scheme = ("incite", r)

        if scheme is None:
            return events, accuse_region, False

        kind, r = scheme
        self.schemes_run[kind] += 1
        # In the tribulation his movements strike harder — it is given
        # to him, for a little while (Rev 13:7).
        strength = self.power * (cfg.tribulation_scheme_boost
                                 if self.released else 1.0)

        if kind == "quench":
            env.revival_tension[r] *= (1.0 - 0.65 * strength)
            env.receptivity[r] = max(0.0,
                                     env.receptivity[r] - 0.15 * strength)
            self.cooldowns["quench"] = 12
            detail = "the seed snatched before ignition"
        elif kind == "gild":
            env.comfort[r] = min(1.0, env.comfort[r] + 0.18 * strength)
            env.vamphoric[r] = min(1.0, env.vamphoric[r] + 0.06 * strength)
            self.cooldowns["gild"] = 25
            detail = "golden chains — comfort for the strong church"
        elif kind == "schism":
            # Division is his sharpest blade in the tribulation:
            # brother betrays brother (Matt 24:10).
            div = cfg.tribulation_schism_bonus if self.released else 1.0
            env.unity[r] = max(
                0.05, env.unity[r]
                - cfg.schism_scheme_unity_cost * strength * div)
            env.schism_pressure[r] += (cfg.schism_scheme_pressure
                                       * strength * div)
            self.cooldowns["schism"] = 12 if self.released else 22
            detail = "brothers set against brothers — division sown"
        elif kind == "accuse":
            accuse_region = r
            self.cooldowns["accuse"] = 18
            detail = "the deep remnant sifted like wheat"
            # Backfire: accusing the formed risks being named by them.
            if self.rng.random() < float(agg["remnant_formation"][r]) * 0.5:
                self.exposure = min(1.0, self.exposure + 0.20)
                detail += " — but the scheme is NAMED; exposure grows"
        else:  # incite
            env.strain[r] += 0.45 * strength
            self.cooldowns["incite"] = 20
            detail = "war stirred where no seed can grow"

        # The distance load: every scheme is rebellion enacted. The
        # breach widens where he works, and part of it sticks to the
        # record — escalation, and the leash that hastens his own end.
        load = cfg.scheme_distance_load * strength
        env.distance[r] = min(1.0, env.distance[r] + load)
        env.rebellion[r] = min(cfg.ratchet_cap,
                               env.rebellion[r]
                               + cfg.scheme_record_stick * load)

        events.append({"tick": tick, "region": env.names[r],
                       "type": "scheme",
                       "detail": f"{kind}: {detail} (power {self.power:.2f})"})
        return events, accuse_region, False
