# -------------------------------------------------------------------------------
#    ____        _   _____ ____        _
#   |  _ \ _   _| | |_   _/ ___| _ __ (_) ___ ___
#   | |_) | | | | |   | | \___ \| '_ \| |/ __/ _ \
#   |  __/| |_| | |___| |  ___) | |_) | | (_|  __/
#   |_|    \__, |_____|_| |____/| .__/|_|\___\___|
#          |___/                |_|
#
# Name:        sweep_iterators.py
# Purpose:     Iterators to use for sweeping values
#
# Author:      Nuno Brum (nuno.brum@gmail.com)
#
# Created:     24-07-2020
# Licence:     refer to the LICENSE file
#
# -------------------------------------------------------------------------------

# ======================== Andreas Kaeberlein Iterator =========================

from collections.abc import Sequence
from typing import Any, TypedDict


class IteratorEntry(TypedDict):
    name: str
    values: list[Any]


class sweep_iterators:

    # *****************************
    def __init__(self):
        """Initialization."""
        self.numTotalIterations: int = 0  # total of iteration if all loops are executed
        self.numCurrentIteration: int = 0  # current iteration
        self.iteratorEntrys: list[IteratorEntry] = []  # list of dicts for iterator entries
        self.idxForNextIter: list[int] = []  # currently used entry value for loop

    # *****************************

    # *****************************
    def add(self, name: str = "", vals: Sequence[Any] | None = None) -> bool:
        """Add an entry to the iterator list."""
        values = list(vals) if vals is not None else []
        # check for valid arguments
        if not name or not values:
            raise ValueError("Empty arguments provided")
        # add to iterator list
        entry: IteratorEntry = {"name": name, "values": values}
        self.iteratorEntrys.append(entry)
        self.idxForNextIter.append(0)  # start on first element
        # update total number of iteration
        self.numTotalIterations = 1
        for entry in self.iteratorEntrys:
            self.numTotalIterations *= len(entry["values"])
        # reset current iterator to ensure restart
        self.numCurrentIteration = 0
        # succesfull end
        return True

    # *****************************

    # *****************************
    def done(self) -> bool:
        """Return True when all iterator combinations were consumed."""
        if not self.iteratorEntrys:
            return True
        return self.numCurrentIteration >= self.numTotalIterations

    # *****************************

    # *****************************
    def next(self) -> dict[str, Any]:
        """Return the next parameter set for the sweep."""
        if not self.iteratorEntrys:
            raise ValueError("No iterator entries defined. Use the 'add' method first.")
        next_iter: dict[str, Any] = {}
        for index, entry in enumerate(self.iteratorEntrys):
            next_iter[entry["name"]] = entry["values"][self.idxForNextIter[index]]
        for i in range(len(self.idxForNextIter) - 1, -1, -1):
            if i == len(self.idxForNextIter) - 1:
                self.idxForNextIter[i] += 1
            if self.idxForNextIter[i] >= len(self.iteratorEntrys[i]["values"]):
                self.idxForNextIter[i] = 0
                if i > 0:
                    self.idxForNextIter[i - 1] += 1
        self.numCurrentIteration += 1
        return next_iter

    # *****************************
