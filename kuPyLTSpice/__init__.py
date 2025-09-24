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
from kupicelib.raw.raw_read import Trace as _Trace
from kupicelib.raw.raw_write import RawWrite as _RawWrite

from kuPyLTSpice.sim.ltspice_simulator import LTspice
from kuPyLTSpice.sim.sim_batch import SimCommander
from kuPyLTSpice.sim.sim_runner import SimRunner

AscEditor = _AscEditor
SpiceCircuit = _SpiceCircuit
SpiceEditor = _SpiceEditor
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



def all_loggers() -> list[str]:
    """Returns all the name strings used as logger identifiers.

    :return: A List of strings which contains all the logger's names used in this
        library.
    :rtype: list[str]
    """
    return [
        "kupicelib.RunTask",
        "kupicelib.SimClient",
        "kupicelib.SimServer",
        "kupicelib.ServerSimRunner",
        "kupicelib.LTSteps",
        "kupicelib.RawRead",
        "kupicelib.LTSpiceSimulator",
        "kupicelib.SimBatch",
        "kupicelib.SimRunner",
        "kupicelib.SimStepper",
        "kupicelib.SpiceEditor",
        "kupicelib.SimBatch",
        "kupicelib.AscEditor",
        "kupicelib.LTSpiceSimulator",
    ]


def set_log_level(level: int) -> None:
    """Sets the logging level for all loggers used in the library.

    :param level: The logging level to be used, eg. logging.ERROR, logging.DEBUG, etc.
    :type level: int
    """
    import logging

    for logger in all_loggers():
        logging.getLogger(logger).setLevel(level)


def add_log_handler(handler: Any) -> None:
    """Sets the logging handler for all loggers used in the library.

    :param handler: The logging handler to be used, eg. logging.NullHandler
    :type handler: Handler
    """
    import logging

    for logger in all_loggers():
        logging.getLogger(logger).addHandler(handler)
