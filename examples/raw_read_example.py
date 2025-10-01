from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from kupicelib.raw.raw_read import RawRead as RawReadType
else:  # pragma: no cover
    from kuPyLTSpice import RawRead as RawReadType

RawRead = RawReadType


def main() -> None:
    reader = RawRead("./testfiles/TRAN - STEP.raw")

    print(reader.get_trace_names())
    print(reader.get_raw_property())

    current_trace = reader.get_trace("I(R1)")
    time_trace = reader.get_trace("time")  # Gets the time axis
    steps = list(reader.get_steps())
    for index, step in enumerate(steps):
        plt.plot(time_trace.get_wave(index), current_trace.get_wave(index), label=str(step))

    plt.legend()  # order a legend
    plt.show()


if __name__ == "__main__":  # pragma: no cover
    main()
