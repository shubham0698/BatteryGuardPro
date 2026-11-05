# 🔋 Battery & Laptop Usage Manager (Python Native Desktop App)

A modern, high-performance **Python desktop application** built with **PyQt6**, **Matplotlib**, **psutil**, and **pywin32**, styled in a clean **White + Emerald Green theme**.

It runs silently in the Windows System Tray (consuming minimal CPU & RAM), monitors battery health, alerts you with a custom sound alarm and centered screen popup dialog when charging reaches your threshold (10% to 90%), features embedded **AI Battery & Energy Advisor Agents**, tracks laptop app usage over 10 days, and automatically purges older logs.

![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-blue?style=for-the-badge&logo=windows)
![Language](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python)
![GUI Theme](https://img.shields.io/badge/Theme-White%20%2B%20Emerald%20Green-10B981?style=for-the-badge)
![AI Agents](https://img.shields.io/badge/AI%20Agents-3%20Built--in-purple?style=for-the-badge)
![Data Retention](https://img.shields.io/badge/Data%20Retention-Past%2010%20Days%20(Auto--Purge)-green?style=for-the-badge)

---

## ✨ Features

### 🔌 1. Smart Battery Threshold & Repeated Alarm
- **Clean White + Emerald Green Theme**: Crisp light mode UI with soft card shadows, emerald green accents, and modern typography.
- **Background System Tray Execution**: Silently monitors battery and active processes with negligible processing & battery consumption.
- **Configurable Threshold (10% to 90%)**: Set your custom target percentage via a smooth slider or quick preset buttons.
- **2-Minute Repeated Alarm Trigger**: When the battery reaches the threshold (e.g. 90%), the alarm window & sound pop up **every 2 minutes** while the charger stays connected.
- **Centered Popup Dialog**: Frameless dialog (`alwaysOnTop=True`) featuring:
  - Top-right **`X`** close button.
  - Prominent **Dismiss & Mute Alarm** button in the **bottom-center** with a high-contrast vibrant color for maximum visibility.
- **Auto-Disappear on Unplug**: Automatically closes the popup dialog and mutes the sound alarm immediately when the charger cable is disconnected.
- **Hardware Power Detection**: Direct kernel32 / `psutil` power API detection for 100% accurate AC charger status (`IsCharging: True / False`).
- **Circular Gauge Background Track**: The Dashboard circular progress gauge displays a faint 360° background circle track.

---

### 🤖 2. Embedded AI Battery & Energy Advisor Agents

The application includes 3 built-in AI agents accessible via the **AI Battery Advisor** tab:

1. **🧠 Smart Dynamic Threshold Agent**:
   - Analyzes 10-day usage history to detect AC power vs mobile battery habits.
   - Auto-tunes threshold (e.g., **75%** when stationary on AC power vs **90%** right before travel).
2. **⚡ Energy-Hog Process Detection Agent**:
   - Monitors idle background apps consuming high CPU/memory while not in foreground focus.
   - Provides live alerts (e.g., *"Google Chrome has 14 background tabs consuming 18% CPU while idle. Closing them will save ~42 mins of battery time."*).
3. **🛡️ Battery Health & Lifespan Advisor Agent**:
   - Calculates avoided high-voltage charge stress cycles (above 80% / 4.2V) over your 10-day history.
   - Displays total months of battery pack lifespan saved.

---

### 📊 3. Battery Analytics
- **Live Battery Monitor**: Real-time battery percentage, charging rate, and power state.
- **10-Day Charge History Curve**: Embedded Matplotlib area chart displaying battery charge curves, charging speed, and session logs.

---

### ⏱️ 4. Laptop & Application Usage Analytics
- **Active App Tracker**: Background worker using Win32 API (`GetForegroundWindow`, `GetWindowThreadProcessId`) to track active process name, description, and window title every 2 seconds.
- **Daily App Time Breakdown**: Ranks top applications used each day by total duration in Matplotlib bar charts and detailed searchable tables.

---

### 🧹 5. Automated 10-Day Data Retention
- **Rolling 10-Day Storage**: Stores detailed logs in a local SQLite database (`battery_manager.db`) for today and the past 9 days.
- **Automated Cleanup**: Records older than 10 days are automatically deleted on startup, every hour, and on demand.

---

## 🛠️ Architecture & Tech Stack

```
BatteryMnager/
├── main.py                     # Application entry point & QApplication initialization
├── requirements.txt            # Python package dependencies (PyQt6, matplotlib, psutil, pywin32)
├── README.md                   # Project documentation
├── services/
│   ├── battery_service.py      # Background QThread for battery polling & 2-min alarm trigger
│   ├── app_tracker_service.py  # Background QThread for Win32 foreground app tracking
│   ├── storage_service.py      # SQLite database & 10-day automated auto-purge engine
│   ├── audio_service.py        # Python audio synthesizer for alarm sound tones
│   └── agents/                 # AI Battery & Energy Advisor Agents
│       ├── threshold_agent.py  # Agent 1: Dynamic Threshold Agent
│       ├── energy_agent.py     # Agent 2: Background Energy-Hog Agent
│       └── health_agent.py     # Agent 3: Battery Health Degradation Agent
└── ui/
    ├── main_window.py          # Main PyQt6 White + Emerald Green window layout
    ├── alarm_dialog.py         # Centered frameless popup alert with bottom-center dismiss button & X button
    ├── dashboard_tab.py        # Circular gauge with faint background track & 10%-90% slider
    ├── battery_tab.py          # Embedded Matplotlib 10-day battery charge graphs
    ├── apps_tab.py             # Top applications bar charts and searchable process table
    ├── history_tab.py          # Past 10 days calendar switcher & auto-purge banner
    ├── settings_tab.py         # Threshold slider, sound tone selector, volume, manual purge
    └── agent_tab.py            # AI Battery & Energy Advisor Agent dashboard
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10** or higher
- Windows 10 or Windows 11

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Application
```bash
python main.py
```

---

## 🔒 Privacy & Data Storage
All metrics are stored locally on your computer in SQLite (`battery_manager.db`). No telemetry or personal usage data ever leaves your device.

---

## 📄 License
MIT License. Created for personal laptop battery health and productivity management.
