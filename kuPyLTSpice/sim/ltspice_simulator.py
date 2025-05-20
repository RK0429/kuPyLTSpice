#!/usr/bin/env python
# coding=utf-8

import logging
import os
import shutil
import subprocess

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
from pathlib import Path
from typing import Any, List, Optional, Union

from kupicelib.sim.simulator import Simulator, run_function

_logger = logging.getLogger("kupicelib.LTSpiceSimulator")
_logger.info(
    "This is maintained for backward compatibility. Use kupicelib.sim.ltspice_simulator instead"
)


# Create a custom LTspice class that extends the base class from kupicelib
class LTspiceCustom(Simulator):
    """LTspice simulator implementation with cross-platform support"""

    # Define the class attributes required by the Simulator base class
    spice_exe: List[str] = []
    process_name: str = "XVIIx64.exe"  # Default process name for Windows

    @classmethod
    def get_default_executable(cls) -> Path:
        """
        Returns the default location for the LTspice executable based on the platform

        Returns:
            Path: Path to the LTspice executable
        """
        if sys.platform == "win32":
            # Windows default path
            return Path(r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe")
        elif sys.platform == "darwin":
            # Mac OS default path
            # LTspice is typically installed in /Applications on Mac
            return Path("/Applications/LTspice.app/Contents/MacOS/LTspice")
        else:
            # Linux or other platforms - assume wine is used
            # This path will need to be adjusted for the specific system
            _logger.warning(
                "Platform %s is not directly supported. Assuming wine is used.",
                sys.platform,
            )
            return Path(
                "wine"
            )  # Just use 'wine' command and rely on user to set up correctly

    @classmethod
    def create_from(cls, path_to_exe, process_name=None):
        """
        Creates a simulator class from a path to the simulator executable

        Args:
            path_to_exe: Path to the LTspice executable or None to use default
            process_name: Optional process name for task manager identification

        Returns:
            Simulator: A new LTspice simulator instance
        """
        # Use default executable if none provided
        if path_to_exe is None:
            path_to_exe = cls.get_default_executable()
        elif not isinstance(path_to_exe, Path):
            path_to_exe = Path(path_to_exe)

        # Add Windows alternative path discovery
        if (
            sys.platform == "win32"
            and path_to_exe == cls.get_default_executable()
            and not path_to_exe.exists()
        ):
            _logger.warning("Default LTspice executable not found at %s", path_to_exe)
            alt_paths = [
                Path(os.path.expanduser(r"~\AppData\Local\Programs\ADI\LTspice\LTspice.exe")),
                Path(r"C:\Program Files\ADI\LTspice\LTspice.exe"),
                Path(r"C:\Program Files (x86)\ADI\LTspice\LTspice.exe"),
            ]
            for path in alt_paths:
                if path.exists():
                    _logger.info("Found LTspice executable at %s", path)
                    path_to_exe = path
                    break

        # If on Mac, check if path exists
        if (
            sys.platform == "darwin"
            and path_to_exe == cls.get_default_executable()
            and not path_to_exe.exists()
        ):
            _logger.warning("Default LTspice executable not found at %s", path_to_exe)
            # Try alternative locations
            alt_paths = [
                Path("/Applications/LTspice.app/Contents/MacOS/LTspice"),
                Path(
                    os.path.expanduser(
                        "~/Applications/LTspice.app/Contents/MacOS/LTspice"
                    )
                ),
            ]
            for path in alt_paths:
                if path.exists():
                    _logger.info("Found LTspice executable at %s", path)
                    path_to_exe = path
                    break

        # Try wine-based Windows installation on non-Windows platforms
        if (
            sys.platform in ("darwin", "linux")
            and path_to_exe == cls.get_default_executable()
            and not path_to_exe.exists()
        ):
            wine_cmd = shutil.which("wine") or shutil.which("wine64")
            if wine_cmd:
                wine_prefix = os.path.expanduser("~/.wine/drive_c")
                alt_wine_paths = [
                    Path(wine_prefix) / "Program Files" / "ADI" / "LTspice" / "LTspice.exe",
                    Path(wine_prefix) / "Program Files (x86)" / "ADI" / "LTspice" / "LTspice.exe",
                    Path(wine_prefix) / "Program Files" / "LTC" / "LTspiceXVII" / "XVIIx64.exe",
                ]
                for wpath in alt_wine_paths:
                    if wpath.exists():
                        _logger.info("Found LTspice executable under wine at %s", wpath)
                        cmd = f"{wine_cmd} {wpath.as_posix()}"
                        return super().create_from(cmd, process_name)

        # Call parent class's create_from method
        return super().create_from(str(path_to_exe), process_name)

    @classmethod
    def create_netlist(
        cls, asc_file: Union[str, Path], cmd_line_switches: Optional[list] = None
    ) -> Path:
        """
        Create a netlist from an ASC file

        Args:
            asc_file: Path to the ASC file
            cmd_line_switches: Additional command line switches

        Returns:
            Path: Path to the created netlist file
        """
        # Ensure the spice executable is configured
        if not cls.spice_exe:
            # initialize with default executable
            cls.create_from(None)
        if not isinstance(asc_file, Path):
            asc_file = Path(asc_file)

        if not asc_file.exists():
            raise FileNotFoundError(f"ASC file not found: {asc_file}")

        # Build command line arguments
        args = ["-netlist"]
        if cmd_line_switches:
            args.extend(cmd_line_switches)
        args.append(str(asc_file))

        # Invoke LTspice to create the netlist on all platforms
        run_function([cls.spice_exe[0]] + args)

        # Return the path to the created netlist file
        return asc_file.with_suffix(".net")

    def run_netlist(
        self, netlist_file: Union[str, Path], cmd_line_switches: Optional[list] = None
    ) -> bool:
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
        return run_function([self.spice_exe[0]] + args) == 0

    @classmethod
    def run(
        cls,
        netlist_file: Union[str, Path],
        cmd_line_switches: Optional[List[Any]] = None,
        timeout: Optional[float] = None,
        stdout=None,
        stderr=None,
        exe_log: bool = False,
    ) -> int:
        """
        Run a simulation on a netlist file (required abstract method implementation)

        Args:
            netlist_file: Path to the netlist file
            cmd_line_switches: Additional command line switches
            timeout: Timeout for the simulation
            stdout: Where to redirect stdout
            stderr: Where to redirect stderr
            exe_log: Whether to log the execution

        Returns:
            int: Return code of the simulation
        """
        if cmd_line_switches is None:
            cmd_line_switches = []

        netlist_path = (
            Path(netlist_file) if not isinstance(netlist_file, Path) else netlist_file
        )

        # Build command line arguments
        args = cls.spice_exe + ["-b"]  # Batch mode
        args.extend(cmd_line_switches)
        args.append(str(netlist_path))

        if exe_log:
            _logger.info(f"Running LTspice simulation on {netlist_path}")

        # Run LTspice to run the simulation in the directory of the netlist file
        cwd = netlist_path.parent
        result = subprocess.run(
            args,
            timeout=timeout,
            stdout=stdout,
            stderr=stderr,
            cwd=str(cwd),
            check=False,
        )
        return result.returncode

    @classmethod
    def valid_switch(cls, switch, switch_param) -> list:
        """
        Validate LTspice command line switches (required abstract method implementation)

        Args:
            switch: The switch to validate
            switch_param: Parameters for the switch

        Returns:
            list: List of validated switches
        """
        # Basic LTspice valid switches
        valid_switches = {
            "-b": None,  # Run in batch mode
            "-netlist": None,  # Generate netlist
            "-run": None,  # Run the simulation
            "-ascii": None,  # Output results in ASCII format
            "-log": None,  # Create a log file
            "-quiet": None,  # Run quietly
        }

        if switch in valid_switches:
            if valid_switches[switch] is None:
                return [switch]
            elif switch_param is not None:
                return [switch, str(switch_param)]

        # If we get here, the switch is not valid
        _logger.warning(f"Invalid LTspice switch: {switch}")
        return []


# Replace the imported LTspice with our custom implementation
LTspice = LTspiceCustom
