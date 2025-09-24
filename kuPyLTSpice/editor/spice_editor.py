#!/usr/bin/env python
# -------------------------------------------------------------------------------
#    ____        _   _____ ____        _
#   |  _ \ _   _| | |_   _/ ___| _ __ (_) ___ ___
#   | |_) | | | | |   | | \___ \| '_ \| |/ __/ _ \
#   |  __/| |_| | |___| |  ___) | |_) | | (_|  __/
#   |_|    \__, |_____|_| |____/| .__/|_|\___\___|
#          |___/                |_|
#
# Name:        spice_editor.py
# Purpose:     Class made to update Generic Spice netlists
#
# Author:      Nuno Brum (nuno.brum@gmail.com)
#
# Licence:     refer to the LICENSE file
# -------------------------------------------------------------------------------
import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from kupicelib.editor.spice_editor import SpiceEditor as SpiceEditorBase
from kupicelib.sim.run_task import RunTask
from kupicelib.sim.simulator import Simulator, run_function

# Use our custom LTspice implementation with Mac support
from kuPyLTSpice.sim.ltspice_simulator import LTspice

_logger = logging.getLogger("kupicelib.SpiceEditor")
_logger.info(
    "This is maintained for compatibility issues. Use kupicelib.editor.spice_editor instead"
)


class SpiceEditor(SpiceEditorBase):

    def __init__(
        self,
        netlist_file: str | Path,
        encoding: str = 'autodetect',
        create_blank: bool = False,
    ) -> None:
        netlist_file = Path(netlist_file)
        if netlist_file.suffix == ".asc":
            # Log platform-specific information when creating a netlist
            if _logger.isEnabledFor(logging.INFO) and sys.platform == "darwin":
                _logger.info("Creating netlist on MacOS using LTSpice")

            ltspice_cls = LTspice.create_from(None)  # pyright: ignore[reportCallIssue]
            command: list[str]
            if ltspice_cls.spice_exe:
                command = [*ltspice_cls.spice_exe, "-netlist", netlist_file.as_posix()]
            else:
                command = ["ltspice", "-netlist", netlist_file.as_posix()]
            run_function(command)
            netlist_file = netlist_file.with_suffix(".net")
        super().__init__(netlist_file, encoding, create_blank)

    def run(
        self,
        wait_resource: bool = True,
        callback: type[Any] | Callable[[Path, Path], Any] | None = None,
        timeout: float | None = 600,
        run_filename: str | None = None,
        simulator: type[Simulator] | None = None,
    ) -> RunTask | None:
        simulator_cls: type[Simulator]
        if simulator is None:
            simulator_cls = LTspice

            # Log platform-specific information when running a simulation
            if _logger.isEnabledFor(logging.INFO) and sys.platform == "darwin":
                _logger.info(
                    "Running simulation on MacOS using LTSpice at: %s",
                    getattr(simulator_cls, "executable", "unknown"),
                )
        else:
            simulator_cls = simulator

        return super().run(
            wait_resource,
            callback,
            timeout,
            run_filename,
            simulator_cls,
        )
