#!/usr/bin/env python

# -------------------------------------------------------------------------------
# Name:        ltsteps.py
# Purpose:     Process LTSpice output files and align data for usage in a spread-
#              sheet tool such as Excel, or Calc.
#
# Author:      Nuno Brum (nuno.brum@gmail.com)
#
# Licence:     refer to the LICENSE file
# -------------------------------------------------------------------------------
import logging

from kupicelib.log.ltsteps import (
    LTSpiceExport,
    LTSpiceLogReader,
    reformat_LTSpice_export,
)

_logger = logging.getLogger("kupicelib.LTSteps")
_logger.info(
    "This module is maintained for backward compatibility. Use kupicelib.log.ltsteps instead"
)

# Re-export the classes
__all__ = ["LTSpiceExport", "LTSpiceLogReader", "reformat_LTSpice_export"]
