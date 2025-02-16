import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QTextEdit, QFileDialog, QLabel, QListWidget
)
from PyQt6.QtCore import QThread, pyqtSignal


class ConverterThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, files, target_format, bitrate, parent=None):
        super().__init__(parent)
        self.files = files
        self.target_format = target_format
        self.bitrate = bitrate

    def run(self):
        for file_path in self.files:
            directory = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            output_name = "c_" + os.path.splitext(base_name)[0] + "." + self.target_format
            output_path = os.path.join(directory, output_name)

            self.log_signal.emit(f"Converting: {file_path} -> {output_path}")

            cmd = ["ffmpeg", "-i", file_path, "-y"]
            if self.bitrate and self.bitrate != "N/A":
                cmd += ["-b:a", self.bitrate]
            cmd.append(output_path)

            self.log_signal.emit("Executing command: " + " ".join(cmd))
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_signal.emit("Successfully converted: " + output_path)
                else:
                    self.log_signal.emit("Error converting file: " + file_path)
                    self.log_signal.emit("stderr: " + result.stderr)
            except Exception as e:
                self.log_signal.emit("Exception during conversion " + file_path + ": " + str(e))
        self.finished_signal.emit()


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

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.select_files_button = QPushButton("Select Files")
        self.select_files_button.clicked.connect(self.select_files)
        layout.addWidget(self.select_files_button)

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

        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_button)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Audio Files", "", "Audio Files (*.*)")
        if files:
            self.selected_files = files
            self.files_list.clear()
            self.files_list.addItems(self.selected_files)

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

        target_format = self.format_combo.currentText()
        bitrate = self.bitrate_combo.currentText() if self.bitrate_combo.isEnabled() else None

        self.convert_button.setEnabled(False)
        self.select_files_button.setEnabled(False)

        self.converter_thread = ConverterThread(self.selected_files, target_format, bitrate)
        self.converter_thread.log_signal.connect(self.update_log)
        self.converter_thread.finished_signal.connect(self.conversion_finished)
        self.converter_thread.start()

    def update_log(self, message):
        self.log_output.append(message)

    def conversion_finished(self):
        self.log_output.append("Conversion completed!")
        self.convert_button.setEnabled(True)
        self.select_files_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
