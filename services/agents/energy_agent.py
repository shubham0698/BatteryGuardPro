import time
import psutil
from collections import defaultdict

class EnergyHogAgent:
    def __init__(self, app_tracker_service):
        self.app_tracker = app_tracker_service

    def scan_idle_energy_hogs(self):
        hogs = []
        active_pid = getattr(self.app_tracker, 'current_pid', 0)
        num_cpus = psutil.cpu_count() or 1

        ignored = {
            'system idle process', 'system', 'idle', 'explorer.exe',
            'python.exe', 'registry', 'smss.exe', 'csrss.exe', 'wininit.exe',
            'services.exe', 'lsass.exe', 'svchost.exe', 'dwm.exe', 'spoolsv.exe',
            'batteryguardpro.exe', 'msmpeng.exe', 'ctfmon.exe', 'conhost.exe',
            'fontdrvhost.exe', 'sihost.exe', 'searchhost.exe', 'taskmgr.exe'
        }

        # Step 1: Gather running processes & snapshot initial CPU count
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                pname = (proc.info['name'] or '').lower()
                if pname and pname not in ignored and proc.info['pid'] != active_pid:
                    proc.cpu_percent(None)  # Baseline sample
                    procs.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Step 2: Short sampling interval (150ms) to compute CPU delta
        time.sleep(0.15)

        # Step 3: Aggregate CPU % & RAM footprint by process name
        app_cpu = defaultdict(float)
        app_mem = defaultdict(float)
        app_proc_count = defaultdict(int)

        for proc in procs:
            try:
                pname = (proc.info['name'] or '').lower()
                raw_cpu = proc.cpu_percent(None) or 0.0
                effective_cpu = raw_cpu / num_cpus
                mem_info = proc.info.get('memory_info')
                mem_mb = (mem_info.rss / (1024 * 1024)) if mem_info else 0.0

                app_cpu[pname] += effective_cpu
                app_mem[pname] += mem_mb
                app_proc_count[pname] += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Step 4: Build hog recommendations
        for pname, cpu_total in app_cpu.items():
            mem_total = app_mem[pname]
            count = app_proc_count[pname]
            display_name = self.format_app_name(pname)

            if cpu_total >= 0.8 or mem_total >= 250:
                mins_lost = max(5, int(cpu_total * 3.5 + (mem_total / 100)))
                proc_str = f" ({count} processes)" if count > 1 else ""

                if cpu_total >= 0.8:
                    reason = f"App <b>{display_name}</b>{proc_str} is consuming <b>{cpu_total:.1f}% CPU</b> and <b>{int(mem_total)} MB RAM</b> in background."
                else:
                    reason = f"App <b>{display_name}</b>{proc_str} is holding <b>{int(mem_total)} MB RAM</b> in background memory."

                hogs.append({
                    'process': pname,
                    'app_name': display_name,
                    'cpu': f"{cpu_total:.1f}%",
                    'impact': f"-{mins_lost} mins battery",
                    'recommendation': reason
                })

        # Sort by CPU usage descending
        hogs.sort(key=lambda x: float(x['cpu'].replace('%', '')), reverse=True)
        return hogs[:6]

    def format_app_name(self, process_name):
        name_map = {
            'chrome.exe': 'Google Chrome',
            'msedge.exe': 'Microsoft Edge',
            'msedgewebview2.exe': 'Microsoft Edge WebView',
            'firefox.exe': 'Mozilla Firefox',
            'code.exe': 'Visual Studio Code',
            'antigravity ide.exe': 'Antigravity IDE',
            'language_server_windows_x64.exe': 'Language Server Tool',
            'devenv.exe': 'Visual Studio',
            'spotify.exe': 'Spotify',
            'discord.exe': 'Discord',
            'slack.exe': 'Slack',
            'node.exe': 'Node.js Runtime',
            'mysqld.exe': 'MySQL Server',
            'powershell.exe': 'PowerShell Background',
            'cmd.exe': 'Command Prompt',
            'teams.exe': 'Microsoft Teams',
            'zoom.exe': 'Zoom'
        }
        if process_name in name_map:
            return name_map[process_name]
        return process_name.replace('.exe', '').title()


