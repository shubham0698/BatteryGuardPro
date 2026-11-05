import os
import sys
import json
import urllib.request
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

APP_VERSION = "1.0.0"

class UpdateService(QThread):
    update_checked = pyqtSignal(bool, str, str, str) # has_update, latest_version, release_notes, download_url

    def __init__(self):
        super().__init__()
        self.version_url = "https://raw.githubusercontent.com/batteryguard/battery-manager-pro/main/version.json"

    def run(self):
        has_update, latest_ver, notes, url = self.check_update_sync()
        self.update_checked.emit(has_update, latest_ver, notes, url)

    def check_update_sync(self):
        try:
            req = urllib.request.Request(self.version_url, headers={'User-Agent': 'BatteryGuardPro/1.0.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                latest_ver = data.get('version', '1.0.0')
                notes = data.get('release_notes', 'Performance improvements and bug fixes.')
                url = data.get('download_url', '')

                if latest_ver != APP_VERSION:
                    return True, latest_ver, notes, url
        except Exception:
            pass

        return False, APP_VERSION, "You are running the latest version of Battery Guard PRO.", ""

    @staticmethod
    def install_update_installer(installer_path):
        if os.path.exists(installer_path):
            subprocess.Popen([installer_path, '/SILENT'], shell=True)
            sys.exit(0)
