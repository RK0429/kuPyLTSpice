# pyright: reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false
from __future__ import annotations

from pathlib import Path
from typing import TypeGuard

from kupicelib.sim.sim_runner import RunResult

from kuPyLTSpice import SimRunner, SpiceEditor

# Force another simulator; uncomment for your OS or rely on auto-detection.
# Windows path
# simulator = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
# Mac OS path
# simulator = r"/Applications/LTspice.app/Contents/MacOS/LTspice"

# select spice model
LTC = SimRunner(output_folder="./temp")
LTC.create_netlist("./testfiles/Batch_Test.asc")
netlist = SpiceEditor("./testfiles/Batch_Test.net")
# set default arguments
netlist.set_parameters(res=0, cap=100e-6)
netlist.set_component_value("R2", "2k")  # Modifying the value of a resistor
netlist.set_component_value("R1", "4k")
netlist.set_element_model("V3", "SINE(0 1 3k 0 0 0)")  # Modifying the
netlist.set_component_value("XU1:C2", 20e-12)  # modifying a define simulation
netlist.add_instructions("; Simulation settings", ";.param run = 0")
netlist.set_parameter("run", 0)

for opamp in ("AD712", "AD820"):
    netlist.set_element_model("XU1", opamp)
    for supply_voltage in (5, 10, 15):
        netlist.set_component_value("V1", supply_voltage)
        netlist.set_component_value("V2", -supply_voltage)
        print(f"simulating OpAmp {opamp} Voltage {supply_voltage}")
        LTC.run(netlist)

def is_result_pair(value: RunResult) -> TypeGuard[tuple[Path | None, Path | None]]:
    return isinstance(value, tuple) and len(value) == 2


for result in LTC:
    if not is_result_pair(result):
        continue
    raw, log = result
    print(f"Raw file: {raw}, Log file: {log}")
    # do something with the data
    # raw_data = RawRead(raw)
    # log_data = LTSteps(log)
    # ...

netlist.reset_netlist()
netlist.add_instructions(
    "; Simulation settings",
    ".ac dec 30 10 1Meg",
    ".meas AC Gain MAX mag(V(out)) ; find the peak response and call it " "Gain" "",
    ".meas AC Fcut TRIG mag(V(out))=Gain/sqrt(2) FALL=last",
)

# Sim Statistics
print(f"Successful/Total Simulations: {LTC.okSim}/{LTC.runno}")

enter = input("Press enter to delete created files")
if enter == "":
    LTC.file_cleanup()
