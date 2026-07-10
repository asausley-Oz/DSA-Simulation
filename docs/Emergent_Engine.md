# DSA v7 — Emergent Covenant Engine

A ground-up rewrite of the DSA v6.5 engine with one governing rule:
**nothing in the simulation reads a date.** Wars, revivals, schisms,
persecution waves, secular drift, and the ending itself all emerge from
coupled feedback between agents and their regional environments.

As of **v7.1**, the master variable is covenant distance (see
"The v7.1 distance reformulation" below), aligning the physics with
Covenant Distance Theology: two threads — humanity's cumulative movement
away and God's relentless counter-movement of drawing near.

Run it:

```
python run_emergent.py                     # one 600-tick history
python run_emergent.py --seed 7            # a different history
python run_emergent.py --sensitivity      # parameter sweeps
```

## Why v6.5 wasn't emergent

v6.5 claimed "no hard-coded events," but its `step()` called
`_update_world_from_data(year)` **every year**, overwriting regional
entropy, unity, and vamphoric load from data tables that had:

- World Wars baked in at 1914–1918 and 1939–1945
- the Depression at 1929–1933
- denominational splits keyed to 1054 and 1517
- consummation gated behind `year >= 2030`

Agents could never actually shape the world — history was injected, not
played out. Two runs differed only in noise around the same script.

## The v7 rule: data initializes, feedback drives

External data (empirical or synthetic) enters exactly once, as the
`RegionInit` initial conditions in `emergent/config.py`. After tick zero,
every macro-variable is updated only from agent aggregates and from other
state variables. Different seeds therefore produce **genuinely different
histories** — different wars, different awakenings, different endings —
from identical rules.

## The v7.1 distance reformulation

The master equation is relational, not thermodynamic:

```
distance(t+1) = distance(t) + rebellion_flux − nearness_flux

rebellion_flux = bent × (1 + vamphoric amplifier) × (1 + ratchet amplifier)
               + empire share push + mass violence (crises)

nearness_flux  = remnant divine labor × (1 + unity)          [human response]
               + nearness_pull × nearness × (0.5 + 0.5·distance)  [God's thread]
               + revival relief
```

**Humanity's thread.** Rebellion flux both moves `distance` and feeds a
near-permanent ratchet, `cumulative_rebellion` (decay ≈ 0): the
accumulated weight amplifies the bent and raises a hard **floor** under
distance. Within history the world never returns all the way to Eden —
renewals in late-game runs land *at* the ratchet floor, not beneath it.

**God's thread.** `nearness` relaxes toward the broken (receptivity,
persecution, crisis) and the praying remnant; it slowly departs from a
comfort that ignores it (Ezekiel 10), but never below a floor — He
remains faithful. The pull of nearness on distance scales **up** with
distance (Rom 5:20 — grace abounds where the breach is greatest). Revival
ignition is a sovereign visitation: the stochastic dice at the moment of
ignition is deliberately where DSA's chosen freedom lives — conditions
make the event possible, they never compel it — and each visitation jumps
nearness. Martyrdom also draws God near to the suffering church.

**Entropy is demoted to a derived shadow.** Physical decay lags
relational breach (`entropy → distance` with a relaxation rate); crises
wreck the physical world faster than they change hearts. Comfort,
migration, and strain read the physical world; vamphoric growth and the
endings read distance itself.

**The fork closes the loop.** Vamphoric load feeds on distance, empire
share, *and comfort* — "comfort substituted for transformation." A golden
age is never placid; it is the era of the drain that runs undetected.
This is what rots golden ages from within and ends the quiet-extinction
pathology: prosperity breeds the parasite, the parasite breeds strain and
persecution, hardship reopens receptivity, and the cycle turns.

## State variables (per region, all endogenous)

| Variable | Raised by | Lowered by |
|---|---|---|
| **distance** (master) | the bent × vamphoric × ratchet, empire share, crises | remnant labor (x unity), nearness pull, revival |
| **nearness** | brokenness, deep remnant, visitation, martyrdom | comfort that ignores it (floored — He remains faithful) |
| **cumulative rebellion** | a fraction of all rebellion flux (ratchet) | almost nothing (decay ≈ 0) |
| entropy (derived) | lags toward distance; crisis shocks | lags toward distance when it closes |
| vamphoric load | distance, empire share, **comfort** (the fork) | unity, remnant labor |
| comfort | calm + low entropy | crises, upkeep |
| unity | shared suffering (crisis, persecution) | comfort drift, schism |
| receptivity | hardship (crisis, persecution, entropy) | comfort |
| persecution | vamphoric x empire pressure on a **visible minority** | remnant becoming a majority, system loosening |

## Event mechanisms (former dated triggers → accumulators)

**Crisis (war/collapse).** Strain accumulates from entropy, vamphoric
load, and disunity; comfort dissipates it. Ignition probability is a
sigmoid of strain, and an igniting crisis dumps strain onto neighboring
regions — so conflicts cluster and cascade into world-war-scale epochs
naturally. (Replaces wars hard-coded at 1914/1939.)

**Revival.** Tension builds as `receptivity × √(deep remnant share)` —
the square root means a tiny praying remnant still generates real
tension. Tension leaks slowly (faster in cold seasons), can pre-load past
threshold during decline, and ignites stochastically once receptivity
rises — so awakenings follow *seasons of hardship*, usually erupting in
the middle of crisis epochs. (Replaces a flat dice roll per year.)

**Secular drift.** Children inherit formation imperfectly from a parent
plus ambient culture, minus a comfort penalty; covenant-household
transmission of faith itself degrades with comfort and weak parental
formation. Comfortable golden ages therefore quietly fail to pass the
faith on, one generation at a time. (Replaces year-indexed decline
trends.)

**Schism.** A large, comfortable, still-unified church accumulates
institutional pressure; past threshold it fractures, costing unity and
defecting the least-formed members. (Replaces splits keyed to 1054/1517.)

**Persecution & martyrdom.** Persecution targets a visible minority in
proportion to vamphoric × empire pressure. Martyrs are drawn from the
deeply formed; their deaths seed receptivity and unity — the blood of the
martyrs is literally the seed of the next revival.

**Empire capture — and collapse.** Locks (scc_lock) grow under vamphoric
pressure and relax when it fades, so empire status is a pressure
equilibrium, not a one-way ratchet: empires crumble when the system that
made them starves.

## Endings are attractors, not appointments

There is no `year >= 2030` check. A run terminates only when a state
condition holds for a sustained window:

- **Consummation** — global distance saturates, or the remnant goes
  extinct (12 sustained ticks).
- **Renewal** — a deeply formed remnant becomes the culture (share ≥ 65%)
  while distance closes to the ratchet floor. Renewal must hold for 60
  ticks — a spike of nearness is not the new creation; it has to survive
  the comfort loop that has undone every golden age before it.
- **Contested** — the tick limit arrives with the struggle unresolved.

Across seeds the engine bifurcates: some worlds spiral down before
revival can ignite (a genuine "too late" race — tension is often ticks
away from threshold when entropy saturates), others catch the wave and
renew.

## The emergent grand cycle

No phase of this is scripted, yet most runs trace it:

```
strong remnant → entropy falls → golden age → comfort rises
   → transmission fails, receptivity closes → remnant declines
   → labor drag disappears → entropy climbs → strain builds
   → crisis epoch (wars cluster) → comfort crashes, receptivity opens
   → revival tension ignites → conversion cascades → remnant rebuilds
   → repeat, or tip into consummation / renewal
```

## Architecture

```
emergent/
  config.py        every tunable parameter + RegionInit (the only data inlet)
  population.py    vectorized numpy agents (struct-of-arrays, slot reuse)
  environment.py   coupled regional dynamics + event accumulators
  simulation.py    orchestrator, history, state-only endings
  analysis.py      one-factor-at-a-time sensitivity sweeps
run_emergent.py    CLI, plots, event timeline
```

Agents live in parallel numpy arrays rather than Python objects, so a
10,000-agent, 600-tick history runs in a few seconds, and sensitivity
sweeps over dozens of runs are practical.

## Falsifiability hooks

Because parameters are cleanly separated from mechanism, the engine
supports the empirical program v6.5 gestured at: fit `RegionInit` from
historical estimates, sweep parameters with `--sensitivity`, and test
whether observed macro-patterns (revival lag behind crises, secular drift
time constants, crisis clustering) fall inside the model's distribution
of histories rather than being painted onto it.
