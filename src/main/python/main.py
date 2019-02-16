from fbs_runtime.application_context import ApplicationContext
from functools import partial
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFileDialog, QComboBox, QRadioButton, QDateTimeEdit, QStackedWidget, QProgressBar, QMessageBox

from PyQt5.QtCore import QDateTime

import threading
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
        self.main_widget = MainWidget()
        self.progress_widget = ProgressWidget()
        self.complete_widget = CompleteWidget()

        self.master = QStackedWidget()
        self.master.addWidget(self.main_widget)
        self.master.addWidget(self.progress_widget)
        self.master.addWidget(self.complete_widget)

        self.setCentralWidget(self.master)
        self.setWindowTitle("CDC/ATSDR Air Quality Analysis v" + version)
        self.setFixedSize(500, 250)

    def start_analysis(self, filename, averaging_duration, time_selected, start_time, end_time):
        self.master.setCurrentIndex(1)
        self.progress_widget.begin_progress(filename, averaging_duration, start_time, end_time)

    def complete_analysis(self):
        self.master.setCurrentIndex(2)

    def start_over(self):
        self.master.widget(0).reset()
        self.master.setCurrentIndex(0)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.title_label = QLabel("CDC Air Quality Analysis")
        self.layout.addWidget(self.title_label)
        self.file_select_layout = self.file_select_layout()
        self.averaging_duration_layout = self.averaging_duration_layout()
        self.time_range_layout = self.time_range_layout()
        self.time_selectors = self.time_selectors()

        self.layout.addLayout(self.file_select_layout)
        self.layout.addLayout(self.averaging_duration_layout)
        self.layout.addLayout(self.time_range_layout)
        self.layout.addWidget(self.time_selectors)

        process_file = QPushButton("Process File")
        process_file.clicked.connect(self.begin_process)
        self.layout.addWidget(process_file)

        self.setLayout(self.layout)

    def file_select_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Select Data File:"))

        self.file_name = QLabel("No File Selected")
        button = QPushButton("Browse")
        button.clicked.connect(partial(self.get_file, self.file_name))

        layout.addWidget(self.file_name)
        layout.addWidget(button)

        self.file = None

        return layout

    def averaging_duration_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Select Averaging Duration:"))

        comboBox = QComboBox(self)
        self.averaging_duration = "1 Minute" # default
        comboBox.addItem("1 Minute")
        comboBox.addItem("5 Minutes")
        comboBox.addItem("1 Hour")
        comboBox.addItem("24 Hours")
        comboBox.addItem("3 Months")
        comboBox.addItem("6 Months")
        comboBox.addItem("1 Year")

        comboBox.currentIndexChanged.connect(partial(self.selection_change, comboBox))

        layout.addWidget(comboBox)

        return layout

    def selection_change(self, cb):
        self.averaging_duration = cb.currentText()

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

        self.time_selected = False

        return layout

    def time_selectors(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Start Time: "))

        self.start = QDateTimeEdit(self)
        self.start.setCalendarPopup(True)
        self.start.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.start)

        layout.addWidget(QLabel("End Time: "))

        self.end = QDateTimeEdit(self)
        self.end.setCalendarPopup(True)
        self.end.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.end)

        widget.setLayout(layout)

        widget.setFixedHeight(50)
        widget.setEnabled(False)
        return widget

    def get_file(self, label):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Data Files", "", "All Files (*)")
        if fileName:
            self.file = fileName.split("/")[-1]
            label.setText(self.file)

    def rb_state(self, clicked):
        if clicked.text() == "Yes" and clicked.isChecked() == True:
            self.time_selectors.setEnabled(True)
            self.time_selected = True
        elif clicked.text() == "No" and clicked.isChecked() == True:
            self.time_selectors.setEnabled(False)
            self.time_selected = False

    def begin_process(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowTitle("Input Error")
        if not self.file:
            msg.setText("No File Selected")
            msg.setInformativeText("Please Select a Valid File")
            msg.exec_()
            return

        if self.time_selected:
            start_time = self.start.dateTime()
            end_time = self.end.dateTime()
            if start_time > end_time:
                msg.setText("Invalid Time Entered")
                msg.setInformativeText("End Time cannot be greater than Start Time")
                msg.exec_()
                return
        else:
            start_time = None
            end_time = None

        self.parentWidget().parentWidget().start_analysis(self.file, self.averaging_duration, self.time_selected, start_time, end_time)

    def reset(self):
        self.file = None
        self.file_name.setText("No File Selected")
        self.start.setDateTime(QDateTime.currentDateTime())
        self.end.setDateTime(QDateTime.currentDateTime())

class ProgressWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Analysis in progress..."))

        self.filename_label = QLabel("")
        self.averaging_label = QLabel("")
        self.start_label = QLabel("")
        self.end_label = QLabel("")

        self.layout.addWidget(self.filename_label)
        self.layout.addWidget(self.averaging_label)
        self.layout.addWidget(self.start_label)
        self.layout.addWidget(self.end_label)

        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.setLayout(self.layout)

    def begin_progress(self, filename, averaging, start, end):
        self.filename_label.setText("File Name: " + filename)
        self.averaging_label.setText("Averaging Duration: " + averaging)
        if start != None and end != None:
            self.start_label.setText("Start Time: " + start.toString())
            self.end_label.setText("End Time: " + end.toString())
        else:
            self.start_label.setText("Start Time: N/A")
            self.end_label.setText("End Time: N/A")

        self.completed = 0

        while self.completed < 100:
            self.completed += .00001
            self.progress.setValue(self.completed)

        self.parentWidget().parentWidget().complete_analysis()


class CompleteWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Analysis Complete!"))

        self.start_over = QPushButton("Start Over")
        self.start_over.clicked.connect(self.reset)
        self.layout.addWidget(self.start_over)

        self.setLayout(self.layout)

    def reset(self):
        self.parentWidget().parentWidget().start_over()


if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)