import os
import sys
import time
import subprocess
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import platform
import re
import webbrowser
import requests
from io import BytesIO
import zipfile
import shutil

class IOSDeviceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("iOS Device Manager")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Check system requirements
        self.check_requirements()
        
        # Device information
        self.device_info = {}
        self.connected_device = None
        self.device_ios_version = None
        
        # Jailbreak tools info
        self.jailbreak_tools = {
            "checkra1n": {
                "description": "Semi-tethered jailbreak for iOS 12.0 - 14.8.1 devices with A7-A11 chips",
                "compatibility": ["12.0", "12.1", "12.2", "12.3", "12.4", "13.0", "13.1", "13.2", "13.3", "13.4", "13.5", "13.6", "13.7", "14.0", "14.1", "14.2", "14.3", "14.4", "14.5", "14.6", "14.7", "14.8", "14.8.1"],
                "devices": ["iPhone 5s", "iPhone 6", "iPhone 6 Plus", "iPhone 6s", "iPhone 6s Plus", "iPhone 7", "iPhone 7 Plus", "iPhone 8", "iPhone 8 Plus", "iPhone X"],
                "url": "https://checkra.in/",
                "type": "External"
            },
            "unc0ver": {
                "description": "Semi-untethered jailbreak for iOS 11.0 - 14.8",
                "compatibility": ["11.0", "11.1", "11.2", "11.3", "11.4", "12.0", "12.1", "12.2", "12.3", "12.4", "13.0", "13.1", "13.2", "13.3", "13.4", "13.5", "13.6", "13.7", "14.0", "14.1", "14.2", "14.3", "14.4", "14.5", "14.6", "14.7", "14.8"],
                "devices": ["All devices up to iPhone 12 Pro Max"],
                "url": "https://unc0ver.dev/",
                "type": "External"
            },
            "Taurine": {
                "description": "Semi-untethered jailbreak for iOS 14.0 - 14.3",
                "compatibility": ["14.0", "14.1", "14.2", "14.3"],
                "devices": ["All devices with A9-A14 chips"],
                "url": "https://taurine.app/",
                "type": "External"
            },
            "palera1n": {
                "description": "Semi-tethered jailbreak for iOS 15.0 - 16.5 on A8-A11 devices",
                "compatibility": ["15.0", "15.1", "15.2", "15.3", "15.4", "15.5", "15.6", "15.7", "16.0", "16.1", "16.2", "16.3", "16.4", "16.5"],
                "devices": ["iPhone 6s", "iPhone 6s Plus", "iPhone 7", "iPhone 7 Plus", "iPhone 8", "iPhone 8 Plus", "iPhone X"],
                "url": "https://palera.in/",
                "type": "External"
            },
            "Dopamine": {
                "description": "Semi-untethered jailbreak for iOS 15.0 - 16.6.1 on A12-A17",
                "compatibility": ["15.0", "15.1", "15.2", "15.3", "15.4", "15.5", "15.6", "15.7", "16.0", "16.1", "16.2", "16.3", "16.4", "16.5", "16.6", "16.6.1"],
                "devices": ["iPhone XS and newer"],
                "url": "https://ellekit.space/dopamine/",
                "type": "External"
            },
            "RootlessJB4": {
                "description": "Rootless jailbreak for iOS 12.0 - 12.4.9",
                "compatibility": ["12.0", "12.1", "12.2", "12.3", "12.4", "12.4.1", "12.4.2", "12.4.3", "12.4.4", "12.4.5", "12.4.6", "12.4.7", "12.4.8", "12.4.9"],
                "devices": ["A7-A11 devices"],
                "url": "https://github.com/sbingner/rootlessjb4",
                "type": "External"
            }
        }
        
        # Create UI
        self.create_ui()
        
        # Start device detection
        self.start_device_detection()
    
    def check_requirements(self):
        """Check if libimobiledevice is installed"""
        try:
            subprocess.run(["idevice_id", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            messagebox.showerror("Missing Dependency", 
                                "libimobiledevice is required but not found.\n\n"
                                "Please install it using:\n"
                                "macOS: brew install libimobiledevice\n"
                                "Linux: sudo apt-get install libimobiledevice-utils\n"
                                "Windows: Install iTunes or libimobiledevice")
            sys.exit(1)
    
    def create_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Device info and controls
        left_panel = ttk.LabelFrame(main_frame, text="Device")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Device image placeholder
        self.device_image_label = ttk.Label(left_panel, text="No device connected")
        self.device_image_label.pack(pady=10)
        
        # Device info frame
        info_frame = ttk.LabelFrame(left_panel, text="Device Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Device info labels
        self.device_name_label = ttk.Label(info_frame, text="Name: Not connected")
        self.device_name_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.device_model_label = ttk.Label(info_frame, text="Model: Not connected")
        self.device_model_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.device_ios_label = ttk.Label(info_frame, text="iOS Version: Not connected")
        self.device_ios_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.device_serial_label = ttk.Label(info_frame, text="Serial: Not connected")
        self.device_serial_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.device_battery_label = ttk.Label(info_frame, text="Battery: Not connected")
        self.device_battery_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Jailbreak status
        self.jb_status_label = ttk.Label(info_frame, text="Jailbreak Status: Unknown")
        self.jb_status_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Action buttons
        actions_frame = ttk.LabelFrame(left_panel, text="Actions")
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.refresh_btn = ttk.Button(actions_frame, text="Refresh", command=self.refresh_device_info)
        self.refresh_btn.pack(fill=tk.X, padx=5, pady=5)
        
        self.restart_btn = ttk.Button(actions_frame, text="Restart Device", command=self.restart_device)
        self.restart_btn.pack(fill=tk.X, padx=5, pady=5)
        
        self.screenshot_btn = ttk.Button(actions_frame, text="Take Screenshot", command=self.take_screenshot)
        self.screenshot_btn.pack(fill=tk.X, padx=5, pady=5)
        
        self.backup_btn = ttk.Button(actions_frame, text="Backup Device", command=self.backup_device)
        self.backup_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Right tabbed panel
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tab_control = ttk.Notebook(right_panel)
        
        # File System tab
        file_tab = ttk.Frame(tab_control)
        tab_control.add(file_tab, text="File System")
        
        file_frame = ttk.Frame(file_tab)
        file_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        file_controls = ttk.Frame(file_frame)
        file_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_controls, text="Upload File", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_controls, text="Download Selected", command=self.download_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_controls, text="Delete Selected", command=self.delete_file).pack(side=tk.LEFT, padx=5)
        
        # Path navigation
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Path:").pack(side=tk.LEFT, padx=5)
        self.path_var = tk.StringVar(value="/")
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(path_frame, text="Go", command=self.navigate_path).pack(side=tk.LEFT, padx=5)
        
        # File treeview
        file_tree_frame = ttk.Frame(file_frame)
        file_tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.file_tree = ttk.Treeview(file_tree_frame, columns=("size", "modified"), show="headings")
        self.file_tree.heading("size", text="Size")
        self.file_tree.heading("modified", text="Modified")
        
        scrollbar = ttk.Scrollbar(file_tree_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Apps tab
        apps_tab = ttk.Frame(tab_control)
        tab_control.add(apps_tab, text="Applications")
        
        apps_frame = ttk.Frame(apps_tab)
        apps_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        apps_control = ttk.Frame(apps_frame)
        apps_control.pack(fill=tk.X, pady=5)
        
        ttk.Button(apps_control, text="Refresh Apps", command=self.refresh_apps).pack(side=tk.LEFT, padx=5)
        ttk.Button(apps_control, text="Install IPA", command=self.install_ipa).pack(side=tk.LEFT, padx=5)
        ttk.Button(apps_control, text="Uninstall Selected", command=self.uninstall_app).pack(side=tk.LEFT, padx=5)
        
        # Apps treeview
        apps_tree_frame = ttk.Frame(apps_frame)
        apps_tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.apps_tree = ttk.Treeview(apps_tree_frame, columns=("bundle", "version"), show="headings")
        self.apps_tree.heading("bundle", text="Bundle ID")
        self.apps_tree.heading("version", text="Version")
        
        apps_scrollbar = ttk.Scrollbar(apps_tree_frame, orient="vertical", command=self.apps_tree.yview)
        self.apps_tree.configure(yscrollcommand=apps_scrollbar.set)
        
        self.apps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        apps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Logs tab
        logs_tab = ttk.Frame(tab_control)
        tab_control.add(logs_tab, text="Logs")
        
        logs_frame = ttk.Frame(logs_tab)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        logs_control = ttk.Frame(logs_frame)
        logs_control.pack(fill=tk.X, pady=5)
        
        ttk.Button(logs_control, text="Start Logging", command=self.start_logging).pack(side=tk.LEFT, padx=5)
        ttk.Button(logs_control, text="Stop Logging", command=self.stop_logging).pack(side=tk.LEFT, padx=5)
        ttk.Button(logs_control, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        
        # Log text area
        self.log_text = tk.Text(logs_frame, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Jailbreak tab
        jailbreak_tab = ttk.Frame(tab_control)
        tab_control.add(jailbreak_tab, text="Jailbreak")
        
        self.create_jailbreak_tab(jailbreak_tab)
        
        # Add the notebook to the UI
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_jailbreak_tab(self, parent):
        """Create the jailbreak tab UI"""
        # Main frame for jailbreak tab
        jailbreak_frame = ttk.Frame(parent)
        jailbreak_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Split into two frames: top (compatibility) and bottom (tools)
        top_frame = ttk.LabelFrame(jailbreak_frame, text="Jailbreak Compatibility")
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Compatibility information
        self.compatibility_text = scrolledtext.ScrolledText(top_frame, height=4, wrap=tk.WORD)
        self.compatibility_text.pack(fill=tk.X, padx=5, pady=5)
        self.compatibility_text.insert(tk.END, "Connect a device to see compatible jailbreak tools.")
        self.compatibility_text.config(state=tk.DISABLED)
        
        # Bottom frame for jailbreak tools
        bottom_frame = ttk.LabelFrame(jailbreak_frame, text="Available Jailbreak Tools")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Jailbreak tools list
        tools_frame = ttk.Frame(bottom_frame)
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Jailbreak tools treeview
        self.jb_tools_tree = ttk.Treeview(tools_frame, columns=("description", "compatibility", "type"), show="headings")
        self.jb_tools_tree.heading("description", text="Description")
        self.jb_tools_tree.heading("compatibility", text="iOS Compatibility")
        self.jb_tools_tree.heading("type", text="Type")
        
        self.jb_tools_tree.column("description", width=300)
        self.jb_tools_tree.column("compatibility", width=150)
        self.jb_tools_tree.column("type", width=80)
        
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=self.jb_tools_tree.yview)
        self.jb_tools_tree.configure(yscrollcommand=tools_scrollbar.set)
        
        self.jb_tools_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tools_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tool details frame
        details_frame = ttk.LabelFrame(bottom_frame, text="Tool Details")
        details_frame.pack(fill=tk.X, pady=5)
        
        self.tool_details_text = scrolledtext.ScrolledText(details_frame, height=5, wrap=tk.WORD)
        self.tool_details_text.pack(fill=tk.X, padx=5, pady=5)
        self.tool_details_text.insert(tk.END, "Select a tool to see details.")
        self.tool_details_text.config(state=tk.DISABLED)
        
        # Action buttons
        action_frame = ttk.Frame(bottom_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.download_jb_btn = ttk.Button(action_frame, text="Download Selected Tool", command=self.download_jb_tool)
        self.download_jb_btn.pack(side=tk.LEFT, padx=5)
        
        self.install_jb_btn = ttk.Button(action_frame, text="Install Selected Tool", command=self.install_jb_tool)
        self.install_jb_btn.pack(side=tk.LEFT, padx=5)
        
        self.run_jb_btn = ttk.Button(action_frame, text="Run Jailbreak", command=self.run_jailbreak)
        self.run_jb_btn.pack(side=tk.LEFT, padx=5)
        
        self.jb_progress = ttk.Progressbar(action_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.jb_progress.pack(side=tk.RIGHT, padx=5)
        
        # Bind selection event to show details
        self.jb_tools_tree.bind("<<TreeviewSelect>>", self.show_jb_tool_details)
        
        # Initial population of jailbreak tools
        self.populate_jailbreak_tools()
    
    def populate_jailbreak_tools(self):
        """Populate the jailbreak tools list"""
        # Clear existing items
        for item in self.jb_tools_tree.get_children():
            self.jb_tools_tree.delete(item)
        
        # Add jailbreak tools to the tree
        for tool_name, tool_info in self.jailbreak_tools.items():
            # Format iOS versions range for display
            ios_range = f"{tool_info['compatibility'][0]} - {tool_info['compatibility'][-1]}"
            
            self.jb_tools_tree.insert("", "end", 
                                      text=tool_name, 
                                      values=(tool_info["description"], 
                                              ios_range, 
                                              tool_info["type"]))
    
    def show_jb_tool_details(self, event):
        """Show details of the selected jailbreak tool"""
        selected = self.jb_tools_tree.selection()
        if not selected:
            return
        
        tool_name = self.jb_tools_tree.item(selected[0], "text")
        tool_info = self.jailbreak_tools.get(tool_name)
        
        if tool_info:
            self.tool_details_text.config(state=tk.NORMAL)
            self.tool_details_text.delete(1.0, tk.END)
            
            details = f"Tool: {tool_name}\n\n"
            details += f"Description: {tool_info['description']}\n\n"
            details += f"Compatible iOS: {', '.join(tool_info['compatibility'])}\n\n"
            details += f"Compatible Devices: {', '.join(tool_info['devices'])}\n\n"
            details += f"URL: {tool_info['url']}\n"
            
            self.tool_details_text.insert(tk.END, details)
            self.tool_details_text.config(state=tk.DISABLED)
    
    def update_jailbreak_compatibility(self):
        """Update jailbreak compatibility information based on connected device"""
        if not self.connected_device or not self.device_ios_version:
            return
        
        compatible_tools = []
        
        # Find compatible tools for current iOS version
        for tool_name, tool_info in self.jailbreak_tools.items():
            if self.device_ios_version in tool_info["compatibility"]:
                compatible_tools.append(tool_name)
        
        # Update compatibility text
        self.compatibility_text.config(state=tk.NORMAL)
        self.compatibility_text.delete(1.0, tk.END)
        
        if compatible_tools:
            self.compatibility_text.insert(tk.END, f"Compatible jailbreak tools for iOS {self.device_ios_version}:\n")
            self.compatibility_text.insert(tk.END, ", ".join(compatible_tools))
        else:
            self.compatibility_text.insert(tk.END, f"No known compatible jailbreak tools for iOS {self.device_ios_version}.")
        
        self.compatibility_text.config(state=tk.DISABLED)
    
    def check_jailbreak_status(self):
        """Check if the connected device is jailbroken"""
        if not self.connected_device:
            return False
        
        try:
            # Try to check for common jailbreak indicators
            result = subprocess.run(["ideviceinfo", "-k", "ProductVersion"], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            
            # Try to access Cydia app info (will fail if not jailbroken)
            cydia_check = subprocess.run(["ideviceinstaller", "-l", "-o", "xml"], 
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            
            jailbroken = "cydia" in cydia_check.stdout.lower() or "sileo" in cydia_check.stdout.lower()
            
            self.jb_status_label.config(text=f"Jailbreak Status: {'Jailbroken' if jailbroken else 'Not Jailbroken'}")
            return jailbroken
            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            self.jb_status_label.config(text="Jailbreak Status: Unknown")
            return False
    
    def download_jb_tool(self):
        """Download selected jailbreak tool"""
        selected = self.jb_tools_tree.selection()
        if not selected:
            messagebox.showinfo("Select Tool", "Please select a jailbreak tool to download")
            return
        
        tool_name = self.jb_tools_tree.item(selected[0], "text")
        tool_info = self.jailbreak_tools.get(tool_name)
        
        if tool_info:
            # Open tool website in browser
            webbrowser.open(tool_info["url"])
            self.status_var.set(f"Opening {tool_name} website for download...")
    
    def install_jb_tool(self):
        """Install selected jailbreak tool"""
        selected = self.jb_tools_tree.selection()
        if not selected:
            messagebox.showinfo("Select Tool", "Please select a jailbreak tool to install")
            return
        
        tool_name = self.jb_tools_tree.item(selected[0], "text")
        
        # Ask for the tool file location
        file_path = filedialog.askopenfilename(
            title=f"Select {tool_name} File",
            filetypes=[("All Files", "*.*"), ("ZIP Files", "*.zip"), ("IPA Files", "*.ipa"), ("DMG Files", "*.dmg")]
        )
        
        if not file_path:
            return
        
        # Get destination directory
        install_dir = os.path.join(os.path.expanduser("~"), "iOSDeviceManager", "JailbreakTools", tool_name)
        
        try:
            # Create directories if they don't exist
            os.makedirs(install_dir, exist_ok=True)
            
            # Set progress bar
            self.jb_progress["value"] = 0
            self.root.update_idletasks()
            
            # Handle different file types
            if file_path.lower().endswith(".zip"):
                # Extract zip file
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    total_files = len(zip_ref.namelist())
                    for i, member in enumerate(zip_ref.namelist()):
                        zip_ref.extract(member, install_dir)
                        self.jb_progress["value"] = (i + 1) / total_files * 100
                        self.root.update_idletasks()
                
                self.status_var.set(f"{tool_name} installed successfully to {install_dir}")
            else:
                # Copy the file directly
                dest_file = os.path.join(install_dir, os.path.basename(file_path))
                shutil.copy2(file_path, dest_file)
                
                # For DMG files on macOS, mount them
                if file_path.lower().endswith(".dmg") and platform.system() == "Darwin":
                    subprocess.run(["hdiutil", "attach", dest_file])
                
                self.jb_progress["value"] = 100
                self.status_var.set(f"{tool_name} installed successfully to {install_dir}")
        
        except Exception as e:
            self.status_var.set(f"Error installing {tool_name}: {e}")
    
    def run_jailbreak(self):
        """Run the selected jailbreak tool"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        selected = self.jb_tools_tree.selection()
        if not selected:
            messagebox.showinfo("Select Tool", "Please select a jailbreak tool to run")
            return
        
        tool_name = self.jb_tools_tree.item(selected[0], "text")
        
        # Path to the installed jailbreak tool
        install_dir = os.path.join(os.path.expanduser("~"), "iOSDeviceManager", "JailbreakTools", tool_name)
        
        if not os.path.exists(install_dir):
            messagebox.showinfo("Tool Not Installed", 
                               f"{tool_name} is not installed. Please install it first.")
            return
        
        try:
            # Different handling for different tools
            if tool_name == "checkra1n":
                if platform.system() == "Darwin":  # macOS
                    # Find the checkra1n app
                    app_path = None
                    for root, dirs, files in os.walk(install_dir):
                        for dir in dirs:
                            if dir.endswith(".app"):
                                app_path = os.path.join(root, dir)
                                break
                    
                    if app_path:
                        subprocess.Popen(["open", app_path])
                        self.status_var.set(f"Launched {tool_name}")
                    else:
                        messagebox.showinfo("App Not Found", f"Could not find {tool_name} application")
                else:
                    # Find executable
                    exe_path = None
                    for root, dirs, files in os.walk(install_dir):
                        for file in files:
                            if file.lower() == "checkra1n" or file.lower() == "checkra1n.exe":
                                exe_path = os.path.join(root, file)
                                break
                    
                    if exe_path:
                        if platform.system() == "Windows":
                            subprocess.Popen([exe_path])
                        else:  # Linux
                            subprocess.Popen(["sudo", exe_path])
                        self.status_var.set(f"Launched {tool_name}")
                    else:
                        messagebox.showinfo("Executable Not Found", f"Could not find {tool_name} executable")
            
            elif tool_name in ["unc0ver", "Taurine", "Dopamine"]:
                # These tools are usually installed on the device via AltStore or similar
                messagebox.showinfo("Installation Instructions", 
                                    f"{tool_name} needs to be installed directly on the device via AltStore, Sideloadly, or similar tools.\n\n"
                                    "Please refer to the documentation for detailed instructions.")
                
                # Open the URL in browser
                webbrowser.open(self.jailbreak_tools[tool_name]["url"])
                self.status_var.set(f"Opened {tool_name} website for installation instructions")
            
            elif tool_name == "palera1n":
                # Usually run from terminal on computer
                if platform.system() in ["Darwin", "Linux"]:
                    terminal_cmd = "open -a Terminal" if platform.system() == "Darwin" else "x-terminal-emulator"
                    script_path = os.path.join(install_dir, "palera1n.sh")
                    
                    if os.path.exists(script_path):
                        subprocess.Popen([terminal_cmd, script_path])
                        self.status_var.set(f"Launched {tool_name} in terminal")
                    else:
                        messagebox.showinfo("Script Not Found", 
                                            f"Could not find {tool_name} script. Please ensure it's properly installed.")
                else:
                    messagebox.showinfo("Platform Not Supported", 
                                        f"{tool_name} is not supported on Windows. Please use macOS or Linux.")
            
            else:
                messagebox.showinfo("Not Implemented", 
                                  f"Running {tool_name} is not yet implemented in this application.")
        
        except Exception as e:
            self.status_var.set(f"Error running {tool_name}: {e}")
    
    def start_device_detection(self):
        """Start the device detection thread"""
        self.detection_running = True
        self.detection_thread = threading.Thread(target=self.device_detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
    
    def device_detection_loop(self):
        """Loop to detect connected devices"""
        while self.detection_running:
            try:
                # Run idevice_id to get list of connected devices
                result = subprocess.run(["idevice_id", "-l"], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
                
                devices = [device.strip() for device in result.stdout.split("\n") if device.strip()]
                
                if devices and (not self.connected_device or self.connected_device not in devices):
                    # New device connected
                    self.connected_device = devices[0]  # Take the first device
                    self.refresh_device_info()
                elif not devices and self.connected_device:
                    # Device disconnected
                    self.connected_device = None
                    self.update_ui_for_disconnected_device()
            
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                if self.connected_device:
                    # Error occurred, assume device disconnected
                    self.connected_device = None
                    self.update_ui_for_disconnected_device()
            
            # Sleep before checking again
            time.sleep(2)
    
    def update_ui_for_disconnected_device(self):
        """Update UI elements when device is disconnected"""
        self.device_name_label.config(text="Name: Not connected")
        self.device_model_label.config(text="Model: Not connected")
        self.device_ios_label.config(text="iOS Version: Not connected")
        self.device_serial_label.config(text="Serial: Not connected")
        self.device_battery_label.config(text="Battery: Not connected")
        self.jb_status_label.config(text="Jailbreak Status: Unknown")
        
        # Clear file listings
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Clear app listings
        for item in self.apps_tree.get_children():
            self.apps_tree.delete(item)
        
        # Reset compatibility text
        self.compatibility_text.config(state=tk.NORMAL)
        self.compatibility_text.delete(1.0, tk.END)
        self.compatibility_text.insert(tk.END, "Connect a device to see compatible jailbreak tools.")
        self.compatibility_text.config(state=tk.DISABLED)
        
        # Update status
        self.status_var.set("Device disconnected")
    
    def refresh_device_info(self):
        """Refresh connected device information"""
        if not self.connected_device:
            return
        
        try:
            # Get device info using ideviceinfo
            device_info = {}
            result = subprocess.run(["ideviceinfo", "-s"], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            
            for line in result.stdout.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    device_info[key.strip()] = value.strip()
            
            # Update device info
            self.device_info = device_info
            
            # Update UI with device info
            device_name = device_info.get("DeviceName", "Unknown")
            self.device_name_label.config(text=f"Name: {device_name}")
            
            device_model = device_info.get("ProductType", "Unknown")
            self.device_model_label.config(text=f"Model: {device_model}")
            
            ios_version = device_info.get("ProductVersion", "Unknown")
            self.device_ios_version = ios_version
            self.device_ios_label.config(text=f"iOS Version: {ios_version}")
            
            serial = device_info.get("SerialNumber", "Unknown")
            self.device_serial_label.config(text=f"Serial: {serial}")
            
            # Get battery level
            try:
                battery_result = subprocess.run(["ideviceinfo", "-q", "com.apple.mobile.battery"], 
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
                
                battery_level = "Unknown"
                battery_state = "Unknown"
                
                for line in battery_result.stdout.split("\n"):
                    if "BatteryCurrentCapacity:" in line:
                        battery_level = line.split(":", 1)[1].strip()
                    elif "BatteryIsCharging:" in line:
                        charging = line.split(":", 1)[1].strip()
                        battery_state = "Charging" if charging == "true" else "Not Charging"
                
                self.device_battery_label.config(text=f"Battery: {battery_level}% ({battery_state})")
            except:
                self.device_battery_label.config(text="Battery: Unknown")
            
            # Check jailbreak status
            self.check_jailbreak_status()
            
            # Update jailbreak compatibility
            self.update_jailbreak_compatibility()
            
            # Update status
            self.status_var.set(f"Connected to {device_name}")
            
            # Try to get device image (not always available)
            self.load_device_image(device_model)
            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.status_var.set(f"Error getting device info: {e}")
    
    def load_device_image(self, model_identifier):
        """Load and display device image based on model identifier"""
        # Map of model identifiers to common names
        device_images = {
            # iPhones
            "iPhone8,1": "iPhone 6s",
            "iPhone8,2": "iPhone 6s Plus",
            "iPhone9,1": "iPhone 7",
            "iPhone9,3": "iPhone 7",
            "iPhone9,2": "iPhone 7 Plus",
            "iPhone9,4": "iPhone 7 Plus",
            "iPhone10,1": "iPhone 8",
            "iPhone10,4": "iPhone 8",
            "iPhone10,2": "iPhone 8 Plus",
            "iPhone10,5": "iPhone 8 Plus",
            "iPhone10,3": "iPhone X",
            "iPhone10,6": "iPhone X",
            "iPhone11,2": "iPhone XS",
            "iPhone11,4": "iPhone XS Max",
            "iPhone11,6": "iPhone XS Max",
            "iPhone11,8": "iPhone XR",
            "iPhone12,1": "iPhone 11",
            "iPhone12,3": "iPhone 11 Pro",
            "iPhone12,5": "iPhone 11 Pro Max",
            "iPhone13,1": "iPhone 12 mini",
            "iPhone13,2": "iPhone 12",
            "iPhone13,3": "iPhone 12 Pro",
            "iPhone13,4": "iPhone 12 Pro Max",
            "iPhone14,2": "iPhone 13 Pro",
            "iPhone14,3": "iPhone 13 Pro Max",
            "iPhone14,4": "iPhone 13 mini",
            "iPhone14,5": "iPhone 13",
            "iPhone14,6": "iPhone SE (3rd gen)",
            "iPhone14,7": "iPhone 14",
            "iPhone14,8": "iPhone 14 Plus",
            "iPhone15,2": "iPhone 14 Pro",
            "iPhone15,3": "iPhone 14 Pro Max",
            "iPhone15,4": "iPhone 15",
            "iPhone15,5": "iPhone 15 Plus",
            "iPhone16,1": "iPhone 15 Pro",
            "iPhone16,2": "iPhone 15 Pro Max",
            
            # iPads
            "iPad5,1": "iPad mini 4",
            "iPad5,2": "iPad mini 4",
            "iPad5,3": "iPad Air 2",
            "iPad5,4": "iPad Air 2",
            "iPad6,3": "iPad Pro (9.7-inch)",
            "iPad6,4": "iPad Pro (9.7-inch)",
            "iPad6,7": "iPad Pro (12.9-inch)",
            "iPad6,8": "iPad Pro (12.9-inch)",
            "iPad6,11": "iPad (5th gen)",
            "iPad6,12": "iPad (5th gen)",
            "iPad7,1": "iPad Pro (12.9-inch) (2nd gen)",
            "iPad7,2": "iPad Pro (12.9-inch) (2nd gen)",
            "iPad7,3": "iPad Pro (10.5-inch)",
            "iPad7,4": "iPad Pro (10.5-inch)",
            "iPad7,5": "iPad (6th gen)",
            "iPad7,6": "iPad (6th gen)",
            "iPad7,11": "iPad (7th gen)",
            "iPad7,12": "iPad (7th gen)",
            "iPad8,1": "iPad Pro (11-inch)",
            "iPad8,2": "iPad Pro (11-inch)",
            "iPad8,3": "iPad Pro (11-inch)",
            "iPad8,4": "iPad Pro (11-inch)",
            "iPad8,5": "iPad Pro (12.9-inch) (3rd gen)",
            "iPad8,6": "iPad Pro (12.9-inch) (3rd gen)",
            "iPad8,7": "iPad Pro (12.9-inch) (3rd gen)",
            "iPad8,8": "iPad Pro (12.9-inch) (3rd gen)",
            "iPad8,9": "iPad Pro (11-inch) (2nd gen)",
            "iPad8,10": "iPad Pro (11-inch) (2nd gen)",
            "iPad8,11": "iPad Pro (12.9-inch) (4th gen)",
            "iPad8,12": "iPad Pro (12.9-inch) (4th gen)",
            "iPad11,1": "iPad mini (5th gen)",
            "iPad11,2": "iPad mini (5th gen)",
            "iPad11,3": "iPad Air (3rd gen)",
            "iPad11,4": "iPad Air (3rd gen)",
            "iPad11,6": "iPad (8th gen)",
            "iPad11,7": "iPad (8th gen)",
            "iPad12,1": "iPad (9th gen)",
            "iPad12,2": "iPad (9th gen)",
            "iPad13,1": "iPad Air (4th gen)",
            "iPad13,2": "iPad Air (4th gen)",
            "iPad13,4": "iPad Pro (11-inch) (3rd gen)",
            "iPad13,5": "iPad Pro (11-inch) (3rd gen)",
            "iPad13,6": "iPad Pro (11-inch) (3rd gen)",
            "iPad13,7": "iPad Pro (11-inch) (3rd gen)",
            "iPad13,8": "iPad Pro (12.9-inch) (5th gen)",
            "iPad13,9": "iPad Pro (12.9-inch) (5th gen)",
            "iPad13,10": "iPad Pro (12.9-inch) (5th gen)",
            "iPad13,11": "iPad Pro (12.9-inch) (5th gen)",
            "iPad13,16": "iPad Air (5th gen)",
            "iPad13,17": "iPad Air (5th gen)",
            "iPad13,18": "iPad (10th gen)",
            "iPad13,19": "iPad (10th gen)",
            "iPad14,1": "iPad mini (6th gen)",
            "iPad14,2": "iPad mini (6th gen)",
            "iPad14,3": "iPad Pro (11-inch) (4th gen)",
            "iPad14,4": "iPad Pro (11-inch) (4th gen)",
            "iPad14,5": "iPad Pro (12.9-inch) (6th gen)",
            "iPad14,6": "iPad Pro (12.9-inch) (6th gen)"
        }
        
        # Get friendly name
        device_name = device_images.get(model_identifier, "Generic iOS Device")
        
        # Try to load image from web (placeholder implementation)
        try:
            # For now just display text, in a real app you'd fetch the image
            self.device_image_label.config(text=f"{device_name}")
        except Exception as e:
            self.device_image_label.config(text=f"{device_name}")
    
    def restart_device(self):
        """Restart the connected device"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        if messagebox.askyesno("Restart Device", "Are you sure you want to restart the device?"):
            try:
                # This is a sample; actual restart would use a different command
                subprocess.run(["idevicediagnostics", "restart"], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
                self.status_var.set("Device restart command sent")
            except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                self.status_var.set(f"Error restarting device: {e}")
    
    def take_screenshot(self):
        """Take a screenshot of the device"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        try:
            # Create a temporary file
            temp_file = os.path.join(os.path.expanduser("~"), "screenshot.png")
            
            # Take screenshot using idevicescreenshot
            subprocess.run(["idevicescreenshot", temp_file], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            
            # Ask where to save the screenshot
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialfile="ios_screenshot.png"
            )
            
            if save_path:
                # Move the temp file to the selected location
                shutil.move(temp_file, save_path)
                self.status_var.set(f"Screenshot saved to {save_path}")
            else:
                # Delete the temp file if user cancelled
                os.remove(temp_file)
        
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.status_var.set(f"Error taking screenshot: {e}")
    
    def backup_device(self):
        """Create a backup of the device"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        # Ask for backup location
        backup_dir = filedialog.askdirectory(
            title="Select Backup Location"
        )
        
        if not backup_dir:
            return
        
        try:
            # Start backup process
            self.status_var.set("Starting backup... This may take a while")
            self.root.update_idletasks()
            
            # Run the backup command
            backup_process = subprocess.Popen(
                ["idevicebackup2", "backup", "--full", backup_dir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            # Show progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Backup Progress")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            ttk.Label(progress_window, text="Backing up device...").pack(pady=10)
            progress = ttk.Progressbar(progress_window, mode="indeterminate")
            progress.pack(fill=tk.X, padx=20, pady=10)
            progress.start()
            
            log_text = scrolledtext.ScrolledText(progress_window, height=5)
            log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
            
            # Function to read output and update progress
            def read_output():
                while backup_process.poll() is None:
                    output = backup_process.stdout.readline()
                    if output:
                        log_text.insert(tk.END, output)
                        log_text.see(tk.END)
                        self.root.update_idletasks()
                
                # Process completed
                progress.stop()
                
                # Get final output and error
                output, error = backup_process.communicate()
                if output:
                    log_text.insert(tk.END, output)
                
                if error:
                    log_text.insert(tk.END, f"\nError: {error}")
                
                # Change the progress dialog to a completion dialog
                progress.pack_forget()
                ttk.Button(progress_window, text="Close", command=progress_window.destroy).pack(pady=10)
                
                if backup_process.returncode == 0:
                    self.status_var.set("Backup completed successfully")
                else:
                    self.status_var.set(f"Backup failed with code {backup_process.returncode}")
            
            # Start the output reading thread
            threading.Thread(target=read_output, daemon=True).start()
            
        except Exception as e:
            self.status_var.set(f"Error starting backup: {e}")
    
    def navigate_path(self):
        """Navigate to the specified path on the device"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        path = self.path_var.get()
        self.list_files(path)
    
    def list_files(self, path):
        """List files at the specified path on the device"""
        if not self.connected_device:
            return
        
        try:
            # Clear existing items
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # Use sftp-server or AFC to list files (simplified example)
            # This is a placeholder - real implementation would use libimobiledevice's tools
            result = subprocess.run(["idevicefs", "-u", self.connected_device, "ls", "-la", path], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            
            if result.returncode != 0:
                self.status_var.set(f"Error listing files: {result.stderr}")
                return
            
            # Parse output and add to tree
            for line in result.stdout.split("\n"):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 9:
                        permissions = parts[0]
                        size = parts[4]
                        date = f"{parts[5]} {parts[6]} {parts[7]}"
                        name = " ".join(parts[8:])
                        
                        self.file_tree.insert("", "end", text=name, values=(size, date))
            
            self.status_var.set(f"Listed files at {path}")
        
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.status_var.set(f"Error listing files: {e}")
    
    def upload_file(self):
        """Upload a file to the device"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        # Ask for file to upload
        file_path = filedialog.askopenfilename(
            title="Select File to Upload"
        )
        
        if not file_path:
            return
        
        try:
            # Get destination path
            dest_path = self.path_var.get()
            file_name = os.path.basename(file_path)
            
            # Use sftp-server or AFC to upload file (simplified example)
            result = subprocess.run(["idevicefs", "-u", self.connected_device, "put", file_path, f"{dest_path}/{file_name}"], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            
            if result.returncode == 0:
                self.status_var.set(f"Uploaded {file_name} to {dest_path}")
                # Refresh file listing
                self.list_files(dest_path)
            else:
                self.status_var.set(f"Error uploading file: {result.stderr}")
        
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.status_var.set(f"Error uploading file: {e}")
    
    def download_file(self):
        """Download a selected file from the device"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        # Get selected file
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a file to download")
            return
        
        file_name = self.file_tree.item(selected[0], "text")
        current_path = self.path_var.get()
        source_path = f"{current_path}/{file_name}"
        
        # Ask where to save the file
        save_path = filedialog.asksaveasfilename(
            defaultextension="",
            initialfile=file_name
        )
        
        if not save_path:
            return
        
        try:
            # Use sftp-server or AFC to download file (simplified example)
            result = subprocess.run(["idevicefs", "-u", self.connected_device, "get", source_path, save_path], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            
            if result.returncode == 0:
                self.status_var.set(f"Downloaded {file_name} to {save_path}")
            else:
                self.status_var.set(f"Error downloading file: {result.stderr}")
        
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.status_var.set(f"Error downloading file: {e}")
    
    def delete_file(self):
        """Delete a selected file from the device"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        # Get selected file
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a file to delete")
            return
        
        file_name = self.file_tree.item(selected[0], "text")
        current_path = self.path_var.get()
        file_path = f"{current_path}/{file_name}"
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {file_name}?"):
            return
        
        try:
            # Use sftp-server or AFC to delete file (simplified example)
            result = subprocess.run(["idevicefs", "-u", self.connected_device, "rm", file_path], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            
            if result.returncode == 0:
                self.status_var.set(f"Deleted {file_name}")
                # Refresh file listing
                self.list_files(current_path)
            else:
                self.status_var.set(f"Error deleting file: {result.stderr}")
        
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.status_var.set(f"Error deleting file: {e}")
    
    def refresh_apps(self):
        """Refresh the list of installed applications"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        try:
            # Clear existing items
            for item in self.apps_tree.get_children():
                self.apps_tree.delete(item)
            
            # Get list of installed apps
            result = subprocess.run(["ideviceinstaller", "-u", self.connected_device, "-l"], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            
            if result.returncode != 0:
                self.status_var.set(f"Error listing applications: {result.stderr}")
                return
            
            # Parse output and add to tree
            lines = result.stdout.splitlines()
            for line in lines[1:]:  # Skip header line
                if line.strip():
                    parts = line.split(" - ")
                    if len(parts) >= 2:
                        bundle_id = parts[0].strip()
                        app_name = parts[1].strip()
                        version = parts[2].strip() if len(parts) > 2 else "Unknown"
                        
                        self.apps_tree.insert("", "end", text=app_name, values=(bundle_id, version))
            
            self.status_var.set("Application list refreshed")
        
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.status_var.set(f"Error listing applications: {e}")
    
    def install_ipa(self):
        """Install an IPA file on the device"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        # Ask for IPA file
        ipa_path = filedialog.askopenfilename(
            title="Select IPA File",
            filetypes=[("IPA Files", "*.ipa")]
        )
        
        if not ipa_path:
            return
        
        try:
            # Start installation
            self.status_var.set(f"Installing {os.path.basename(ipa_path)}...")
            self.root.update_idletasks()
            
            # Use ideviceinstaller to install the IPA
            process = subprocess.Popen(
                ["ideviceinstaller", "-u", self.connected_device, "-i", ipa_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            # Show progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Installation Progress")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            ttk.Label(progress_window, text=f"Installing {os.path.basename(ipa_path)}...").pack(pady=10)
            progress = ttk.Progressbar(progress_window, mode="indeterminate")
            progress.pack(fill=tk.X, padx=20, pady=10)
            progress.start()
            
            log_text = scrolledtext.ScrolledText(progress_window, height=5)
            log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
            
            # Function to read output and update progress
            def read_output():
                while process.poll() is None:
                    output = process.stdout.readline()
                    if output:
                        log_text.insert(tk.END, output)
                        log_text.see(tk.END)
                        self.root.update_idletasks()
                
                # Process completed
                progress.stop()
                
                # Get final output and error
                output, error = process.communicate()
                if output:
                    log_text.insert(tk.END, output)
                
                if error:
                    log_text.insert(tk.END, f"\nError: {error}")
                
                # Change the progress dialog to a completion dialog
                progress.pack_forget()
                ttk.Button(progress_window, text="Close", command=progress_window.destroy).pack(pady=10)
                
                if process.returncode == 0:
                    self.status_var.set("Installation completed successfully")
                    # Refresh app list
                    self.refresh_apps()
                else:
                    self.status_var.set(f"Installation failed with code {process.returncode}")
            
            # Start the output reading thread
            threading.Thread(target=read_output, daemon=True).start()
            
        except Exception as e:
            self.status_var.set(f"Error installing IPA: {e}")
    
    def uninstall_app(self):
        """Uninstall selected application"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        # Get selected app
        selected = self.apps_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select an app to uninstall")
            return
        
        app_name = self.apps_tree.item(selected[0], "text")
        bundle_id = self.apps_tree.item(selected[0], "values")[0]
        
        if not messagebox.askyesno("Confirm Uninstall", f"Are you sure you want to uninstall {app_name}?"):
            return
        
        try:
            # Use ideviceinstaller to uninstall the app
            result = subprocess.run(["ideviceinstaller", "-u", self.connected_device, "-U", bundle_id], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            
            if result.returncode == 0:
                self.status_var.set(f"Uninstalled {app_name}")
                # Refresh app list
                self.refresh_apps()
            else:
                self.status_var.set(f"Error uninstalling app: {result.stderr}")
        
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.status_var.set(f"Error uninstalling app: {e}")
    
    def start_logging(self):
        """Start device logging"""
        if not self.connected_device:
            messagebox.showinfo("No Device", "No device connected")
            return
        
        # Clear log text
        self.log_text.delete(1.0, tk.END)
        
        # Start log collection in a thread
        self.logging_active = True
        log_thread = threading.Thread(target=self._logging_thread, daemon=True)
        log_thread.start()
        
        self.status_var.set("Logging started")
    
    def _logging_thread(self):
        try:
            process = subprocess.Popen(["idevicesyslog"], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            while self.logging_active:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Update log text in main thread
                self.root.after(0, lambda l=line: self._append_log(l))
            
            # Kill process when stopped
            process.kill()
        except Exception as e:
            self.root.after(0, lambda e=e: self.status_var.set(f"Logging error: {e}"))
    
    def _append_log(self, line):
        """Append line to log text"""
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)
    
    def stop_logging(self):
        """Stop device logging"""
        self.logging_active = False
        self.status_var.set("Logging stopped")
    
    def clear_logs(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Logs cleared")

def main():
    root = tk.Tk()
    app = IOSDeviceManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
