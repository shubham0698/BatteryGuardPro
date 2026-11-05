import sys
import os
import winreg
import subprocess
from pathlib import Path

# Add root directory to python module search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon

from services.storage_service import StorageService
from services.battery_service import BatteryService
from services.app_tracker_service import AppTrackerService
from services.audio_service import AudioService
from ui.main_window import MainWindow

def perform_uninstall():
    app = QApplication(sys.argv)
    app.setApplicationName("Battery Guard PRO Uninstaller")

    reply = QMessageBox.question(
        None,
        "Uninstall Battery Guard PRO",
        "Are you sure you want to uninstall Battery Guard PRO and all of its components?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )

    if reply != QMessageBox.StandardButton.Yes:
        sys.exit(0)

    # 1. Remove Desktop Shortcut
    desktop = Path(os.path.expanduser('~')) / 'Desktop' / 'Battery Guard PRO.lnk'
    if desktop.exists():
        try:
            desktop.unlink()
        except Exception as e:
            print("Failed to remove desktop shortcut:", e)

    # 2. Remove Start Menu Shortcut
    start_menu = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Battery Guard PRO.lnk'
    if start_menu.exists():
        try:
            start_menu.unlink()
        except Exception as e:
            print("Failed to remove start menu shortcut:", e)

    # 3. Remove Windows Registry Key
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryGuardPro")
    except Exception as e:
        print("Failed to remove registry key:", e)

    # 4. Schedule directory cleanup after process exits
    install_dir = os.path.dirname(os.path.abspath(__file__))
    cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 1; Remove-Item -Recurse -Force \'{install_dir}\'"'
    subprocess.Popen(cmd, shell=True)

    QMessageBox.information(
        None,
        "Uninstall Complete",
        "Battery Guard PRO has been successfully removed from your computer."
    )
    sys.exit(0)

def main():
    if "--uninstall" in sys.argv:
        perform_uninstall()
        return

    app = QApplication(sys.argv)
    app.setApplicationName("Battery Guard PRO")
    app.setStyle("Fusion")

    # Set Application Icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'app_icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Storage service
    storage = StorageService()

    # Background Services
    battery_service = BatteryService(storage)
    app_tracker_service = AppTrackerService(storage)
    audio_service = AudioService()

    battery_service.start()
    app_tracker_service.start()

    # Main Window
    window = MainWindow(storage, battery_service, app_tracker_service, audio_service)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

