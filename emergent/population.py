"""Vectorized agent population.

Agents live in parallel numpy arrays (struct-of-arrays) instead of Python
objects, so 10k+ agents update in microseconds per tick. Dead agents leave
free slots that newborns reuse, keeping memory flat over long runs.
"""

import numpy as np

from .config import EmergentConfig


class Population:
    def __init__(self, cfg: EmergentConfig, rng: np.random.Generator):
        self.cfg = cfg
        self.rng = rng
        n_regions = len(cfg.regions)

        capacity = int(cfg.n_agents * cfg.capacity_factor * 1.25)
        self.capacity = capacity

        self.alive = np.zeros(capacity, dtype=bool)
        self.region = np.zeros(capacity, dtype=np.int16)
        self.age = np.zeros(capacity, dtype=np.int16)
        self.formation = np.zeros(capacity, dtype=np.float64)
        self.scc_lock = np.zeros(capacity, dtype=np.float64)
        self.agency = np.zeros(capacity, dtype=np.float64)
        self.pride = np.zeros(capacity, dtype=np.float64)
        self.born = np.zeros(capacity, dtype=bool)    # born-from-above
        self.empire = np.zeros(capacity, dtype=bool)  # fully captured agents
        self.martyr = np.zeros(capacity, dtype=bool)  # died as martyr
        # The skin of the apple: blindness in two layers. The skin is
        # the secular coating (brittle, recent); the flesh is the
        # ancient three-realm default (deep, distorting, entry-pointed).
        self.skin = np.zeros(capacity, dtype=np.float64)
        self.flesh = np.zeros(capacity, dtype=np.float64)
        self.seed = np.zeros(capacity, dtype=bool)    # bearer of the promise

        self.seed_passes = 0   # times the seed passed at a bearer's death
        self.seed_raised = 0   # times it was raised from the stones

        # Regional carrying capacities, fixed from the initial seeding.
        self.region_capacity = np.zeros(n_regions, dtype=np.int64)

        self._seed_initial(n_regions)

    def _seed_initial(self, n_regions: int):
        cfg, rng = self.cfg, self.rng
        shares = np.array([r.population_share for r in cfg.regions])
        shares = shares / shares.sum()
        counts = np.maximum(1, (shares * cfg.n_agents).astype(int))

        idx = 0
        for r, count in enumerate(counts):
            sl = slice(idx, idx + count)
            init = cfg.regions[r]
            self.alive[sl] = True
            self.region[sl] = r
            self.age[sl] = rng.integers(0, 80, count)
            self.formation[sl] = np.clip(
                rng.normal(init.formation_mean, init.formation_std, count),
                0.0, 1.0)
            self.scc_lock[sl] = np.clip(
                rng.normal(init.vamphoric * 0.7, 0.1, count), 0.0, 0.95)
            self.agency[sl] = rng.uniform(0.6, 1.0, count)
            self.pride[sl] = rng.beta(2, 5, count)
            self.born[sl] = rng.random(count) < init.born_rate
            # Pre-modern worlds: no secular skin yet, flesh default on.
            self.skin[sl] = np.clip(rng.normal(0.03, 0.02, count), 0.0, 0.3)
            self.flesh[sl] = np.clip(rng.normal(0.30, 0.12, count), 0.0, 0.9)
            idx += count

            self.region_capacity[r] = int(count * cfg.capacity_factor)

        # Remnant agents start with a formation floor — conversion forms.
        seeded = self.alive & self.born
        self.formation[seeded] = np.maximum(self.formation[seeded], 0.35)

        # Eve's promise: one bearer of the seed from the very beginning.
        if cfg.seed_bearer:
            self._appoint_bearer(initial=True)

    def _appoint_bearer(self, initial: bool = False) -> str:
        """Place the seed on the best living candidate. Returns how:
        'passed' (to a living remnant) or 'raised' (from the stones)."""
        cfg = self.cfg
        self.seed[:] = False
        candidates = np.flatnonzero(self.alive & self.born)
        if candidates.size:
            bearer = candidates[int(np.argmax(self.formation[candidates]))]
            how = "passed"
        else:
            living = np.flatnonzero(self.alive)
            if living.size == 0:
                return "none"
            blindness = self.skin[living] + self.flesh[living]
            bearer = living[int(np.argmin(blindness))]
            self.born[bearer] = True
            how = "raised"
        self.seed[bearer] = True
        self.formation[bearer] = max(self.formation[bearer],
                                     cfg.seed_formation_floor)
        self.skin[bearer] = 0.0
        self.flesh[bearer] = min(self.flesh[bearer], 0.1)
        self.empire[bearer] = False
        if not initial:
            self.seed_passes += 1
            if how == "raised":
                self.seed_raised += 1
        return how

    def maintain_seed(self) -> str:
        """Invariant: there is always exactly one living seed-bearer.
        Called after deaths each tick; the promise is kept formed."""
        if not self.cfg.seed_bearer:
            return "disabled"
        alive_bearer = self.alive & self.seed
        if alive_bearer.any():
            b = np.flatnonzero(alive_bearer)
            self.formation[b] = np.maximum(self.formation[b],
                                           self.cfg.seed_formation_floor)
            return "held"
        return self._appoint_bearer()

    # ------------------------------------------------------------------
    # Aggregates the environment needs each tick
    # ------------------------------------------------------------------
    def regional_aggregates(self, n_regions: int) -> dict:
        alive = self.alive
        reg = self.region

        pop = np.bincount(reg[alive], minlength=n_regions).astype(float)
        safe_pop = np.maximum(pop, 1.0)

        remnant_mask = alive & self.born & ~self.empire
        remnant = np.bincount(reg[remnant_mask], minlength=n_regions).astype(float)

        empire = np.bincount(reg[alive & self.empire],
                             minlength=n_regions).astype(float)

        # Divine labor output: voltage x formation x agency, per remnant agent.
        voltage = self.voltage()
        labor_w = np.where(remnant_mask,
                           voltage * self.formation * self.agency, 0.0)
        labor = np.bincount(reg, weights=labor_w, minlength=n_regions)

        # "Praying" fuel for revival tension: deep-formation remnant share.
        deep_mask = remnant_mask & (self.formation > 0.65)
        deep = np.bincount(reg[deep_mask], minlength=n_regions).astype(float)

        # Mean formation of the remnant (for reporting / schism logic).
        rem_form_sum = np.bincount(
            reg, weights=np.where(remnant_mask, self.formation, 0.0),
            minlength=n_regions)

        # Regional ambient blindness: skin blocks hearing entirely,
        # flesh distorts it but leaves entry points.
        aware = self.awareness()
        blind_sum = np.bincount(
            reg, weights=np.where(alive, 1.0 - aware, 0.0),
            minlength=n_regions)
        # Exposed flesh — the ancient battlefield reopened wherever the
        # skin has cracked. The parasite's home turf.
        exposed_sum = np.bincount(
            reg, weights=np.where(alive,
                                  self.flesh * (1.0 - self.skin), 0.0),
            minlength=n_regions)
        skin_sum = np.bincount(
            reg, weights=np.where(alive, self.skin, 0.0),
            minlength=n_regions)

        return {
            "pop": pop,
            "remnant_share": remnant / safe_pop,
            "empire_share": empire / safe_pop,
            "labor_share": labor / safe_pop,
            "deep_share": deep / safe_pop,
            "remnant_formation": rem_form_sum / np.maximum(remnant, 1.0),
            "delusion": blind_sum / safe_pop,
            "flesh_exposed": exposed_sum / safe_pop,
            "skin": skin_sum / safe_pop,
        }

    def awareness(self) -> np.ndarray:
        """Per-agent awareness: the skin blocks hearing entirely; the
        flesh distorts what is heard but leaves entry points open."""
        return ((1.0 - self.skin)
                * (1.0 - self.cfg.flesh_opacity * self.flesh))

    def voltage(self) -> np.ndarray:
        """Effective spiritual output multiplier per agent."""
        v = 1.0 - 0.5 * self.scc_lock - 0.3 * self.pride
        return np.clip(v, 0.1, 1.0) * (0.4 + 0.6 * self.formation)

    # ------------------------------------------------------------------
    # Demography
    # ------------------------------------------------------------------
    def deaths(self, crisis_active: np.ndarray) -> np.ndarray:
        """Natural + crisis mortality. Returns indices of the dead, so the
        faithful among them can be counted into the covering."""
        cfg, rng = self.cfg, self.rng
        alive_idx = np.flatnonzero(self.alive)
        if alive_idx.size == 0:
            return alive_idx
        age = self.age[alive_idx].astype(float)
        p = (cfg.mortality_base +
             cfg.mortality_gompertz_a * np.exp(cfg.mortality_gompertz_b * age))
        p += cfg.crisis_mortality * crisis_active[self.region[alive_idx]]
        died = alive_idx[rng.random(alive_idx.size) < np.clip(p, 0, 0.6)]
        self.alive[died] = False
        return died

    def births(self, comfort: np.ndarray) -> int:
        """Spawn newborns into free slots, inheriting formation imperfectly.

        Children of comfortable eras form weaker — this is where secular
        drift comes from, generation by generation, with no date trend.
        """
        cfg, rng = self.cfg, self.rng
        n_regions = len(cfg.regions)
        alive = self.alive
        pop = np.bincount(self.region[alive], minlength=n_regions)

        # Logistic damping toward regional carrying capacity.
        headroom = np.clip(1.0 - pop / np.maximum(self.region_capacity, 1), 0, 1)
        expected = pop * cfg.fertility * headroom
        n_births = rng.poisson(expected)

        total = int(n_births.sum())
        if total == 0:
            return 0

        free = np.flatnonzero(~self.alive)
        if free.size < total:
            total = free.size  # capacity is the hard ceiling
        slots = free[:total]

        # Regional mean formation of living adults (the ambient culture).
        form_sum = np.bincount(self.region[alive],
                               weights=self.formation[alive],
                               minlength=n_regions)
        region_mean = form_sum / np.maximum(pop, 1)
        skin_sum = np.bincount(self.region[alive],
                               weights=self.skin[alive],
                               minlength=n_regions)
        region_mean_skin = skin_sum / np.maximum(pop, 1)
        flesh_sum = np.bincount(self.region[alive],
                                weights=self.flesh[alive],
                                minlength=n_regions)
        region_mean_flesh = flesh_sum / np.maximum(pop, 1)

        # Assign regions to slots according to per-region birth counts.
        birth_regions = np.repeat(np.arange(n_regions), n_births)[:total]

        # Each child gets a random living "parent" from its region.
        parent_form = np.empty(total)
        parent_born = np.zeros(total, dtype=bool)
        parent_skin = np.full(total, 0.05)
        parent_flesh = np.full(total, 0.3)
        for r in range(n_regions):
            mask = birth_regions == r
            k = int(mask.sum())
            if k == 0:
                continue
            candidates = np.flatnonzero(alive & (self.region == r))
            if candidates.size:
                # Devout households bear more children — a small, real
                # demographic edge that lets the remnant persist without
                # any scripted help.
                pw = 1.0 + cfg.fertility_remnant_bonus * self.born[candidates]
                pw = pw / pw.sum()
                parents = rng.choice(candidates, size=k, p=pw)
                parent_form[mask] = self.formation[parents]
                parent_born[mask] = self.born[parents]
                parent_skin[mask] = self.skin[parents]
                parent_flesh[mask] = self.flesh[parents]
            else:
                parent_form[mask] = region_mean[r]

        w = cfg.inheritance_weight
        child_form = (w * parent_form
                      + (1 - w) * region_mean[birth_regions]
                      - cfg.comfort_erosion * comfort[birth_regions]
                      + rng.normal(0, cfg.formation_noise, total))

        # Covenant-household transmission: remnant parents usually raise
        # remnant children — but weak formation and ambient comfort both
        # erode the handoff. Secular drift happens right here, one
        # generation at a time, with no date-based trend anywhere.
        excess_comfort = np.maximum(
            comfort[birth_regions] - cfg.transmission_comfort_floor, 0.0)
        p_transmit = np.clip(
            cfg.household_transmission * (0.5 + 0.5 * parent_form)
            - cfg.transmission_comfort_penalty * excess_comfort,
            0.0, 0.97)
        child_born = parent_born & (rng.random(total) < p_transmit)

        self.alive[slots] = True
        self.region[slots] = birth_regions
        self.age[slots] = 0
        self.formation[slots] = np.clip(child_form, 0.0, 1.0)
        self.scc_lock[slots] = rng.uniform(0.0, 0.2, total)
        self.agency[slots] = 1.0
        self.pride[slots] = rng.beta(2, 5, total)
        self.born[slots] = child_born
        self.empire[slots] = False
        self.martyr[slots] = False
        self.seed[slots] = False  # the seed passes at death, never at birth
        # Blindness is raised, not chosen: children start inside their
        # parents' frame, blended with the ambient culture's — the
        # secular coating and the ancient default each inherited.
        w_s = cfg.skin_inheritance
        self.skin[slots] = np.clip(
            w_s * parent_skin + (1 - w_s) * region_mean_skin[birth_regions]
            + rng.normal(0, 0.03, total), 0.0, 1.0)
        w_f = cfg.delusion_inheritance
        self.flesh[slots] = np.clip(
            w_f * parent_flesh + (1 - w_f) * region_mean_flesh[birth_regions]
            + rng.normal(0, 0.05, total), 0.0, 1.0)
        return total

    def migrate(self, attractiveness: np.ndarray,
                neighbors: list) -> int:
        """A small fraction of agents moves toward better neighbors."""
        cfg, rng = self.cfg, self.rng
        alive_idx = np.flatnonzero(self.alive)
        movers = alive_idx[rng.random(alive_idx.size) < cfg.migration_rate]
        moved = 0
        for i in movers:
            r = self.region[i]
            if not neighbors[r]:
                continue
            best = max(neighbors[r], key=lambda n: attractiveness[n])
            if attractiveness[best] > attractiveness[r] + 0.05:
                self.region[i] = best
                moved += 1
        return moved
