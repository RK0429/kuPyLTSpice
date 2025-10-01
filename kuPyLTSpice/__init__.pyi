from __future__ import annotations

from typing import Any

from kupicelib.editor.asc_editor import AscEditor as _AscEditor
from kupicelib.editor.spice_editor import (
    SpiceCircuit as _SpiceCircuit,
)
from kupicelib.editor.spice_editor import (
    SpiceEditor as _SpiceEditor,
)
from kupicelib.log.ltsteps import LTSpiceLogReader as _LTSpiceLogReader
from kupicelib.raw.raw_read import RawRead as _RawRead
from kupicelib.raw.raw_write import RawWrite as _RawWrite
from kupicelib.raw.raw_write import Trace as _Trace

from .sim.ltspice_simulator import LTspice
from .sim.sim_batch import SimCommander
from .sim.sim_runner import SimRunner

AscEditor = _AscEditor
SpiceEditor = _SpiceEditor
SpiceCircuit = _SpiceCircuit
LTSpiceLogReader = _LTSpiceLogReader
RawRead = _RawRead
RawWrite = _RawWrite
Trace = _Trace

__all__ = [
    "AscEditor",
    "LTSpiceLogReader",
    "LTspice",
    "RawRead",
    "RawWrite",
    "SimCommander",
    "SimRunner",
    "SpiceCircuit",
    "SpiceEditor",
    "Trace",
    "add_log_handler",
    "all_loggers",
    "set_log_level",
]

def all_loggers() -> list[str]: ...

def set_log_level(level: int) -> None: ...

def add_log_handler(handler: Any) -> None: ...
