import os
import sys
import subprocess
import platform
import re
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext


class AndroidDeviceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Device Manager")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        self.devices = []
        self.selected_device = None
        self.scrcpy_process = None
        self.recording_process = None
        self.is_recording = False
        
        # Get the script directory to find adb and scrcpy
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check for dependencies
        self.check_dependencies()
        
        # Create the UI
        self.create_ui()
        
        # Refresh device list
        self.refresh_devices()

    def check_dependencies(self):
        # Define commands with paths
        adb_cmd = self.get_adb_path()
        scrcpy_cmd = self.get_scrcpy_path()
        
        try:
            subprocess.run([adb_cmd, "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            messagebox.showerror("Error", f"ADB is not found. Checked at: {adb_cmd}")
            sys.exit(1)

        try:
            subprocess.run([scrcpy_cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            messagebox.showerror("Error", f"scrcpy is not found. Checked at: {scrcpy_cmd}")
            sys.exit(1)

    def get_adb_path(self):
        """Get the ADB path based on whether it's in the same directory as the script or in PATH"""
        # First try in the same directory
        script_dir_adb = os.path.join(self.script_dir, "adb")
        if platform.system() == "Windows":
            script_dir_adb += ".exe"
            
        if os.path.exists(script_dir_adb):
            return script_dir_adb
        
        # Otherwise return just "adb" to use PATH
        return "adb"
        
    def get_scrcpy_path(self):
        """Get the scrcpy path based on whether it's in the same directory as the script or in PATH"""
        # First try in the same directory
        script_dir_scrcpy = os.path.join(self.script_dir, "scrcpy")
        if platform.system() == "Windows":
            script_dir_scrcpy += ".exe"
            
        if os.path.exists(script_dir_scrcpy):
            return script_dir_scrcpy
        
        # Otherwise return just "scrcpy" to use PATH
        return "scrcpy"

    def create_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        main_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(main_frame, text="Device Manager")

        adb_cmd_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(adb_cmd_frame, text="ADB Command Line")

        self.setup_device_manager_tab(main_frame)
        self.setup_adb_cmd_tab(adb_cmd_frame)

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.root.after(5000, self.auto_refresh)

    def setup_device_manager_tab(self, parent):
        devices_frame = ttk.LabelFrame(parent, text="Connected Devices", padding="5")
        devices_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.device_tree = ttk.Treeview(devices_frame, columns=("Name", "Model", "Status"))
        self.device_tree.heading("#0", text="ID")
        self.device_tree.heading("Name", text="Name")
        self.device_tree.heading("Model", text="Model")
        self.device_tree.heading("Status", text="Status")
        self.device_tree.column("#0", width=100)
        self.device_tree.column("Name", width=150)
        self.device_tree.column("Model", width=150)
        self.device_tree.column("Status", width=100)
        self.device_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.device_tree.bind("<<TreeviewSelect>>", self.on_device_selected)

        refresh_button = ttk.Button(devices_frame, text="Refresh Devices", command=self.refresh_devices)
        refresh_button.pack(anchor=tk.W, padx=5, pady=5)

        actions_frame = ttk.LabelFrame(parent, text="Device Actions", padding="5", width=300)
        actions_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        actions_frame.pack_propagate(False)

        self.mirror_button = ttk.Button(actions_frame, text="Start Screen Mirror", command=self.toggle_screen_mirror)
        self.mirror_button.pack(fill=tk.X, padx=5, pady=5)

        self.record_button = ttk.Button(actions_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(actions_frame, text="Install APK", command=self.install_apk).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(actions_frame, text="Uninstall App", command=self.show_uninstall_dialog).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(actions_frame, text="Take Screenshot", command=self.take_screenshot).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(actions_frame, text="Reboot Device", command=self.reboot_device).pack(fill=tk.X, padx=5, pady=5)

        options_frame = ttk.LabelFrame(actions_frame, text="scrcpy Options", padding="5")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(options_frame, text="Maximum Size:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.size_var = tk.StringVar(value="1280")
        ttk.Entry(options_frame, textvariable=self.size_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(options_frame, text="Video Bit Rate (Mbps):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.bitrate_var = tk.StringVar(value="8")
        ttk.Entry(options_frame, textvariable=self.bitrate_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        self.always_on_top_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Always on top", variable=self.always_on_top_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.fullscreen_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Fullscreen", variable=self.fullscreen_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.no_control_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="View Only (No Control)", variable=self.no_control_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

    def setup_adb_cmd_tab(self, parent):
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(top_frame, text="Device:").pack(side=tk.LEFT, padx=(0, 5))
        self.cmd_device_var = tk.StringVar()
        self.cmd_device_dropdown = ttk.Combobox(top_frame, textvariable=self.cmd_device_var, state="readonly", width=30)
        self.cmd_device_dropdown.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(top_frame, text="ADB Command:").pack(side=tk.LEFT, padx=(10, 5))
        self.adb_cmd_var = tk.StringVar()
        self.adb_cmd_entry = ttk.Entry(top_frame, textvariable=self.adb_cmd_var, width=40)
        self.adb_cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.adb_cmd_entry.bind("<Return>", lambda e: self.execute_adb_command())

        ttk.Button(top_frame, text="Execute", command=self.execute_adb_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=5)

        common_cmd_frame = ttk.LabelFrame(parent, text="Common Commands")
        common_cmd_frame.pack(fill=tk.X, padx=5, pady=5)

        common_commands = [
            ("List Packages", "shell pm list packages"),
            ("Device Info", "shell getprop"),
            ("Battery Stats", "shell dumpsys battery"),
            ("List Files in /sdcard", "shell ls -la /sdcard"),
            ("Logcat", "logcat"),
            ("Clear Logcat", "logcat -c")
        ]

        cmd_buttons_frame = ttk.Frame(common_cmd_frame)
        cmd_buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        for i, (label, cmd) in enumerate(common_commands):
            row, col = divmod(i, 3)
            ttk.Button(cmd_buttons_frame, text=label, 
                       command=lambda c=cmd: self.insert_command(c)).grid(
                       row=row, column=col, padx=5, pady=5, sticky=tk.W)

        output_frame = ttk.LabelFrame(parent, text="Command Output")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)

    def insert_command(self, cmd):
        self.adb_cmd_var.set(cmd)

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def update_device_dropdown(self):
        current = self.cmd_device_var.get()

        values = ["All Devices"]
        for device in self.devices:
            values.append(f"{device['id']} ({device['name']})")

        self.cmd_device_dropdown["values"] = values

        if current in values:
            self.cmd_device_var.set(current)
        else:
            self.cmd_device_var.set(values[0] if values else "")

    def execute_adb_command(self):
        cmd = self.adb_cmd_var.get().strip()
        if not cmd:
            messagebox.showwarning("Empty Command", "Please enter an ADB command")
            return

        device_selection = self.cmd_device_var.get()

        adb_cmd = [self.get_adb_path()]

        if device_selection != "All Devices" and device_selection:
            device_id = device_selection.split(" ")[0]                     
            adb_cmd.extend(["-s", device_id])

        adb_cmd.extend(cmd.split())

        self.status_var.set(f"Executing: {' '.join(adb_cmd)}")
        threading.Thread(target=self.run_command, args=(adb_cmd,), daemon=True).start()

    def run_command(self, cmd):
        try:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)

            self.output_text.insert(tk.END, f"$ {' '.join(cmd)}\n\n", "command")
            self.output_text.config(state=tk.DISABLED)

            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                self.root.after(0, self.append_output, line)

            return_code = process.wait()

            completion_msg = f"\n\n--- Command completed with return code: {return_code} ---\n"
            self.root.after(0, self.append_output, completion_msg)
            self.root.after(0, self.status_var.set, "Command completed")

        except Exception as e:
            error_msg = f"\n\nError executing command: {e}\n"
            self.root.after(0, self.append_output, error_msg)
            self.root.after(0, self.status_var.set, "Command failed")

    def append_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)  
        self.output_text.config(state=tk.DISABLED)

    def auto_refresh(self):
        self.refresh_devices(show_message=False)
        self.root.after(5000, self.auto_refresh)

    def refresh_devices(self, show_message=True):
        try:
            self.status_var.set("Refreshing devices...")
            self.root.update_idletasks()

            for item in self.device_tree.get_children():
                self.device_tree.delete(item)

            self.devices = []

            result = subprocess.run(
                [self.get_adb_path(), "devices", "-l"], 
                capture_output=True, 
                text=True, 
                check=True
            )

            lines = result.stdout.strip().split('\n')[1:]              
            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) < 2:
                    continue

                device_id = parts[0]
                status = parts[1]

                if status != "device":
                    self.device_tree.insert("", tk.END, text=device_id, values=("N/A", "N/A", status))
                    continue

                device_name = "Unknown"
                device_model = "Unknown"

                model_match = re.search(r'model:(\S+)', line)
                if model_match:
                    device_model = model_match.group(1)

                try:
                    name_result = subprocess.run(
                        [self.get_adb_path(), "-s", device_id, "shell", "settings", "get", "global", "device_name"],
                        capture_output=True, text=True, check=True
                    )
                    if name_result.stdout.strip():
                        device_name = name_result.stdout.strip()
                except subprocess.SubprocessError:
                    pass

                self.devices.append({"id": device_id, "name": device_name, "model": device_model, "status": status})
                self.device_tree.insert("", tk.END, text=device_id, values=(device_name, device_model, status))

            self.update_device_dropdown()

            if not self.devices and show_message:
                messagebox.showinfo("No Devices", "No Android devices found. Please connect a device.")

            self.status_var.set(f"Found {len(self.devices)} device(s)")

        except subprocess.SubprocessError as e:
            self.status_var.set("Error refreshing devices")
            if show_message:
                messagebox.showerror("Error", f"Failed to get device list: {e}")

    def on_device_selected(self, event):
        selection = self.device_tree.selection()
        if not selection:
            self.selected_device = None
            return

        device_id = self.device_tree.item(selection[0], "text")
        for device in self.devices:
            if device["id"] == device_id:
                self.selected_device = device
                self.status_var.set(f"Selected device: {device['name']} ({device_id})")
                self.cmd_device_var.set(f"{device_id} ({device['name']})")
                return

    def toggle_screen_mirror(self):
        if not self.selected_device:
            messagebox.showerror("Error", "No device selected")
            return

        if self.scrcpy_process and self.scrcpy_process.poll() is None:
            self.scrcpy_process.terminate()
            self.scrcpy_process = None
            self.mirror_button.config(text="Start Screen Mirror")
            self.status_var.set("Screen mirroring stopped")
        else:
            try:
                cmd = [self.get_scrcpy_path(), "-s", self.selected_device["id"]]

                max_size = self.size_var.get().strip()
                if max_size:
                    cmd.extend(["--max-size", max_size])

                bitrate = self.bitrate_var.get().strip()
                if bitrate:
                    bitrate_bps = int(float(bitrate) * 1000000)
                    cmd.extend(["--video-bit-rate", str(bitrate_bps)])

                if self.always_on_top_var.get():
                    cmd.append("--always-on-top")

                if self.fullscreen_var.get():
                    cmd.append("--fullscreen")

                if self.no_control_var.get():
                    cmd.append("--no-control")

                self.scrcpy_process = subprocess.Popen(cmd)
                self.mirror_button.config(text="Stop Screen Mirror")
                self.status_var.set("Screen mirroring started")

            except subprocess.SubprocessError as e:
                messagebox.showerror("Error", f"Failed to start screen mirroring: {e}")

    def toggle_recording(self):
        if not self.selected_device:
            messagebox.showerror("Error", "No device selected")
            return

        if self.is_recording:
            if self.recording_process and self.recording_process.poll() is None:
                self.recording_process.terminate()
                self.recording_process = None
                self.is_recording = False
                self.record_button.config(text="Start Recording")
                self.status_var.set("Recording stopped")
                messagebox.showinfo("Recording Finished", "Screen recording has been saved")
        else:
            try:
                output_file = filedialog.asksaveasfilename(
                    defaultextension=".mp4",
                    filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
                    title="Save Screen Recording As"
                )

                if not output_file:
                    return

                cmd = [self.get_scrcpy_path(), "-s", self.selected_device["id"], "--record", output_file, "--no-display"]

                max_size = self.size_var.get().strip()
                if max_size:
                    cmd.extend(["--max-size", max_size])

                bitrate = self.bitrate_var.get().strip()
                if bitrate:
                    bitrate_bps = int(float(bitrate) * 1000000)
                    cmd.extend(["--video-bit-rate", str(bitrate_bps)])

                self.recording_process = subprocess.Popen(cmd)
                self.is_recording = True
                self.record_button.config(text="Stop Recording")
                self.status_var.set("Recording screen to " + os.path.basename(output_file))

            except subprocess.SubprocessError as e:
                messagebox.showerror("Error", f"Failed to start screen recording: {e}")

    def install_apk(self):
        if not self.selected_device:
            messagebox.showerror("Error", "No device selected")
            return

        apk_file = filedialog.askopenfilename(
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")],
            title="Select APK file to install"
        )

        if not apk_file:
            return

        try:
            self.status_var.set(f"Installing {os.path.basename(apk_file)}...")
            self.root.update_idletasks()

            result = subprocess.run(
                [self.get_adb_path(), "-s", self.selected_device["id"], "install", "-r", apk_file],
                capture_output=True, text=True, check=True
            )

            if "Success" in result.stdout:
                messagebox.showinfo("Success", f"APK installed successfully")
                self.status_var.set("APK installed successfully")
            else:
                messagebox.showwarning("Warning", f"Installation completed but success message not found.\nOutput: {result.stdout}")
                self.status_var.set("APK installation completed")

        except subprocess.SubprocessError as e:
            messagebox.showerror("Error", f"Failed to install APK: {e}")
            self.status_var.set("APK installation failed")

    def show_uninstall_dialog(self):
        if not self.selected_device:
            messagebox.showerror("Error", "No device selected")
            return

        try:
            self.status_var.set("Getting app list...")
            self.root.update_idletasks()

            result = subprocess.run(
                [self.get_adb_path(), "-s", self.selected_device["id"], "shell", "pm", "list", "packages", "-3"],
                capture_output=True, text=True, check=True
            )

            packages = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith("package:"):
                    packages.append(line[8:])                            

            if not packages:
                messagebox.showinfo("No Apps", "No third-party apps found on the device")
                return

            dialog = tk.Toplevel(self.root)
            dialog.title("Uninstall App")
            dialog.geometry("400x400")
            dialog.transient(self.root)
            dialog.grab_set()

            ttk.Label(dialog, text="Select an app to uninstall:").pack(padx=10, pady=10)

            listbox_frame = ttk.Frame(dialog)
            listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            scrollbar = ttk.Scrollbar(listbox_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            package_listbox = tk.Listbox(listbox_frame)
            package_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            package_listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=package_listbox.yview)

            for package in sorted(packages):
                package_listbox.insert(tk.END, package)

            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=10)

            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

            def do_uninstall():
                selection = package_listbox.curselection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select an app to uninstall")
                    return

                package = package_listbox.get(selection[0])

                if messagebox.askyesno("Confirm", f"Are you sure you want to uninstall {package}?"):
                    try:
                        result = subprocess.run(
                            [self.get_adb_path(), "-s", self.selected_device["id"], "uninstall", package],
                            capture_output=True, text=True, check=True
                        )

                        if "Success" in result.stdout:
                            messagebox.showinfo("Success", f"App uninstalled successfully")
                            dialog.destroy()
                            self.status_var.set(f"Uninstalled {package}")
                        else:
                            messagebox.showwarning("Warning", f"Uninstall completed but success message not found.\nOutput: {result.stdout}")

                    except subprocess.SubprocessError as e:
                        messagebox.showerror("Error", f"Failed to uninstall app: {e}")

            ttk.Button(button_frame, text="Uninstall", command=do_uninstall).pack(side=tk.RIGHT, padx=5)

        except subprocess.SubprocessError as e:
            messagebox.showerror("Error", f"Failed to get app list: {e}")

def take_screenshot(self):
    # Check if a device is selected and raise an error if not
    if not self.selected_device:
        messagebox.showerror("Error", "No device selected")
        return
    
    # Make absolutely sure we have a valid device ID before proceeding
    if not self.selected_device or "id" not in self.selected_device:
        messagebox.showerror("Error", "Invalid device selection. Please refresh and select a device.")
        return

    try:
        output_file = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Screenshot As"
        )

        if not output_file:
            return

        self.status_var.set("Taking screenshot...")
        self.root.update_idletasks()

        temp_file = f"/sdcard/screenshot_{int(time.time())}.png"

        subprocess.run(
            [self.get_adb_path(), "-s", self.selected_device["id"], "shell", "screencap", "-p", temp_file],
            check=True
        )

        subprocess.run(
            [self.get_adb_path(), "-s", self.selected_device["id"], "pull", temp_file, output_file],
            check=True
        )

        subprocess.run(
            [self.get_adb_path(), "-s", self.selected_device["id"], "shell", "rm", temp_file],
            check=True
        )

        messagebox.showinfo("Success", f"Screenshot saved to {os.path.basename(output_file)}")
        self.status_var.set("Screenshot saved")

    except subprocess.SubprocessError as e:
        messagebox.showerror("Error", f"Failed to take screenshot: {e}")
        self.status_var.set("Screenshot failed")
        
    def reboot_device(self):
        if not self.selected_device:
            messagebox.showerror("Error", "No device selected")
            return

        if not messagebox.askyesno("Confirm", f"Are you sure you want to reboot {self.selected_device['name']}?"):
            return

        try:
            subprocess.run(
                [self.get_adb_path(), "-s", self.selected_device["id"], "reboot"],
                check=True
            )

            self.status_var.set(f"Rebooting {self.selected_device['name']}...")
            messagebox.showinfo("Reboot", "Device is rebooting")

            self.device_tree.selection_remove(self.device_tree.selection())
            self.selected_device = None

            self.root.after(5000, self.refresh_devices)

        except subprocess.SubprocessError as e:
            messagebox.showerror("Error", f"Failed to reboot device: {e}")


def main():
    root = tk.Tk()
    app = AndroidDeviceManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()