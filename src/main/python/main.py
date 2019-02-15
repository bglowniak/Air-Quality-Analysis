from fbs_runtime.application_context import ApplicationContext
from functools import partial
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFileDialog, QComboBox, QRadioButton, QDateTimeEdit

from PyQt5.QtCore import QDateTime

import sys

class AppContext(ApplicationContext):
    def run(self):
        version = self.build_settings['version']
        main_screen = MainWindow(version)
        main_screen.show()
        return self.app.exec_()

class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        central_widget = QWidget()
        #central_widget.setFixedWidth(400)

        # set up layouts and widgets
        self.master_layout = QVBoxLayout()
        self.file_select_layout = self.file_select_layout()
        self.averaging_duration_layout = self.averaging_duration_layout()
        self.time_range_layout = self.time_range_layout()
        self.time_selectors = self.time_selectors()

        # apply layouts and show window
        self.master_layout.addLayout(self.file_select_layout)
        self.master_layout.addLayout(self.averaging_duration_layout)
        self.master_layout.addLayout(self.time_range_layout)
        self.master_layout.addWidget(self.time_selectors)

        process_file = QPushButton("Process File")
        process_file.clicked.connect(self.begin_process)
        self.master_layout.addWidget(process_file)

        central_widget.setLayout(self.master_layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("CDC/ATSDR Air Quality Analysis v" + version)
        self.setFixedSize(500, 250)

    def file_select_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Select Data File:"))

        file_name = QLabel("No File Selected")
        button = QPushButton("Browse")
        button.clicked.connect(partial(self.get_file, file_name))

        layout.addWidget(file_name)
        layout.addWidget(button)

        return layout

    def averaging_duration_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Select Averaging Duration:"))

        comboBox = QComboBox(self)
        comboBox.addItem("1 Minute")
        comboBox.addItem("5 Minutes")
        comboBox.addItem("1 Hour")
        comboBox.addItem("24 Hours")
        comboBox.addItem("3 Months")
        comboBox.addItem("6 Months")
        comboBox.addItem("1 Year")

        layout.addWidget(comboBox)

        return layout

    def time_range_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Use Time Range?"))

        yes_rb = QRadioButton("Yes")
        no_rb = QRadioButton("No")
        no_rb.setChecked(True)

        yes_rb.toggled.connect(partial(self.rb_state, yes_rb))
        no_rb.toggled.connect(partial(self.rb_state, no_rb))

        layout.addWidget(yes_rb)
        layout.addWidget(no_rb)

        return layout

    def time_selectors(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Start Time: "))

        start = QDateTimeEdit(self)
        start.setCalendarPopup(True)
        start.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(start)

        layout.addWidget(QLabel("End Time: "))

        end = QDateTimeEdit(self)
        end.setCalendarPopup(True)
        end.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(end)

        widget.setLayout(layout)

        widget.setFixedHeight(50)
        widget.hide()
        return widget

    def get_file(self, label):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Data Files", "", "All Files (*)")
        if fileName:
            label.setText(fileName.split("/")[-1])

    def rb_state(self, clicked):
        if clicked.text() == "Yes" and clicked.isChecked() == True:
            self.time_selectors.show()
        elif clicked.text() == "No" and clicked.isChecked() == True:
            self.time_selectors.hide()

    def begin_process(self):
        print("Beginning File Process With:")

if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)