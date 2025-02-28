#!/usr/bin/env python

# -------------------------------------------------------------------------------
#    ____        _   _____ ____        _
#   |  _ \ _   _| | |_   _/ ___| _ __ (_) ___ ___
#   | |_) | | | | |   | | \___ \| '_ \| |/ __/ _ \
#   |  __/| |_| | |___| |  ___) | |_) | | (_|  __/
#   |_|    \__, |_____|_| |____/| .__/|_|\___\___|
#          |___/                |_|
#
# Name:        sim_stepping.py
# Purpose:     Spice Simulation Library intended to automate the exploring of
#              design corners, try different models and different parameter
#              settings.
#
# Author:      Nuno Brum (nuno.brum@gmail.com)
#
# Created:     31-07-2020
# Licence:     refer to the LICENSE file
# -------------------------------------------------------------------------------

__author__ = "Nuno Canto Brum <nuno.brum@gmail.com>"
__copyright__ = "Copyright 2017, Fribourg Switzerland"

import logging

from kupicelib.sim.sim_stepping import SimStepper

_logger = logging.getLogger("kupicelib.SimStepper")
_logger.info(
    "This module is maintained for compatibility reasons."
    " Please use the new SimStepper class from PyLTSpice.sim.sim_stepping instead"
)


if __name__ == "__main__":
    from kupicelib.editor.spice_editor import SpiceEditor
    from kupicelib.sim.sim_runner import SimRunner
    from kupicelib.utils.sweep_iterators import sweep_log

    # Create a SimRunner instance
    runner = SimRunner()

    # Create a SimStepper instance with a SpiceEditor and the runner
    test = SimStepper(SpiceEditor("../../tests/DC sweep.asc"), runner)

    # Set parameters and add sweeps
    test.set_parameter(param="R1", value="3")
    test.add_param_sweep("res", [10, 11, 9])
    test.add_value_sweep("R1", sweep_log(0.1, 10))
    # test.add_model_sweep("D1", ("model1", "model2"))

    # Run all simulations
    test.run_all()
    print("Finished")
    exit(0)
