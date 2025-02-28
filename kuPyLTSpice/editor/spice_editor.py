#!/usr/bin/env python
# coding=utf-8
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
from pathlib import Path
from typing import Any, Callable, Optional, Type, Union

from kupicelib.editor.spice_editor import SpiceEditor as SpiceEditorBase

# Use our custom LTspice implementation with Mac support
from kuPyLTSpice.sim.ltspice_simulator import LTspice

_logger = logging.getLogger("kupicelib.SpiceEditor")
_logger.info(
    "This is maintained for compatibility issues. Use kupicelib.editor.spice_editor instead"
)


class SpiceEditor(SpiceEditorBase):

    def __init__(
        self, netlist_file: Union[str, Path], encoding="autodetect", create_blank=False
    ):
        netlist_file = Path(netlist_file)
        if netlist_file.suffix == ".asc":
            # Log platform-specific information when creating a netlist
            if _logger.isEnabledFor(logging.INFO) and sys.platform == "darwin":
                _logger.info("Creating netlist on MacOS using LTSpice")

            # Create a LTspice instance to use its create_netlist method
            ltspice_instance = LTspice.create_from(None)
            ltspice_instance.create_netlist(netlist_file)
            netlist_file = netlist_file.with_suffix(".net")
        super().__init__(netlist_file, encoding, create_blank)

    def run(
        self,
        wait_resource: bool = True,
        callback: Optional[Union[Type[Any], Callable[[Path, Path], Any]]] = None,
        timeout: Optional[float] = 600,
        run_filename: Optional[str] = None,
        simulator=None,
    ):
        if simulator is None:
            simulator = LTspice

            # Log platform-specific information when running a simulation
            if _logger.isEnabledFor(logging.INFO) and sys.platform == "darwin":
                _logger.info(
                    "Running simulation on MacOS using LTSpice at: %s",
                    getattr(simulator, "executable", "unknown"),
                )

        return super().run(wait_resource, callback, timeout, run_filename, simulator)
