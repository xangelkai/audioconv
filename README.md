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

---

## 📂 File Structure
```
/audioconv
│── main.py          # Main application script
│── README.md        # This file
└── requirements.txt # Dependencies (optional)
```

---

## 🔧 Development

### Clone the repository:
```bash
git clone https://github.com/your-username/audioconv.git
cd audioconv
```

### Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run the program:
```bash
python main.py
```

## ⚖️ License
This project is open-source under the **MIT License**.
