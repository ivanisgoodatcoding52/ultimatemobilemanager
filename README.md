# 📱 Ultimate Mobile Manager

A powerful Windows-based toolkit for managing both **jailbroken iOS (iOS 9 and below)** and **rooted Android** devices — packed into one unified app. Built for enthusiasts, reverse engineers, and developers who want **direct control over mobile devices** without using bloated OEM software.

---

## ✨ Features

### 📱 iOS Device Manager (iOS 9 and under)
- ✅ **File Manager**: Browse full root filesystem (via AFC2 or SSH)
- ✅ **App Control**: Install/remove IPA files, view installed apps
- ✅ **Remote Control**: Veency-based screen mirroring/control
- ✅ **Real-Time Logs**: View syslog output and crash logs
- ✅ **libimobiledevice Integration**: Uses [L1ghtmann’s build](https://github.com/L1ghtmann/libimobiledevice/releases) for robust support
- ✅ **Backup/Restore**: Manual or scripted backups
- ✅ **Terminal**: SSH terminal for command execution

> 📌 Requires jailbroken device (checkra1n, Phoenix, etc.)

---

### 🤖 Android Device Manager (Rooted)
- ✅ **File System Access**: Browse and transfer files using ADB
- ✅ **App Manager**: Install/uninstall APKs, list installed apps
- ✅ **ADB Shell**: Terminal with root access (if available)
- ✅ **Screen Mirroring**: Built-in scrcpy integration
- ✅ **Custom Tools**: Reboot to recovery/bootloader, push/pull files, etc.

> 📌 Requires USB debugging and optionally root access

---

## 🖥️ Platform Support

- 🪟 **Windows 10/11**
- 📅 macOS/Linux planned in future

---

## 🔧 Installation

### 1. Clone the Repo
```bash
git clone https://github.com/ivanisgoodatcoding52/ultimatemobilemanager.git
cd ultimatemobilemanager
2. Install Python Dependencies
Make sure Python 3.10+ is installed:

bash
Copy
Edit
pip install -r requirements.txt
3. Set Up
iOS Devices:
Jailbreak your device

Install OpenSSH (via Cydia/Sileo)

[Optional] Install Veency for screen mirroring

Android Devices:
Enable USB Debugging

(Optional) Root for advanced functions

🚀 Running the App
bash
Copy
Edit
python main.py
Once launched, you’ll get access to:

iOS Device Tab

Android Device Tab

File Explorer

App Manager

Live Console

Remote Viewer (scrcpy / Veency)

