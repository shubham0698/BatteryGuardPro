import time
from PyQt6.QtCore import QThread, pyqtSignal
import win32gui
import win32process
import psutil

class AppTrackerService(QThread):
    app_updated = pyqtSignal(str, str) # process_name, app_name

    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.running = True
        self.current_process = ""
        self.current_pid = 0

    def run(self):
        while self.running:
            try:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid > 0:
                        proc = psutil.Process(pid)
                        process_name = proc.name().lower()
                        app_name = self.format_app_name(process_name, proc)
                        
                        self.current_process = process_name
                        self.current_pid = pid
                        self.storage.record_app_usage(process_name, app_name, duration_seconds=2)
                        self.app_updated.emit(process_name, app_name)
            except Exception:
                pass

            
            time.sleep(2)

    def format_app_name(self, process_name, proc=None):
        name_map = {
            'chrome.exe': 'Google Chrome',
            'msedge.exe': 'Microsoft Edge',
            'firefox.exe': 'Mozilla Firefox',
            'code.exe': 'Visual Studio Code',
            'devenv.exe': 'Visual Studio',
            'spotify.exe': 'Spotify',
            'discord.exe': 'Discord',
            'slack.exe': 'Slack',
            'explorer.exe': 'Windows Explorer',
            'powershell.exe': 'PowerShell',
            'cmd.exe': 'Command Prompt',
            'notepad.exe': 'Notepad',
            'taskmgr.exe': 'Task Manager',
            'teams.exe': 'Microsoft Teams',
            'zoom.exe': 'Zoom'
        }
        if process_name in name_map:
            return name_map[process_name]
        
        base = process_name.replace('.exe', '')
        return base.capitalize()

    def stop(self):
        self.running = False
        self.wait()
