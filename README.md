# Roboflow Dataset Downloader v0.1

A professional desktop application for HPI AI Traffic systems, designed to download and organize datasets from Roboflow with a modern, high-performance GUI.

---

## 🚀 Key Features
- **Modern UI**: Dark-themed, non-resizable "Slate-Navy" dashboard.
- **Zero-Scroll Design**: Optimized two-column layout for immediate configuration.
- **Credential Persistence**: Automatically masks and remembers your API Key/Workspace.
- **Real-time Feedback**: Mono-spaced console log and indeterminate progress bar.
- **Smart Organization**: Precision timestamps and custom format support (YOLO v2-v11, etc.).

---

## 🛠️ Installation & Setup
### 1. Requirements
- Python 3.10 or higher
- [Roboflow API Key](https://app.roboflow.com/settings/api)

### 2. Install Dependencies
```bash
pip install -r src/requirements.txt
```

### 3. Run Locally
```bash
python src/main.py
```

---

## 📦 Building Standalone Artifacts (GUI to .exe/Binary)

You can build the app into a single executable for distribution using **Docker** or **PyInstaller**. Detailed instructions are available in [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md).

### Method 1: Using Docker (Recommended for Isolation)
Run these commands from the root of the downloader tool:

- **Build Linux Binary**:
  ```bash
  mkdir dist
  docker build -f docker/Dockerfile.linux_build --output dist .
  ```
- **Build Windows .exe (from Linux/Docker)**:
  ```bash
  mkdir dist
  docker build -f docker/Dockerfile.win_build --output dist .
  ```

### Method 2: Local Build (PyInstaller)
Commands to run from the `src/` directory:

- **Windows**:
  ```bash
  cd src
  pyinstaller --noconfirm --onefile --windowed --name "Roboflow_Downloader" --add-data "config.json;." main.py
  ```
- **Linux**:
  ```bash
  cd src
  pyinstaller --noconfirm --onefile --windowed --name "roboflow-downloader" --add-data "config.json:." main.py
  ```

---

## 📁 Technical Architecture
- `src/`: Core Python source code and configuration.
- `docker/`: Dockerfiles for runtime and multi-stage builds.
- `docs/`: Technical guides and documentation.
- `README.md`: Tool overview.

---

**Built by HPI AI Core © 2026**
