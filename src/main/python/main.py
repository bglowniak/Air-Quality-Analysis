from fbs_runtime.application_context import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFileDialog

import sys

class AppContext(ApplicationContext):
    def run(self):
        version = self.build_settings['version']
        main_screen = MainWindow(version)
        main_screen.show()
        return self.app.exec_()

class MainWindow():
    def __init__(self, version):
        self.window = QMainWindow()
        central_widget = QWidget()
        central_widget.setFixedWidth(400)

        # set up layouts and widgets
        master_layout = QVBoxLayout()

        # apply layouts and show window
        master_layout.addLayout(self.generate_file_select())
        central_widget.setLayout(master_layout)

        self.window.setCentralWidget(central_widget)
        self.window.setWindowTitle("CDC/ATSDR Air Quality Analysis v" + version)
        self.window.setFixedSize(500, 250)

    def show(self):
        self.window.show()

    def generate_file_select(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Select Data File:"))

        file_name = QLabel("No File Selected")
        button = QPushButton("Browse")
        button.clicked.connect(self.get_file)

        layout.addWidget(file_name)
        layout.addWidget(button)

        return layout

    def get_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self.window, "Select Data Files", "", "All Files (*)")
        if fileName:
            print(fileName)

if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)