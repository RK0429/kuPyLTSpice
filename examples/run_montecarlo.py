from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kupicelib.editor.asc_editor import AscEditor as AscEditorType
    from kupicelib.sim.sim_runner import SimRunner as SimRunnerType
    from kupicelib.sim.tookit.montecarlo import Montecarlo as MontecarloType
else:  # pragma: no cover
    from kuPyLTSpice import AscEditor as AscEditorType
    from kuPyLTSpice import SimRunner as SimRunnerType
    from kuPyLTSpice.sim.tookit.montecarlo import Montecarlo as MontecarloType

AscEditor = AscEditorType
SimRunner = SimRunnerType
Montecarlo = MontecarloType


def main() -> None:
    sallenkey = AscEditor("./testfiles/sallenkey.asc")
    runner = SimRunner(output_folder="./temp_mc")
    mc = Montecarlo(sallenkey, runner)

    mc.set_tolerance("R", 0.01)
    mc.set_tolerance("C", 0.1, distribution="uniform")
    mc.set_tolerance("V", 0.1, distribution="normal")
    mc.set_tolerance("R1", 0.05)
    mc.set_parameter_deviation("Vos", 3e-4, 5e-3, "uniform")
    mc.prepare_testbench(num_runs=1000)

    mc.save_netlist("./testfiles/sallenkey_mc.net")

    mc.run_testbench(runs_per_sim=100)
    logs = mc.read_logfiles()
    logs.obtain_amplitude_and_phase_from_complex_values()
    logs.export_data("./temp_mc/data_testbench.csv")
    logs.plot_histogram("fcut")
    mc.cleanup_files()

    print("=====================================")
    mc.clear_simulation_data()
    mc.reset_netlist()
    mc.run_analysis(num_runs=1000)
    logs = mc.read_logfiles()
    logs.export_data("./temp_mc/data_sims.csv")
    logs.plot_histogram("fcut")
    mc.cleanup_files()


if __name__ == "__main__":  # pragma: no cover
    main()
