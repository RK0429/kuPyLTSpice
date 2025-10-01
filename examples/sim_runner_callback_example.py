# pyright: reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

import logging
from pathlib import Path
from random import random
from time import sleep

try:
    from rich.logging import RichHandler
except ImportError:
    RichHandler = None
import kuPyLTSpice
from kuPyLTSpice import AscEditor, SimRunner

kuPyLTSpice.set_log_level(logging.DEBUG)
if RichHandler:
    kuPyLTSpice.add_log_handler(RichHandler())


def processing_data(raw_file: Path | str, log_file: Path | str) -> str:
    print(f"Handling the simulation data of {raw_file}, log file {log_file}")
    time_to_sleep = random() * 5
    print(f"Sleeping for {time_to_sleep} seconds")
    sleep(time_to_sleep)
    return "This is the result passed to the iterator"


runner = SimRunner(
    output_folder="./temp_batch3"
)  # Configures the simulator to use and output
# folder

netlist = AscEditor(
    "./testfiles/Batch_Test.asc"
)  # Open the Spice Model, and creates the .net
# set default arguments
netlist.set_parameters(res=0, cap=100e-6)
netlist.set_component_value("R2", "2k")  # Modifying the value of a resistor
netlist.set_component_value("R1", "4k")
netlist.set_element_model("V3", "SINE(0 1 3k 0 0 0)")  # Modifying the
netlist.set_component_value("U1:C2", 20e-12)  # modifying a
# define simulation
netlist.add_instructions("; Simulation settings", ";.param run = 0")
netlist.set_parameter("run", 0)

use_run_now = False

for opamp in ("AD712", "AD820"):
    netlist.set_element_model("U1", opamp)
    for supply_voltage in (5, 10, 15):
        netlist.set_component_value("V1", supply_voltage)
        netlist.set_component_value("V2", -supply_voltage)
        # overriding the automatic netlist naming
        run_netlist_file = f"{netlist.circuit_file.stem}_{opamp}_{supply_voltage}.net"
        if use_run_now:
            runner.run_now(netlist, run_filename=run_netlist_file)
        else:
            runner.run(netlist, run_filename=run_netlist_file, callback=processing_data)

for results in runner:
    print(results)

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
processing_data(raw, log)

if use_run_now is False:
    results = runner.wait_completion(1, abort_all_on_timeout=True)

    # Sim Statistics
    print(f"Successful/Total Simulations: {runner.okSim}/{runner.runno}")
