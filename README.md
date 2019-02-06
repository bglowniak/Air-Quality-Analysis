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

## Developers

### Environment Setup

```shell

# 1. Clone the project
git clone https://github.com/bglowniak/Air-Quality-Analysis.git
cd Air-Quality-Analysis
  
# 2. Global installation/initialization of virtualenv
pip install virtualenv
  
# If you have one than one installation of Python, be sure to select Python 3.5+
virtualenv -p path/to/python3 venv
# You can find the path/to/python3 using $(which python3) in Bash
  
# 3. On Mac/Linux:
source venv/bin/activate
  
# 3. On Windows:
venv/Scripts/activate.bat
  
# 4. Local installation project-specific requirements
pip install -r requirements.txt
  
# 5. Run the app
python app.py
```

### QtDesigner developer tools

Download from https://build-system.fman.io/qt-designer-download
