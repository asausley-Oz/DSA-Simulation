# DSA v7 — Emergent Covenant Engine

A ground-up rewrite of the DSA v6.5 engine with one governing rule:
**nothing in the simulation reads a date.** Wars, revivals, schisms,
persecution waves, secular drift, and the ending itself all emerge from
coupled feedback between agents and their regional environments.

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

## State variables (per region, all endogenous)

| Variable | Raised by | Lowered by |
|---|---|---|
| entropy | the bent (amplified by vamphoric load), empire share, crises | remnant divine labor (x unity), rebuilding, revival |
| vamphoric load | entropy, empire share | unity, remnant labor |
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

- **Consummation** — global entropy saturates, or the remnant goes
  extinct.
- **Renewal** — a deeply formed remnant becomes the culture (share ≥ 65%)
  while entropy collapses.
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
