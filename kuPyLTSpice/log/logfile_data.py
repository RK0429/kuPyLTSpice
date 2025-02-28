#!/usr/bin/env python
# coding=utf-8

# -------------------------------------------------------------------------------
# Name:        logfile_data.py
# Purpose:     Store data related to log files. This is a superclass of LTSpiceLogReader
#
# Author:      Nuno Brum (nuno.brum@gmail.com)
#
# Licence:     refer to the LICENSE file
# -------------------------------------------------------------------------------

import logging

from kupicelib.log.logfile_data import LogfileData, LTComplex

_logger = logging.getLogger("kupicelib.LTSteps")
_logger.info("This module is deprecated. Use kupicelib.log.logfile_data instead")

# Re-export the classes
__all__ = ["LogfileData", "LTComplex"]
