# -*- coding: utf-8 -*-

# Convenience direct imports - these are re-exported for user convenience
# flake8: noqa: F401
from kupicelib.editor.asc_editor import AscEditor
from kupicelib.editor.spice_editor import SpiceCircuit, SpiceEditor
from kupicelib.log.ltsteps import LTSpiceLogReader
from kupicelib.raw.raw_read import RawRead, SpiceReadException
from kupicelib.raw.raw_write import RawWrite, Trace

from PyLTSpice.sim.ltspice_simulator import LTspice
from PyLTSpice.sim.sim_batch import SimCommander
from PyLTSpice.sim.sim_runner import SimRunner


def all_loggers():
    """
    Returns all the name strings used as logger identifiers.

    :return: A List of strings which contains all the logger's names used in this library.
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


def set_log_level(level):
    """
    Sets the logging level for all loggers used in the library.

    :param level: The logging level to be used, eg. logging.ERROR, logging.DEBUG, etc.
    :type level: int
    """
    import logging

    for logger in all_loggers():
        logging.getLogger(logger).setLevel(level)


def add_log_handler(handler):
    """
    Sets the logging handler for all loggers used in the library.

    :param handler: The logging handler to be used, eg. logging.NullHandler
    :type handler: Handler
    """
    import logging

    for logger in all_loggers():
        logging.getLogger(logger).addHandler(handler)
