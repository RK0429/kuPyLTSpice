# README #

kuPyLTSpice is a toolchain of python utilities designed to interact with LTSpice Electronic Simulator.
It is a fork of PyLTSpice with modifications to better support specific use cases.
The main difference from the original PyLTSpice is that LTSpice is automatically selected to perform all simulations.

## What is contained in this repository ##

* __LTSteps.py__
  An utility that extracts from LTSpice output files data, and formats it for import in a spreadsheet, such like Excel
  or Calc.

* __raw_read.py__
  A pure python class that serves to read raw files into a python class.

* __raw_write.py__
  A class to write RAW files that can be read by LTSpice Wave Application.

* __spice_editor.py and asc_editor.py__
  Scripts that can update spice netlists. The following methods are available to manipulate the component values,
  parameters as well as the simulation commands. These methods allow to update a netlist without having to open the
  schematic in LTSpice. The simulations can then be run in batch mode (see sim_runner.py).

  * `set_element_model('D1', '1N4148') # Replaces the Diode D1 with the model 1N4148`
  * `set_component_value('R2', '33k') # Replaces the value of R2 by 33k`
  * `set_parameters(run=1, TEMP=80) # Creates or updates the netlist to have .PARAM run=1 or .PARAM TEMP=80`
  * `add_instructions(".STEP run -1 1023 1", ".dc V1 -5 5")`
  * `remove_instruction(".STEP run -1 1023 1")  # Removes previously added instruction`
  * `reset_netlist() # Resets all edits done to the netlist.`

* __sim_runner.py__
  A python script that can be used to run LTSpice simulations in batch mode without having to open the LTSpice GUI.
  This in cooperation with the classes defined in spice_editor.py or asc_editor.py is useful because:

  * Can overcome the limitation of only stepping 3 parameters
  * Different types of simulations .TRAN .AC .NOISE can be run in a single batch
  * The RAW Files are smaller and easier to treat
  * When used with the RawRead.py and LTSteps.py, validation of the circuit can be done automatically.
  * Different models can be simulated in a single batch, by using the following instructions:

  Note: It supports both Windows and Mac OS. For Mac, LTspice is expected to be installed in the standard location (/Applications/LTspice.app).

* __Analysis Toolkit__
  A set of tools that prepare an LTSpice netlist for a Montecarlo or Worst Case Analysis. The device tolerances are set
  by the user and the netlist is updated accordingly. The netlist can then be used with the sim_runner.py to run a
  batch of simulations or with the LTSpice GUI.

* __Histogram.py__
  A python script that uses numpy and matplotlib to create a histogram and calculate the sigma deviations. This is
  useful for Monte-Carlo analysis.

## How to Install ##

`pip install kuPyLTSpice`

### Updating kuPyLTSpice ###

`pip install --upgrade kuPyLTSpice`

### Using GitHub ###

`git clone https://github.com/RK0429/kuPyLTSpice.git`

If using this method it would be good to add the path where you cloned the site to python path.

`import sys`  
`sys.path.append(<path to kuPyLTSpice>)`

## How to use ##

Here follows a quick outlook on how to use each of the tools.

More comprehensive documentation can be found in the docstrings and examples.

## LICENSE ##

GNU V3 License
(refer to the LICENSE file)

### RawRead ###

The example below reads the data from a Spice Simulation called
"TRAN - STEP.raw" and displays all steps of the "I(R1)" trace in a matplotlib plot

```python
from kuPyLTSpice import RawRead

from matplotlib import pyplot as plt

LTR = RawRead("./testfiles/TRAN - STEP.raw")

print(LTR.get_trace_names())
print(LTR.get_raw_property())

IR1 = LTR.get_trace("I(R1)")
x = LTR.get_trace('time')  # Gets the time axis
steps = LTR.get_steps()
for step in range(len(steps)):
    # print(steps[step])
    plt.plot(x.get_wave(step), IR1.get_wave(step), label=steps[step])

plt.legend()  # order a legend
plt.show()
```

-- in examples/raw_read_example.py

### RawWrite ###

The following example writes a RAW file with a 3 milliseconds transient simulation sine with a 10kHz and a cosine with
9.997kHz

```python
import numpy as np
from kuPyLTSpice import RawRead, Trace, RawWrite
LW = RawWrite(fastacces=False)
tx = Trace('time', np.arange(0.0, 3e-3, 997E-11))
vy = Trace('N001', np.sin(2 * np.pi * tx.data * 10000))
vz = Trace('N002', np.cos(2 * np.pi * tx.data * 9970))
LW.add_trace(tx)
LW.add_trace(vy)
LW.add_trace(vz)
LW.save("./testfiles/teste_snippet1.raw")
```

-- in examples/raw_write_example.py [RawWrite Example]

### SpiceEditor, AscEditor and SimRunner.py ###

This module is used to launch LTSPice simulations. Results then can be processed with either the RawRead or with the
LTSteps module to read the log file which can contain .MEAS results.

The script will firstly invoke the LTSpice in command line to generate a netlist, and then this netlist can be updated
directly by the script, in order to change component values, parameters or simulation commands.

Here follows an example of operation.

```python
from kuPyLTSpice import SimRunner
from kuPyLTSpice import SpiceEditor

# Force another simulator
# Windows path
# simulator = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
# On Mac, use:
# simulator = "/Applications/LTspice.app/Contents/MacOS/LTspice"
# Or let kuPyLTSpice auto-detect the path based on your OS

# select spice model
LTC = SimRunner(output_folder='./temp')
LTC.create_netlist('./testfiles/Batch_Test.asc')
netlist = SpiceEditor('./testfiles/Batch_Test.net')
# set default arguments
netlist.set_parameters(res=0, cap=100e-6)
netlist.set_component_value('R2', '2k')  # Modifying the value of a resistor
netlist.set_component_value('R1', '4k')
netlist.set_element_model('V3', "SINE(0 1 3k 0 0 0)")  # Modifying the
netlist.set_component_value('XU1:C2', 20e-12)  # modifying a define simulation
netlist.add_instructions(
    "; Simulation settings",
    ";.param run = 0"
)
netlist.set_parameter('run', 0)

for opamp in ('AD712', 'AD820'):
    netlist.set_element_model('XU1', opamp)
    for supply_voltage in (5, 10, 15):
        netlist.set_component_value('V1', supply_voltage)
        netlist.set_component_value('V2', -supply_voltage)
        print("simulating OpAmp", opamp, "Voltage", supply_voltage)
        LTC.run(netlist)

for raw, log in LTC:
    print("Raw file: %s, Log file: %s" % (raw, log))
    # do something with the data
    # raw_data = RawRead(raw)
    # log_data = LTSteps(log)
    # ...

netlist.reset_netlist()
netlist.add_instructions(
    "; Simulation settings",
    ".ac dec 30 10 1Meg",
    ".meas AC Gain MAX mag(V(out)) ; find the peak response and call it ""Gain""",
    ".meas AC Fcut TRIG mag(V(out))=Gain/sqrt(2) FALL=last"
)

# Sim Statistics
print('Successful/Total Simulations: ' + str(LTC.okSim) + '/' + str(LTC.runno))

enter = input("Press enter to delete created files")
if enter == '':
    LTC.file_cleanup()
```

-- in examples/sim_runner_example.py

The example above is using the SpiceEditor to create and modify a spice netlist, but it is also possible to use the
AscEditor to directly modify the .asc file. The edited .asc file can then be opened by the LTSpice GUI and the
simulation can be run from there.

### Simulation Analysis Toolkit ###

The AscEditor can be used with the Simulation Analysis Toolkit to perform Monte Carlo or Wost Case simulations.
These simulations can either be done on the LTSpice GUI or using the Runner Class described above.

Let's consider the following circuit:

![Sallen-Key Amplifier](./doc/modules/sallenkey.png "Sallen-Key Amplifier")

When performing a Monte Carlo simulation on this circuit, we need to manually modify the value of each component,
and then add the .step command for making several runs on the same circuit.
To simplify this process, the AscEditor class can be used as exemplified below:

```python
from kuPyLTSpice import AscEditor, SimRunner  # Imports the class that manipulates the asc file
from kuPyLTSpice.sim.tookit.montecarlo import Montecarlo  # Imports the Montecarlo toolkit class

sallenkey = AscEditor("./testfiles/sallenkey.asc")  # Reads the asc file into memory
runner = SimRunner(output_folder='./temp_mc')  # Instantiates the runner class, with the output folder already set
mc = Montecarlo(sallenkey, runner)  # Instantiates the Montecarlo class, with the asc file already in memory

# The following lines set the default tolerances for the components
mc.set_tolerance('R', 0.01)  # 1% tolerance, default distribution is uniform
mc.set_tolerance('C', 0.1, distribution='uniform')  # 10% tolerance, explicit uniform distribution
mc.set_tolerance('V', 0.1, distribution='normal')  # 10% tolerance, but using a normal distribution

# Some components can have a different tolerance
mc.set_tolerance('R1', 0.05)  # 5% tolerance for R1 only. This only overrides the default tolerance for R1

# Tolerances can be set for parameters as well
mc.set_parameter_deviation('Vos', 3e-4, 5e-3, 'uniform')  # The keyword 'distribution' is optional
mc.prepare_testbench(num_runs=1000)  # Prepares the testbench for 1000 simulations

# Finally the netlist is saved to a file
mc.save_netlist('./testfiles/sallenkey_mc.net')

mc.run_testbench(runs_per_sim=100)  # Runs the simulation with splits of 100 runs each
logs = mc.read_logfiles()   # Reads the log files and stores the results in the results attribute
logs.obtain_amplitude_and_phase_from_complex_values()  # Splits the complex values into real and imaginary parts
logs.export_data('./temp_mc/data_testbench.csv')  # Exports the data to a csv file
logs.plot_histogram('fcut')  # Plots the histograms for the results
mc.cleanup_files()  # Deletes the temporary files

print("=====================================")
# Now using the second method, where the simulations are ran one by one
mc.clear_simulation_data()  # Clears the simulation data
mc.reset_netlist()  # Resets the netlist to the original
mc.run_analysis(num_runs=1000)  # Runs the 1000 simulations
logs = mc.read_logfiles()   # Reads the log files and stores the results in the results attribute
logs.export_data('./temp_mc/data_sims.csv')  # Exports the data to a csv file
logs.plot_histogram('fcut')  # Plots the histograms for the results
mc.cleanup_files()  # Deletes the temporary files
```

-- in examples/run_montecarlo.py

When opening the created sallenkey_mc.net file, we can see that the following circuit.

![Sallen-Key Amplifier with Montecarlo](./doc/modules/sallenkey_mc.png "Sallen-Key Amplifier with Montecarlo")

The following updates were made to the circuit:

* The value of each component was replaced by a function that generates a random value within the specified tolerance.
* The .step param run command was added to the netlist. Starts at -1 which it's the nominal value simulation, and
finishes that the number of simulations specified in the prepare_testbench() method.
* A default value for the run parameter was added. This is useful if the .step param run is commented out.
* The R1 tolerance is different from the other resistors. This is because the tolerance was explicitly set for R1.
* The Vos parameter was added to the .param list. This is because the parameter was explicitly set using the
set_parameter_deviation method.
* Functions utol, ntol and urng were added to the .func list. These functions are used to generate random values.
Uniform distributions use the LTSpice built-in mc(x, tol) and flat(x) functions, while normal distributions use the
gauss(x) function.

Similarly, the worst case analysis can also be setup by using the class WorstCaseAnalysis, as exemplified below:

```python
from kuPyLTSpice import AscEditor, SimRunner  # Imports the class that manipulates the asc file
from kuPyLTSpice.sim.tookit.worst_case import WorstCaseAnalysis

sallenkey = AscEditor("./testfiles/sallenkey.asc")  # Reads the asc file into memory
runner = SimRunner(output_folder='./temp_wca')  # Instantiates the runner class, with the output folder already set
wca = WorstCaseAnalysis(sallenkey, runner)  # Instantiates the Worst Case Analysis class

# The following lines set the default tolerances for the components
wca.set_tolerance('R', 0.01)  # 1% tolerance
wca.set_tolerance('C', 0.1)  # 10% tolerance
wca.set_tolerance('V', 0.1)  # 10% tolerance. For Worst Case analysis, the distribution is irrelevant

# Some components can have a different tolerance
wca.set_tolerance('R1', 0.05)  # 5% tolerance for R1 only. This only overrides the default tolerance for R1

# Tolerances can be set for parameters as well.
wca.set_parameter_deviation('Vos', 3e-4, 5e-3)

# Finally the netlist is saved to a file
wca.save_netlist('./testfiles/sallenkey_wc.asc')

wca.run_testbench()  # Runs the simulation with splits of 100 runs each

logs = wca.read_logfiles()   # Reads the log files and stores the results in the results attribute
logs.export_data('./temp_wca/data.csv')  # Exports the data to a csv file

print("Worst case results:")
for param in ('fcut', 'fcut_FROM'):
    print(f"{param}: min:{logs.min_measure_value(param)} max:{logs.max_measure_value(param)}")

wca.cleanup_files()  # Deletes the temporary files
```

-- in examples/run_worst_case.py

When opening the created sallenkey_wc.net file, we can see that the following circuit.

![Sallen-Key Amplifier with WCA](./doc/modules/sallenkey_wc.png "Sallen-Key Amplifier with WCA")

The following updates were made to the circuit:

* The value of each component was replaced by a function that generates a nominal, minimum and maximum value depending
on the run parameter and is assigned a unique index number. (R1=0, Vos=1, R2=2, ... V2=7, VIN=8)
The unique number corresponds to the bit position of the run parameter. Bit 0 corresponds to the minimum value and
bit 1 corresponds to the maximum value. Calculating all possible permutations of maximum and minimum values for each
component, we get 2**9 = 512 possible combinations. This maps into a 9 bit binary number, which is the run parameter.
* The .step param run command was added to the netlist. It starts at -1 which it's the nominal value simulation, then 0
which corresponds to the minimum value for each component, then it makes all combinations of minimum and maximum values
until 511, which is the simulation with all maximum values.
* A default value for the run parameter was added. This is useful if the .step param run is commented out.
* The R1 tolerance is different from the other resistors. This is because the tolerance was explicitly set for R1.
* The wc() function is added to the circuit. This function is used to calculate the worst case value for each component,
given a tolerance value and its respective index.
* The wc1() function is added to the circuit. This function is used to calculate the worst case value for each component,
given a minimum and maximum value and its respective index.

### LTSteps.py ###

This module defines a class that can be used to parse LTSpice log files where the information about .STEP information is
written. There are two possible usages of this module, either programmatically by importing the module and then
accessing data through the class as exemplified here:

```python
#!/usr/bin/env python
# coding=utf-8

from kuPyLTSpice import LTSpiceLogReader

data = LTSpiceLogReader("./testfiles/Batch_Test_AD820_15.log")

print("Number of steps  :", data.step_count)
step_names = data.get_step_vars()
meas_names = data.get_measure_names()

# Printing Headers
print(' '.join([f"{step:15s}" for step in step_names]), end='')  # Print steps names with no new line
print(' '.join([f"{name:15s}" for name in meas_names]), end='\n')
# Printing data
for i in range(data.step_count):
    print(' '.join([f"{data[step][i]:15}" for step in step_names]), end='')  # Print steps names with no new line
    print(' '.join([f"{data[name][i]:15}" for name in meas_names]), end='\n')  # Print Header

print("Total number of measures found :", data.measure_count)
```

-- in examples/ltsteps_example.py

The second possibility is to use the module directly on the command line

## Command Line Interface ##

### ltsteps.exe ###

The `<filename>` can be either be a log file (.log), a data export file (.txt) or a measurement output file (.meas)
This will process all the data and export it automatically into a text file with the extension (tlog, tsv, tmeas)
where the data read is formatted into a more convenient tab separated format. In case the `<logfile>` is not provided, the
script will scan the directory and process the newest log, txt or out file found.

### histogram.exe ###

This module uses the data inside on the filename to produce a histogram image.

```text
Usage: Histogram.py [options] LOG_FILE TRACE

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SIGMA, --sigma=SIGMA
                        Sigma to be used in the distribution fit. Default=3
  -n NBINS, --nbins=NBINS
                        Number of bins to be used in the histogram. Default=20
  -c FILTERS, --condition=FILTERS
                        Filter condition writen in python. More than one
                        expression can be added but each expression should be
                        preceded by -c. EXAMPLE: -c V(N001)>4 -c parameter==1
                        -c  I(V1)<0.5
  -f FORMAT, --format=FORMAT
                        Format string for the X axis. Example: -f %3.4f
  -t TITLE, --title=TITLE
                        Title to appear on the top of the histogram.
  -r RANGE, --range=RANGE
                        Range of the X axis to use for the histogram in the
                        form min:max. Example: -r -1:1
  -C, --clipboard       If the data from the clipboard is to be used.
  -i IMAGEFILE, --image=IMAGEFILE
                        Name of the image File. extension 'png'    
```

### rawconvert.exe ###

A tool to convert .raw files into csv or Excel files.

```text
Usage: raw_convert.exe [options] <rawfile> <trace_list>

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -o FILE, --output=FILE
                        Output file name. Use .csv for CSV output, .xlsx for
                        Excel output
  -c, --clipboard       Output to clipboard
  -v, --verbose         Verbose output
  -s SEPARATOR, --sep=SEPARATOR
                        Value separator for CSV output. Default: "\t" <TAB>
                        Example: -d ";"
```

## Debug Logging ##

The library uses the standard `logging` module. Three convenience functions have been added for easily changing logging
settings across the entire library. `kuPyLTSpice.all_loggers()` returns a list of all the logger's
names, `kuPyLTSpice.set_log_level(logging.DEBUG)`
would set the library's logging level to debug, and `kuPyLTSpice.add_log_handler(my_handler)` would add `my_handler` as a
handler for all loggers.

### Single Module Logging ###

It is also possible to set the logging settings for a single module by using its name acquired from
the `kuPyLTSpice.all_loggers()`
function. For example:

```python
import logging

logging.basicConfig(level=logging.INFO)  # Set up the root logger first

import kuPyLTSpice  # Import kuPyLTSpice to set the logging levels

kuPyLTSpice.set_log_level(logging.DEBUG)  # Set kuPyLTSpice's global log level
logging.getLogger("kupicelib.RawRead").level = logging.WARNING  # Set the log level for only RawRead to warning
```

Would set only `kupicelib.RawRead` file's logging level to warning while the other modules would remain at debug level.
_Make sure to initialize the root logger before importing the library to be able to see the logs._

## To whom do I talk to? ##

For support and improvement requests please open an Issue in [GitHub kuPyLTSpice issues](https://github.com/RK0429/kuPyLTSpice/issues)

## History ##

* Version 1.0.0
  * Fork of PyLTSpice 5.4.2 with modifications to better support specific use cases
  * Changes to logging and configuration
  * Updated dependencies to use kupicelib

* For previous version history, see the original PyLTSpice repository at https://github.com/nunobrum/PyLTSpice
