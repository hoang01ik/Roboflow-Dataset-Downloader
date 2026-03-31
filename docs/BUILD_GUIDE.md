# Distribution & Build Guide (Windows & Linux)

This document provides instructions for building and distributing the **Roboflow Dataset Downloader** as a standalone application or via Docker.

---

## Method A: Standard Local Build (Single Executable)
If you want to share a `.exe` (Windows) or binary (Linux) with others without requiring them to install Python.

### 1. Requirements
Ensure you are in the tool directory (`tools/download_dataset/`) and have the following installed:
```powershell
pip install pyinstaller customtkinter roboflow pillow darkdetect
```

### 2. Build for Windows (.exe)
Run this command from the `tools/download_dataset/` directory:
```powershell
pyinstaller --noconfirm --onefile --windowed --name "Roboflow_Downloader" --icon "NONE" --add-data "config.json;." main.py
```
*   `--onefile`: Compiles everything into a single `.exe`.
*   `--windowed`: Prevents the console from showing when opening the app.
*   Your final file will be in the `dist/` folder.

### 3. Build for Linux (Binary)
Run this command from the tool directory on a Linux machine:
```bash
pyinstaller --noconfirm --onefile --windowed --name "roboflow-downloader" --add-data "config.json:." main.py
```

---

## Method B: Docker Deployment (X11 GUI)
Use this if you want to run the application in a persistent, isolated container.

### 1. Build the Image
From the `tools/download_dataset/` directory, run:
```bash
docker build -t roboflow-downloader .
```

### 2. Run on Linux (With X11 Host)
To see the GUI from inside Docker, you must share your X11 display:
```bash
xhost +local:docker
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    roboflow-downloader
```

### 3. Run on Windows (via WSL2 + GWSL)
1. Ensure **WSLg** is active or use an X-Server like **VcXsrv** or **GWSL**.
2. Run with the host IP:
```powershell
docker run -it --rm -e DISPLAY=<YOUR_IP>:0.0 roboflow-downloader
```

---

## Distribution Notes
- **`config.json`**: This file stores your API Key. If you distribute the `.exe`, warn users that deleting this file will reset their credentials.
- **`datasets/`**: By default, data is saved in a subfolder. If running in Docker, you should mount a volume to persist downloads:
  `-v ./my_datasets:/app/datasets`
