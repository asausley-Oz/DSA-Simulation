"""Coupled regional environment — Covenant Distance formulation (v7.1).

The master equation is relational, not thermodynamic:

    distance(t+1) = distance(t) + rebellion_flux - nearness_flux

Two threads, per CDT: humanity's cumulative movement away (the bent,
amplified by vamphoric systems and empire; ratcheted by cumulative
rebellion that is never fully erased within history) and God's
counter-movement of drawing near (incremental intimacy toward the broken,
sovereign visitations, the pull of nearness). Entropy is demoted to a
DERIVED variable — the physical shadow that relational breach casts on
the world, lagging behind distance.

All state variables are ENDOGENOUS: updated from agent aggregates and
from each other, never from a data table or a calendar. Macro-events are
threshold crossings of accumulators with stochastic ignition — and the
ignition dice at a revival is deliberately where sovereign freedom lives:
conditions make the event possible, they never compel it.
"""

import numpy as np
from typing import List, Tuple

from .config import EmergentConfig


class Environment:
    def __init__(self, cfg: EmergentConfig, rng: np.random.Generator):
        self.cfg = cfg
        self.rng = rng
        n = len(cfg.regions)
        self.n = n
        self.names = [r.name for r in cfg.regions]

        # Neighbor lists from the adjacency edge list.
        self.neighbors: List[List[int]] = [[] for _ in range(n)]
        for a, b in cfg.adjacency:
            self.neighbors[a].append(b)
            self.neighbors[b].append(a)

        # --- covenant distance state (per region) ---
        self.distance = np.array([r.entropy for r in cfg.regions])
        self.nearness = np.full(n, 0.30)   # God's counter-movement
        self.rebellion = np.zeros(n)       # cumulative ratchet, near-permanent

        # --- derived + continuous state (per region) ---
        self.entropy = np.array([r.entropy for r in cfg.regions])
        self.vamphoric = np.array([r.vamphoric for r in cfg.regions])
        self.unity = np.array([r.unity for r in cfg.regions])
        self.comfort = np.array([r.comfort for r in cfg.regions])
        self.receptivity = np.full(n, 0.25)
        self.persecution = np.zeros(n)

        # --- accumulators (the "pressure gauges" behind events) ---
        self.strain = np.zeros(n)            # -> crisis
        self.revival_tension = np.zeros(n)   # -> revival
        self.schism_pressure = np.zeros(n)   # -> schism

        # --- active event countdowns (ticks remaining) ---
        self.crisis_remaining = np.zeros(n, dtype=int)
        self.revival_remaining = np.zeros(n, dtype=int)

        self.events: List[dict] = []

    # ------------------------------------------------------------------
    @property
    def crisis_active(self) -> np.ndarray:
        return (self.crisis_remaining > 0).astype(float)

    @property
    def revival_active(self) -> np.ndarray:
        return (self.revival_remaining > 0).astype(float)

    def attractiveness(self) -> np.ndarray:
        """What migrants move toward: low entropy, no crisis, some comfort."""
        return (1.0 - self.entropy) + 0.5 * self.comfort - 0.8 * self.crisis_active

    # ------------------------------------------------------------------
    def step(self, agg: dict, tick: int) -> List[dict]:
        """Advance environment one tick given agent aggregates."""
        cfg = self.cfg
        new_events: List[dict] = []

        crisis = self.crisis_active
        revival = self.revival_active

        # ==============================================================
        # THE MASTER EQUATION — covenant distance
        # ==============================================================
        # Humanity's thread: the bent (amplified by vamphoric load and by
        # the accumulated weight of rebellion), empire capture, and mass
        # violence — a crisis IS rebellion enacted at scale.
        effective_bent = cfg.bent * (
            (1.0 + cfg.bent_vamphoric_gain * self.vamphoric)
            * (1.0 + cfg.ratchet_bent_gain * self.rebellion))
        rebellion_flux = (
            effective_bent
            + cfg.empire_entropy_push * agg["empire_share"]
            + 0.5 * cfg.crisis_entropy_shock * crisis
        )

        # God's thread: the remnant's response (divine labor multiplied by
        # unity) and the pull of nearness itself. Distance does not heal
        # on its own — it closes only because Someone crosses it.
        nearness_flux = (
            cfg.labor_efficiency * agg["labor_share"] * (1.0 + self.unity)
            + cfg.nearness_pull * self.nearness * (0.5 + 0.5 * self.distance)
            + cfg.revival_entropy_relief * revival
        )

        # Cultural osmosis along adjacency.
        diff = np.zeros(self.n)
        for r in range(self.n):
            if self.neighbors[r]:
                nb_mean = self.distance[list(self.neighbors[r])].mean()
                diff[r] = cfg.distance_diffusion * (nb_mean - self.distance[r])

        # The ratchet: a fraction of every act of rebellion sticks, and is
        # almost never forgotten. It raises the floor under distance —
        # within history the world never returns all the way to Eden.
        self.rebellion = np.clip(
            self.rebellion + cfg.ratchet_rate * rebellion_flux
            - cfg.ratchet_decay, 0.0, cfg.ratchet_cap)
        distance_floor = np.clip(
            cfg.ratchet_floor_gain * self.rebellion, 0.0, 0.6)

        self.distance = np.clip(
            self.distance + rebellion_flux - nearness_flux + diff,
            distance_floor, 1.0)

        # --- nearness: incremental intimacy, departure, visitation ------
        # God draws near to the broken and to the praying remnant; the
        # movement is toward humanity even in rebellion, but comfort that
        # ignores the presence sees the glory slowly depart (Ezekiel 10).
        brokenness = np.clip(0.5 * self.receptivity + 0.3 * self.persecution
                             + 0.2 * crisis, 0.0, 1.0)
        nearness_target = np.clip(
            cfg.nearness_floor + 0.55 * brokenness + 0.40 * agg["deep_share"],
            0.0, 1.0)
        self.nearness += cfg.nearness_relax * (nearness_target - self.nearness)
        self.nearness -= cfg.nearness_departure * np.maximum(
            self.comfort - self.receptivity, 0.0)
        # He remains faithful (2 Tim 2:13) — nearness never fully withdraws.
        self.nearness = np.clip(self.nearness, cfg.nearness_floor * 0.5, 1.0)

        # --- entropy: the physical shadow of relational breach ----------
        # Decay lags distance both ways: breach corrodes the world slowly,
        # and a closed distance rebuilds it slowly. Crises wreck the
        # physical world faster than they change hearts.
        self.entropy = np.clip(
            self.entropy
            + cfg.entropy_shadow_rate * (self.distance - self.entropy)
            + cfg.crisis_entropy_shock * crisis,
            0.0, 1.0)

        # --- vamphoric load: parasitic systems grow in the breach AND in
        # prosperity — the fork is "comfort substituted for transformation."
        # A golden age is never placid; it is the era of the drain that
        # runs undetected. Starved by unity and remnant labor.
        d_vamp = (cfg.vamphoric_growth *
                  (0.5 * self.distance + 1.5 * agg["empire_share"]
                   + cfg.vamphoric_comfort_gain * self.comfort)
                  - cfg.vamphoric_decay *
                  (0.5 * self.unity + agg["labor_share"]))
        self.vamphoric = np.clip(self.vamphoric + d_vamp, 0.0, 1.0)

        # --- comfort: prosperity compounds in calm, crashes in crisis ---
        d_comfort = (cfg.comfort_growth * (1.0 - self.entropy) * (1.0 - crisis)
                     - cfg.comfort_crisis_crash * crisis
                     - 0.002)  # slow upkeep cost
        self.comfort = np.clip(self.comfort + d_comfort, 0.0, 1.0)

        # --- unity: drifts apart in ease, pulls together under suffering ---
        hardship = crisis + self.persecution
        d_unity = (cfg.unity_suffering_gain * hardship * agg["remnant_share"]
                   - cfg.unity_erosion * self.comfort)
        self.unity = np.clip(self.unity + d_unity, 0.05, 1.0)

        # --- receptivity: hardship opens hearts, comfort closes them ---
        target = np.clip(0.20 + 0.45 * crisis + 0.55 * self.persecution
                         + 0.25 * self.entropy - 0.45 * self.comfort,
                         0.0, 1.0)
        self.receptivity += cfg.receptivity_relax * (target - self.receptivity)

        # --- persecution: extractive systems attack a visible minority ---
        visibility = np.sqrt(np.clip(agg["remnant_share"], 0, 1))
        minority = np.clip(1.0 - 2.0 * agg["remnant_share"], 0.0, 1.0)
        pers_target = np.clip(
            cfg.persecution_gain * self.vamphoric
            * (0.3 + agg["empire_share"]) * visibility * minority,
            0.0, 1.0)
        self.persecution += 0.15 * (pers_target - self.persecution)

        # ==============================================================
        # CRISIS: strain accumulates from systemic stress, ignites
        # stochastically past a soft threshold, and spills onto neighbors
        # so conflicts can cascade into world-war-scale clusters.
        # ==============================================================
        # Conflict breeds from the breach itself, not only from the rubble
        # it leaves: strain tracks distance and its physical shadow both.
        breach = 0.5 * self.distance + 0.5 * self.entropy
        d_strain = (cfg.strain_from_breach * breach
                    + cfg.strain_from_vamphoric * self.vamphoric
                    + cfg.strain_from_disunity * (1.0 - self.unity)
                    - cfg.strain_relief * (0.5 + 0.5 * self.comfort))
        self.strain = np.maximum(self.strain + d_strain, 0.0)

        ignition_p = cfg.crisis_base_prob / (
            1.0 + np.exp(-(self.strain - cfg.crisis_strain_midpoint)
                         / cfg.crisis_strain_width))
        for r in range(self.n):
            if self.crisis_remaining[r] == 0 and \
                    self.strain[r] >= cfg.crisis_min_strain and \
                    self.rng.random() < ignition_p[r]:
                lo, hi = cfg.crisis_duration
                self.crisis_remaining[r] = self.rng.integers(lo, hi + 1)
                released = self.strain[r]
                self.strain[r] *= 0.25
                for nb in self.neighbors[r]:
                    self.strain[nb] += cfg.crisis_spillover * released \
                        / max(len(self.neighbors[r]), 1)
                new_events.append({
                    "tick": tick, "region": self.names[r], "type": "crisis",
                    "detail": f"strain {released:.2f} released; "
                              f"duration {self.crisis_remaining[r]}"})

        # ==============================================================
        # REVIVAL: tension = receptivity x praying remnant, builds until
        # it ignites a conversion cascade. Not a dice roll on a flat
        # probability — a slow fuse that crises and martyrdom light.
        # ==============================================================
        # sqrt: a tiny praying remnant still generates real tension —
        # revivals historically erupt from small bands, not majorities.
        fuel = self.receptivity * np.sqrt(np.clip(agg["deep_share"], 0, 1))
        # Tension bleeds off faster in cold (low-receptivity) seasons.
        leak = cfg.revival_tension_leak * (
            1.0 + (self.receptivity < cfg.revival_min_receptivity))
        self.revival_tension = np.maximum(
            self.revival_tension
            + cfg.revival_tension_rate * fuel * cfg.revival_fuel_scale
            - leak, 0.0)

        for r in range(self.n):
            if (self.revival_remaining[r] == 0
                    and self.revival_tension[r] >= cfg.revival_threshold
                    and self.receptivity[r] >= cfg.revival_min_receptivity
                    and self.rng.random() < cfg.revival_ignition_prob):
                lo, hi = cfg.revival_duration
                self.revival_remaining[r] = self.rng.integers(lo, hi + 1)
                self.revival_tension[r] = 0.0
                # A revival IS a sovereign visitation — the ignition dice
                # is where DSA's chosen freedom lives. Nearness jumps.
                self.nearness[r] = min(
                    1.0, self.nearness[r] + cfg.nearness_visitation)
                new_events.append({
                    "tick": tick, "region": self.names[r], "type": "revival",
                    "detail": f"receptivity {self.receptivity[r]:.2f}; "
                              f"nearness {self.nearness[r]:.2f}; "
                              f"duration {self.revival_remaining[r]}"})

        # ==============================================================
        # SCHISM: a large, comfortable, still-unified church builds
        # institutional pressure; past threshold it fractures.
        # ==============================================================
        big_and_soft = ((agg["remnant_share"] > 0.20)
                        & (self.comfort > 0.55)
                        & (self.unity > 0.35))
        self.schism_pressure = np.where(
            big_and_soft,
            self.schism_pressure + self.cfg.schism_pressure_rate
            * (agg["remnant_share"] + self.comfort),
            np.maximum(self.schism_pressure - 0.01, 0.0))

        schisms = []
        for r in range(self.n):
            if self.schism_pressure[r] >= cfg.schism_threshold:
                self.schism_pressure[r] = 0.0
                self.unity[r] = max(0.05, self.unity[r] - cfg.schism_unity_cost)
                schisms.append(r)
                new_events.append({
                    "tick": tick, "region": self.names[r], "type": "schism",
                    "detail": f"unity falls to {self.unity[r]:.2f}"})

        # --- countdown active events ---
        self.crisis_remaining = np.maximum(self.crisis_remaining - 1, 0)
        self.revival_remaining = np.maximum(self.revival_remaining - 1, 0)

        self.events.extend(new_events)
        # Schism region indices are returned so the simulation can
        # institutionalize part of the remnant there.
        return new_events, schisms

    # ------------------------------------------------------------------
    def martyr_seed(self, martyr_share: np.ndarray):
        """The blood of the martyrs: seeds receptivity, unity — and draws
        God near to the suffering church."""
        cfg = self.cfg
        self.receptivity = np.clip(
            self.receptivity + cfg.martyr_receptivity_seed * martyr_share,
            0.0, 1.0)
        self.unity = np.clip(
            self.unity + cfg.martyr_unity_seed * martyr_share, 0.05, 1.0)
        self.nearness = np.clip(
            self.nearness + cfg.martyr_nearness_seed * martyr_share,
            0.0, 1.0)
