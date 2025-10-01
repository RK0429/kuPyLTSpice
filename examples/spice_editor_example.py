# pyright: reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingParameterType=false

from kuPyLTSpice import SpiceEditor

se = SpiceEditor("./testfiles/Noise.asc")

se.set_component_value("R1", 11000)
se.set_component_value("C1", 1.1e-6)
se.set_component_value("V1", 11)

se.save_netlist("./testfiles/Noise_updated.net")
se.run()
