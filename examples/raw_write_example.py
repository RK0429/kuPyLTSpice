from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np

if TYPE_CHECKING:
    from kupicelib.raw.raw_read import RawRead as RawReadType
    from kupicelib.raw.raw_write import RawWrite as RawWriteType
    from kupicelib.raw.raw_write import Trace as TraceType
else:  # pragma: no cover
    from kuPyLTSpice import RawRead as RawReadType
    from kuPyLTSpice import RawWrite as RawWriteType
    from kuPyLTSpice import Trace as TraceType

RawRead = RawReadType
RawWrite = RawWriteType
Trace = TraceType

TESTFILES = Path(__file__).parent / "testfiles"


def _add_basic_traces(writer: RawWriteType) -> tuple[TraceType, TraceType, TraceType]:
    time_values = np.arange(0.0, 3e-3, 997e-11, dtype=float)
    time_trace = Trace("time", time_values.tolist())
    sine_trace = Trace("N001", np.sin(2 * np.pi * time_values * 10000).tolist())
    cosine_trace = Trace("N002", np.cos(2 * np.pi * time_values * 9970).tolist())
    writer.add_trace(time_trace)
    writer.add_trace(sine_trace)
    writer.add_trace(cosine_trace)
    return time_trace, sine_trace, cosine_trace


def test_readme_snippet() -> None:
    """Mimic the example from the README that creates a simple raw file."""
    writer = RawWrite(fastacces=False)
    _add_basic_traces(writer)
    writer.save(TESTFILES / "teste_snippet1.raw")


def _read_trace_metadata(trace_path: Path) -> tuple[str, int]:
    raw_type = ""
    wave_size = 0
    with trace_path.open(encoding="utf-8") as handle:
        for line in handle:
            tokens = line.rstrip("\r\n").split(",")
            if len(tokens) == 4 and tokens[0] == "Segments" and tokens[2] == "SegmentSize":
                wave_size = int(tokens[1]) * int(tokens[3])
            if len(tokens) == 2 and tokens[0] == "Time" and tokens[1] == "Ampl":
                raw_type = "transient"
                break
    return raw_type, wave_size

def _iter_trace_data(trace_path: Path, rows: int) -> list[tuple[float, float]]:
    with trace_path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("Time,Ampl"):
                break
        data = np.genfromtxt(handle, dtype="float,float", delimiter=",", max_rows=rows)
    result: list[tuple[float, float]] = []
    for row in data.tolist():
        pair = cast(tuple[float, float], tuple(map(float, row)))
        result.append(pair)
    return result


def test_trc2raw() -> None:
    """Convert a Teledyne-Lecroy trace file to an LTSpice raw file."""
    trace_file = TESTFILES / "Current_Lock_Front_Right_8V.trc"
    raw_type, wave_size = _read_trace_metadata(trace_file)
    if raw_type != "transient" or wave_size <= 0:
        return

    data = list(_iter_trace_data(trace_file, wave_size))
    writer = RawWrite()
    writer.add_trace(Trace("time", [row[0] for row in data]))
    writer.add_trace(Trace("Ampl", [row[1] for row in data]))
    writer.save(TESTFILES / "teste_trc.raw")


def test_axis_sync() -> None:
    """Demonstrate adding aligned traces from an existing raw file."""
    writer = RawWrite()
    _, vy, _ = _add_basic_traces(writer)
    writer.save(TESTFILES / "teste_w.raw")

    reader = RawRead(TESTFILES / "testfile.raw")
    writer.add_traces_from_raw(reader, ("V(out)",), force_axis_alignment=True)
    writer.save(TESTFILES / "merge.raw")

    max_error = max(abs(reader.get_trace("N001")[idx] - vy[idx]) for idx in range(len(vy)))
    print("Maximum interpolation error", max_error)


def test_write_ac() -> None:
    """Show how to rewrite .AC raw files."""
    writer = RawWrite()
    reference = RawRead(TESTFILES / "PI_Filter.raw")
    resampled = RawRead(TESTFILES / "PI_Filter_resampled.raw")
    writer.add_traces_from_raw(reference, ("V(N002)",))
    writer.add_traces_from_raw(
        resampled,
        "V(N002)",
        rename_format="N002_resampled",
        force_axis_alignment=True,
    )
    writer.flag_fastaccess = False
    writer.save(TESTFILES / "PI_filter_rewritten.raw")
    writer.flag_fastaccess = True
    writer.save(TESTFILES / "PI_filter_rewritten_fast.raw")


def test_write_tran() -> None:
    """Create a subset of a transient raw file."""
    reader = RawRead(TESTFILES / "TRAN - STEP.raw")
    writer = RawWrite()
    writer.add_traces_from_raw(reader, ("V(out)", "I(C1)"))
    writer.flag_fastaccess = False
    writer.save(TESTFILES / "TRAN - STEP0_normal.raw")
    writer.flag_fastaccess = True
    writer.save(TESTFILES / "TRAN - STEP0_fast.raw")


def test_combine_tran() -> None:
    """Combine traces from multiple raw files into a single dataset."""
    writer = RawWrite()
    for tag, raw_path in (
        ("AD820_15", TESTFILES / "Batch_Test_AD820_15.raw"),
        ("AD712_15", TESTFILES / "Batch_Test_AD712_15.raw"),
    ):
        reader = RawRead(raw_path)
        writer.add_traces_from_raw(
            reader,
            ("V(out)", "I(R1)"),
            rename_format="{}_{tag}",
            tag=tag,
            force_axis_alignment=True,
        )
    writer.flag_fastaccess = False
    writer.save(TESTFILES / "Batch_Test_Combine.raw")


def _run_examples() -> None:
    test_readme_snippet()
    test_axis_sync()
    test_write_ac()
    test_write_tran()
    test_combine_tran()


if __name__ == "__main__":
    _run_examples()
