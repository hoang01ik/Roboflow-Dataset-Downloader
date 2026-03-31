import threading
import json
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from roboflow_service import RoboflowService

# UI Colors from DESIGN.md
BG_COLOR = "#1a1c23"
SURFACE_COLOR = "#242730"
ACCENT_GREEN = "#2ecc71"
ACCENT_HOVER = "#27ae60"
TEXT_PRIMARY = "#f8f9fa"
TEXT_MUTED = "#9ca3af"

import os
import sys
import json
import base64

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# Professional Config Path: %LOCALAPPDATA%/HPI_AI_Core/RoboflowDownloader/config.bin
def get_config_path():
    if sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
    else:
        base = os.path.expanduser("~/.config")
    
    config_dir = os.path.join(base, "HPI_AI_Core", "RoboflowDownloader")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.bin")

CONFIG_FILE = get_config_path()

def encrypt_data(data_str):
    """Simple obfuscation using Base64."""
    return base64.b64encode(data_str.encode()).decode()

def decrypt_data(enc_str):
    """Decode simple Base64 obfuscation."""
    try:
        return base64.b64decode(enc_str.encode()).decode()
    except:
        return ""

class RoboflowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Traffic Roboflow Downloader")
        self.geometry("700x780") 
        self.configure(fg_color=BG_COLOR)
        
        # Appearance settings
        ctk.set_appearance_mode("dark")
        self.resizable(False, False) # Lock resizing

        # UI Layout
        self._setup_layout()
        self._create_header()
        self._create_tabview()
        self._create_log_area()
        self._create_download_button()
        
        # Load encrypted credentials from User AppData
        self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    if "api_key" in data:
                        api_key = decrypt_data(data["api_key"])
                        self.api_entry.insert(0, api_key)
                    if "workspace_id" in data:
                        workspace_id = decrypt_data(data["workspace_id"])
                        self.workspace_entry.insert(0, workspace_id)
            except Exception as e:
                self.update_log(f"Error loading credentials: {e}")

    def _save_config(self):
        try:
            data = {
                "api_key": encrypt_data(self.api_entry.get()),
                "workspace_id": encrypt_data(self.workspace_entry.get())
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            self.update_log(f"Error securing credentials: {e}")

    def _setup_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=(20, 5), sticky="ew")
        
        self.label = ctk.CTkLabel(
            header_frame, text="Download Manager", 
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.label.pack(side="top", anchor="w")
        
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.pack(side="top", anchor="w")
        
        self.status_dot = ctk.CTkLabel(status_frame, text="●", font=ctk.CTkFont(size=14), text_color="#555")
        self.status_dot.pack(side="left", padx=(0, 5))
        
        self.subtitle = ctk.CTkLabel(
            status_frame, text="Dataset Acquisition System v2.9.0", 
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        self.subtitle.pack(side="left")

    def _create_tabview(self):
        # Create Tabview as the main area
        self.tabview = ctk.CTkTabview(
            self, 
            fg_color=SURFACE_COLOR,
            segmented_button_fg_color="#1a1c23",
            segmented_button_selected_color="#333",
            segmented_button_selected_hover_color="#444",
            corner_radius=12
        )
        self.tabview.grid(row=1, column=0, padx=30, pady=(5, 10), sticky="nsew")
        
        # Add tabs
        self.tabview.add("Downloader")
        self.tabview.add("Help Support")
        self.tabview.add("About App")
        
        # Configure Downloader Tab - NO SCROLLING
        self.downloader_tab = self.tabview.tab("Downloader")
        # Use a 2-column grid inside the tab to save vertical space
        self.downloader_tab.grid_columnconfigure(0, weight=1)
        self.downloader_tab.grid_columnconfigure(1, weight=1)
        self._create_downloader_tab_content()
        
        # Configure Help Tab
        self.help_tab = self.tabview.tab("Help Support")
        self.help_tab.grid_columnconfigure(0, weight=1)
        self._create_help_tab_content()
        
        # Configure About Tab
        self.about_tab = self.tabview.tab("About App")
        self.about_tab.grid_columnconfigure(0, weight=1)
        self._create_about_tab_content()

    def _create_downloader_tab_content(self):
        # We now use grid for sections to fit them neatly
        
        # --- Column 0: Authentication ---
        auth_frame = ctk.CTkFrame(self.downloader_tab, fg_color="transparent")
        auth_frame.grid(row=0, column=0, padx=15, pady=0, sticky="nsew")
        
        self._create_section_label_grid(auth_frame, "1. AUTHENTICATION")
        self.api_entry = self._create_input_grid(auth_frame, "API Key:", "Key...", 0, show="*")
        self.workspace_entry = self._create_input_grid(auth_frame, "Workspace:", "ID...", 1)
        
        self.load_btn = ctk.CTkButton(
            auth_frame, text="Connect & Sync Repository", 
            command=self._fetch_projects,
            height=32, font=ctk.CTkFont(size=12, weight="bold"),
            border_width=1, border_color="#333",
            hover_color="#34495e"
        )
        self.load_btn.pack(fill="x", padx=10, pady=(15, 0))

        # --- Column 1: Selection ---
        select_frame = ctk.CTkFrame(self.downloader_tab, fg_color="transparent")
        select_frame.grid(row=0, column=1, padx=15, pady=0, sticky="nsew")
        
        self._create_section_label_grid(select_frame, "2. DATASET SELECTION")
        self.project_var = ctk.StringVar(value="Select Project...")
        self.project_menu = self._create_dropdown_grid(select_frame, "Project:", self.project_var, ["Select Project..."], 0, command=self._fetch_versions)
        
        self.version_var = ctk.StringVar(value="Select Version...")
        self.version_menu = self._create_dropdown_grid(select_frame, "Version:", self.version_var, ["Select Version..."], 1)

        # --- Span Both Columns: Configuration ---
        config_frame = ctk.CTkFrame(self.downloader_tab, fg_color="transparent")
        config_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=(20, 0), sticky="ew")
        
        self._create_section_label_grid(config_frame, "3. EXPORT CONFIGURATION")
        
        # 3.1 Format
        f_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        f_frame.pack(fill="x", pady=2)
        lbl = ctk.CTkLabel(f_frame, text="Export Format:", width=100, anchor="w", text_color=TEXT_PRIMARY)
        lbl.pack(side="left", padx=10)
        self.format_var = ctk.StringVar(value="yolo26")
        self.format_menu = ctk.CTkOptionMenu(
            f_frame, variable=self.format_var, values=RoboflowService.get_available_formats(),
            fg_color="#333", button_color="#444", button_hover_color="#555"
        )
        self.format_menu.pack(side="left", expand=True, fill="x", padx=10)

        # 3.2 Save Path
        self.save_path_var = ctk.StringVar(value="datasets")
        p_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        p_frame.pack(fill="x", pady=2)
        lbl = ctk.CTkLabel(p_frame, text="Save To Path:", width=100, anchor="w", text_color=TEXT_PRIMARY)
        lbl.pack(side="left", padx=10)
        
        btn = ctk.CTkButton(p_frame, text="Browse", width=60, height=28, fg_color="#444", hover_color="#555", command=self._browse_save_path)
        btn.pack(side="right", padx=10)
        
        entry = ctk.CTkEntry(p_frame, textvariable=self.save_path_var, height=28)
        entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

    def _create_section_label_grid(self, parent, text):
        lbl = ctk.CTkLabel(
            parent, text=text, 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_MUTED
        )
        lbl.pack(fill="x", padx=10, pady=(10, 5), anchor="w")

    def _create_input_grid(self, parent, label_text, placeholder, row_idx, show=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=2)
        
        lbl = ctk.CTkLabel(frame, text=label_text, width=80, anchor="w", text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=12))
        lbl.pack(side="top", anchor="w")
        
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, height=30, show=show)
        entry.pack(side="top", fill="x", pady=(2, 0))
        return entry

    def _create_dropdown_grid(self, parent, label_text, variable, values, row_idx, command=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=2)
        
        lbl = ctk.CTkLabel(frame, text=label_text, width=80, anchor="w", text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=12))
        lbl.pack(side="top", anchor="w")
        
        menu = ctk.CTkOptionMenu(
            frame, variable=variable, values=values, command=command,
            fg_color="#333", button_color="#444", button_hover_color="#555", height=30
        )
        menu.pack(side="top", fill="x", pady=(2, 0))
        return menu

    def _create_help_tab_content(self):
        content_frame = ctk.CTkScrollableFrame(self.help_tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_text = (
            "HOW TO USE THIS SYSTEM\n\n"
            "1. Authentication\n"
            "   - Get your API Key from Roboflow.\n"
            "   - Enter your Workspace ID.\n\n"
            "2. Dynamic Sync\n"
            "   - Click 'Connect & Sync' to load projects.\n"
            "   - Your credentials are auto-saved for the next session.\n\n"
            "3. Selection Flow\n"
            "   - Select a Project to fetch its versions.\n"
            "   - Choose a target Export Format.\n\n"
            "4. Resource Paths\n"
            "   - Files are auto-named with precision timestamps.\n\n"
            "SUPPORTED FORMATS\n"
            "- YOLO v26 (Modern Standard)\n"
            "- YOLO v8/v5 (Legacy Support)\n"
            "- COCO & TFRecord"
        )
        
        lbl = ctk.CTkLabel(
            content_frame, text=help_text, 
            justify="left", font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY, anchor="w", wraplength=550
        )
        lbl.pack(padx=20, pady=20, fill="x")

    def _create_about_tab_content(self):
        content_frame = ctk.CTkFrame(self.about_tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        about_text = (
            "TRAFFIC ROBOFLOW DOWNLOADER\n"
            "Autonomous Data Module v2.9.0\n\n"
            "Designed for AI Traffic Systems.\n"
            "Engineered with CustomTkinter.\n\n"
            "© 2026 HPI AI Core."
        )
        
        lbl = ctk.CTkLabel(
            content_frame, text=about_text, 
            justify="center", font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        lbl.pack(pady=100)

    def _create_log_area(self):
        # Log frame with inset look
        log_container = ctk.CTkFrame(self, fg_color="#12141a", corner_radius=8)
        log_container.grid(row=2, column=0, padx=30, pady=(5, 0), sticky="ew")
        
        self.log_text = ctk.CTkTextbox(
            log_container, height=120, 
            fg_color="transparent", 
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#00ff00"
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self, height=8, fg_color="#333", progress_color=ACCENT_GREEN)
        self.progress_bar.grid(row=3, column=0, padx=30, pady=(5, 5), sticky="ew")
        self.progress_bar.set(0)

    def update_log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def _fetch_projects(self):
        api_key = self.api_entry.get()
        workspace_id = self.workspace_entry.get()

        if not api_key or not workspace_id:
            self._show_notification("warning", "Incomplete Data", "Please enter both API Key and Workspace ID.")
            return

        self.update_log(f"Connecting to {workspace_id}...")
        self.load_btn.configure(state="disabled", text="Connecting...")
        
        def run():
            service = RoboflowService(api_key)
            success, result = service.list_projects(workspace_id)
            if success:
                self._save_config() # Save credentials on success
                self.after(0, lambda: self.status_dot.configure(text_color=ACCENT_GREEN))
            else:
                self.after(0, lambda: self.status_dot.configure(text_color="#e74c3c"))
            self.after(0, lambda: self._update_projects_list(success, result))
        
        threading.Thread(target=run, daemon=True).start()

    def _update_projects_list(self, success, result):
        self.load_btn.configure(state="normal", text="Connect & Sync Repository")
        if success:
            self.project_menu.configure(values=result)
            self.project_var.set(result[0] if result else "No projects found")
            self.update_log(f"Sync complete. {len(result)} projects found.")
            self._fetch_versions(self.project_var.get())
        else:
            self.update_log(f"Error: {result}")
            self._show_notification("error", "Sync Failed", result)

    def _fetch_versions(self, project_id):
        if project_id in ["Select Project...", "No projects found"]:
            return

        api_key = self.api_entry.get()
        workspace_id = self.workspace_entry.get()
        self.update_log(f"Fetching versions for {project_id}...")
        
        def run():
            service = RoboflowService(api_key)
            success, result = service.list_versions(workspace_id, project_id)
            self.after(0, lambda: self._update_versions_list(success, result))
        
        threading.Thread(target=run, daemon=True).start()

    def _update_versions_list(self, success, result):
        if success:
            self.version_menu.configure(values=result)
            self.version_var.set(result[0] if result else "No versions")
            self.update_log(f"Found {len(result)} versions.")
        else:
            self.update_log(f"Fetch Error: {result}")

    def _create_download_button(self):
        self.download_btn = ctk.CTkButton(
            self, text="INITIATE DATASET DOWNLOAD", command=self._on_download_click, 
            height=45, fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER, 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.download_btn.grid(row=4, column=0, padx=30, pady=(10, 20), sticky="ew")

    def _on_download_click(self):
        api_key = self.api_entry.get()
        workspace_id = self.workspace_entry.get()
        project_id = self.project_var.get()
        version = self.version_var.get()
        model_format = self.format_var.get()
        save_path = self.save_path_var.get()

        if project_id in ["Select Project...", "No projects found"] or version in ["Select Version...", "No versions"]:
            self._show_notification("warning", "Selection Missing", "Please select a Project and Version first.")
            return

        self.download_btn.configure(state="disabled", text="DOWNLOADING...")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        thread = threading.Thread(target=self._run_download_process, args=(api_key, workspace_id, project_id, version, model_format, save_path))
        thread.daemon = True
        thread.start()

    def _run_download_process(self, api_key, workspace, project, version, fmt, save_path):
        service = RoboflowService(api_key)
        success, result = service.download_dataset(workspace, project, version, fmt, target_root=save_path, log_callback=self.update_log)
        self.after(0, lambda: self._finalize_download(success, result))

    def _finalize_download(self, success, result):
        self.download_btn.configure(state="normal", text="INITIATE DATASET DOWNLOAD")
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1 if success else 0)
        
        if success:
            self.update_log(f"Success! Saved to {result}")
            self._show_notification("success", "Download Complete", f"Dataset was successfully exported to:\n{result}")
        else:
            self.update_log(f"CRITICAL ERROR: {result}")
            self._show_notification("error", "Download Failed", f"An internal error occurred: {result}")

    def _show_notification(self, type, title, message):
        """Stylish custom notification window."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x220")
        dialog.configure(fg_color="#1a1c23")
        dialog.attributes("-topmost", True)
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (220 // 2)
        dialog.geometry(f"+{x}+{y}")

        icon_color = ACCENT_GREEN if type == "success" else "#e74c3c" if type == "error" else "#f1c40f"
        
        header = ctk.CTkLabel(dialog, text=title.upper(), font=ctk.CTkFont(size=16, weight="bold"), text_color=icon_color)
        header.pack(pady=(20, 10))
        
        msg = ctk.CTkLabel(dialog, text=message, wraplength=350, font=ctk.CTkFont(size=12), text_color=TEXT_PRIMARY)
        msg.pack(pady=5, padx=20)
        
        btn = ctk.CTkButton(dialog, text="DISMISS", fg_color="#333", hover_color="#444", command=dialog.destroy, height=30)
        btn.pack(pady=(15, 10))

    def _browse_save_path(self):
        selected_dir = ctk.filedialog.askdirectory(initialdir=".")
        if selected_dir:
            self.save_path_var.set(selected_dir)

