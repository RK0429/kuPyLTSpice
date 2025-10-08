from __future__ import annotations

from pathlib import Path
from typing import cast

from kuPyLTSpice import AscEditor
from kuPyLTSpice.sim.sim_runner import SimRunner

# Force another simulator - uncomment for your OS or rely on auto-detection.
# Windows path
# simulator = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
# Mac OS path
# simulator = r"/Applications/LTspice.app/Contents/MacOS/LTspice"

def main() -> None:
    # select spice model
    runner: SimRunner = SimRunner(output_folder="./temp")

    netlist = AscEditor("./testfiles/Batch_Test.asc")
    # set default arguments
    netlist.set_parameters(res=0, cap=100e-6)
    netlist.set_component_value("R2", "2k")  # Modifying the value of a resistor
    netlist.set_component_value("R1", "4k")
    netlist.set_component_value("V3", "SINE(0 1 3k 0 0 0)")

    netlist.add_instructions("; Simulation settings", ";.param run = 0")
    netlist.set_parameter("run", 0)

    for opamp in ("AD712", "AD820"):
        netlist.set_element_model("U1", opamp)
        for supply_voltage in (5, 10, 15):
            netlist.set_component_value("V1", supply_voltage)
            netlist.set_component_value("V2", -supply_voltage)
            print("simulating OpAmp", opamp, "Voltage", supply_voltage)
            runner.run(netlist)

    for result in runner:
        if not isinstance(result, tuple):
            continue
        raw_file, log_file = cast(tuple[Path | None, Path | None], result)
        if raw_file is None or log_file is None:
            continue
        print(f"Raw file: {raw_file}, Log file: {log_file}")
        # do something with the data
        # raw_data = RawRead(raw)
        # log_data = LTSteps(log)
        # ...

    # Sim Statistics
    print(f"Successful/Total Simulations: {runner.okSim}/{runner.runno}")

    enter = input("Press enter to delete created files")
    if enter == "":
        runner.file_cleanup()


if __name__ == "__main__":
    main()
