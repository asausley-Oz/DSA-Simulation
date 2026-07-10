"""Configuration for the Emergent Covenant Engine.

Every number that shapes the dynamics lives here so sensitivity analysis
can sweep it. Nothing in the engine reads a calendar date; a tick is an
abstract year and all behavior is driven by state, not by time.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class RegionInit:
    """Initial conditions for one region.

    This is the ONLY place external data enters the simulation. A real
    data source can populate these from empirical estimates; after tick
    zero the engine never consults them again.
    """
    name: str
    population_share: float   # fraction of total agents seeded here
    entropy: float            # initial corruption level (0-1)
    vamphoric: float          # initial extractive-system load (0-1)
    unity: float              # initial church unity (0-1)
    comfort: float            # initial material comfort (0-1)
    formation_mean: float     # mean spiritual formation of seeded agents
    formation_std: float      # spread of formation
    born_rate: float          # initial fraction born-from-above


# Abstract regions with distinct starting textures. Names are kept from
# v6.5 for continuity, but nothing about them is tied to real history —
# they are just zones with different initial conditions and neighbors.
DEFAULT_REGIONS: List[RegionInit] = [
    RegionInit("WEST",      0.11, 0.35, 0.30, 0.65, 0.60, 0.45, 0.20, 0.20),
    RegionInit("EAST",      0.33, 0.45, 0.40, 0.55, 0.35, 0.35, 0.18, 0.05),
    RegionInit("SOUTH",     0.18, 0.40, 0.50, 0.75, 0.25, 0.55, 0.20, 0.35),
    RegionInit("MIDEAST",   0.07, 0.55, 0.60, 0.50, 0.30, 0.30, 0.15, 0.03),
    RegionInit("NORTH",     0.04, 0.40, 0.40, 0.60, 0.50, 0.40, 0.18, 0.10),
    RegionInit("SOUTHASIA", 0.27, 0.48, 0.50, 0.55, 0.25, 0.40, 0.18, 0.12),
]

# Undirected adjacency between regions (indices into DEFAULT_REGIONS).
# Crises spill strain across these edges and migrants move along them.
DEFAULT_ADJACENCY: List[Tuple[int, int]] = [
    (0, 1), (0, 4), (0, 2),          # WEST—EAST, WEST—NORTH, WEST—SOUTH
    (1, 4), (1, 3), (1, 5),          # EAST—NORTH, EAST—MIDEAST, EAST—SOUTHASIA
    (3, 5), (3, 2),                  # MIDEAST—SOUTHASIA, MIDEAST—SOUTH
    (2, 5),                          # SOUTH—SOUTHASIA
]


@dataclass
class EmergentConfig:
    # --- scale ---
    n_agents: int = 10_000
    n_ticks: int = 600
    seed: Optional[int] = 42
    regions: List[RegionInit] = field(
        default_factory=lambda: list(DEFAULT_REGIONS))
    adjacency: List[Tuple[int, int]] = field(
        default_factory=lambda: list(DEFAULT_ADJACENCY))

    # --- covenant distance (the master equation) ---
    # distance(t+1) = distance(t) + rebellion_flux - nearness_flux
    # Humanity's thread pushes distance open; God's counter-movement and
    # the remnant's response pull it closed. Entropy is downstream: the
    # physical shadow that relational breach casts on the world.
    bent: float = 0.006              # baseline rebellion pressure per tick
    bent_vamphoric_gain: float = 0.8  # vamphoric systems amplify the bent
    labor_efficiency: float = 0.22   # remnant divine-labor pull on distance
    distance_diffusion: float = 0.03  # cultural osmosis between neighbors

    # --- God's counter-movement (the second thread) ---
    # The counter-movement is relentless (CDT) and abounds where the
    # breach is greatest (Rom 5:20): the pull scales UP with distance.
    nearness_pull: float = 0.045     # how strongly nearness closes distance
    nearness_relax: float = 0.03     # incremental intimacy toward the broken
    nearness_floor: float = 0.25     # God never fully withdraws within history
    nearness_visitation: float = 0.18  # sovereign jump when revival ignites
    nearness_departure: float = 0.003  # the glory departs when comfort ignores it
    martyr_nearness_seed: float = 0.2  # God draws near to the suffering church

    # --- cumulative rebellion (the ratchet) ---
    # CDT: rebellion accumulates and is never fully erased within history.
    # The ratchet raises both the bent and the floor under distance, so
    # each cycle starts slightly worse — the trap closing.
    ratchet_rate: float = 0.22       # fraction of rebellion flux that sticks
    ratchet_decay: float = 0.0002    # almost never forgotten
    ratchet_cap: float = 2.0
    ratchet_bent_gain: float = 0.5   # accumulated weight amplifies the bent
    ratchet_floor_gain: float = 0.12  # distance floor from accumulated weight

    # --- entropy (derived: the physical shadow of distance) ---
    entropy_shadow_rate: float = 0.12  # decay/rebuilding lag behind distance

    # --- vamphoric system ---
    vamphoric_growth: float = 0.010  # feeds on distance + empire share
    vamphoric_comfort_gain: float = 0.5  # the fork: comfort feeds the parasite
    vamphoric_decay: float = 0.012   # eroded by unity + remnant labor
    drain_rate: float = 0.020        # scc_lock accumulation on nominal agents
    lock_relax: float = 0.015        # locks loosen when vamphoric load is low
    empire_release_lock: float = 0.70  # empire agents freed below this lock
    empire_entropy_push: float = 0.04  # entropy pressure per unit empire share

    # --- comfort / secular drift ---
    comfort_growth: float = 0.015    # comfort rises when entropy is low
    comfort_crisis_crash: float = 0.10  # comfort lost per crisis tick
    comfort_erosion: float = 0.10    # how much comfort weakens child formation
    apostasy_base: float = 0.015     # comfort-driven falling-away rate
    fear_apostasy: float = 0.03      # persecution-driven falling-away rate

    # --- receptivity / conversion ---
    receptivity_relax: float = 0.10  # speed receptivity tracks its target
    conversion_base: float = 0.10    # contact-conversion coefficient
    conversion_formation_gift: float = 0.35  # formation bump for new converts

    # --- household transmission ---
    # Children of remnant parents are usually raised into the faith, but
    # transmission depends on the parent's formation and is undermined by
    # ambient comfort. This is the engine of multi-generation secular
    # drift: comfortable eras quietly fail to pass the faith on.
    household_transmission: float = 0.90
    transmission_comfort_penalty: float = 0.40
    transmission_comfort_floor: float = 0.35  # comfort below this is harmless
    fertility_remnant_bonus: float = 0.5      # devout households bear more

    # --- revival (phase transition) ---
    revival_tension_rate: float = 0.08   # tension gain per tick per unit fuel
    revival_fuel_scale: float = 8.0      # amplifies receptivity x sqrt(remnant)
    revival_tension_leak: float = 0.005  # tension decay (doubles when cold)
    revival_threshold: float = 1.0       # tension level that ignites revival
    revival_min_receptivity: float = 0.30
    revival_ignition_prob: float = 0.12  # per-tick chance once conditions hold
    revival_conversion_boost: float = 9.0
    revival_duration: Tuple[int, int] = (3, 7)   # min/max ticks
    revival_entropy_relief: float = 0.015        # entropy drop per revival tick

    # --- crisis (war / collapse) ---
    strain_from_breach: float = 0.012    # from distance + its physical shadow
    strain_from_vamphoric: float = 0.009
    strain_from_disunity: float = 0.006
    strain_relief: float = 0.006         # baseline strain dissipation
    crisis_base_prob: float = 0.22       # max per-tick ignition probability
    crisis_strain_midpoint: float = 1.1  # strain at 50% of max ignition prob
    crisis_strain_width: float = 0.22    # softness of the ignition sigmoid
    crisis_min_strain: float = 0.30      # no ignition on a near-empty tank
    crisis_duration: Tuple[int, int] = (3, 9)
    crisis_entropy_shock: float = 0.022  # entropy added per crisis tick
    crisis_mortality: float = 0.02       # extra death probability in crisis
    crisis_spillover: float = 0.45       # strain pushed onto neighbors at ignition

    # --- persecution / martyrdom ---
    persecution_gain: float = 1.6        # scales vamphoric x empire pressure
    martyr_rate: float = 0.012           # per-tick death rate of visible remnant
    martyr_receptivity_seed: float = 0.5 # receptivity gain per martyr share
    martyr_unity_seed: float = 0.3       # unity gain per martyr share

    # --- schism ---
    schism_pressure_rate: float = 0.02   # builds when church is big+comfortable
    schism_threshold: float = 1.0
    schism_unity_cost: float = 0.25
    schism_defection: float = 0.15       # fraction of remnant institutionalized

    # --- unity dynamics ---
    unity_erosion: float = 0.004         # slow drift apart in comfort
    unity_suffering_gain: float = 0.02   # shared hardship pulls together

    # --- demography ---
    fertility: float = 0.030             # births per alive agent per tick
    mortality_base: float = 0.003
    mortality_gompertz_a: float = 0.00008
    mortality_gompertz_b: float = 0.088
    inheritance_weight: float = 0.55     # child formation weight on parent
    formation_noise: float = 0.08
    capacity_factor: float = 1.8         # regional carrying capacity multiple

    # --- migration ---
    migration_rate: float = 0.003        # fraction considering a move per tick

    # --- endings (state-only, no dates) ---
    consummation_distance: float = 0.96  # sustained global distance => collapse
    consummation_remnant_floor: float = 0.005  # remnant share extinction
    renewal_remnant: float = 0.65        # sustained remnant share => renewal
    renewal_distance_ceiling: float = 0.22
    consummation_sustain_ticks: int = 12  # condition must hold this long
    renewal_sustain_ticks: int = 60      # renewal must survive the comfort loop

    def param_dict(self) -> Dict[str, float]:
        """Flat dict of numeric parameters (for sensitivity sweeps)."""
        out = {}
        for k, v in self.__dict__.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out[k] = v
        return out
