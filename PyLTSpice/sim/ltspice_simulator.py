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
# Name:        ltspice_simulator.py
# Purpose:     Represents a LTspice tool and it's command line options
#
# Author:      Nuno Brum (nuno.brum@gmail.com)
#
# Created:     23-12-2016
# Licence:     refer to the LICENSE file
# -------------------------------------------------------------------------------
import sys
import os
import logging
from pathlib import Path
from typing import Union, Optional

from spicelib.sim.simulator import run_function, Simulator

_logger = logging.getLogger("spicelib.LTSpiceSimulator")
_logger.info("This is maintained for backward compatibility. Use spicelib.sim.ltspice_simulator instead")


# Create a custom LTspice class that extends the base class from spicelib
class LTspiceCustom(Simulator):
    """LTspice simulator implementation with cross-platform support"""

    @classmethod
    def get_default_executable(cls) -> Path:
        """
        Returns the default location for the LTspice executable based on the platform

        Returns:
            Path: Path to the LTspice executable
        """
        if sys.platform == 'win32':
            # Windows default path
            return Path(r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe")
        elif sys.platform == 'darwin':
            # Mac OS default path
            # LTspice is typically installed in /Applications on Mac
            return Path("/Applications/LTspice.app/Contents/MacOS/LTspice")
        else:
            # Linux or other platforms - assume wine is used
            # This path will need to be adjusted for the specific system
            _logger.warning("Platform %s is not directly supported. Assuming wine is used.", sys.platform)
            return Path("wine")  # Just use 'wine' command and rely on user to set up correctly

    @classmethod
    def create_from(cls, exec_path: Optional[Union[str, Path]] = None) -> 'LTspiceCustom':
        """
        Creates a new LTspice simulator instance with the given executable path

        Args:
            exec_path: Path to the LTspice executable or None to use default

        Returns:
            LTspiceCustom: A new LTspice simulator instance
        """
        if exec_path is None:
            exec_path = cls.get_default_executable()
        elif not isinstance(exec_path, Path):
            exec_path = Path(exec_path)

        # If on Mac, check if path exists
        if sys.platform == 'darwin' and exec_path == cls.get_default_executable() and not exec_path.exists():
            _logger.warning("Default LTspice executable not found at %s", exec_path)
            # Try alternative locations
            alt_paths = [
                Path("/Applications/LTspice.app/Contents/MacOS/LTspice"),
                Path(os.path.expanduser("~/Applications/LTspice.app/Contents/MacOS/LTspice"))
            ]
            for path in alt_paths:
                if path.exists():
                    _logger.info("Found LTspice executable at %s", path)
                    exec_path = path
                    break

        return LTspiceCustom(str(exec_path))

    def __init__(self, executable_path: str):
        """
        Initialize the LTspice simulator with the given executable path

        Args:
            executable_path: Path to the LTspice executable
        """
        super().__init__(executable_path)

    def create_netlist(self, asc_file: Union[str, Path], cmd_line_switches: Optional[list] = None) -> Path:
        """
        Create a netlist from an ASC file

        Args:
            asc_file: Path to the ASC file
            cmd_line_switches: Additional command line switches

        Returns:
            Path: Path to the created netlist file
        """
        if not isinstance(asc_file, Path):
            asc_file = Path(asc_file)

        if not asc_file.exists():
            raise FileNotFoundError(f"ASC file not found: {asc_file}")

        # Build command line arguments
        args = ["-netlist"]
        if cmd_line_switches:
            args.extend(cmd_line_switches)
        args.append(str(asc_file))

        # On Mac, we need to use the actual executable
        if sys.platform == 'darwin':
            # Run LTspice to create the netlist
            run_function(self.executable, args)
        else:
            # On Windows and Linux (wine)
            run_function(self.executable, args)

        # Return the path to the created netlist file
        return asc_file.with_suffix(".net")

    def run_netlist(self, netlist_file: Union[str, Path], cmd_line_switches: Optional[list] = None) -> bool:
        """
        Run a simulation on a netlist file

        Args:
            netlist_file: Path to the netlist file
            cmd_line_switches: Additional command line switches

        Returns:
            bool: True if the simulation was successful
        """
        if not isinstance(netlist_file, Path):
            netlist_file = Path(netlist_file)

        if not netlist_file.exists():
            raise FileNotFoundError(f"Netlist file not found: {netlist_file}")

        # Build command line arguments
        args = ["-b"]  # Batch mode
        if cmd_line_switches:
            args.extend(cmd_line_switches)
        args.append(str(netlist_file))

        # Run LTspice to run the simulation
        return run_function(self.executable, args) == 0


# Replace the imported LTspice with our custom implementation
LTspice = LTspiceCustom
