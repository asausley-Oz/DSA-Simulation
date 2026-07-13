"""Orchestrator for the Emergent Covenant Engine.

Tick order:
  1. read agent aggregates
  2. environment updates itself from them (and fires emergent events)
  3. environment pressures flow back onto agents (drain, conversion,
     apostasy, martyrdom, revival cascades, schism defection)
  4. demography (deaths, births with generational transmission, migration)
  5. record history; check state-only ending conditions

There is no calendar anywhere in this loop, and no world exits history:
every run ends in the consummation of the age — the Shaking — arriving
one of three ways: CONSUMMATION (the blind death, the account unpaid),
PAROUSIA (the days cut short amid the tribulation), or FULLNESS (the
harvest complete, "and then the end will come," Matt 24:14). A run that
hits the tick limit is merely contested — the end not yet arrived.
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
        # The v7.6 sequence: incarnation -> deicide -> atonement.
        self.incarnation_tick: Optional[int] = None
        self.incarnation_region: Optional[int] = None
        self.deicide_tick: Optional[int] = None
        self.atonement_tick: Optional[int] = None
        # The store of faith: every believer who lives and dies before
        # the atonement is counted into the covering (Heb 11:39-40).
        self.faith_store = 0.0
        # THE ACCOUNT (Macro Cup): every unit of rebellion ever enacted,
        # never decaying, never erased — presented and PAID at the
        # deicide (Col 2:14). The TAV seals the old aeon's condemnation.
        self.account = 0.0
        self.account_paid = False
        # THE TWO SUBSTANCES: what the passing age builds (wood-hay)
        # and what is laid up unshakeable (treasure) — divine labor,
        # the faithful dead, the martyrs banked double. The Shaking
        # measures what remains (1 Cor 3:12-15, Heb 12:27).
        self.treasure = 0.0
        self.wood_hay = 0.0
        # Patience (2 Pet 3:9): post-atonement, the end is held open
        # while the world still responds. Exhausted patience ends in
        # the great falling away (2 Thess 2).
        self.patience_active = False
        self.falling_away_tick: Optional[int] = None
        self.fullness_tick: Optional[int] = None  # the harvest complete
        self.tribulation_martyrs = 0   # the souls under the altar (Rev 6:9)
        # The millennium and the descent (Rev 20-21).
        self.millennium_tick: Optional[int] = None
        self.release_tick: Optional[int] = None
        self._harvest_ema = 0.0
        self._dry_streak = 0
        self._ending_streak = {"consummation": 0, "fullness": 0}

    # ------------------------------------------------------------------
    def step(self):
        cfg, rng, env, pop = self.cfg, self.rng, self.env, self.pop
        n_regions = env.n

        agg = pop.regional_aggregates(n_regions)

        # While incarnate, divine labor in the vessel runs at the
        # perfect-image rate — a visible golden thread in one region.
        incarnate = (self.incarnation_region
                     if self.atonement_tick is None else None)
        if incarnate is not None:
            agg["labor_share"] = agg["labor_share"].copy()
            agg["labor_share"][incarnate] += cfg.incarnate_labor_bonus

        _, schism_regions = env.step(agg, self.tick)

        alive = pop.alive
        reg = pop.region
        counters = {"conversions": 0, "apostasies": 0, "martyrs": 0}

        # ---- 0a. the embodied presence --------------------------------
        if incarnate is not None:
            env.nearness[incarnate] = max(env.nearness[incarnate],
                                          cfg.incarnation_nearness_hold)
            # The Light in person: both layers of blindness collapse
            # where He stands — coating and ancient distortion alike.
            local = alive & (reg == incarnate)
            pop.skin[local] = np.maximum(
                0.0, pop.skin[local] - cfg.incarnate_delusion_break)
            pop.flesh[local] = np.maximum(
                0.0, pop.flesh[local] - cfg.incarnate_delusion_break)
            # The presence names the enemy daily.
            if self.adversary is not None:
                self.adversary.exposure = min(
                    1.0, self.adversary.exposure
                    + cfg.incarnate_exposure_gain)

        # ---- 0b. the adversary schemes ---------------------------------
        accuse_region = None
        if self.adversary is not None:
            adv_events, accuse_region, deicide = self.adversary.step(
                env, agg, self.tick, incarnate_region=incarnate)
            env.events.extend(adv_events)
            if deicide and incarnate is not None:
                self._deicide(incarnate)
                incarnate = None

        # He lays it down regardless — no one takes it from Him.
        if (incarnate is not None and self.incarnation_tick is not None
                and self.tick - self.incarnation_tick
                >= cfg.incarnation_max_duration):
            self._spring_atonement(incarnate, cause="laid down freely")
            incarnate = None

        # ---- 0c. the millennium: correspondence at saturation ----------
        # The beloved city hosts the reign; the two Jerusalems in
        # maximal alignment, no merger — the most heaven and earth can
        # share while remaining two. The trap decays under an embodied
        # reign; strain and persecution wither.
        if self.millennium_tick is not None and self.release_tick is None:
            floor = np.clip(cfg.ratchet_floor_gain * env.rebellion, 0.0, 0.6)
            env.distance = np.clip(env.distance - 0.02, floor, 1.0)
            env.strain *= 0.97
            env.persecution *= 0.80
            env.containment *= 0.985

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
        # whose locks loosen fall back out — empires can crumble. The
        # seed-bearer cannot be captured.
        captured = nominal & (pop.scc_lock >= 1.0) & ~pop.seed
        pop.empire[captured] = True
        released = alive & pop.empire & (pop.scc_lock < cfg.empire_release_lock)
        pop.empire[released] = False

        # ---- 2. formation dynamics ------------------------------------
        # Remnant deepens slowly (faster under hardship), everyone else
        # erodes toward the ambient comfort level. Discipleship needs
        # unmediated presence: the Container throttles formation.
        hardship = (env.crisis_active + env.persecution)[reg]
        throttle = (1.0 - cfg.container_formation_throttle
                    * env.containment)[reg]
        pop.formation[remnant] += (0.004 + 0.006 * hardship[remnant]) \
            * throttle[remnant]
        pop.formation[nominal] -= 0.002 * env.comfort[reg][nominal]
        np.clip(pop.formation, 0.0, 1.0, out=pop.formation)

        # ---- 2b. blindness in two layers (the skin of the apple) -------
        crisis_r = env.crisis_active[reg]
        revival_r = env.revival_active[reg]
        whisper = (cfg.adversary_delusion_gain * self.adversary.power
                   if self.adversary is not None else 0.0)

        # THE SKIN: the secular coating grows only where the vamphoric
        # buyout has delivered its comfort — and not on the remnant.
        # Inside the Container the coating is architecture: shocks are
        # metabolized, not transmitted — every crack-channel is muted
        # in proportion to containment.
        transmit = (1.0 - env.containment)[reg]
        d_skin = (cfg.skin_growth * env.comfort[reg] * vamp
                  * (~pop.born).astype(float)
                  - cfg.skin_crack_crisis * crisis_r * transmit
                  - cfg.skin_crack_revival * revival_r * transmit)
        pop.skin[alive] += d_skin[alive]

        # THE FLESH: the ancient default, fed slowly by the systems and
        # the whisper; only discipleship reworks it.
        d_flesh = ((cfg.flesh_growth * vamp + whisper)
                   * (1.0 - 0.5 * pop.formation))
        pop.flesh[alive] += d_flesh[alive]
        pop.flesh[remnant] -= cfg.flesh_clarity * pop.formation[remnant]

        # The encounter: one conversation with someone who names the
        # drain and the fork shatters surface certainty — the skin
        # cracks in a chunk, and what lies beneath is the old cosmos.
        # In the Container, witness is indistinguishable from its
        # simulacra: the encounter loses force as containment grows.
        p_witness = (cfg.witness_contact_rate
                     * np.sqrt(np.clip(agg["deep_share"], 0, 1)))[reg]
        met_witness = alive & (rng.random(pop.capacity) < p_witness)
        pop.skin[met_witness] -= (cfg.skin_crack_witness
                                  * transmit[met_witness])
        pop.flesh[met_witness] -= (cfg.delusion_formation_clarity
                                   * transmit[met_witness])

        np.clip(pop.skin, 0.0, 1.0, out=pop.skin)
        np.clip(pop.flesh, 0.0, 1.0, out=pop.flesh)

        # ---- 3. conversion (contact + receptivity + revival cascade) --
        # Awareness gates turning PER PERSON: contact and openness cannot
        # convert a heart that does not know it is dying. A small floor
        # remains — grace can reach even the blind, just rarely. Revivals
        # therefore sweep those who can see and leave a hardened core.
        contact = (agg["remnant_share"]
                   * np.maximum(agg["remnant_formation"], 0.2))
        boost = 1.0 + cfg.revival_conversion_boost * env.revival_active
        aware_i = pop.awareness()
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
        # The seed-bearer cannot fall away — the promise holds the line.
        falling = remnant & (rng.random(pop.capacity) < p_apost) & ~pop.seed
        if falling.any():
            pop.born[falling] = False
            counters["apostasies"] = int(falling.sum())

        # In the tribulation, deception rises to lead astray — if
        # possible — even the elect (Matt 24:24): every remnant member
        # faces a per-tick apostasy chance shielded only by formation.
        # It ends at the parousia — the millennium knows no sift.
        if (self.falling_away_tick is not None and self.ending is None
                and self.millennium_tick is None):
            p_trib = cfg.tribulation_apostasy * (1.0 - pop.formation)
            led_astray = (remnant & ~pop.seed
                          & (rng.random(pop.capacity) < p_trib))
            if led_astray.any():
                pop.born[led_astray] = False
                counters["apostasies"] += int(led_astray.sum())

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
            in_tribulation = (self.falling_away_tick is not None
                              and self.millennium_tick is None
                              and cfg.tribulation_martyr_mute)
            # Whatever the old world does with the blood, the martyrs
            # are banked double in the unshakeable substance — treasure
            # where moth and rust do not destroy (Matt 6:20).
            self.treasure += (cfg.treasure_martyr
                              * pop.formation[martyred].sum() / cfg.n_agents)
            if in_tribulation:
                # Rev 13:7 — it is given to him to conquer the saints:
                # in the tribulation the martyr seed is muted. The blood
                # falls on ground held by strong delusion and bears no
                # fruit until the vindication. The souls wait under the
                # altar (Rev 6:9) — but their treasure is banked in full.
                self.tribulation_martyrs += counters["martyrs"]
            else:
                env.martyr_seed(martyr_share * 50.0)
                # Martyrdom is exposure that cannot be argued with: the
                # secular coating shatters across the region where the
                # blood falls, and even the old distortion is chipped.
                # In the Container the blood trends instead of speaking.
                m_break = (cfg.martyr_delusion_break
                           * martyr_share * 50.0)[reg] * transmit
                pop.skin[alive] = np.clip(
                    pop.skin[alive] - m_break[alive], 0.0, 1.0)
                pop.flesh[alive] = np.clip(
                    pop.flesh[alive] - 0.5 * m_break[alive], 0.0, 1.0)
            # Martyrs weigh double in the store of faith.
            if self.atonement_tick is None:
                self.faith_store += (cfg.martyr_faith_weight
                                     * pop.formation[martyred].sum()
                                     / cfg.n_agents)

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
        died = pop.deaths(env.crisis_active)
        deaths = int(died.size)
        if deaths:
            faithful = died[pop.born[died]]
            banked = pop.formation[faithful].sum() / cfg.n_agents
            # The faithful dead bank their formation as treasure — and,
            # before the atonement, into the covering to come.
            self.treasure += cfg.treasure_death * banked
            if self.atonement_tick is None:
                self.faith_store += banked

        # The two ledgers of the age: the Account fills with every
        # tick's rebellion; wood-hay with the comfort-economy's output;
        # treasure with the remnant's divine labor.
        weights_now = agg["pop"] / max(agg["pop"].sum(), 1.0)
        self.account += env.last_rebellion_flux
        self.wood_hay += cfg.wood_hay_rate * float(env.comfort @ weights_now)
        self.treasure += (cfg.treasure_labor
                          * float(agg["labor_share"] @ weights_now))
        births = pop.births(env.comfort)
        moved = pop.migrate(env.attractiveness(), env.neighbors)

        # Eve's promise: the seed always has a living bearer — UNTIL the
        # incarnation. The line exists to carry the promise to the
        # vessel; when the Word is made flesh the line is fulfilled,
        # and the promise is no longer carried by blood but poured out.
        if self.incarnation_tick is None:
            how = pop.maintain_seed()
            if how == "raised":
                env.events.append({
                    "tick": self.tick,
                    "region": env.names[int(pop.region[pop.seed][0])],
                    "type": "seed",
                    "detail": ("the remnant line was cut — a bearer "
                               "raised from the stones (Matt 3:9)")})

        # ---- 7b. incarnation: the fullness of time ---------------------
        agg_after = pop.regional_aggregates(n_regions)
        if (cfg.enable_atonement and self.incarnation_tick is None):
            self._check_incarnation(agg_after)

        # ---- 7c. patience and the great falling away -------------------
        if self.patience_active:
            self._update_patience(agg_after, counters["conversions"])

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
            "skin": float(agg_after["skin"] @ weights),
            "flesh_exposed": float(agg_after["flesh_exposed"] @ weights),
            "containment": float(env.containment @ weights),
            "treasure": self.treasure,
            "wood_hay": self.wood_hay,
            "account": self.account,
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
    def _check_incarnation(self, agg: dict):
        """The fullness of time — state conditions, never a date.

        The trap must be fully sprung (the record of rebellion heavy
        across the world) AND a prepared vessel must exist: a region
        holding even a small deeply-formed remnant under drawn-near
        presence. Then God fully enters the convergence point.
        """
        cfg, env = self.cfg, self.env
        weights = agg["pop"] / max(agg["pop"].sum(), 1.0)
        record_weight = float(env.rebellion @ weights)
        if record_weight < cfg.incarnation_rebellion_trigger:
            return

        vessel_mask = ((agg["deep_share"] >= cfg.incarnation_vessel_deep)
                       & (env.nearness >= cfg.incarnation_vessel_nearness))

        # Election: the line of promise itself suffices as vessel — a
        # lone Mary in a backwater qualifies where whole churches are
        # not required. But the world must still receive the visitation:
        # the bearer's region needs the full measure of drawn-near
        # presence, or the fullness of time does not come (a hardened
        # world can hold the seed and still refuse the Son).
        if cfg.seed_bearer:
            bearer = np.flatnonzero(self.pop.alive & self.pop.seed)
            if bearer.size:
                r_b = int(self.pop.region[bearer[0]])
                if env.nearness[r_b] >= cfg.incarnation_vessel_nearness:
                    vessel_mask[r_b] = True

        if not vessel_mask.any():
            return
        vessel = int(np.argmax(np.where(vessel_mask, env.nearness, -1.0)))

        self.incarnation_tick = self.tick
        self.incarnation_region = vessel
        env.nearness[vessel] = max(env.nearness[vessel],
                                   cfg.incarnation_nearness_hold)
        # The line of the woman is FULFILLED, not continued: the seed
        # it carried has arrived. From here there is no protected
        # bearer — the promise is no longer held by blood.
        self.pop.seed[:] = False
        env.events.append({
            "tick": self.tick, "region": env.names[vessel],
            "type": "incarnation",
            "detail": (f"the Word made flesh — the seed of the woman "
                       f"arrives, the line fulfilled; record weight "
                       f"{record_weight:.2f}, nearness held at "
                       f"{cfg.incarnation_nearness_hold:.2f}")})

    def _deicide(self, vessel: int):
        """His final scheme — the one he cannot resist and cannot
        survive. Darkness at noon, and the trap springs."""
        cfg, env = self.cfg, self.env
        self.deicide_tick = self.tick
        env.distance[vessel] = min(
            1.0, env.distance[vessel] + cfg.deicide_distance_spike)
        env.strain[vessel] += 0.3
        env.events.append({
            "tick": self.tick, "region": env.names[vessel],
            "type": "deicide",
            "detail": ("the fullest expression of cumulative rebellion — "
                       "had they known, they would not have crucified")})
        self._spring_atonement(vessel, cause="deicide")

    def _spring_atonement(self, vessel: int, cause: str):
        """The trap broken from within — retroactive for the faithful.

        The covering scales with the store of faith: every believer who
        lived and died before this tick is counted into it, only
        together made perfect (Heb 11:39-40).
        """
        cfg, env = self.cfg, self.env
        clear = min(0.95, cfg.atonement_base_clear
                    + cfg.atonement_faith_scale * self.faith_store)
        light = min(0.60, cfg.atonement_delusion_break
                    + cfg.atonement_faith_delusion * self.faith_store)

        # The record of debt cancelled — for every region, from one.
        env.rebellion *= (1.0 - clear)
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
        # The Light has come — both layers break worldwide,
        # retroactively brighter for every faithful life in the store.
        self.pop.skin = np.clip(self.pop.skin - light, 0.0, 1.0)
        self.pop.flesh = np.clip(self.pop.flesh - light, 0.0, 1.0)
        # The accuser disarmed (Col 2:15).
        if self.adversary is not None:
            self.adversary.disarmed = True

        self.atonement_tick = self.tick
        self.incarnation_region = None
        # THE TAV — the final letter. The Account is not erased: it is
        # presented and PAID in full (Col 2:14, the record nailed to the
        # cross), and the same stroke seals the old aeon's condemnation
        # (John 12:31). From this tick the passing of the first heavens
        # and earth is irreversible; only the Shaking remains.
        self.account_paid = True
        # The patience of God begins: the end held open for response.
        if self.cfg.patience:
            self.patience_active = True
        env.events.append({
            "tick": self.tick, "region": env.names[vessel],
            "type": "atonement",
            "detail": (f"sprung by {cause}; the TAV — account of "
                       f"{self.account:.1f} presented and paid in full, "
                       f"the old aeon's passing sealed; store of faith "
                       f"{self.faith_store:.2f} -> record cancelled "
                       f"{clear:.0%}, light {light:.2f}")})

    def _update_patience(self, agg: dict, conversions: int):
        """The end is held open while the world still responds. When the
        harvest dries in a world that has not been won, patience is
        exhausted — and the great falling away comes (2 Thess 2)."""
        cfg, pop, env = self.cfg, self.pop, self.env

        # Harvest rate among the still-unconverted field.
        field = np.count_nonzero(pop.alive & ~pop.born & ~pop.empire)
        rate = conversions / max(field, 1)
        self._harvest_ema += 0.1 * (rate - self._harvest_ema)

        pop_total = agg["pop"].sum()
        remnant_share = float(
            (agg["remnant_share"] * agg["pop"]).sum() / max(pop_total, 1.0))

        # A won world is fullness, not dryness — patience is not
        # exhausted by having little field left to harvest.
        if remnant_share >= cfg.patience_remnant_ceiling:
            self._dry_streak = 0
            return
        if self._harvest_ema < cfg.patience_response_floor:
            self._dry_streak += 1
        else:
            self._dry_streak = 0
        if self._dry_streak < cfg.patience_dry_ticks:
            return
        self._the_falling_away(
            f"patience exhausted after {cfg.patience_dry_ticks} dry ticks")

    def _the_falling_away(self, cause: str):
        """THE GREAT FALLING AWAY (2 Thess 2). Fires once, by either
        road: the harvest drying in an unwon world, or the harvest
        COMPLETING — for the day does not come unless the rebellion
        comes first (2 Thess 2:3), even in a world that was won."""
        cfg, pop, env = self.cfg, self.pop, self.env
        self.patience_active = False
        self.falling_away_tick = self.tick
        # The love of many grows cold: the lukewarm fall away.
        lukewarm = (pop.alive & pop.born & ~pop.seed
                    & (pop.formation < cfg.falling_away_formation_bar))
        n_fallen = int(lukewarm.sum())
        pop.born[lukewarm] = False
        # Strong delusion sent on those who refused to love the truth —
        # it strikes the FLESH: not a secular coating but a deep,
        # near-irreversible sealing of the ancient distortion.
        refused = pop.alive & ~pop.born
        pop.flesh[refused] = np.clip(
            pop.flesh[refused] + cfg.strong_delusion, 0.0, 1.0)
        # The restrainer removed — lawlessness unveiled (2 Thess 2:7) —
        # and the strong delusion acquires its substrate: the Container
        # seals across the world.
        env.distance = np.clip(env.distance + cfg.restrainer_removed,
                               0.0, 1.0)
        env.containment = np.clip(
            env.containment + cfg.falling_away_containment, 0.0, 1.0)
        # The adversary released for a little while (Rev 20:3).
        if self.adversary is not None:
            self.adversary.released = True
        env.events.append({
            "tick": self.tick, "region": "GLOBAL",
            "type": "falling_away",
            "detail": (f"{cause}; {n_fallen} grow cold, strong delusion "
                       "sent, the adversary loosed for a little while")})

    def _check_endings(self, row: dict):
        """State-only terminal attractors on covenant distance. No dates.

        Two structural laws of the age, both scriptural, both enforced:
        the gospel reaches its fullness before the end (Matt 24:14),
        AND the day does not come unless the rebellion comes first
        (2 Thess 2:3). Fullness is therefore a STAGE, not an exit: a
        won world's harvest completes — and then the falling away, the
        tribulation, and the parousia. Every atonement-world ends at
        the parousia; every vesselless world in the blind death.
        """
        cfg = self.cfg

        if (row["distance"] >= cfg.consummation_distance
                or row["remnant_share"] <= cfg.consummation_remnant_floor):
            self._ending_streak["consummation"] += 1
        else:
            self._ending_streak["consummation"] = 0
        # The patience of God: while the world still responds, the end
        # is held open — consummation cannot complete (2 Pet 3:9).
        if self.patience_active:
            self._ending_streak["consummation"] = 0

        # Fullness lands AT the ratchet floor, never beneath it: the
        # ceiling rises with the accumulated weight of history.
        renewal_ceiling = max(
            cfg.renewal_distance_ceiling,
            cfg.ratchet_floor_gain * row["rebellion"] + 0.08)
        if (row["remnant_share"] >= cfg.renewal_remnant
                and row["distance"] <= renewal_ceiling):
            self._ending_streak["fullness"] += 1
        else:
            self._ending_streak["fullness"] = 0

        # THE HARVEST COMPLETE: fullness does not end the world — it
        # summons the end. The full number has come in (Rom 11:25),
        # patience's purpose is fulfilled, and the rebellion comes
        # first (2 Thess 2:3), even here — especially here.
        if (self._ending_streak["fullness"] >= cfg.renewal_sustain_ticks
                and self.fullness_tick is None
                and self.atonement_tick is not None):
            self.fullness_tick = self.tick
            self.env.events.append({
                "tick": self.tick, "region": "GLOBAL",
                "type": "fullness",
                "detail": (f"the harvest of the earth is ripe (Rev 14:15)"
                           f" — remnant {row['remnant_share']:.3f}; the "
                           "full number has come in (Rom 11:25), and the "
                           "end is summoned: the rebellion comes first")})
            if self.falling_away_tick is None:
                self._the_falling_away(
                    "the harvest complete — the rebellion comes first "
                    "(2 Thess 2:3)")
        # After the great falling away the verdict is in: tribulation,
        # cut short for the sake of the elect (Matt 24:22) — but the
        # Parousia does not end the world. It opens the sequence of
        # Revelation 20-21: millennium -> release -> Gog and Magog ->
        # the passing away -> the DESCENT.
        if self.falling_away_tick is not None:
            self._ending_streak["fullness"] = 0

            # THE PAROUSIA: the King arrives; the tribulation ends; the
            # accuser is bound with a great chain; the beloved city
            # hosts the reign of the first-resurrection body.
            if (self.millennium_tick is None and self.ending is None
                    and self.tick - self.falling_away_tick
                    >= cfg.parousia_after):
                self.millennium_tick = self.tick
                if self.adversary is not None:
                    self.adversary.released = False
                    self.adversary.bound = True
                self.env.persecution[:] = 0.0
                self.env.nearness_floor_bonus = cfg.millennium_floor_bonus
                # The Container is broken open by the one object it
                # cannot ingest.
                self.env.containment *= 0.3
                self.env.events.append({
                    "tick": self.tick, "region": "GLOBAL",
                    "type": "parousia",
                    "detail": (f"the days cut short for the elect — "
                               f"enduring remnant "
                               f"{row['remnant_share']:.3f} vindicated, "
                               f"{self.tribulation_martyrs} souls under "
                               f"the altar answered in the first "
                               "resurrection; the lawless one destroyed, "
                               "the accuser bound with a great chain — "
                               "the millennium of correspondence begins")})
                return

            # THE RELEASE: he must be loosed for a little while
            # (Rev 20:3,7) — the nations deceived one final time, with
            # no curse, no Container, no excuse: agency isolated from
            # every condition ever built.
            if (self.millennium_tick is not None
                    and self.release_tick is None
                    and self.tick - self.millennium_tick
                    >= cfg.millennium_length):
                self.release_tick = self.tick
                if self.adversary is not None:
                    self.adversary.bound = False
                    self.adversary.released = True
                    self.adversary.power = 0.4
                deceived = (self.pop.alive & ~self.pop.born
                            & ~self.pop.seed)
                self.pop.flesh[deceived] = np.clip(
                    self.pop.flesh[deceived] + cfg.final_deception,
                    0.0, 1.0)
                self.env.strain += 0.5
                self.env.events.append({
                    "tick": self.tick, "region": "GLOBAL",
                    "type": "release",
                    "detail": ("loosed from his prison, he goes out to "
                               "deceive the nations at the four corners "
                               "— Gog and Magog gather against the camp "
                               "of the saints and the beloved city")})
                return

            # GOG AND MAGOG CONSUMED: fire from heaven, not the saints'
            # swords, ends the last rebellion — then the first heaven
            # and earth pass, and the city comes down.
            if (self.release_tick is not None and self.ending is None
                    and self.tick - self.release_tick
                    >= cfg.gog_magog_window):
                pop = self.pop
                besiegers = (pop.alive & ~pop.born
                             & (pop.flesh > 0.6))
                struck = besiegers & (self.rng.random(pop.capacity)
                                      < cfg.fire_from_heaven)
                pop.alive[struck] = False
                if self.adversary is not None:
                    self.adversary.bound = True
                    self.adversary.power = 0.0
                self.ending = "descent"
                self.env.events.append({
                    "tick": self.tick, "region": "GLOBAL",
                    "type": "final_rebellion",
                    "detail": (f"fire came down from heaven and consumed "
                               f"them ({int(struck.sum())} of the "
                               "deceived) — the last rebellion proves "
                               "the division was always agency, never "
                               "conditions; the deceiver is thrown down "
                               "for good")})
                self._the_shaking("descent")
                self.env.events.append({
                    "tick": self.tick, "region": "GLOBAL",
                    "type": "descent",
                    "detail": (f"the holy city, new Jerusalem, coming "
                               f"down out of heaven from God — the "
                               f"treasure ({self.treasure:.2f}) descends "
                               "as the city-who-is-the-people; the tree "
                               "of life restored, Babel healed, the "
                               "face seen; the dwelling of God is with "
                               "man, the gates never shut, and the "
                               "increase never ends")})
                return

        # The blind death: the only ending besides the parousia. No
        # world exits history by getting better — a won world's harvest
        # summons the sequence above; a vesselless world falls here.
        if (self._ending_streak["consummation"]
                >= cfg.consummation_sustain_ticks and self.ending is None):
            self.ending = "consummation"
            detail = (f"distance {row['distance']:.3f}, "
                      f"remnant {row['remnant_share']:.3f}")
            # Even a consummated world does not extinguish the seed:
            # the bearer endures the end (Gen 3:15).
            bearer = np.flatnonzero(self.pop.alive & self.pop.seed)
            if bearer.size:
                r_b = self.env.names[int(self.pop.region[bearer[0]])]
                detail += f"; the seed endures in {r_b}"
            self.env.events.append({
                "tick": self.tick, "region": "GLOBAL",
                "type": "consummation", "detail": detail})
            self._the_shaking("consummation")

    def _the_shaking(self, verdict: str):
        """Every history ends in the same event (Hag 2:6, Heb 12:27):
        the old heavens and earth are shaken; the verdicts differ, the
        shaking does not. What cannot be shaken remains — the fire
        tests each world's work (1 Cor 3:12-15) — and the 8th day
        dawns on the remainder."""
        remains = self.treasure / max(self.treasure + self.wood_hay, 1e-9)
        account_state = ("paid in full at the cross (TAV)"
                         if self.account_paid else
                         f"UNPAID — {self.account:.1f} answered in the fall")
        pop_w = None
        containment = float(self.env.containment.mean())
        container_note = ""
        if containment > 0.4:
            container_note = (f"; the Container (containment "
                              f"{containment:.2f}) is broken open from "
                              "the other side")
        self.env.events.append({
            "tick": self.tick, "region": "GLOBAL",
            "type": "shaking",
            "detail": (f"once more the heavens and the earth are shaken "
                       f"— verdict: {verdict}; the account "
                       f"{account_state}; treasure {self.treasure:.2f} "
                       f"vs wood-hay {self.wood_hay:.2f} -> "
                       f"{remains:.0%} of all that was built remains"
                       f"{container_note}; "
                       f"the 8th day dawns on what cannot be shaken")})

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
            "incarnation_tick": self.incarnation_tick,
            "deicide_tick": self.deicide_tick,
            "atonement_tick": self.atonement_tick,
            "faith_store": round(self.faith_store, 3),
            "seed_passes": self.pop.seed_passes,
            "seed_raised": self.pop.seed_raised,
            "seed_endures": bool((self.pop.alive & self.pop.seed).any()),
            "seed_fulfilled": self.incarnation_tick is not None,
            "fullness_tick": self.fullness_tick,
            "falling_away_tick": self.falling_away_tick,
            "millennium_tick": self.millennium_tick,
            "release_tick": self.release_tick,
            "ending_path": ("harvest" if self.fullness_tick is not None
                            else ("dry" if self.falling_away_tick is not None
                                  else None)),
            "patience_open": self.patience_active,
            "final_skin": last["skin"],
            "final_containment": last["containment"],
            "account": round(self.account, 2),
            "account_paid": self.account_paid,
            "treasure": round(self.treasure, 3),
            "wood_hay": round(self.wood_hay, 3),
            "remains_fraction": round(
                self.treasure / max(self.treasure + self.wood_hay, 1e-9), 4),
            "schemes_run": (dict(self.adversary.schemes_run)
                            if self.adversary else {}),
            "events_by_type": by_type,
        }
