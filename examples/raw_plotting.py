from __future__ import annotations

import sys
from collections.abc import Iterable, Sequence
from os.path import join as pathjoin
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
from numpy import abs as mag
from numpy import angle

if TYPE_CHECKING:
    from kupicelib.raw.raw_read import RawRead as RawReadType
else:  # pragma: no cover - typed import only used for editors
    from kuPyLTSpice import RawRead as RawReadType

RawRead = RawReadType


def what_to_units(whattype: str) -> str:
    """Determine the unit string for a given trace type."""
    if "voltage" in whattype:
        return "V"
    if "current" in whattype:
        return "A"
    return ""


def _coerce_steps(raw_steps: Sequence[int] | Iterable[int]) -> list[int]:
    """Return the provided sequence of steps as a concrete list."""
    if isinstance(raw_steps, list):
        return raw_steps
    return list(raw_steps)


def _iter_axes(axis_set: Any, index: int, is_complex: bool, total_axes: int) -> list[Any]:
    if is_complex:
        return list(axis_set[2 * index : 2 * index + 2])
    if total_axes == 1:
        return [axis_set]
    return [axis_set[index]]


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raw_filename = argv[1]
        trace_names: list[str] = list(argv[2:])
        if not trace_names:
            trace_names = ["*"]
    else:
        test_directory = "./testfiles"
        filename = "Noise.raw"
        trace_names = ["V(onoise)"]
        raw_filename = pathjoin(test_directory, filename)

    ltr = RawRead(raw_filename, trace_names, verbose=True)
    for param, value in ltr.raw_params.items():
        padding = " " * max(0, 20 - len(param))
        print(f"{param}: {padding}{str(value).strip()}")

    if trace_names == ["*"]:
        print("Reading all the traces in the raw file")
        trace_names = list(ltr.get_trace_names())

    traces: list[Any] = [ltr.get_trace(trace) for trace in trace_names]
    steps_data = (
        _coerce_steps(ltr.get_steps()) if ltr.axis is not None else [0]
    )
    print("Steps read are :", list(steps_data))

    flags = set(ltr.flags)
    n_axis = len(traces) * 2 if "complex" in flags else len(traces)

    _fig, axis_set = plt.subplots(n_axis, 1, sharex="all")
    write_labels = True

    for idx, trace in enumerate(traces):
        axes_group = _iter_axes(axis_set, idx, "complex" in flags, n_axis)
        magnitude = True
        for ax in axes_group:
            ax.grid(True)
            if "log" in flags:
                ax.set_xscale("log")
            for step_i in steps_data:
                x: Iterable[float] = (
                    ltr.get_axis(step_i)
                    if ltr.axis is not None
                    else np.arange(ltr.nPoints)
                )
                y = ltr.get_wave(trace.name, step_i)
                if "complex" in flags:
                    x = mag(x)
                    if magnitude:
                        ax.set_yscale("log")
                        y = mag(y)
                    else:
                        y = angle(y, deg=True)
                if write_labels:
                    ax.plot(x, y, label=str(step_i))
                else:
                    ax.plot(x, y)
            write_labels = False

            if "complex" in flags:
                if magnitude:
                    title = f"{trace.name} Mag [db{what_to_units(trace.whattype)}]"
                    magnitude = False
                else:
                    title = f"{trace.name} Phase [deg]"
            else:
                title = f"{trace.name} [{what_to_units(trace.whattype)}]"
            ax.set_title(title)

    if n_axis:
        plt.legend()
    plt.show()


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
