from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kupicelib.editor.asc_editor import AscEditor as AscEditorType
    from kupicelib.sim.sim_runner import SimRunner as SimRunnerType
    from kupicelib.sim.tookit.worst_case import WorstCaseAnalysis as WorstCaseAnalysisType
else:  # pragma: no cover
    from kuPyLTSpice import AscEditor as AscEditorType
    from kuPyLTSpice import SimRunner as SimRunnerType
    from kuPyLTSpice.sim.tookit.worst_case import WorstCaseAnalysis as WorstCaseAnalysisType

AscEditor = AscEditorType
SimRunner = SimRunnerType
WorstCaseAnalysis = WorstCaseAnalysisType


def main() -> None:
    sallenkey = AscEditor("./testfiles/sallenkey.asc")
    runner = SimRunner(output_folder="./temp_wca")
    wca = WorstCaseAnalysis(sallenkey, runner)

    wca.set_tolerance("R", 0.01)
    wca.set_tolerance("C", 0.1)
    wca.set_tolerance("V", 0.1)
    wca.set_tolerance("R1", 0.05)
    wca.set_parameter_deviation("Vos", 3e-4, 5e-3)

    wca.save_netlist("./testfiles/sallenkey_wc.asc")

    wca.run_testbench()
    logs = wca.read_logfiles()
    logs.export_data("./temp_wca/data.csv")

    print("Worst case results:")
    for param in ("fcut", "fcut_FROM"):
        print(
            f"{param}: min:{logs.min_measure_value(param)} max:{logs.max_measure_value(param)}"
        )

    wca.cleanup_files()


if __name__ == "__main__":  # pragma: no cover
    main()
