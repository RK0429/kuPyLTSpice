# pyright: reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

import sys
from pathlib import Path

from kuPyLTSpice import SimRunner, SpiceEditor
from kuPyLTSpice.sim.process_callback import (
    ProcessCallback,  # Importing the ProcessCallback class type
)

sys.path.insert(0, "..")  # This is to allow the import from the PyLTSpice folder


class CallbackProc(ProcessCallback):
    """Class encapsulating the callback function.

    It can have whatever name.
    """

    @staticmethod
    def callback(raw_file: Path | str, log_file: Path | str, **kwargs: object) -> object:
        print(f"Handling the simulation data of {raw_file}, log file {log_file}")
        # Doing some processing here
        return f"Parsed Result of {raw_file}, log file {log_file}"


if __name__ == "__main__":
    from kuPyLTSpice.sim.ltspice_simulator import LTspice

    runner = SimRunner(
        output_folder="./temp_batch4", simulator=LTspice
    )  # Configures the simulator to use and output
    # folder

    netlist = SpiceEditor(
        "./testfiles/Batch_Test.asc"
    )  # Open the Spice Model, and creates the .net
    # set default arguments
    netlist.set_parameters(res=0, cap=100e-6)
    netlist.set_component_value("R2", "2k")  # Modifying the value of a resistor
    netlist.set_component_value("R1", "4k")
    netlist.set_element_model("V3", "SINE(0 1 3k 0 0 0)")  # Modifying the
    netlist.set_component_value("XU1:C2", 20e-12)  # modifying a
    # define simulation
    netlist.add_instructions("; Simulation settings", ";.param run = 0")
    netlist.set_parameter("run", 0)

    for opamp in ("AD712", "AD820"):
        netlist.set_element_model("XU1", opamp)
        for supply_voltage in (5, 10, 15):
            netlist.set_component_value("V1", supply_voltage)
            netlist.set_component_value("V2", -supply_voltage)
            # overriding the automatic netlist naming
            run_netlist_file = f"{netlist.netlist_file.stem}_{opamp}_{supply_voltage}.net"
            runner.run(netlist, run_filename=run_netlist_file, callback=CallbackProc)

    for result in runner:
        print(result)  # Prints the result of the callback function

    netlist.reset_netlist()
    netlist.add_instructions(  # Adding additional instructions
        "; Simulation settings",
        ".ac dec 30 10 1Meg",
        ".meas AC Gain MAX mag(V(out)) ; find the peak response and call it " "Gain" "",
        ".meas AC Fcut TRIG mag(V(out))=Gain/sqrt(2) FALL=last",
    )

    task = runner.run(netlist, run_filename="no_callback.net")
    if task is None:
        raise RuntimeError("Simulation task did not start")
    result = task.wait_results()
    if result is None:
        raise RuntimeError("Simulation did not produce results")
    raw, log = result
    CallbackProc.callback(raw, log)

    results = runner.wait_completion(1, abort_all_on_timeout=True)

    # Sim Statistics
    print(f"Successful/Total Simulations: {runner.okSim}/{runner.runno}")
