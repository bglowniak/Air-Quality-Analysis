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
Aaron Grober
Bradley Goodwin

## Development Information

### Libraries Used
    * [PyQt5](https://pypi.org/project/PyQt5/) - PyQt5 is a set of Python bindings for Qt, which is a widely used set of cross platform C++ libraries for developing desktop GUIs.
    * [fbs](https://github.com/mherrmann/fbs) - fman build system is a library created by Michael Herrmann that is used to easily package PyQt5 apps for cross-platform distribution.

### Environment Setup

```shell
# 1. Clone the project
git clone https://github.com/bglowniak/Air-Quality-Analysis.git
cd Air-Quality-Analysis

# 2. Initialization of virtualenv
pip install virtualenv

# If you have one than one installation of Python, be sure to select Python 3.5+
virtualenv -p path/to/python3 venv
# You can find the path/to/python3 using $(which python3) in Bash

# 3. On Mac/Linux:
source venv/bin/activate

# 3. On Windows:
call venv\Scripts\activate.bat

# 4. Local installation project-specific requirements
pip install -r requirements.txt

# 5. Run the app (virtual environment must be running)
fbs run
```

To install a new package:
```shell
# 1. Install the package in your virtual environment
pip install package-name
EX) pip install python-dateutil

# 2. Add it to the requirements.txt
pip freeze > requirements.txt
```

### To package the application

To package the code into a standalone executable, run

```shell
fbs freeze
```

This will create a subfolder titled `target/` that contains the .exe of the application (titled AppName.exe). If you receive an error stating that you are missing DLLs (specifically, api-ms-win-crt-multibyte-l1-1-0.dll), follow the instructions located [here](https://answers.microsoft.com/en-us/windows/forum/windows_10-other_settings/problem-with-universal-runtime-on-windows-10-pro/9fda2f7d-5cf8-4906-a542-77147e557d5d?auth=1). You can also refer to an fbs issue [here](https://github.com/mherrmann/fbs-tutorial/issues/4). The outlined fix is to install the [Windows 10 SDK](https://dev.windows.com/en-us/downloads/windows-10-sdk) and then add `C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x86` to your PATH environment variable (or x64 if you have a 64 bit Python interpreter).

Then, to create a distributable installer for the application, run

```shell
fbs installer
```
Before you can use the installer command on Windows, you need to install [NSIS](http://nsis.sourceforge.net/Main_Page) and add its installation directory to your PATH environment variable. The resultant installer will be located in the `target/` directory as AppNameSetup.exe.

To remove the `target/` directory and all packaged code, run:

```shell
fbs clean
```
