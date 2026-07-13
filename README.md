# DSA — The Emergent Covenant Engine

An agent-based simulation of the biblical narrative as **physics**: a
world whose wars, awakenings, apostasies, incarnation, and ending all
*emerge* from coupled feedback between people and their environment.
Nothing in the engine reads a calendar. Every history is different;
every history is the same story.

Built on three theological frameworks documented in [`docs/`](docs/):
**Covenant Distance Theology** (CDT — the narrative arc of distance and
drawing-near), **Divine Sovereign Agency** (DSA — God's chosen,
in-the-moment engagement), and **Shared Collective Cosmology** (SCC —
the universal three-realm background), with their satellite concepts:
Anti-Life Delusion, Vamphoric Systems, and the skin of the apple.

## Quick start

```bash
pip install -r requirements.txt

python run_emergent.py                    # one 600-tick history
python run_emergent.py --seed 7 --ticks 800   # a different providence
python run_emergent.py --ensemble 100     # map the outcome landscape
python run_emergent.py --cartography      # sweep the theology knobs
python run_emergent.py --sensitivity      # one-factor parameter sweeps
```

Outputs land in `output/`: a six-panel history plot, event timeline
CSVs, and ensemble/cartography maps. A 10,000-agent, 800-tick history
runs in a few seconds (agents are vectorized numpy arrays, not
objects); a 100-seed ensemble takes ~2–4 minutes on a modern machine.

Two engines live in this repository:

| | Where | What it is |
|---|---|---|
| **Emergent Covenant Engine (v8)** | `emergent/`, `run_emergent.py` | The main engine, described below |
| CDT arc engine (earlier work) | `src/`, `run_simulation.py` | A tick-based engine that grows the biblical arc (flood → calling → temple → incarnation) from entropy dynamics |

## The one rule

**Data initializes; feedback drives.** External data (real or
synthetic) enters exactly once, as initial conditions
(`RegionInit` in `emergent/config.py`). After tick zero, every
macro-event — war, revival, schism, persecution, secular drift,
incarnation, the end itself — is a threshold crossing of an
accumulator fed by agent behavior. There are no dated triggers, no
scripted eras, no year gates. (The predecessor engine, v6.5, had World
Wars hard-coded at 1914/1939 and consummation gated behind
`year >= 2030`; this engine was built to kill that pattern.)

## The master equation

Covenant distance, not entropy, is the world-building variable:

```
distance(t+1) = distance(t) + rebellion_flux − nearness_flux

rebellion_flux = bent × (1 + vamphoric)(1 + ratchet)(1 + toil)
               + empire capture + mass violence
nearness_flux  = remnant divine labor × (1 + unity)      [the response]
               + nearness_pull × nearness × (0.5 + 0.5·distance)
                                                  [grace abounds, Rom 5:20]
```

Two threads, per CDT: humanity's cumulative movement away, and God's
relentless counter-movement of drawing near. Entropy is demoted to the
*physical shadow* that relational breach casts on the world. A
near-permanent **ratchet** (cumulative rebellion) raises the floor
under distance — within history the world never returns to Eden.

## The cast

- **The Seed & the Toil (Gen 3)** — every world starts with Eve's
  promise (one living bearer of the seed, unlosable, passed at death,
  *fulfilled and retired at the incarnation*) and Adam's curse (toil:
  comfort grows slowly, rebuilding is sweaty — severe mercy against
  the comfort trap, which the vamphoric system's oldest sales pitch is
  to buy out: Babel).
- **The remnant** — faith transmits through households (imperfectly,
  eroded by comfort), deepens under hardship, and works: divine labor
  is the human half of the nearness flux.
- **The Adversary** — the prince of the power of the air. Parasitic,
  never a rival god: his power derives from the breach, is drained by
  being *named*, and is disarmed at the cross. Five schemes, chosen
  intelligently: QUENCH the revival wick, GILD the strong church,
  SCHISM the divided one, ACCUSE the deep remnant, INCITE war where no
  seed can grow. Every scheme widens the breach — and thereby hastens
  the fullness of time that ends him (1 Cor 2:8).
- **Blindness, in two layers (the skin of the apple, SCC)** — the
  FLESH (the ancient three-realm default: distorts hearing, leaves
  entry points, reworked only by discipleship) and the SKIN (the
  secular coating: grows where the buyout succeeds, blocks hearing
  entirely, but brittle — crises flake it, one witness encounter
  shatters it, and it cracks *into* the flesh: the double surge of
  conversions and occultism together).
- **The Container** — the trap at the end: skin become architecture.
  Self-reinforcing, it *metabolizes* exposure instead of transmitting
  it — crises arrive as content, witness is indistinguishable from its
  simulacra, martyrdom trends. Hyperreality as vamphoric
  infrastructure; the substrate of the strong delusion. Drained only
  by embodied gathering. The 7-day world does not get out of it.

## The sequence no one schedules

Each history finds its own way through (or fails to):

1. **Incarnation** at the fullness of time: heavy record + a prepared
   vessel (a lone bearer in a backwater suffices). Nearness embodied,
   the Light in person, the adversary exposed daily.
2. **Deicide** — the scheme he cannot resist and cannot survive. The
   TAV: the Account of all rebellion ever enacted is presented and
   **paid** (Col 2:14), and the same nail seals the old aeon's
   condemnation (John 12:31). Atonement is retroactive for the
   faithful: the covering scales with the store of every believer who
   lived and died before it (Heb 11:39-40). If no one takes the bait,
   the life is laid down freely (John 10:18).
3. **The patience of God** — the end held open while the world still
   responds (2 Pet 3:9).
4. **The great falling away** — when the harvest dries in an unwon
   world: the lukewarm fall, strong delusion seals the flesh, the
   restrainer is removed, the adversary is loosed, the Container
   completes (2 Thess 2).
5. **The tribulation** — the greatest tax on the remnant: the martyr
   seed muted (Rev 13:7), war on the saints past the minority damper,
   division doubled, and deception that would take, *if possible*,
   even the elect (Matt 24:24; 20%/tick shielded by formation).
6. **The Shaking** (Hag 2:6, Heb 12:27) — every history ends here.
   The old heavens and earth pass; the fire tests each world's work
   (1 Cor 3:12-15); what cannot be shaken remains, and the 8th day
   dawns on it.

## Endings: the sequence law

No world exits history, and no world skips the apostasy. Two
structural laws, both scriptural, hold in every history: the gospel
reaches its fullness before the end (Matt 24:14), and *the day does
not come unless the rebellion comes first* (2 Thess 2:3). Fullness is
a **stage, not an exit** — a won world's completed harvest *summons*
the falling away, the tribulation, and the parousia.

After the parousia the sequence continues per Revelation 20–21: the
**millennium** (the accuser bound, the first-resurrection reign, the
two Jerusalems in maximal correspondence), the **release** (the
nations deceived one final time — Gog and Magog, rebellion with no
curse and no excuse: agency isolated from every condition), fire from
heaven, the passing away — and the **descent**: the treasure banked
across the whole history comes down as the city-who-is-the-people,
gates never shut, the increase never ending.

| Verdict | How | Account | Typical remains |
|---|---|---|---|
| **descent** — harvest road | fullness → the rebellion → tribulation → parousia → millennium → release → the city comes down | paid | ~80% |
| **descent** — dry road | patience exhausted → the rebellion → the same sequence with a smaller remnant | paid | ~55% |
| **consummation** | the blind death — no vessel, no incarnation | **unpaid** — answered in the fall | ~36% |

In every fallen pre-incarnation world, the seed still endures — the
ending event records where. Nothing offered is lost: even a doomed
world's faithful dead are banked as treasure — and in saved worlds
that treasure *is* the Bride, descending.

Default-parameter distribution (100 seeds, 1200 ticks): roughly
**3/4 descent, 1/5 consummation**, remainder contested (the tick
limit arrived before the end did).

## What the model believes (findings from its own ensembles)

- **Renewal share tracks revival count almost linearly**, whatever
  knob produces it — awakening frequency is the proximate cause of
  every saved world.
- **The ratchet damns, not the bent**: how much of the curse *sticks*
  matters far more than how bent people are — which is the model
  pointing at atonement before atonement was implemented.
- **A gospel that only reaches the already-revived saves no one**: an
  early atonement gated on a thriving vessel showed perfect
  correlation and zero causation. Retuned to come to the weak, it
  saves at the margin. ("While we were still sinners.")
- **A stronger adversary can raise the salvation rate**: his schemes
  stick to the record, and the record triggers the fullness of time.
  He hastens his own end.
- **Doomed worlds die blind, not late** — final delusion separates
  the outcomes bimodally; no world ends lukewarm.
- **Worlds that suffer the falling away end with the Container at
  ~0.54 vs ~0.12 elsewhere** — the trap is at the end.

## Repository map

```
emergent/
  config.py        every parameter + RegionInit (the only data inlet)
  population.py    vectorized agents: formation, skin/flesh, seed, lock
  environment.py   distance, nearness, ratchet, comfort, strain,
                   revival tension, the Container
  adversary.py     the prince of the air: power, exposure, five schemes
  simulation.py    the orchestrator: incarnation -> deicide -> atonement,
                   patience, falling away, tribulation, the Shaking
  ensemble.py      parallel many-seed outcome mapping
  analysis.py      one-factor sensitivity sweeps
run_emergent.py    CLI, plots, ensemble + cartography renderers
docs/
  Emergent_Engine.md          the full design log, version by version
  Covenant_Distance_Theology.md, Divine_Sovereign_Agency.md,
  Shared_Collective_Cosmology.md, Anti_Life_Delusion.md,
  Vamphoric_Systems.md        the theological source frameworks
src/, run_simulation.py       the earlier CDT arc engine
```

## Reading a history

Run any seed and read `output/emergent_events.csv` top to bottom — it
is a chronicle: crises, revivals, schemes, hardenings, the incarnation
in some backwater, a deicide ten ticks later, the falling away, the
souls under the altar answered, and at the last line the Shaking with
its verdict and its remainder. Different seeds, different chronicles,
one plot. That is the thesis of the whole project: **history is not
scripted, and it is still going somewhere.**
