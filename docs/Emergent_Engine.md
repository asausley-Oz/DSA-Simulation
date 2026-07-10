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

## The v7.2 delusion layer (Anti-Life Delusion)

Delusion is the mechanism that conceals the dying. Per region it:

- **grows** where vamphoric systems suppress self-awareness and where
  comfort makes the lie preferable to the truth;
- is **not** removed by suffering alone (Pharaoh's pattern) — it yields
  only to **exposure**: the deep-formation remnant naming the system
  (√-scaled, so a small faithful band still cuts), martyrdom's testimony
  that cannot be argued with, the visible failure of the simulacra when
  crisis strikes, and the light of revival.

`awareness = 1 − 0.95 × delusion` (complete blindness is possible) gates
the two doors of turning:

1. **Receptivity** — hardship opens only hearts that can still see; a
   deluded region misreads its own suffering.
2. **Conversion** — contact and openness cannot convert a heart that
   does not know it is dying (a small grace floor remains).

When a region's delusion crosses 0.85 a **hardening** event is logged:
the drain now runs undetected. Hardened regions can pass through entire
crisis epochs without revival — which changes the diagnosis of doomed
histories. The doomed runs are no longer "too late" — they are blind.

## v7.3: delusion moves onto the agents

Delusion is now a **per-agent** variable, not a regional field:

- **Inherited**: children start inside their parents' frame, blended
  with the ambient culture (`delusion_inheritance`). Blindness is
  raised, not chosen — structural, generational.
- **Grown**: by the vamphoric and comfort systems around each person,
  dampened by their own formation.
- **Broken person-to-person**: each tick an agent may encounter a
  witness (probability ∝ √deep-remnant-share); one conversation that
  names the drain and the fork shatters a large block of delusion.
  Martyrdom breaks it region-wide; crisis and revival expose ambiently.
- **Conversion gates per person**: revivals sweep those who can see and
  leave a hardened core behind — repeated revivals in one region show
  diminishing returns unless witness contact keeps cutting.

The regional "delusion" the environment reads is simply the population
mean; hardening events fire on it as before.

## The outcome landscape (ensemble mode)

`python run_emergent.py --ensemble 100` runs 100 seeds in parallel and
maps the distribution of histories — the falsifiable object is the
distribution, not any single run. Under default parameters:

- **~57% renewal** (median resolution tick ~443; final delusion ~0.02;
  ~34 revivals per history)
- **~36% consummation** (median tick ~265; final delusion ~0.32;
  **0.2 revivals on average** — doomed worlds essentially never ignite)
- **~7% contested** at the 600-tick limit

The landscape is **bimodal**: final states cluster at
(low delusion, high remnant) or (high delusion, low remnant) with a void
between — no world ends lukewarm. The two endings also separate cleanly
in time: consummations all resolve early (~250–290), renewals late
(~390–600). The fork in every history is whether the first revival wave
ignites before the first great collapse completes.

Renewal's distance ceiling rises with the ratchet floor
(`floor + 0.08`), so a late-age world can still renew — carrying its
scars with it — rather than being locked out by its own accumulated
history.

## The adversary (v7.4): the prince of the power of the air

Per Anti-Life Delusion, the powers that entice delusion are "not
independent powers but expressions of the disorder rebellion
introduced." The adversary is therefore **parasitic, never a rival
god**: his power derives entirely from the breach (accumulated
rebellion + open distance + captured agents), and three structural
limits bind him — he works in the dark (being *named* drains his
power), his sharpest weapon backfires (violence makes martyrs, and
martyr-seed grows what he strikes), and the atonement disarms him
(Col 2:15).

He schemes with intelligence, prioritized against God's counter-
movement: **QUENCH** (crush revival tension nearest ignition — the
seed snatched away), **GILD** (the subtlest: reward the strongest
church into comfort — golden chains), **SCHISM** (sow division where
unity is already weak — set brothers against brothers, loading the
church's own fracture pressure until it splits itself), **ACCUSE**
(sift the deep remnant — drain agency, inflate pride; risks being
named, which raises his exposure), **INCITE** (stir war where the
remnant is absent, so ruin cannot seed). Schemes appear in the event
timeline.

**The distance load — his engine and his leash.** Every scheme is
rebellion enacted: it widens the breach directly and part of it sticks
to the permanent record. This makes his power self-feeding (breach →
power → schemes → breach) — and it is also his undoing, because the
record is precisely what triggers the fullness of time. In ensemble,
strengthening the adversary *raised* the renewal share: the harder he
works, the sooner the atonement fires and disarms him. He hastens his
own end (1 Cor 2:8).

Effect: with the adversary active, consummation rises from ~36% to
~40-55% of histories (depending on tuning). Quench is his most-used
weapon — the engine's own play confirms that suppressing awakening is
the efficient strategy.

## The primordial pair (v7.7): Eve's promise and Adam's curse

Every world now begins with both halves of Eden's aftermath (Gen 3).

**The Seed (Gen 3:15).** Until the incarnation, there is always
exactly one living bearer of the promise. The bearer cannot
apostatize, cannot be empire-captured, and is kept formed (≥ 0.75).
At the bearer's death the seed passes to the most-formed living
remnant; if the whole remnant line has been cut, God raises a bearer
from the stones (Matt 3:9). The line survives ~25–30 generational
passes per history. Election also has its purpose: the bearer's
region qualifies as an incarnation vessel (a lone Mary in a backwater
suffices where whole churches are not required) — but only under the
full measure of drawn-near presence. A hardened world can hold the
seed and still refuse the Son.

**The line is fulfilled, not perpetual.** The seed of the woman IS
the one who arrives: at the incarnation the bearer mechanic ends —
the promise is no longer carried by blood but poured out. Every world
therefore ends in exactly one of two seed-states, and never a third:
*enduring* (the world died before the fullness of time, the promise
still held — the consummation event records where the seed stands) or
*fulfilled* (the promise delivered, whatever the world did with it).
No history ends with the promise lost.

**The Toil (Gen 3:17-19).** The ground resists: comfort grows slower,
rebuilding is sweaty (decay is free, restoration is not), and the
frustration of the curse feeds both the bent and the strain of
conflict (Cain follows Eden immediately). The curse is severe mercy —
it guards worlds against the comfort trap — but the vamphoric system's
oldest sales pitch is escape from the curse without God (Babel, the
antediluvian slide): `effective_toil = toil × (1 − vamphoric)`. As the
system's load grows it buys the toil out, and the trap reopens. Doomed
worlds in this engine are almost always worlds that engineered away
their own severe mercy.

Ensemble (100 seeds): 84% renewal / 12% consummation / 4% contested.
Incarnation reaches ~89% of histories; worlds that never receive it
die blind and vessel-less — with the seed still alive inside them.

## The v7.6 sequence: incarnation → deicide → atonement

The one-shot atonement trigger is replaced by the full CDT shape:

1. **Incarnation** fires at the fullness of time (heavy record + a
   prepared vessel, however small). While incarnate: nearness in the
   vessel region is held near 1.0 (Immanuel), delusion there collapses
   tick by tick (the Light in person), divine labor runs at the
   perfect-image rate — a visible golden thread in one region — and
   the adversary is exposed daily just by the presence standing there.
2. **The adversary cannot ignore it.** His scheming bends toward the
   vessel, and a deicide compulsion grows every incarnate tick — the
   one scheme he cannot resist and cannot survive (1 Cor 2:8). In
   ensemble, ~90% of incarnations end in deicide after a median
   ministry of ~8 ticks; darkness falls on the vessel (distance spike,
   strain spike) — and the trap springs.
3. **If no one takes the bait** (e.g. the adversary is disabled), the
   life is laid down freely at the end of the incarnation window
   (John 10:18). Atonement comes either way; no one takes it.
4. **Atonement is retroactive for the faithful** (Heb 11:39–40): the
   engine accumulates a *store of faith* — the formation of every
   believer who dies before the atonement, martyrs counted double —
   and the covering scales with it: record cancelled
   `base 50% + faith_store`, worldwide delusion break likewise. The
   faithful dead are counted into the covering; only together made
   perfect.

Ensemble effect (100 seeds): incarnation reaches ~60% of histories;
every renewal is an atonement-history — but for the first time the
partition is imperfect: a few worlds receive the atonement and still
fall. Grace in this engine is decisive, not coercive: a sufficiently
rotted world can refuse it.

## Atonement (v7.4): the trap broken from within

Fires **once**, at the fullness of time — state conditions, never a
date: the record of accumulated rebellion must be heavy across the
world AND a prepared vessel must exist (a region holding even a small
deeply-formed remnant under drawn-near presence). Effects, per CDT:
the record of debt cancelled (cumulative rebellion slashed 75%), the
veil torn (distance breaks), the indwelling begins (nearness jumps and
its floor permanently rises), the Light comes (delusion breaks
worldwide), grace covers half of what would otherwise ratchet, and the
accuser is disarmed.

**What the A/B ensembles taught (100 seeds each):**

1. A first implementation gated the vessel on a *thriving* church
   (deep remnant + nearness ≥ 0.55). Result: outcome distributions
   with and without atonement were statistically identical — perfect
   correlation (every atonement-world renewed), zero causation. The
   vessel condition selected worlds already being saved. A gospel
   that only comes to the already-revived saves no one.
2. Retuned to come to the weak ("while we were still sinners" — tiny
   vessel, lower nearness bar, earlier trigger, stronger light),
   atonement fires in ~56% of histories and every world it reaches
   escapes consummation; total non-doomed histories rise from ~45 to
   ~56 (+24% relative). Real rescue at the margin — but the partition
   stands: worlds whose faithful line goes extinct before the fullness
   of time never receive it.
3. The remaining gap names the next missing doctrine: **election** —
   the biblical arc has God actively preserving the remnant line
   (Noah, Abram, Egypt, the return) precisely so a vessel exists at
   the fullness of time. The engine has no line-preservation
   mechanism yet.

## Eschatological cartography

`python run_emergent.py --cartography` sweeps a 2-D grid
(witness_contact_rate × nearness_pull, 8 seeds/cell) plus 1-D phase
lines over five theology-laden knobs (nearness_pull,
witness_contact_rate, revival_ignition_prob, ratchet_rate, bent, 10
seeds/value). Findings under the default configuration (read trends,
not single cells — 8–10 seeds gives ±15pp noise per point):

1. **The model leans hopeful.** Renewal is the modal outcome (~50–75%)
   across nearly the whole explored space; consummation is a robust
   minority fate that almost never vanishes. Broadly: renewal within
   history is normal, collapse is always possible.
2. **Revival count mediates everything.** Whatever knob is turned,
   renewal share tracks mean revivals-per-history almost linearly
   (~25% at 9 revivals → ~100% at 32). Awakening frequency is the
   proximate cause of every renewal; the knobs only matter through it.
3. **The ratchet is the strongest doom knob.** Raising ratchet_rate
   (how much of each act of rebellion permanently sticks) from 0.10 to
   0.40 collapses renewal from ~80% to ~50% and raises consummation
   from ~0% to ~50–60% — the clearest monotone signal in the sweep.
   Notably, `bent` (the depth of the rebellion pressure itself) shows
   no comparable effect. What damns worlds in this model is not how
   bent people are but how much of the curse is never cleared. The
   engine currently has NO atonement mechanism (ratchet_decay ≈ 0);
   the cartography is, in effect, pointing at the missing
   Christological term.
4. **The nearness U-shape (tentative).** Renewal is high at weak pull
   (~90%) and strong pull (~80%) but dips to ~50% at the middle. This
   is consistent with the comfort trap: weak grace keeps worlds
   poor-but-receptive, strong grace carries them through the rot, and
   moderate grace produces exactly enough golden age to secularize —
   the Beatitude paradox surfacing at the level of providence.
5. **Providence beats tuning in the mid-range.** Within the central
   region of parameter space, seed-to-seed variance dwarfs parameter
   effects: which history a world gets matters more than any modest
   doctrinal re-tuning of its physics.

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
| receptivity | hardship (crisis, persecution, entropy) × awareness | comfort |
| **delusion** | vamphoric load, comfort | exposure: remnant witness, martyrdom, crisis, revival |
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

## Patience and the great falling away (v7.8)

**Patience (2 Pet 3:9).** After the atonement the end is held open —
consummation cannot complete — as long as the world is still
responding, measured as the harvest rate among the still-unconverted.
A world already won (remnant ≥ 50%) is fullness, not dryness; patience
is never exhausted by having little field left.

**The great falling away (2 Thess 2).** When the harvest stays dry
through a long season in a world that has not been won, patience is
exhausted and the apostasy fires once: the lukewarm remnant falls (the
love of many grows cold), strong delusion is sent on those who refused
to love the truth (2:11), the restrainer is removed (distance jumps —
lawlessness unveiled, 2:7), and the adversary is released for a little
while (Rev 20:3). After the falling away the verdict is in: gradual
renewal is no longer possible.

**Parousia (Matt 24:22).** The tribulation does not end gradually —
those days are cut short for the sake of the elect. After a bounded
endurance past the falling away (relative to the emergent event, not a
calendar), the world ends in a fourth way: the enduring remnant
vindicated, the lawless one destroyed by the appearance of His coming.

**The tribulation tax (v7.9).** Between the falling away and the
parousia, the tribulation is the greatest tax the remnant ever pays:

- **The martyr seed is muted** (Rev 13:7 — it is given to him to
  conquer the saints): the blood falls on ground held by strong
  delusion and bears no fruit until the vindication. The souls wait
  under the altar (Rev 6:9), counted and answered at the parousia.
- **He makes war on the saints directly**: released, his persecution
  bypasses the minority damper — a large remnant no longer shields
  itself by its size (~110 martyrs per tribulation, up from near zero).
- **His movements strike harder and faster** (Rev 12:12 — he knows his
  time is short): scheme force and cadence are boosted, and division —
  brother betraying brother (Matt 24:10) — becomes his sharpest blade,
  with doubled schism force on a short cooldown.
- **The deception that would take even the elect** (Matt 24:24): every
  tribulation tick, every remnant member faces a 20% apostasy chance
  shielded only by formation — 2%/tick for the deeply formed,
  10%/tick for the barely formed. "If possible" is load-bearing: the
  elect mostly stand, the middle is sifted away. The enduring remnant
  at the parousia falls from ~28% to ~8% — when the Son of Man comes,
  He finds faith, but little (Luke 18:8). The sift can even drag a
  tribulation world below the extinction floor into consummation:
  the falling away can now genuinely kill a world it grips.

A complete falling-away arc from one history: incarnation 259 →
deicide 269 → atonement (record cancelled 81%) → response dries →
falling away 293 (343 grow cold) → tribulation (martyr seed muted,
war on the saints) → parousia 353, enduring remnant vindicated and
the souls under the altar answered.

Ensemble (100 seeds, 800 ticks): **79% renewal / 12% consummation /
9% parousia**, zero unresolved. The seed endures in every consummated
and every parousia world. Our own world, per CDT, reads as a history
inside the patience window — the contest deliberately held open.

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
