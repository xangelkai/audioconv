import sys
import os
import subprocess
import threading
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QTextEdit, QFileDialog, QLabel, QListWidget,
    QSpinBox, QProgressBar
)
from PyQt6.QtCore import pyqtSignal, QRunnable, QObject, QThreadPool

class WorkerSignals(QObject):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

class Worker(QRunnable):
    def __init__(self, file_path, target_format, bitrate, cancel_event):
        super().__init__()
        self.file_path = file_path
        self.target_format = target_format
        self.bitrate = bitrate
        self.cancel_event = cancel_event
        self.signals = WorkerSignals()
        self.process = None

    def run(self):
        # Check for cancellation before starting
        if self.cancel_event.is_set():
            self.signals.log_signal.emit("Conversion canceled before start: " + self.file_path)
            self.signals.finished_signal.emit()
            return

        directory = os.path.dirname(self.file_path)
        base_name = os.path.basename(self.file_path)
        output_name = "c_" + os.path.splitext(base_name)[0] + "." + self.target_format
        output_path = os.path.join(directory, output_name)
        self.signals.log_signal.emit(f"Converting: {self.file_path} -> {output_path}")

        cmd = ["ffmpeg", "-i", self.file_path, "-y"]
        if self.bitrate and self.bitrate != "N/A":
            cmd += ["-b:a", self.bitrate]
        cmd.append(output_path)

        self.signals.log_signal.emit("Executing command: " + " ".join(cmd))
        try:
            # Start the conversion process
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # Poll for process completion while checking for cancellation
            while True:
                if self.cancel_event.is_set():
                    self.process.terminate()
                    self.signals.log_signal.emit("Conversion canceled: " + self.file_path)
                    break
                retcode = self.process.poll()
                if retcode is not None:
                    # Process finished – retrieve output
                    stdout, stderr = self.process.communicate()
                    if retcode == 0:
                        self.signals.log_signal.emit("Successfully converted: " + output_path)
                    else:
                        self.signals.log_signal.emit("Error converting file: " + self.file_path)
                        self.signals.log_signal.emit("stderr: " + stderr)
                    break
                time.sleep(0.1)
        except Exception as e:
            self.signals.log_signal.emit("Exception during conversion " + self.file_path + ": " + str(e))
        self.signals.finished_signal.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Converter")
        self.presets = {
            "mp3": ["128k", "192k", "256k", "320k"],
            "aac": ["96k", "128k", "160k", "192k", "256k"],
            "ogg": ["64k", "96k", "128k", "160k", "192k"],
            "flac": [],
            "wav": []
        }
        self.selected_files = []
        self.threadpool = QThreadPool()
        self.cancel_event = threading.Event()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Layout for file selection buttons
        file_buttons_layout = QHBoxLayout()
        self.select_files_button = QPushButton("Select Files")
        self.select_files_button.clicked.connect(self.select_files)
        file_buttons_layout.addWidget(self.select_files_button)

        self.clear_files_button = QPushButton("Clear Selected Files")
        self.clear_files_button.clicked.connect(self.clear_selected_files)
        file_buttons_layout.addWidget(self.clear_files_button)

        layout.addLayout(file_buttons_layout)

        self.files_list = QListWidget()
        layout.addWidget(self.files_list)

        format_layout = QHBoxLayout()
        format_label = QLabel("Select Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(list(self.presets.keys()))
        self.format_combo.currentTextChanged.connect(self.update_bitrate_options)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        bitrate_layout = QHBoxLayout()
        bitrate_label = QLabel("Select Bitrate:")
        self.bitrate_combo = QComboBox()
        bitrate_layout.addWidget(bitrate_label)
        bitrate_layout.addWidget(self.bitrate_combo)
        layout.addLayout(bitrate_layout)
        self.update_bitrate_options(self.format_combo.currentText())

        cores_layout = QHBoxLayout()
        cores_label = QLabel("Number of Threads:")
        self.cores_spinbox = QSpinBox()
        self.cores_spinbox.setMinimum(1)
        cpu_count = os.cpu_count() if os.cpu_count() is not None else 4
        self.cores_spinbox.setMaximum(cpu_count)
        self.cores_spinbox.setValue(cpu_count)
        cores_layout.addWidget(cores_label)
        cores_layout.addWidget(self.cores_spinbox)
        layout.addLayout(cores_layout)

        # Layout for conversion and cancel buttons
        action_buttons_layout = QHBoxLayout()
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.start_conversion)
        action_buttons_layout.addWidget(self.convert_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_all)
        self.cancel_button.setEnabled(False)
        action_buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(action_buttons_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        layout.addWidget(self.progress_bar)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Audio Files", "", "Audio Files (*.*)")
        if files:
            self.selected_files = files
            self.files_list.clear()
            self.files_list.addItems(self.selected_files)

    def clear_selected_files(self):
        self.selected_files = []
        self.files_list.clear()
        self.log_output.append("Selected files cleared.")

    def update_bitrate_options(self, format_text):
        self.bitrate_combo.clear()
        presets = self.presets.get(format_text, [])
        if presets:
            self.bitrate_combo.addItems(presets)
            self.bitrate_combo.setEnabled(True)
        else:
            self.bitrate_combo.addItem("N/A")
            self.bitrate_combo.setEnabled(False)

    def start_conversion(self):
        if not self.selected_files:
            self.log_output.append("No files selected for conversion!")
            return

        # Clear any previous cancellation flag
        self.cancel_event.clear()

        target_format = self.format_combo.currentText()
        bitrate = self.bitrate_combo.currentText() if self.bitrate_combo.isEnabled() else None
        cores = self.cores_spinbox.value()
        self.threadpool.setMaxThreadCount(cores)

        self.convert_button.setEnabled(False)
        self.select_files_button.setEnabled(False)
        self.clear_files_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        self.completed_tasks = 0
        total_files = len(self.selected_files)
        self.progress_bar.setMaximum(total_files)
        self.progress_bar.setValue(0)

        for file_path in self.selected_files:
            worker = Worker(file_path, target_format, bitrate, self.cancel_event)
            worker.signals.log_signal.connect(self.update_log)
            worker.signals.finished_signal.connect(self.worker_finished)
            self.threadpool.start(worker)

    def worker_finished(self):
        self.completed_tasks += 1
        self.progress_bar.setValue(self.completed_tasks)
        if self.completed_tasks == len(self.selected_files):
            self.conversion_finished()

    def update_log(self, message):
        self.log_output.append(message)

    def conversion_finished(self):
        if self.cancel_event.is_set():
            self.log_output.append("Conversion canceled!")
        else:
            self.log_output.append("Conversion completed!")
        self.convert_button.setEnabled(True)
        self.select_files_button.setEnabled(True)
        self.clear_files_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def cancel_all(self):
        self.log_output.append("Canceling all operations...")
        self.cancel_event.set()
        self.cancel_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec())
