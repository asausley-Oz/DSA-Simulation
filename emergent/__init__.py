"""DSA v7 — Emergent Covenant Engine.

A fully endogenous rewrite of the DSA v6.5 engine. External data (real or
synthetic) is consulted only to set initial conditions. After tick zero,
every macro-event — war, revival, schism, persecution, secular drift,
consummation — emerges from coupled feedback between agents and their
regional environments. There are no dated triggers anywhere in the engine.
"""

from .config import EmergentConfig, RegionInit, DEFAULT_REGIONS
from .simulation import EmergentSimulation

__all__ = [
    "EmergentConfig",
    "RegionInit",
    "DEFAULT_REGIONS",
    "EmergentSimulation",
]
