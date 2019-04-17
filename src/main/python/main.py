from fbs_runtime.application_context import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFileDialog, QComboBox, QRadioButton, QDateTimeEdit, QStackedWidget, QProgressBar, QMessageBox, QLineEdit
from PyQt5.QtCore import QDateTime

from functools import partial
import sys
import os

from clean import process_file

class AppContext(ApplicationContext):
    def run(self):
        version = self.build_settings['version']
        with open(self.get_resource('style.qss')) as f:
            stylesheet = f.read()
        main_screen = MainWindow(version, stylesheet)
        main_screen.show()
        return self.app.exec_()

class MainWindow(QMainWindow):
    def __init__(self, version, stylesheet):
        super().__init__()
        self.main_widget = MainWidget()
        self.progress_widget = ProgressWidget()
        self.complete_widget = CompleteWidget()

        self.master = QStackedWidget()
        self.master.addWidget(self.main_widget)
        self.master.addWidget(self.progress_widget)
        self.master.addWidget(self.complete_widget)

        self.setCentralWidget(self.master)
        self.setWindowTitle("Air Quality Analysis v" + version)
        self.setFixedSize(500, 350)

        self.setStyleSheet(stylesheet)

    def start_analysis(self, filename, filepath, output, ad_number, ad_unit, time_selected, start_time, end_time):
        self.master.setCurrentIndex(1)

        if output == None:
            output_path = filepath[:len(filepath) - len(filename)] + "data_out"
        else:
            output_path = output
        try:
            self.progress_widget.begin_progress(filename, filepath, output_path, ad_number, ad_unit, start_time, end_time)
        except Exception as e:
            print(e) # TODO: Raise Error Dialog
            self.start_over()

    def complete_analysis(self, output_path, output_name):
        self.master.widget(2).set_output(output_path, output_name)
        self.master.setCurrentIndex(2)

    def start_over(self):
        self.master.widget(0).reset()
        self.master.setCurrentIndex(0)

    def raise_error(self, window_title, text, informative_text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowTitle(window_title)
        msg.setText(text)
        msg.setInformativeText(informative_text)
        msg.exec_()

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.output_path = None
        self.file = None
        self.ad_number = None
        self.ad_unit = None
        self.time_selected = False
        self.VALID_FILES = ["xlsx", "xls", "csv"]
        self.AD_UNITS = ["Minutes", "Hours", "Days", "Weeks", "Months", "Years"]

        title_label = QLabel("CDC Air Quality Analysis")
        title_label.setObjectName("title")
        file_select_layout = self.file_select_layout()
        output_path_layout = self.output_path_layout()
        averaging_duration_layout = self.averaging_duration_layout()
        time_range_layout = self.time_range_layout()
        self.time_selectors = self.create_time_selectors()

        process_file = QPushButton("Process File")
        process_file.clicked.connect(self.begin_process)

        self.layout = QVBoxLayout()
        self.layout.addWidget(title_label)
        self.layout.addLayout(file_select_layout)
        self.layout.addLayout(output_path_layout)
        self.layout.addLayout(averaging_duration_layout)
        self.layout.addLayout(time_range_layout)
        self.layout.addWidget(self.time_selectors)
        self.layout.addWidget(process_file)
        self.setLayout(self.layout)

    def file_select_layout(self):
        instruction = QLabel("Select Data File:")
        instruction.setObjectName("instruction")

        self.file_name = QLabel("No File Selected")
        self.file_name.setObjectName("fileName")
        self.file_name.setFixedWidth(200)

        button = QPushButton("Browse")
        button.setFixedWidth(100)
        button.clicked.connect(partial(self.get_file, self.file_name))

        layout = QHBoxLayout()
        layout.addWidget(instruction)
        layout.addWidget(self.file_name)
        layout.addWidget(button)
        layout.setContentsMargins(6, 10, 6, 8)

        return layout

    def output_path_layout(self):
        instruction = QLabel("Select Output Path:")
        instruction.setObjectName("instruction")

        self.output_select = QLabel("No Path Selected")
        self.output_select.setObjectName("fileName")
        self.output_select.setFixedWidth(200)

        button = QPushButton("Browse")
        button.setFixedWidth(100)
        button.clicked.connect(partial(self.get_output, self.output_select))

        layout = QHBoxLayout()
        layout.addWidget(instruction)
        layout.addWidget(self.output_select)
        layout.addWidget(button)
        layout.setContentsMargins(6, 10, 6, 8)

        return layout

    def averaging_duration_layout(self):
        instruction = QLabel("Select Averaging Duration:")
        instruction.setObjectName("instruction")

        self.ad_number_input = QLineEdit(self)
        self.ad_number_input.setPlaceholderText("Input an Integer")
        self.ad_number_input.setFixedWidth(125)
        self.ad_number_input.setFixedHeight(25)

        self.ad_unit = self.AD_UNITS[0] # default
        comboBox = QComboBox(self)
        comboBox.setFixedWidth(100)
        for item in self.AD_UNITS:
            comboBox.addItem(item)
        comboBox.currentIndexChanged.connect(partial(self.selection_change, comboBox))

        layout = QHBoxLayout()
        layout.addWidget(instruction)
        layout.addWidget(self.ad_number_input)
        layout.addWidget(comboBox)
        layout.setContentsMargins(6, 8, 6, 8)

        return layout

    def selection_change(self, cb):
        self.ad_unit = cb.currentText()

    def time_range_layout(self):
        instruction = QLabel("Use Time Range?")
        instruction.setObjectName("instruction")

        yes_rb = QRadioButton("Yes")
        no_rb = QRadioButton("No")
        no_rb.setChecked(True)

        yes_rb.toggled.connect(partial(self.rb_state, yes_rb))
        no_rb.toggled.connect(partial(self.rb_state, no_rb))

        layout = QHBoxLayout()
        layout.addWidget(instruction)
        layout.addWidget(yes_rb)
        layout.addWidget(no_rb)
        layout.setContentsMargins(6,8,6,8)
        layout.insertSpacing(1, 85)
        layout.insertSpacing(3, 80)

        return layout

    def create_time_selectors(self):
        instruction = QLabel("Start Time:")
        instruction.setObjectName("instruction")

        self.start = QDateTimeEdit(self)
        self.start.setCalendarPopup(True)
        self.start.setDateTime(QDateTime.currentDateTime())

        instruction2 = QLabel("End Time:")
        instruction2.setObjectName("instruction")

        self.end = QDateTimeEdit(self)
        self.end.setCalendarPopup(True)
        self.end.setDateTime(QDateTime.currentDateTime())

        layout = QHBoxLayout()
        layout.setContentsMargins(6, 8, 6, 10)
        layout.addWidget(instruction)
        layout.addWidget(self.start)
        layout.addWidget(instruction2)
        layout.addWidget(self.end)

        widget = QWidget()
        widget.setLayout(layout)
        widget.setFixedHeight(50)
        widget.setEnabled(False)

        return widget

    def get_file(self, label):
        valid_files = ""
        for ext in self.VALID_FILES:
            valid_files += "*." + ext + " "

        fileName, _ = QFileDialog.getOpenFileName(self, "Select Data Files", "",
                                                        "Data Files (" + valid_files.strip() +");;All Files (*)")
        if fileName:
            self.file = fileName.split("/")[-1]
            self.filepath = fileName
            label.setText(self.file)

    def get_output(self, label):
        path = QFileDialog.getExistingDirectory(self, "Choose an Output Directory", options = QFileDialog.ShowDirsOnly)
        if path:
            self.output_path = path
            split_path = path.split("/")
            if len(split_path) >= 2:
                label.setText(split_path[-2] + "/" + split_path[-1])
            else:
                label.setText(self.output_path)

    def rb_state(self, clicked):
        if clicked.text() == "Yes" and clicked.isChecked() == True:
            self.time_selectors.setEnabled(True)
            self.time_selected = True
        elif clicked.text() == "No" and clicked.isChecked() == True:
            self.time_selectors.setEnabled(False)
            self.time_selected = False

    # TODO: Improve Error Messages, make sure this is fully robust
    def begin_process(self):
        main_window = self.parentWidget().parentWidget()
        if not self.file:
            main_window.raise_error("Input Error",
                                    "No File Selected",
                                    "Please Select a Valid File")
            return

        extension = self.file.split(".")[-1]
        if not extension in self.VALID_FILES:
            main_window.raise_error("Input Error",
                                    "Invalid File Type",
                                    "Valid File Types Include " + ", ".join(self.VALID_FILES))
            return

        self.ad_number = self.ad_number_input.text()
        if not self.ad_number or not self.ad_unit:
            main_window.raise_error("Input Error",
                                    "Invalid Averaging Duration Selected",
                                    "Please input a number and unit")
            return

        try:
            self.ad_number = float(self.ad_number)
        except ValueError:
            main_window.raise_error("Input Error",
                                    "Invalid Averaging Duration Selected",
                                    "Input must be a number.")
            return

        if not round(self.ad_number) == self.ad_number:
            main_window.raise_error("Input Error",
                                    "Invalid Averaging Duration Selected",
                                    "Input cannot be a decimal/must be a whole number.")
            return

        if self.time_selected:
            start_time = self.start.dateTime()
            end_time = self.end.dateTime()
            if start_time > end_time:
                main_window.raise_error("Input Error",
                                        "Invalid Time Entered",
                                        "End Time cannot be greater than Start Time")
                return
        else:
            start_time = None
            end_time = None

        main_window.start_analysis(
            self.file,
            self.filepath,
            self.output_path,
            self.ad_number,
            self.ad_unit,
            self.time_selected,
            start_time,
            end_time
        )

    def reset(self):
        self.file = None
        self.file_name.setText("No File Selected")
        self.output_path = None
        self.output_select.setText("No Path Selected")
        self.ad_number = None
        self.ad_unit = self.AD_UNITS[0]
        self.ad_number_input.clear()
        self.start.setDateTime(QDateTime.currentDateTime())
        self.end.setDateTime(QDateTime.currentDateTime())

class ProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        title_label = QLabel("Analysis in progress...")
        title_label.setObjectName("title")

        self.filename_label = QLabel("")
        self.filename_label.setObjectName("details")

        self.averaging_label = QLabel("")
        self.averaging_label.setObjectName("details")

        self.start_label = QLabel("")
        self.start_label.setObjectName("details")

        self.end_label = QLabel("")
        self.end_label.setObjectName("details")

        self.progress = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.filename_label)
        layout.addWidget(self.averaging_label)
        layout.addWidget(self.start_label)
        layout.addWidget(self.end_label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

    def begin_progress(self, filename, filepath, output_path, ad_num, ad_unit, start, end):
        self.filename_label.setText("File Name: " + filename)
        self.averaging_label.setText("Averaging Duration: " + ad_num + " " + ad_unit)
        if start != None and end != None:
            self.start_label.setText("Start Time: " + start.toString())
            self.end_label.setText("End Time: " + end.toString())
        else:
            self.start_label.setText("Start Time: N/A")
            self.end_label.setText("End Time: N/A")

        self.completed = 0

        while self.completed < 100:
            self.completed += .00005
            self.progress.setValue(self.completed)

        output_name = process_file(filepath,
                                   output_path,
                                   (ad_num, ad_unit),
                                   start_time=start,
                                   stop_time=end)

        self.parentWidget().parentWidget().complete_analysis(output_path, output_name)

class CompleteWidget(QWidget):
    def __init__(self):
        super().__init__()
        title = QLabel("Analysis Complete!")
        title.setObjectName("title")

        self.filepath = QLabel()
        self.filepath.setWordWrap(True)
        self.filepath.setObjectName("details")
        self.filepath.setFixedHeight(50)

        result = QPushButton("View Results")
        result.clicked.connect(partial(self.open_result))

        start_over = QPushButton("Start Over")
        start_over.clicked.connect(self.reset)

        button_layout = QHBoxLayout()
        button_layout.addWidget(result)
        button_layout.addWidget(start_over)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.filepath)
        layout.insertSpacing(3, 75)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def set_output(self, output_path, output_name):
        self.output_path = output_path
        self.output_name = output_name
        self.filepath.setText("Files Generated At: " + self.output_path)

    def reset(self):
        self.output_path = None
        self.output_name = None
        self.parentWidget().parentWidget().start_over()

    def open_result(self):
        if not self.output_path is None and not self.output_name is None:
            full_path = os.path.join(self.output_path, self.output_name)
            os.startfile(full_path)

if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
