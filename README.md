# Audio Converter

A simple **audio file converter** using `ffmpeg` and PyQt6. It allows users to convert multiple audio files into different formats with optional bitrate settings.

## 🚀 Features
- Supports **MP3, AAC, OGG, FLAC, WAV** formats.
- Allows users to **select bitrate** for lossy formats.
- Simple **GUI** using PyQt6.
- Uses **ffmpeg** for efficient conversion.
- Converts files with a **"c_" prefix** to avoid overwriting originals.

---

## 🛠️ Installation

### 1. Install dependencies
Make sure you have Python and `pip` installed.

```bash
pip install PyQt6
```

### 2. Install `ffmpeg`
#### Ubuntu / Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS (using Homebrew):
```bash
brew install ffmpeg
```

#### Windows:
- Download `ffmpeg` from [official site](https://ffmpeg.org/download.html).
- Add `ffmpeg.exe` to your system **PATH**.

---

## ▶️ Usage

### Run the script:
```bash
python main.py
```

### Steps:
1. Click **"Select Files"** to choose audio files.
2. Choose an **output format** from the dropdown.
3. Select a **bitrate** (if applicable).
4. Click **"Convert"** and wait for the process to complete.

Converted files will be saved in the **same directory** with a `"c_"` prefix.


## ⚖️ License
This project is open-source under the **MIT License**.
