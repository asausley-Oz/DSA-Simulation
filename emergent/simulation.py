"""Orchestrator for the Emergent Covenant Engine.

Tick order:
  1. read agent aggregates
  2. environment updates itself from them (and fires emergent events)
  3. environment pressures flow back onto agents (drain, conversion,
     apostasy, martyrdom, revival cascades, schism defection)
  4. demography (deaths, births with generational transmission, migration)
  5. record history; check state-only ending conditions

There is no calendar anywhere in this loop. Endings are attractors, not
appointments: a run terminates in CONSUMMATION (entropy saturates or the
remnant goes extinct) or RENEWAL (a formed remnant becomes the culture and
entropy collapses) — or simply runs out of ticks, still contested.
"""

import numpy as np
import pandas as pd
from typing import List, Optional

from .adversary import Adversary
from .config import EmergentConfig
from .environment import Environment
from .population import Population


class EmergentSimulation:
    def __init__(self, cfg: Optional[EmergentConfig] = None):
        self.cfg = cfg or EmergentConfig()
        self.rng = np.random.default_rng(self.cfg.seed)
        self.env = Environment(self.cfg, self.rng)
        self.pop = Population(self.cfg, self.rng)
        self.adversary = (Adversary(self.cfg, self.rng)
                          if self.cfg.enable_adversary else None)

        self.tick = 0
        self.history: List[dict] = []
        self.ending: Optional[str] = None
        self.atonement_tick: Optional[int] = None
        self._ending_streak = {"consummation": 0, "renewal": 0}

    # ------------------------------------------------------------------
    def step(self):
        cfg, rng, env, pop = self.cfg, self.rng, self.env, self.pop
        n_regions = env.n

        agg = pop.regional_aggregates(n_regions)
        _, schism_regions = env.step(agg, self.tick)

        alive = pop.alive
        reg = pop.region
        counters = {"conversions": 0, "apostasies": 0, "martyrs": 0}

        # ---- 0. the adversary schemes ---------------------------------
        accuse_region = None
        if self.adversary is not None:
            adv_events, accuse_region = self.adversary.step(
                env, agg, self.tick)
            env.events.extend(adv_events)

        # ---- 1. vamphoric drain on agents -----------------------------
        vamp = env.vamphoric[reg]
        nominal = alive & ~pop.born & ~pop.empire
        remnant = alive & pop.born & ~pop.empire

        pop.scc_lock[nominal] += cfg.drain_rate * vamp[nominal]
        pop.agency[nominal] -= 0.01 * vamp[nominal]
        # Remnant resists in proportion to formation x agency.
        resist = pop.formation * pop.agency
        pop.scc_lock[remnant] += (cfg.drain_rate * 0.5 * vamp[remnant]
                                  * (1.0 - resist[remnant]))
        # Locks loosen wherever the vamphoric system is weak — so empire
        # capture is an equilibrium of pressure, not a one-way ratchet.
        pop.scc_lock[alive] -= cfg.lock_relax * (1.0 - vamp[alive])
        # Labor restores agency; drift restores a little for everyone.
        pop.agency[remnant] += 0.008
        np.clip(pop.scc_lock, 0.0, 1.2, out=pop.scc_lock)
        np.clip(pop.agency, 0.0, 1.0, out=pop.agency)

        # Fully locked nominal agents become empire agents; empire agents
        # whose locks loosen fall back out — empires can crumble.
        captured = nominal & (pop.scc_lock >= 1.0)
        pop.empire[captured] = True
        released = alive & pop.empire & (pop.scc_lock < cfg.empire_release_lock)
        pop.empire[released] = False

        # ---- 2. formation dynamics ------------------------------------
        # Remnant deepens slowly (faster under hardship), everyone else
        # erodes toward the ambient comfort level.
        hardship = (env.crisis_active + env.persecution)[reg]
        pop.formation[remnant] += 0.004 + 0.006 * hardship[remnant]
        pop.formation[nominal] -= 0.002 * env.comfort[reg][nominal]
        np.clip(pop.formation, 0.0, 1.0, out=pop.formation)

        # ---- 2b. delusion: personal blindness --------------------------
        # Grows out of the systems around each person (dampened by their
        # own formation); broken person-to-person by encountering a
        # witness, and ambiently when crisis or revival exposes the lie.
        crisis_r = env.crisis_active[reg]
        revival_r = env.revival_active[reg]
        whisper = (cfg.adversary_delusion_gain * self.adversary.power
                   if self.adversary is not None else 0.0)
        d_del = ((cfg.delusion_growth_vamphoric * vamp
                  + cfg.delusion_growth_comfort * env.comfort[reg]
                  + whisper)
                 * (1.0 - 0.5 * pop.formation)
                 - cfg.delusion_exposure_crisis * crisis_r
                 - cfg.delusion_exposure_revival * revival_r)
        pop.delusion[alive] += d_del[alive]
        # The encounter: one conversation with someone who names the
        # drain and the fork — blindness breaks one person at a time.
        p_witness = (cfg.witness_contact_rate
                     * np.sqrt(np.clip(agg["deep_share"], 0, 1)))[reg]
        met_witness = alive & (rng.random(pop.capacity) < p_witness)
        pop.delusion[met_witness] -= cfg.witness_break
        # The formed see ever clearer.
        pop.delusion[remnant] -= (cfg.delusion_formation_clarity
                                  * pop.formation[remnant])
        np.clip(pop.delusion, 0.0, 1.0, out=pop.delusion)

        # ---- 3. conversion (contact + receptivity + revival cascade) --
        # Awareness gates turning PER PERSON: contact and openness cannot
        # convert a heart that does not know it is dying. A small floor
        # remains — grace can reach even the blind, just rarely. Revivals
        # therefore sweep those who can see and leave a hardened core.
        contact = (agg["remnant_share"]
                   * np.maximum(agg["remnant_formation"], 0.2))
        boost = 1.0 + cfg.revival_conversion_boost * env.revival_active
        aware_i = 1.0 - cfg.awareness_blindness_cap * pop.delusion
        p_conv = ((cfg.conversion_base * contact * env.receptivity
                   * boost)[reg]
                  * (0.05 + 0.95 * aware_i))
        convertible = alive & ~pop.born & ~pop.empire
        converts = convertible & (rng.random(pop.capacity) < p_conv)
        if converts.any():
            pop.born[converts] = True
            pop.formation[converts] = np.clip(
                pop.formation[converts] + cfg.conversion_formation_gift, 0, 1)
            pop.scc_lock[converts] *= 0.5
            counters["conversions"] = int(converts.sum())

        # ---- 4. apostasy (comfort-drift and fear under persecution) ---
        p_apost = ((cfg.apostasy_base * env.comfort[reg]
                    + cfg.fear_apostasy * env.persecution[reg])
                   * (1.0 - pop.formation) * (0.5 + pop.scc_lock))
        falling = remnant & (rng.random(pop.capacity) < p_apost)
        if falling.any():
            pop.born[falling] = False
            counters["apostasies"] = int(falling.sum())

        # ---- 5. martyrdom under persecution ---------------------------
        visible = remnant & (pop.formation > 0.6)
        p_mart = cfg.martyr_rate * env.persecution[reg]
        martyred = visible & (rng.random(pop.capacity) < p_mart)
        if martyred.any():
            pop.alive[martyred] = False
            pop.martyr[martyred] = True
            counters["martyrs"] = int(martyred.sum())
            m_count = np.bincount(reg[martyred], minlength=n_regions)
            martyr_share = m_count / np.maximum(agg["pop"], 1.0)
            env.martyr_seed(martyr_share * 50.0)
            # Martyrdom is exposure that cannot be argued with: delusion
            # breaks across the whole region where the blood falls.
            m_break = (cfg.martyr_delusion_break * martyr_share * 50.0)[reg]
            pop.delusion[alive] = np.clip(
                pop.delusion[alive] - m_break[alive], 0.0, 1.0)

        # ---- 5b. accusation: the deep remnant sifted like wheat --------
        if accuse_region is not None:
            sifted = remnant & (reg == accuse_region) & (pop.formation > 0.6)
            pop.agency[sifted] = np.maximum(
                0.0, pop.agency[sifted] - cfg.accuse_agency_drain)
            pop.pride[sifted] = np.minimum(
                1.0, pop.pride[sifted] + cfg.accuse_pride_gain)

        # ---- 6. schism defection: institutionalized remnant falls back -
        for r in schism_regions:
            members = np.flatnonzero(remnant & (reg == r))
            k = int(len(members) * cfg.schism_defection)
            if k:
                # The least-formed members are likeliest to drift out.
                weights = 1.0 - pop.formation[members] + 0.05
                weights /= weights.sum()
                lost = rng.choice(members, size=k, replace=False, p=weights)
                pop.born[lost] = False

        # ---- 7. demography --------------------------------------------
        pop.age[pop.alive] += 1
        deaths = pop.deaths(env.crisis_active)
        births = pop.births(env.comfort)
        moved = pop.migrate(env.attractiveness(), env.neighbors)

        # ---- 7b. atonement: the trap broken from within ----------------
        agg_after = pop.regional_aggregates(n_regions)
        if (cfg.enable_atonement and self.atonement_tick is None):
            self._check_atonement(agg_after)

        # ---- 8. record ---------------------------------------------
        pop_total = agg_after["pop"].sum()
        weights = agg_after["pop"] / max(pop_total, 1.0)
        row = {
            "tick": self.tick,
            "distance": float(env.distance @ weights),
            "nearness": float(env.nearness @ weights),
            "rebellion": float(env.rebellion @ weights),
            "entropy": float(env.entropy @ weights),
            "vamphoric": float(env.vamphoric @ weights),
            "unity": float(env.unity @ weights),
            "comfort": float(env.comfort @ weights),
            "receptivity": float(env.receptivity @ weights),
            "delusion": float(env.delusion @ weights),
            "awareness": float(env.awareness @ weights),
            "persecution": float(env.persecution @ weights),
            "strain": float(env.strain @ weights),
            "remnant_share": float(agg_after["remnant_share"] @ weights),
            "empire_share": float(agg_after["empire_share"] @ weights),
            "population": int(pop_total),
            "crises_active": int(env.crisis_active.sum()),
            "revivals_active": int(env.revival_active.sum()),
            "adversary_power": (self.adversary.power
                                if self.adversary else 0.0),
            "adversary_exposure": (self.adversary.exposure
                                   if self.adversary else 0.0),
            "conversions": counters["conversions"],
            "apostasies": counters["apostasies"],
            "martyrs": counters["martyrs"],
            "deaths": deaths,
            "births": births,
            "migrants": moved,
        }
        for r, name in enumerate(env.names):
            row[f"distance_{name}"] = float(env.distance[r])
            row[f"remnant_{name}"] = float(agg_after["remnant_share"][r])
        self.history.append(row)

        self._check_endings(row)
        self.tick += 1

    # ------------------------------------------------------------------
    def _check_atonement(self, agg: dict):
        """The fullness of time — state conditions, never a date.

        The trap must be fully sprung (the record of rebellion heavy
        across the world) AND a prepared vessel must exist: a region
        holding a deeply formed remnant under drawn-near presence. Then
        the trap is broken from within, once, for all regions.
        """
        cfg, env = self.cfg, self.env
        weights = agg["pop"] / max(agg["pop"].sum(), 1.0)
        record_weight = float(env.rebellion @ weights)
        if record_weight < cfg.atonement_rebellion_trigger:
            return

        vessel_mask = ((agg["deep_share"] >= cfg.atonement_vessel_deep)
                       & (env.nearness >= cfg.atonement_vessel_nearness))
        if not vessel_mask.any():
            return
        vessel = int(np.argmax(np.where(vessel_mask, env.nearness, -1.0)))

        # The record of debt cancelled — for every region, from one.
        env.rebellion *= (1.0 - cfg.atonement_rebellion_clear)
        # The veil torn.
        floor = np.clip(cfg.ratchet_floor_gain * env.rebellion, 0.0, 0.6)
        env.distance = np.clip(
            env.distance - cfg.atonement_distance_break, floor, 1.0)
        # The indwelling begins: presence jumps and its floor rises.
        env.nearness = np.clip(
            env.nearness + cfg.atonement_nearness_gift, 0.0, 1.0)
        env.nearness_floor_bonus = cfg.atonement_nearness_floor_gain
        # Grace now covers part of what would otherwise stick.
        env.grace_factor = cfg.atonement_grace
        # The Light has come — delusion breaks worldwide.
        self.pop.delusion = np.clip(
            self.pop.delusion - cfg.atonement_delusion_break, 0.0, 1.0)
        # The accuser disarmed (Col 2:15).
        if self.adversary is not None:
            self.adversary.disarmed = True

        self.atonement_tick = self.tick
        env.events.append({
            "tick": self.tick, "region": env.names[vessel],
            "type": "atonement",
            "detail": (f"record weight {record_weight:.2f} cancelled "
                       f"{cfg.atonement_rebellion_clear:.0%}; "
                       "the accuser disarmed")})

    def _check_endings(self, row: dict):
        """State-only terminal attractors on covenant distance. No dates.

        Renewal must hold much longer than consummation: a spike of
        nearness is not the new creation — it has to survive the comfort
        loop that has undone every golden age before it.
        """
        cfg = self.cfg

        if (row["distance"] >= cfg.consummation_distance
                or row["remnant_share"] <= cfg.consummation_remnant_floor):
            self._ending_streak["consummation"] += 1
        else:
            self._ending_streak["consummation"] = 0

        # Renewal lands AT the ratchet floor, never beneath it: the
        # ceiling rises with the accumulated weight of history, so a
        # late-age world can still renew — carrying its scars with it.
        renewal_ceiling = max(
            cfg.renewal_distance_ceiling,
            cfg.ratchet_floor_gain * row["rebellion"] + 0.08)
        if (row["remnant_share"] >= cfg.renewal_remnant
                and row["distance"] <= renewal_ceiling):
            self._ending_streak["renewal"] += 1
        else:
            self._ending_streak["renewal"] = 0

        sustain = {"consummation": cfg.consummation_sustain_ticks,
                   "renewal": cfg.renewal_sustain_ticks}
        for name, streak in self._ending_streak.items():
            if streak >= sustain[name] and self.ending is None:
                self.ending = name
                self.env.events.append({
                    "tick": self.tick, "region": "GLOBAL",
                    "type": name,
                    "detail": (f"distance {row['distance']:.3f}, "
                               f"remnant {row['remnant_share']:.3f}")})

    # ------------------------------------------------------------------
    def run(self, verbose: bool = True) -> pd.DataFrame:
        while self.tick < self.cfg.n_ticks and self.ending is None:
            self.step()
            if verbose and self.tick % 100 == 0:
                r = self.history[-1]
                print(f"  tick {r['tick']:4d}  distance={r['distance']:.3f}  "
                      f"nearness={r['nearness']:.3f}  "
                      f"remnant={r['remnant_share']*100:5.1f}%  "
                      f"pop={r['population']}")
        return pd.DataFrame(self.history)

    def get_events_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.env.events)

    def get_summary(self) -> dict:
        if not self.history:
            return {}
        last = self.history[-1]
        events = self.get_events_df()
        by_type = (events["type"].value_counts().to_dict()
                   if not events.empty else {})
        return {
            "ticks_run": self.tick,
            "ending": self.ending or "contested (tick limit reached)",
            "final_distance": last["distance"],
            "final_nearness": last["nearness"],
            "final_rebellion": last["rebellion"],
            "final_delusion": last["delusion"],
            "final_entropy": last["entropy"],
            "final_remnant_share": last["remnant_share"],
            "final_population": last["population"],
            "total_conversions": sum(h["conversions"] for h in self.history),
            "total_apostasies": sum(h["apostasies"] for h in self.history),
            "total_martyrs": sum(h["martyrs"] for h in self.history),
            "atonement_tick": self.atonement_tick,
            "schemes_run": (dict(self.adversary.schemes_run)
                            if self.adversary else {}),
            "events_by_type": by_type,
        }
