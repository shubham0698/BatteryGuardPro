import time
import ctypes
from PyQt6.QtCore import QThread, pyqtSignal
import psutil

class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', ctypes.c_byte),
        ('BatteryFlag', ctypes.c_byte),
        ('BatteryLifePercent', ctypes.c_byte),
        ('SystemStatusFlag', ctypes.c_byte),
        ('BatteryLifeTime', ctypes.c_int),
        ('BatteryFullLifeTime', ctypes.c_int),
    ]

def get_system_power_status():
    status = SYSTEM_POWER_STATUS()
    try:
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
            ac_status = int(status.ACLineStatus)
            percent = int(status.BatteryLifePercent)
            if percent == 255:
                batt = psutil.sensors_battery()
                percent = int(batt.percent) if batt else 85
            is_charging = (ac_status == 1)
            return percent, is_charging
    except Exception:
        pass
    
    # Fallback to psutil
    batt = psutil.sensors_battery()
    if batt:
        return int(batt.percent), bool(batt.power_plugged)
    return 85, False

class BatteryService(QThread):
    battery_updated = pyqtSignal(int, bool)
    trigger_alarm = pyqtSignal(int)
    stop_alarm = pyqtSignal()

    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.running = True
        self.alarm_active = False
        self.last_alarm_time = 0

    def run(self):
        last_log_time = 0
        
        while self.running:
            percent, is_charging = get_system_power_status()
            self.battery_updated.emit(percent, is_charging)

            # Record log every 60 seconds
            now = time.time()
            if now - last_log_time >= 60:
                self.storage.record_battery_log(percent, is_charging)
                last_log_time = now

            # Alarm threshold logic
            threshold = int(self.storage.get_setting('threshold', '80'))
            alarm_enabled = self.storage.get_setting('alarm_enabled', '1') == '1'

            if alarm_enabled and is_charging and percent >= threshold:
                # Trigger alarm if not active OR if 120 seconds (2 minutes) have elapsed while charger connected
                if not self.alarm_active or (now - self.last_alarm_time >= 120):
                    self.alarm_active = True
                    self.last_alarm_time = now
                    self.trigger_alarm.emit(percent)
            else:
                # Disconnected charger or below threshold -> immediately stop alarm
                if not is_charging or percent < threshold:
                    if self.alarm_active:
                        self.alarm_active = False
                        self.stop_alarm.emit()

            # Sleep 2 seconds for low resource usage
            time.sleep(2)

    def stop(self):
        self.running = False
        self.wait()
