# pyright: reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false

from __future__ import annotations

from pathlib import Path

from kuPyLTSpice.log.ltsteps import LTSpiceLogReader


def main() -> None:
    log_path = Path("./testfiles/Batch_Test_AD820_15.log")
    data = LTSpiceLogReader(log_path)

    step_names = data.get_step_vars()
    measure_names = data.get_measure_names()

    print("Number of steps  :", data.step_count)
    header_steps = " ".join(f"{step:15s}" for step in step_names)
    header_measures = " ".join(f"{name:15s}" for name in measure_names)
    print(header_steps, end="")
    print(header_measures)

    for index in range(data.step_count):
        step_values = " ".join(f"{data[step][index]:15}" for step in step_names)
        measure_values = " ".join(
            f"{data[name][index]:15}" for name in measure_names
        )
        print(step_values, end="")
        print(measure_values)

    print("Total number of measures found :", data.measure_count)


if __name__ == "__main__":
    main()
