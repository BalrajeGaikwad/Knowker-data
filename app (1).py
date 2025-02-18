import sys
import os
import pandas as pd
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTabWidget, QVBoxLayout, QWidget,
    QPushButton, QStatusBar, QHBoxLayout, QLabel, QVBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT


class PlotCanvas(FigureCanvas):
    def __init__(self, data=None, title='', parent=None):
        self.fig, self.ax = Figure(figsize=(5, 4), dpi=100), None
        super().__init__(self.fig)
        self.setParent(parent)
        self.plot(data, title)

    def plot(self, data, title):
        self.ax = self.fig.add_subplot(111)
        if data is not None:
            self.ax.plot(data)
        self.ax.set_title(title)
        self.draw()


class Worker(QThread):
    # Signal to communicate status updates to the main thread
    update_status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, folder_path, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path

    def run(self):
        # Start the long-running process
        self.update_status.emit("Status: Running analysis...")

        command = ["python", "vibration_analysis.py", "-i", self.folder_path]
        try:
            subprocess.run(command, check=True)
            self.update_status.emit("Status: Analysis completed successfully.")
        except subprocess.CalledProcessError as e:
            self.update_status.emit(f"Status: Error occurred: {e}")

        # Emit finished signal
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Plot Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Tab widget for plots
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Buttons
        self.upload_button = QPushButton("Upload Folder")
        self.submit_button = QPushButton("Submit")
        self.submit_button.setEnabled(False)  # Initially disable the submit button
        self.status_label = QLabel("Status: Waiting for folder upload...")

        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.submit_button)

        # Add buttons and status to layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)

        central_widget.setLayout(main_layout)

        # Connect buttons to their respective methods
        self.upload_button.clicked.connect(self.upload_folder)
        self.submit_button.clicked.connect(self.submit_folder)

        # Initialize with empty plots in four tabs
        self.initialize_tabs()

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def initialize_tabs(self):
        # Create four empty tabs with placeholder plots
        plots = {
            "Sensor1 Fundamental Frequency": None,
            "Sensor2 Fundamental Frequency": None,
            "Sensor3 Fundamental Frequency": None,
            "Sensor4 Fundamental Frequency": None,
        }

        self.tab_widget.clear()  # Clear any existing tabs
        for title, data in plots.items():
            tab = QWidget()
            layout = QVBoxLayout()

            # Create canvas and toolbar for each tab
            canvas = PlotCanvas(data, title)
            toolbar = NavigationToolbar2QT(canvas, self)  # Add toolbar for each canvas

            layout.addWidget(toolbar)
            layout.addWidget(canvas)
            tab.setLayout(layout)
            self.tab_widget.addTab(tab, title)

        # Add the combined plot tab
        self.add_combined_plot_tab()

    def add_combined_plot_tab(self):
        # Create a new tab for the combined plot
        combined_tab = QWidget()
        layout = QVBoxLayout()

        # Placeholder canvas for combined plot
        canvas = PlotCanvas(data=None, title="Combined Sensor Plot")
        toolbar = NavigationToolbar2QT(canvas, self)  # Add toolbar for combined plot

        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        combined_tab.setLayout(layout)
        self.tab_widget.addTab(combined_tab, "Combined Plot")

        # Store the canvas for later update
        self.combined_canvas = canvas

    def plot_combined_data(self, df):
        # Update the combined plot with real data from the CSV file
        if hasattr(self, 'combined_canvas'):
            ax = self.combined_canvas.ax
            ax.clear()  # Clear the previous plot

            ax.plot(df['s1_f0'], label='Sensor1', color='blue')
            ax.plot(df['s2_f0'], label='Sensor2', color='green')
            ax.plot(df['s3_f0'], label='Sensor3', color='red')
            ax.plot(df['s4_f0'], label='Sensor4', color='purple')

            ax.set_title("Combined Sensor Plot")
            ax.legend()
            self.combined_canvas.draw()

    def upload_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.status_label.setText(f"Status: Folder '{folder_path}' selected.")
            self.submit_button.setEnabled(True)  # Enable the submit button

            # Store the folder path for later use
            self.selected_folder = folder_path

    def submit_folder(self):
        if not hasattr(self, 'selected_folder') or not self.selected_folder:
            self.status_label.setText("Status: No folder selected.")
            return

        self.status_label.setText("Status: Processing CSV file...")

        # Assume first CSV file in the folder
        csv_files = [f for f in os.listdir(self.selected_folder) if f.endswith('.csv')]
        if not csv_files:
            self.status_label.setText("Status: No CSV files found.")
            return
        
        # Disable submit button and show status
        self.submit_button.setEnabled(False)
        self.status_label.setText("Status: Processing...")

        # Start the worker thread
        self.worker = Worker(self.selected_folder)
        self.worker.update_status.connect(self.update_status)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def update_status(self, message):
        self.status_label.setText(message)

    def on_worker_finished(self):
        self.submit_button.setEnabled(True)  # Re-enable the submit button after task completion
        csv_filename = os.path.join(self.selected_folder, 'results', 'F0_Analysis.csv')
        self.process_csv(csv_filename, self.selected_folder)

    def process_csv(self, csv_filename, out_dir):
        # Columns for the CSV data
        columns = ['filename', 's1_f0', 's2_f0', 's3_f0', 's4_f0', 's1_M', 's2_M', 's3_M', 's4_M']
        df = pd.read_csv(csv_filename, names=columns, skiprows=1, index_col=False, delimiter=',')

        # Data for the plots
        plots = {
            "Sensor1 Fundamental Frequency": list(df['s1_f0']),
            "Sensor2 Fundamental Frequency": list(df['s2_f0']),
            "Sensor3 Fundamental Frequency": list(df['s3_f0']),
            "Sensor4 Fundamental Frequency": list(df['s4_f0']),
        }

        # Clear existing tabs and add new ones with the updated data
        self.tab_widget.clear()
        for title, data in plots.items():
            tab = QWidget()
            layout = QVBoxLayout()

            # Create canvas and toolbar for each tab
            canvas = PlotCanvas(data, title)
            toolbar = NavigationToolbar2QT(canvas, self)  # Add toolbar for each canvas

            layout.addWidget(toolbar)
            layout.addWidget(canvas)
            tab.setLayout(layout)
            self.tab_widget.addTab(tab, title)

        # Add the combined plot tab after updating individual plots
        self.add_combined_plot_tab()
        self.plot_combined_data(df)

        # Update status
        self.status_label.setText("Status: Processing completed.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
