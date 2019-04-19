# Python standard library imports
from functools import partial
import sys
import os

# fbs imports
from fbs_runtime.application_context import ApplicationContext

# PyQt5 imports
from PyQt5.QtWidgets import qApp, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFileDialog, QComboBox, QRadioButton, QDateTimeEdit, QStackedWidget, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt, QDateTime, QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QMovie

# Data Processor function import (from clean.py)
from clean import process_file


class AppContext(ApplicationContext):
    '''The AppContext class is used by fbs to manage and initialize the application.'''
    def run(self):
        # get version, load stylesheet and resources, and initalize main screen
        version = self.build_settings["version"]
        with open(self.get_resource("style.qss")) as f:
            stylesheet = f.read()
        progress_icon = self.get_resource("loading-icon.gif")
        main_screen = MainWindow(version, stylesheet, progress_icon)
        main_screen.show()
        return self.app.exec_()


class MainWindow(QMainWindow):
    '''
    The MainWindow class acts as a container for the three screens of the app.

    Args:
        version (str): the current build version of the application
        stylesheet (str): the opened .qss file containing styles for the application
        progress_icon (str): the path to the progress icon gif located in src/main/resources

    Attributes:
        main_widget (QWidget): represents the home screen of the app that accepts user input
        progress_widget (QWidget): displays information as the data processor runs in the background
        complete_widget (QWidget): displays when the app has completed
        master (QStackedWidget): the master stacked widget that contains all three screens

    '''
    def __init__(self, version, stylesheet, progress_icon):
        super().__init__()

        # initialize the three screens (each is a QWidget)
        self.main_widget = MainWidget()
        self.progress_widget = ProgressWidget(progress_icon)
        self.complete_widget = CompleteWidget()

        # load the three screens into a stacked widget that the window will cycle through
        self.master = QStackedWidget()
        self.master.addWidget(self.main_widget)
        self.master.addWidget(self.progress_widget)
        self.master.addWidget(self.complete_widget)
        self.setCentralWidget(self.master)

        # finish setting up the window
        self.setWindowTitle("Air Quality Analysis v" + version)
        self.setFixedSize(500, 350)
        self.setStyleSheet(stylesheet)

    # take in parameters from the main screen, move to progress screen, and begin the analysis
    def start_analysis(self, file_name, file_path, output_path, ad_number, ad_unit, start_time, end_time):
        # move to the progress screen
        self.master.setCurrentIndex(1)

        # if user has not provided an output path, set default
        if output_path == None:
            output_path = file_path[:len(file_path) - len(file_name)] + "data_out"

        self.progress_widget.begin_progress(file_name,
                                            file_path,
                                            output_path,
                                            ad_number, ad_unit,
                                            start_time, end_time)

    # move to the completion screen with the resultant output path
    # if an error occurred, display to the user and return to main screen
    def complete_analysis(self, output, error):
        if error:
            self.raise_error("Data Processing Error", "An error has occurred while processing the file.", output)
            self.start_over()
        else:
            self.master.widget(2).set_output(output)
            self.master.setCurrentIndex(2)

    # return to the main screen and reset inputs
    def start_over(self):
        self.master.widget(0).reset()
        self.master.setCurrentIndex(0)

    # raise error dialog
    def raise_error(self, window_title, text, informative_text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowTitle(window_title)
        msg.setText(text)
        msg.setInformativeText(informative_text)
        msg.exec_()


class MainWidget(QWidget):
    '''
    The MainWidget class is the home screen of the app and allows the user to input parameters for analysis.

    Attributes:
        output_path (str): the output path selected by the user
        file (str): the file path selected by the user
        ad_number (int): the integer selected by the user for the averaging duration
        ad_unit (int): the unit of time selected by the user for the averaging duration
        time_selected (bool): whether or not the user has selected a specific time range
        VALID_FILES (list of str): the list of valid file types accepted
        AD_UNITS (list of str): the list of time units selectable by the user
        time_selectors (QWidget): a widget containing the time range inputs
        layout (QVBoxLayout): a vertical layout for the screen
    '''
    def __init__(self):
        super().__init__()
        # initialize variables
        self.output_path = None
        self.file = None
        self.ad_number = None
        self.ad_unit = None
        self.time_selected = False

        # single definition point for hardcoded values (valid file types and averaging duration units)
        self.VALID_FILES = ["xlsx", "xls", "csv"]
        self.AD_UNITS = ["Minutes", "Hours", "Days", "Weeks", "Months", "Years"]

        # create static UI elements
        title_label = QLabel("CDC Air Quality Analysis")
        title_label.setObjectName("title")
        file_select_layout = self.file_select_layout()
        output_path_layout = self.output_path_layout()
        averaging_duration_layout = self.averaging_duration_layout()
        time_range_layout = self.time_range_layout()
        self.time_selectors = self.create_time_selectors()

        # create process button and connect to function
        process_file = QPushButton("Process File")
        process_file.clicked.connect(self.begin_process)

        # define the layout of the screen
        self.layout = QVBoxLayout()
        self.layout.addWidget(title_label)
        self.layout.addLayout(file_select_layout)
        self.layout.addLayout(output_path_layout)
        self.layout.addLayout(averaging_duration_layout)
        self.layout.addLayout(time_range_layout)
        self.layout.addWidget(self.time_selectors)
        self.layout.addWidget(process_file)
        self.setLayout(self.layout)

    # define UI elements and layout for the file select input
    def file_select_layout(self):
        instruction_label = QLabel("Select Data File:")
        instruction_label.setObjectName("instruction")

        self.file_name = QLabel("No File Selected")
        self.file_name.setObjectName("fileName")
        self.file_name.setFixedWidth(200)

        button = QPushButton("Browse")
        button.setFixedWidth(100)
        button.clicked.connect(partial(self.get_file, self.file_name))

        layout = QHBoxLayout()
        layout.addWidget(instruction_label)
        layout.addWidget(self.file_name)
        layout.addWidget(button)
        layout.setContentsMargins(6, 10, 6, 8)

        return layout

    # define UI elements and layout for the output path select input
    def output_path_layout(self):
        instruction_label = QLabel("Select Output Path:")
        instruction_label.setObjectName("instruction")

        self.output_select = QLabel("No Path Selected")
        self.output_select.setObjectName("fileName")
        self.output_select.setFixedWidth(200)

        button = QPushButton("Browse")
        button.setFixedWidth(100)
        button.clicked.connect(partial(self.get_output, self.output_select))

        layout = QHBoxLayout()
        layout.addWidget(instruction_label)
        layout.addWidget(self.output_select)
        layout.addWidget(button)
        layout.setContentsMargins(6, 10, 6, 8)

        return layout

    # define UI elements and layout for averaging duration input
    def averaging_duration_layout(self):
        instruction_label = QLabel("Select Averaging Duration:")
        instruction_label.setObjectName("instruction")

        self.ad_number_input = QLineEdit(self)
        self.ad_number_input.setPlaceholderText("Input an Integer")
        self.ad_number_input.setFixedWidth(125)
        self.ad_number_input.setFixedHeight(25)

        # define dropdown menu (known as a ComboBox)
        self.ad_unit = self.AD_UNITS[0] # default
        comboBox = QComboBox(self)
        comboBox.setFixedWidth(100)
        for item in self.AD_UNITS:
            comboBox.addItem(item)
        comboBox.currentIndexChanged.connect(partial(self.selection_change, comboBox))

        layout = QHBoxLayout()
        layout.addWidget(instruction_label)
        layout.addWidget(self.ad_number_input)
        layout.addWidget(comboBox)
        layout.setContentsMargins(6, 8, 6, 8)

        return layout

    # called whenever the user makes a new selection from the averaging duration dropdown
    def selection_change(self, cb):
        self.ad_unit = cb.currentText()

    # define UI elements and layout for the time range input
    def time_range_layout(self):
        instruction_label = QLabel("Use Time Range?")
        instruction_label.setObjectName("instruction")

        # time range is optional, so these radio buttons formalize that choice
        yes_rb = QRadioButton("Yes")
        no_rb = QRadioButton("No")
        no_rb.setChecked(True)

        yes_rb.toggled.connect(partial(self.rb_state, yes_rb))
        no_rb.toggled.connect(partial(self.rb_state, no_rb))

        layout = QHBoxLayout()
        layout.addWidget(instruction_label)
        layout.addWidget(yes_rb)
        layout.addWidget(no_rb)
        layout.setContentsMargins(6,8,6,8)
        layout.insertSpacing(1, 85)
        layout.insertSpacing(3, 80)

        return layout

    # define UI elements and layout for the time range selectors
    def create_time_selectors(self):
        instruction_label = QLabel("Start Time:")
        instruction_label.setObjectName("instruction")

        self.start = QDateTimeEdit(self)
        self.start.setCalendarPopup(True)
        self.start.setDateTime(QDateTime.currentDateTime())

        instruction2_label = QLabel("End Time:")
        instruction2_label.setObjectName("instruction")

        self.end = QDateTimeEdit(self)
        self.end.setCalendarPopup(True)
        self.end.setDateTime(QDateTime.currentDateTime())

        layout = QHBoxLayout()
        layout.setContentsMargins(6, 8, 6, 10)
        layout.addWidget(instruction_label)
        layout.addWidget(self.start)
        layout.addWidget(instruction2_label)
        layout.addWidget(self.end)

        # define a new widget so we can enable and disable it based on the radio button input
        widget = QWidget()
        widget.setLayout(layout)
        widget.setFixedHeight(50)
        widget.setEnabled(False)

        return widget

    # called when the user clicks the select file button
    def get_file(self, label):
        # get valid file types from array
        valid_files = ""
        for ext in self.VALID_FILES:
            valid_files += "*." + ext + " "

        # open file explorer dialog prefilled with valid file types
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Data Files", "",
                                                        "Data Files (" + valid_files.strip() +");;All Files (*)")
        # if user closes dialog without selecting a file path, it will return None
        if file_name:
            self.file = file_name.split("/")[-1]
            self.file_path = file_name
            label.setText(self.file)

    # called when the user clicks the select output path button
    def get_output(self, label):
        path = QFileDialog.getExistingDirectory(self, "Choose an Output Directory", options=QFileDialog.ShowDirsOnly)
        if path:
            self.output_path = path
            split_path = path.split("/")
            if len(split_path) >= 2:
                label.setText(split_path[-2] + "/" + split_path[-1])
            else:
                label.setText(self.output_path)

    # change the state of the radio buttons and toggle the time range widget
    def rb_state(self, clicked):
        if clicked.text() == "Yes" and clicked.isChecked() == True:
            self.time_selectors.setEnabled(True)
            self.time_selected = True
        elif clicked.text() == "No" and clicked.isChecked() == True:
            self.time_selectors.setEnabled(False)
            self.time_selected = False

    # perform input validation and begin processing
    def begin_process(self):
        main_window = self.parentWidget().parentWidget()
        # check that a file has been selected
        if not self.file:
            main_window.raise_error("Input Error",
                                    "No File Selected",
                                    "Please select a file for analysis.")
            return

        extension = self.file.split(".")[-1]
        # check that the file selected is a valid file type
        if not extension in self.VALID_FILES:
            main_window.raise_error("Input Error",
                                    "Invalid File Type Selected",
                                    "Valid file types include " + ", ".join(self.VALID_FILES) + ".")
            return

        # check that the user has inputted a number and unit for averaging duration
        self.ad_number = self.ad_number_input.text()
        if not self.ad_number or not self.ad_unit:
            main_window.raise_error("Input Error",
                                    "Invalid Averaging Duration Selected",
                                    "Please input an integer and unit for the averaging duration.")
            return

        # check that the ad_num input is actually a number
        try:
            self.ad_number = int(self.ad_number)
        except ValueError:
            main_window.raise_error("Input Error",
                                    "Invalid Averaging Duration Selected",
                                    "Averaging duration must be a whole number.")
            return

        # check that the ad_num input is actually an integer
        # we want the user to be made aware that it must be an integer
        if not round(self.ad_number) == self.ad_number:
            main_window.raise_error("Input Error",
                                    "Invalid Averaging Duration Selected",
                                    "Averaging duration must be a whole number.")
            return

        # if the user has chosen a time range, make sure that end time is not before start time
        if self.time_selected:
            start_time = self.start.dateTime()
            end_time = self.end.dateTime()
            if start_time > end_time:
                main_window.raise_error("Input Error",
                                        "Invalid Time Entered",
                                        "End Time cannot be greater than Start Time.")
                return
        else:
            start_time = None
            end_time = None

        # callback to main window to initiate process and change the screen
        main_window.start_analysis(
            self.file,
            self.file_path,
            self.output_path,
            self.ad_number,
            self.ad_unit,
            start_time,
            end_time
        )

    # reset and clear all inputs
    def reset(self):
        self.file = None
        self.file_name.setText("No File Selected")
        self.output_path = None
        self.output_select.setText("No Path Selected")
        self.ad_number = None
        self.ad_number_input.clear()
        self.start.setDateTime(QDateTime.currentDateTime())
        self.end.setDateTime(QDateTime.currentDateTime())


# credit to https://stackoverflow.com/questions/41526832/pyqt5-qthread-signal-not-working-gui-freeze
class Processor(QObject):
    '''
    The Processor class defines an object that will run the data processor function.
    This essentially a container for our process_file function so that we can delegate it to a QThread.

    Args:
        file_path (str): the path to the selected file
        output_path (str): the path to the output directory
        ad_num (int): the selected number for the averaging duration
        ad_unit (str): the selected unit for the averaging duration
        start (QDateTime): the selected start time
        end (QDateTime): the selected end time

    Attributes:
        result_signal (pyqtSignal): used to emit the resultant output path back to the main thread

    '''
    result_signal = pyqtSignal(str, bool)

    def __init__(self, file_path, output_path, ad_num, ad_unit, start, end):
        super().__init__()
        self.file_path = file_path
        self.output_path = output_path
        self.ad_tuple = (ad_num, ad_unit)
        self.start_time = start
        self.end_time = end

    def work(self):
        error = False
        try:
            output = process_file(self.file_path,
                                  self.output_path,
                                  self.ad_tuple,
                                  start_time=self.start_time,
                                  stop_time=self.end_time)
        except Exception as e:
            error = True
            output = str(e) # we trust the back end to describe errors

        # tell the main thread that we're done processing
        self.result_signal.emit(output, error)


class ProgressWidget(QWidget):
    '''
    The ProgressWidget initializes the process and displays information about it.

    Args:
        progress_icon (str): the file path of the loading icon gif

    Attributes:
        thread (QThread): the thread used by the widget to delegate the processor to
        file_name_label (QLabel): displays the file name that was selected
        averaging_label (QLabel): displays the averaging duration number and unit selected
        start_label (QLabel): displays the start time selected (or N/A)
        end_label (QLabel): displays the end time selected (or N/A)
        movie (QMovie): runs the loading icon gif

        All labels are defined as attributes of the class so they can be modified at the start of each process.
    '''
    def __init__(self, progress_icon):
        super().__init__()
        # delegation thread used to run the process off of the main event loop
        self.thread = QThread()
        self.thread.setObjectName("Data Processor Thread")

        # define information labels
        title_label = QLabel("Analysis in progress...")
        title_label.setObjectName("title")
        self.file_name_label = QLabel("")
        self.file_name_label.setObjectName("details")
        self.averaging_label = QLabel("")
        self.averaging_label.setObjectName("details")
        self.start_label = QLabel("")
        self.start_label.setObjectName("details")
        self.end_label = QLabel("")
        self.end_label.setObjectName("details")

        # define movie and container label
        self.movie = QMovie(progress_icon)
        loading_label = QLabel()
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setMovie(self.movie)

        # define layout
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.file_name_label)
        layout.addWidget(self.averaging_label)
        layout.addWidget(self.start_label)
        layout.addWidget(self.end_label)
        layout.addWidget(loading_label)
        self.setLayout(layout)

    # takes in all parameters related to the process and spawns a worker to run it
    def begin_progress(self, file_name, file_path, output_path, ad_num, ad_unit, start, end):
        # populate labels with inputted parameters
        self.file_name_label.setText("File Name: " + file_name)
        self.averaging_label.setText("Averaging Duration: " + str(ad_num) + " " + ad_unit)
        if start != None and end != None:
            self.start_label.setText("Start Time: " + start.toString())
            self.end_label.setText("End Time: " + end.toString())
        else:
            self.start_label.setText("Start Time: N/A")
            self.end_label.setText("End Time: N/A")

        # start icon gif and allow main event loop to process it
        self.movie.start()
        qApp.processEvents()

        # define a worker object, move it to a new thread, and begin the processor work
        self.processor = Processor(file_path, output_path, ad_num, ad_unit, start, end)
        self.processor.moveToThread(self.thread)
        self.thread.started.connect(self.processor.work)
        self.processor.result_signal.connect(self.finish)
        self.thread.start()

    # ends the process and makes a callback to the main window with the result
    @pyqtSlot(str, bool)
    def finish(self, output, error):
        # stop and disconnect the thread from the processor object
        self.thread.quit()
        self.thread.wait()
        self.thread.disconnect()
        self.movie.stop()
        self.parentWidget().parentWidget().complete_analysis(output, error)


class CompleteWidget(QWidget):
    '''
    The CompleteWidget presents the results of the analysis to the user.

    Attributes:
        file_path (QLabel): a label containing the output path
        output (str): the resultant output path of the analysis
    '''
    def __init__(self):
        super().__init__()
        title = QLabel("Analysis Complete!")
        title.setObjectName("title")

        self.file_path = QLabel()
        self.file_path.setWordWrap(True)
        self.file_path.setObjectName("details")
        self.file_path.setFixedHeight(50)

        result = QPushButton("View Results")
        result.clicked.connect(partial(self.open_result))

        start_over = QPushButton("Start Over")
        start_over.clicked.connect(self.reset)

        button_layout = QHBoxLayout()
        button_layout.addWidget(result)
        button_layout.addWidget(start_over)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.file_path)
        layout.insertSpacing(3, 75)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    # set a new output path on the screen after an analysis runs
    def set_output(self, output):
        self.output = output.replace("\\", "/")
        self.file_path.setText("Output Files Generated At: " + self.output)

    # clear the result and call back to the main window to start over
    def reset(self):
        self.output = None
        self.parentWidget().parentWidget().start_over()

    # open the resultant output path
    def open_result(self):
        if not self.output is None:
            os.startfile(self.output)


if __name__ == "__main__":
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
