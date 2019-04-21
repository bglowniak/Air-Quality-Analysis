# Automated Air Quality Analysis and Data Visualization Tool

GT Junior Design Project for the ATSDR/CDC

Team Members:
Austin Bayon
Brian Glowniak
Zach Hussin
Joel Katz
Pramod Kotipalli
Thomas Napolitano

Clients:
Lt. Aaron Grober
Lt. Bradley Goodwin

## Release Notes - v1.0.0

### New Features
* Added the ability for a user to input a custom averaging duration.
* Implemented a PDF generator that compiles all results into a single report.
* Added the ability for a user to select a custom output folder. If a path is not selected, the app places the results in a folder called data_out in the same directory as where the data file was selected.
* Added new statistics (25/50/75% quartiles and number of times a sample passed PM thresholds).

### Bug Fixes
* Fixed a bug on the completion screen where clicking "View Results" after multiple runs of the tool would open files from all runs.
* When running the data processor, the app now properly transitions to the progress screen and the GUI does not freeze.
* Fixed an issue where errors created on the back end would not be properly displayed in the GUI.
* The app no longer crashes if the user inputs a start and end time outside of the range of the file selected.

### Known Bugs/Defects
* There is no way for the user to cancel an analysis once it has been initiated.
* If the app encounters an error while processing the data, the app does not delete any files created up to that point.
* Only one data file can be processed at a time.
* When selecting a file or output path, the user can only click the "Browse" button to open the dialog. Clicking the text field (i.e. "No File Selected") does nothing.

The app currently only accepts AirBeam, Purple Air, and AirEgg data sets based on what was provided from our client. This is in line with what was expected, but for future development, if these sensors modify how they present their data or our clients want to add functionality for different data sets, then the back end will need to be modified.

## Development/Installation Information

### Environment Setup

If you want to run the app, but do not have access to the installer/packaged application, or you want to continue to develop the app, you will first need to set up your development environment. Otherwise, you can run the app installer .exe which is located in this repository.

The only prerequisite is to have Python 3 installed on your machine. The app was developed in Python 3.6 and is platform independent. The instructions below outline how to set it up and install the other required libraries (the full list can be found in requirements.txt).

```shell
# 1. Clone the project codebase
# You can also download a ZIP file from the Github repository (https://github.com/bglowniak/Air-Quality-Analysis).

git clone https://github.com/bglowniak/Air-Quality-Analysis.git

# 2. Navigate into the folder and initialize a virtual environment.
# This will allow you to install the required libraries locally in the repo.

cd Air-Quality-Analysis
pip install virtualenv

# If you have more than one installation of Python, be sure to select Python 3.5+

virtualenv -p [path/to/python3] venv

# The path to Python 3 depends on your computer and where you installed Python.
# If you are using Bash, you can find it by using $(which python3) in Bash. If this doesn't work, see Troubleshooting below.

# 3. Activate your virtual environment

# On Mac/Linux:
source venv/bin/activate

# On Windows:
call venv/Scripts/activate.bat

# 4. Locally install required libraries
pip install -r requirements.txt

# 5. Build and run the app (virtual environment must be running)
fbs run
```

### Libraries Used
  * [PyQt5](https://pypi.org/project/PyQt5) - PyQt5 is a set of Python bindings for Qt, which is a widely used set of cross platform C++ libraries for developing desktop GUIs.
  * [fbs](https://github.com/mherrmann/fbs) - fman build system is a library created by Michael Herrmann that is used to easily package PyQt5 apps for cross-platform distribution.
  * [pandas](https://pandas.pydata.org/) - pandas is a data analysis toolkit for Python
  * [numpy](https://www.numpy.org/) - numpy is a scientific computing toolkit for Python that provides a powerful array manipulation functions
  * [matplotlib](https://matplotlib.org/) - matplotlib provides core plotting support for Python.
  * [fpdf](https://pyfpdf.readthedocs.io/en/latest/) - fpdf is a PDF document generation libary that we use to compile our results into a report

To install a new package:
```shell
# 1. Install the package in your virtual environment
pip install package-name
EX) pip install python-dateutil

# 2. Add it to the requirements.txt
pip freeze > requirements.txt
```

### To package the application into an installer

To package the code into a standalone executable, run

```shell
fbs freeze
```

This will create a subfolder titled `target/` that contains the .exe of the application (titled AppName.exe). Then, to create a distributable installer for the application, run

```shell
fbs installer
```

Before you can use the installer command on Windows, you need to install [NSIS](http://nsis.sourceforge.net/Main_Page) and add its installation directory to your PATH environment variable. The resultant installer will be located in the `target/` directory as AppNameSetup.exe.

To remove the `target/` directory and all packaged code, run:

```shell
fbs clean
```

### Troubleshooting
* If you have multiple versions of Python and/or pip installed on your machine, you will need to ensure that you are using Python 3. To check which version you are using, you can run "python -V" and "pip -V" in the command line. If you have a different version installed, will need to download [Python 3](https://www.python.org/downloads/) and then change your PATH variable so the python command runs the correct version.
* When running the command in step 2 of the setup, you may have to manually get the path to Python. An example path (on Windows) is C:/Python36/python.exe
* For creating the installer, if you are on Windows and receive an error stating that you are missing DLLs (specifically, api-ms-win-crt-multibyte-l1-1-0.dll), follow the instructions located [here](https://answers.microsoft.com/en-us/windows/forum/windows_10-other_settings/problem-with-universal-runtime-on-windows-10-pro/9fda2f7d-5cf8-4906-a542-77147e557d5d?auth=1). You can also refer to an fbs issue [here](https://github.com/mherrmann/fbs-tutorial/issues/4). The outlined fix is to install the [Windows 10 SDK](https://dev.windows.com/en-us/downloads/windows-10-sdk) and then add `C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x86` to your PATH environment variable (or x64 if you have a 64 bit Python interpreter).
