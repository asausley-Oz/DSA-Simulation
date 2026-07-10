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

from .config import EmergentConfig
from .environment import Environment
from .population import Population


class EmergentSimulation:
    def __init__(self, cfg: Optional[EmergentConfig] = None):
        self.cfg = cfg or EmergentConfig()
        self.rng = np.random.default_rng(self.cfg.seed)
        self.env = Environment(self.cfg, self.rng)
        self.pop = Population(self.cfg, self.rng)

        self.tick = 0
        self.history: List[dict] = []
        self.ending: Optional[str] = None
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

        # ---- 3. conversion (contact + receptivity + revival cascade) --
        contact = (agg["remnant_share"]
                   * np.maximum(agg["remnant_formation"], 0.2))
        boost = 1.0 + cfg.revival_conversion_boost * env.revival_active
        p_conv = (cfg.conversion_base * contact * env.receptivity * boost)[reg]
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

        # ---- 8. record ---------------------------------------------
        agg_after = pop.regional_aggregates(n_regions)
        pop_total = agg_after["pop"].sum()
        weights = agg_after["pop"] / max(pop_total, 1.0)
        row = {
            "tick": self.tick,
            "entropy": float(env.entropy @ weights),
            "vamphoric": float(env.vamphoric @ weights),
            "unity": float(env.unity @ weights),
            "comfort": float(env.comfort @ weights),
            "receptivity": float(env.receptivity @ weights),
            "persecution": float(env.persecution @ weights),
            "strain": float(env.strain @ weights),
            "remnant_share": float(agg_after["remnant_share"] @ weights),
            "empire_share": float(agg_after["empire_share"] @ weights),
            "population": int(pop_total),
            "crises_active": int(env.crisis_active.sum()),
            "revivals_active": int(env.revival_active.sum()),
            "conversions": counters["conversions"],
            "apostasies": counters["apostasies"],
            "martyrs": counters["martyrs"],
            "deaths": deaths,
            "births": births,
            "migrants": moved,
        }
        for r, name in enumerate(env.names):
            row[f"entropy_{name}"] = float(env.entropy[r])
            row[f"remnant_{name}"] = float(agg_after["remnant_share"][r])
        self.history.append(row)

        self._check_endings(row)
        self.tick += 1

    # ------------------------------------------------------------------
    def _check_endings(self, row: dict):
        """State-only terminal attractors. No dates, only sustained state."""
        cfg = self.cfg

        if (row["entropy"] >= cfg.consummation_entropy
                or row["remnant_share"] <= cfg.consummation_remnant_floor):
            self._ending_streak["consummation"] += 1
        else:
            self._ending_streak["consummation"] = 0

        if (row["remnant_share"] >= cfg.renewal_remnant
                and row["entropy"] <= cfg.renewal_entropy_ceiling):
            self._ending_streak["renewal"] += 1
        else:
            self._ending_streak["renewal"] = 0

        for name, streak in self._ending_streak.items():
            if streak >= cfg.ending_sustain_ticks and self.ending is None:
                self.ending = name
                self.env.events.append({
                    "tick": self.tick, "region": "GLOBAL",
                    "type": name,
                    "detail": (f"entropy {row['entropy']:.3f}, "
                               f"remnant {row['remnant_share']:.3f}")})

    # ------------------------------------------------------------------
    def run(self, verbose: bool = True) -> pd.DataFrame:
        while self.tick < self.cfg.n_ticks and self.ending is None:
            self.step()
            if verbose and self.tick % 100 == 0:
                r = self.history[-1]
                print(f"  tick {r['tick']:4d}  entropy={r['entropy']:.3f}  "
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
            "final_entropy": last["entropy"],
            "final_remnant_share": last["remnant_share"],
            "final_population": last["population"],
            "total_conversions": sum(h["conversions"] for h in self.history),
            "total_apostasies": sum(h["apostasies"] for h in self.history),
            "total_martyrs": sum(h["martyrs"] for h in self.history),
            "events_by_type": by_type,
        }
