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

    # --- the primordial pair: Eve's promise and Adam's curse (Gen 3) ---
    # Every world begins with both. THE SEED: there is always exactly
    # one living person carrying the promise (Gen 3:15) — the line
    # cannot apostatize, cannot be captured, and when the bearer dies
    # the seed passes to the most-formed living remnant; if none
    # remains, God raises a bearer from the stones (Matt 3:9). The
    # world can fall; the seed endures even through consummation.
    # THE TOIL: the ground resists (thorns and thistles) — comfort
    # grows slower, rebuilding is sweaty, and a floor of hardship keeps
    # hearts from sealing shut. The curse is also severe mercy.
    seed_bearer: bool = True
    seed_formation_floor: float = 0.75   # the line of promise is kept formed
    toil: float = 0.25                   # by the sweat of your brow
    # The curse cuts both ways: frustration of the ground breeds
    # resentment and conflict (Cain follows Eden immediately).
    toil_bent_gain: float = 0.4          # frustration feeds the bent
    toil_strain: float = 0.003           # scarce bread breeds conflict

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

    # --- delusion / awareness (Anti-Life Delusion) ---
    # Delusion is the mechanism that conceals the dying: it grows where
    # vamphoric systems institutionalize it and where comfort makes the
    # lie preferable. It is NOT removed by suffering alone (Pharaoh
    # hardened) — it breaks only under exposure: the remnant naming the
    # system, martyrdom's undeniable testimony, visible systemic failure,
    # and the light of revival. Awareness is the precondition of turning.
    # Delusion is PER-AGENT (v7.3): each person carries their own
    # blindness, inherited from the household they were raised in, grown
    # by the systems around them, and broken one encounter at a time.
    delusion_growth_vamphoric: float = 0.008  # systems suppress self-awareness
    delusion_growth_comfort: float = 0.005    # the comfortable lie, embraced
    witness_contact_rate: float = 0.28   # chance/tick of meeting a witness
    witness_break: float = 0.35          # delusion shattered by one encounter
    delusion_exposure_crisis: float = 0.030   # the simulacra visibly fail
    delusion_exposure_revival: float = 0.06   # the Light exposes
    delusion_formation_clarity: float = 0.015  # the formed see ever clearer
    martyr_delusion_break: float = 0.4        # testimony that cannot be unseen
    awareness_blindness_cap: float = 0.95     # complete blindness is possible
    hardening_threshold: float = 0.85         # regional mean logged as event
    delusion_inheritance: float = 0.6         # raised inside the parents' frame

    # --- the skin of the apple (SCC): two-layer blindness ---
    # Blindness is not one substance. The SKIN is the secular coating —
    # historically thin, grown only where the vamphoric buyout of toil
    # has succeeded (comfort delivered by the system); it blocks hearing
    # entirely, but it is brittle: shocks and witness crack it in
    # chunks, and what it cracks INTO is not neutrality but the FLESH —
    # the ancient three-realm default (eternity set in the heart,
    # Eccl 3:11). The flesh distorts what is heard but leaves entry
    # points (curse, spirits, sacrifice are words it already knows);
    # it is also the parasite's oldest home turf, so newly exposed
    # flesh feeds vamphoric folk-religion — crack a secular region and
    # you get the double surge: conversions AND occultism together.
    # Only discipleship reworks the flesh, slowly.
    skin_growth: float = 0.018       # comfort x vamphoric: the buyout coating
    skin_crack_crisis: float = 0.05  # shocks flake the coating in chunks
    skin_crack_witness: float = 0.45  # one encounter shatters surface certainty
    skin_crack_revival: float = 0.08
    flesh_growth: float = 0.004      # the pagan default, civilizationally slow
    flesh_clarity: float = 0.012     # only discipleship reworks cosmology
    flesh_opacity: float = 0.55      # flesh distorts hearing; entry points remain
    vamphoric_flesh_gain: float = 0.006  # exposed flesh feeds the parasite
    skin_inheritance: float = 0.6    # raised inside the parents' coating

    # --- the Container (v8.1): the trap at the end ---
    # The skin with the brittleness engineered out. Where the buyout's
    # terminal product accumulates (skin x comfort x vamphoric), the
    # coating becomes ARCHITECTURE: a habitat that does not resist
    # exposure but metabolizes it. Crises arrive as content; witness is
    # indistinguishable from its simulacra; martyrdom trends. Every
    # crack-channel is muted in proportion to containment — the first
    # delusion with its own real estate, and the substrate of the
    # strong delusion (2 Thess 2:11). Its one dependency it cannot
    # remove: its subjects still have bodies. Embodied gathering is the
    # counter-practice, and the resurrected body is the one object it
    # structurally cannot ingest — the 7-day world does not get out of
    # the Container; the Shaking opens it from the other side.
    container_growth: float = 0.008   # skin x comfort x vamphoric -> architecture
    container_self: float = 0.010     # the trap builds itself once begun
    container_decay: float = 0.010    # embodied gathering, the counter-practice
    container_threshold: float = 0.70  # the trap completes (logged event)
    container_formation_throttle: float = 0.5  # discipleship needs presence
    falling_away_containment: float = 0.30  # strong delusion gets its substrate
    adversary_container_gain: float = 0.25  # the air is his medium (Eph 2:2)

    # --- the Account and the 8th day (Macro Cup) ---
    # A global ledger accumulates every unit of rebellion ever enacted —
    # it never decays and is never erased. At the deicide it is
    # PRESENTED AND PAID (Col 2:14, the record nailed to the cross) —
    # the TAV, the final letter: the same stroke that pays the account
    # seals the old aeon's condemnation (John 12:31). From Eden onward
    # every history also builds two kinds of substance: WOOD-HAY (the
    # comfort-economy of the passing age) and TREASURE (unshakeable
    # substance: divine labor, the formation of the faithful dead, the
    # martyrs banked double — laid up where moth and rust do not
    # destroy; tribulation martyrs bear no fruit in the old world but
    # bank fully in the new). Every verdict ends in the same event: the
    # SHAKING (Hag 2:6, Heb 12:27) — the old heavens and earth pass,
    # and what remains is measured. The 8th day dawns on the remainder.
    treasure_labor: float = 0.02     # divine labor banks unshakeable substance
    treasure_martyr: float = 2.0     # the martyrs banked double
    treasure_death: float = 1.0      # the faithful dead bank their formation
    wood_hay_rate: float = 0.005     # the passing age's output, per comfort

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

    # --- the adversary (the prince of the power of the air) ---
    # Parasitic, never independent: his power derives from the breach —
    # accumulated rebellion, open distance, captured agents. Naming him
    # (exposure) drains him; the atonement disarms him.
    enable_adversary: bool = True
    adversary_power_relax: float = 0.05    # how fast power tracks the breach
    adversary_from_rebellion: float = 0.35
    adversary_from_distance: float = 0.35
    adversary_from_empire: float = 0.50
    adversary_exposure_damp: float = 0.60  # being named cuts his power
    adversary_scheme_prob: float = 0.45    # per-tick chance x power
    adversary_delusion_gain: float = 0.006  # the passive whisper
    adversary_vamphoric_gain: float = 0.004
    adversary_disarmed_factor: float = 0.35  # power ceiling after Col 2:15
    accuse_agency_drain: float = 0.15      # sifting the deep remnant
    accuse_pride_gain: float = 0.08
    # Every scheme is rebellion enacted: it widens the breach directly
    # and part of it sticks to the record — the parasite feeding the
    # very disorder it feeds on.
    scheme_distance_load: float = 0.05
    scheme_record_stick: float = 0.5       # fraction of the load that ratchets
    # SCHISM, the fifth movement: sow division where accusation has
    # already inflated pride — load the church's own fracture pressure.
    schism_scheme_unity_cost: float = 0.15
    schism_scheme_pressure: float = 0.60

    # --- incarnation -> deicide -> atonement (the v7.6 sequence) ---
    # INCARNATION fires once, at the fullness of time — state conditions,
    # no dates: the record of rebellion heavy across the world AND a
    # prepared vessel (a region holding even a small deeply-formed
    # remnant under drawn-near presence). While incarnate: nearness in
    # the vessel is held near 1.0, delusion there collapses (the Light in
    # person), divine labor runs at the perfect-image rate, and the
    # adversary is exposed wherever the presence stands.
    #
    # The adversary cannot ignore it: a deicide compulsion grows every
    # tick of the incarnation — the one scheme he cannot resist and
    # cannot survive (1 Cor 2:8). DEICIDE springs the ATONEMENT: the
    # record cancelled, the veil torn, the indwelling given, the accuser
    # disarmed — scaled RETROACTIVELY by the accumulated faith of every
    # believer who lived and died before that tick (Heb 11:39-40). If no
    # adversary takes the bait, the life is laid down freely at the end
    # of the incarnation window (John 10:18) — atonement comes anyway.
    enable_atonement: bool = True
    incarnation_rebellion_trigger: float = 0.55  # the fullness of the weight
    incarnation_vessel_deep: float = 0.015     # a faithful few suffice...
    incarnation_vessel_nearness: float = 0.55  # ...under drawn-near presence
    incarnation_nearness_hold: float = 0.95    # Immanuel — presence embodied
    incarnate_labor_bonus: float = 0.15        # the perfect image at work
    incarnate_delusion_break: float = 0.08     # per tick, in the vessel region
    incarnate_exposure_gain: float = 0.02      # the presence names him daily
    incarnation_max_duration: int = 35         # he lays it down regardless
    deicide_urge_base: float = 0.012            # compulsion per incarnate tick
    deicide_urge_power: float = 0.02           # plus per unit of his power
    deicide_distance_spike: float = 0.15       # darkness at noon
    atonement_base_clear: float = 0.50         # covering before the faithful
    atonement_faith_scale: float = 1.0         # retroactive: per unit stored faith
    atonement_distance_break: float = 0.30     # the veil torn
    atonement_nearness_gift: float = 0.25      # the indwelling begins
    atonement_nearness_floor_gain: float = 0.10
    atonement_grace: float = 0.50   # post-atonement ratchet multiplier
    atonement_delusion_break: float = 0.20     # the Light has come (base)
    atonement_faith_delusion: float = 0.50     # retroactive light per stored faith
    martyr_faith_weight: float = 2.0           # martyrs weigh double in the store

    # --- patience and the great falling away (2 Pet 3:9, 2 Thess 2) ---
    # After the atonement the end is HELD OPEN as long as the world is
    # still responding — the Lord is patient, not willing that any
    # should perish. Response is measured as the harvest rate among the
    # still-unconverted. When that rate stays dry for a long season in a
    # world that has not been won, patience is exhausted and the great
    # falling away fires ONCE: the lukewarm fall (the love of many grows
    # cold), strong delusion is sent on those who refused the truth
    # (2 Thess 2:11), and the adversary is released for a little while
    # (Rev 20:3). Then the end comes swiftly.
    patience: bool = True
    patience_response_floor: float = 0.003  # harvest rate that still counts
    patience_dry_ticks: int = 25             # the dry season that exhausts it
    patience_remnant_ceiling: float = 0.50   # a won world is fullness, not dryness
    falling_away_formation_bar: float = 0.50  # the lukewarm fall
    strong_delusion: float = 0.25             # sent on those who refused
    restrainer_removed: float = 0.10          # lawlessness unveiled (2 Thess 2:7)
    adversary_release_factor: float = 0.85    # loosed for a little while
    # The tribulation does not end gradually — those days are cut short
    # for the sake of the elect (Matt 24:22): after this many ticks of
    # endurance past the falling away, the PAROUSIA ends the world with
    # the remnant vindicated. (Relative to an emergent event, no date.)
    parousia_after: int = 60
    # --- the millennium, the release, and the descent (Rev 20-21) ---
    # The parousia does not end the world; it opens the MILLENNIUM:
    # the adversary bound, the glorified first-resurrection body
    # reigning from the beloved city, the two Jerusalems in maximal
    # correspondence — the most heaven and earth can share while
    # remaining two. At its end the adversary is RELEASED (Rev 20:3
    # belongs here, not before the parousia) to deceive the nations one
    # final time — Gog and Magog, rebellion with no curse, no
    # Container, no excuse: agency isolated from every condition.
    # Fire from heaven ends it; the first creation passes (20:11); and
    # the last event of every saved history is the DESCENT (21:2): the
    # treasure comes down as the city-who-is-the-people.
    millennium_length: int = 120     # the thousand years, scaled
    millennium_floor_bonus: float = 0.35  # correspondence at saturation
    gog_magog_window: int = 15       # the little while of the release
    final_deception: float = 0.40    # he goes out to deceive the nations
    fire_from_heaven: float = 0.60   # the besiegers consumed

    # --- the great tribulation: the greatest tax on the remnant ---
    # Between the falling away and the parousia, it is given to him to
    # make war on the saints and to conquer them (Rev 13:7): the martyr
    # seed is MUTED — the blood falls on ground held by strong delusion
    # and bears no fruit until the vindication. His movements strike
    # harder, and division — brother betraying brother (Matt 24:10) —
    # becomes his sharpest blade.
    tribulation_martyr_mute: bool = True
    tribulation_scheme_boost: float = 1.6   # his movements strike harder
    tribulation_schism_bonus: float = 2.0   # division, his sharpest blade
    # "To lead astray, IF POSSIBLE, even the elect" (Matt 24:24): each
    # tribulation tick every remnant member faces this apostasy chance,
    # shielded by formation — 20% base becomes 2%/tick for the deeply
    # formed and 10%/tick for the barely formed. The elect stand; the
    # middle is sifted. The seed-bearer cannot fall.
    tribulation_apostasy: float = 0.20

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
