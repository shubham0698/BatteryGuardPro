import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction, QPixmap, QColor, QPainter, QBrush

from ui.dashboard_tab import DashboardTab
from ui.battery_tab import BatteryTab
from ui.apps_tab import AppsTab
from ui.history_tab import HistoryTab
from ui.settings_tab import SettingsTab
from ui.agent_tab import AgentTab
from ui.alarm_dialog import AlarmDialog

def create_tray_icon_pixmap(percent=85, is_charging=False):
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    bg_color = QColor(16, 185, 129) if is_charging else QColor(14, 165, 233)
    painter.setBrush(QBrush(bg_color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, 28, 28, 8, 8)

    painter.setPen(QColor(255, 255, 255))
    font = painter.font()
    font.setBold(True)
    font.setPixelSize(12)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, f"{percent}")
    painter.end()
    return pixmap

class MainWindow(QMainWindow):
    def __init__(self, storage, battery_service, app_tracker_service, audio_service):
        super().__init__()
        self.storage = storage
        self.battery_service = battery_service
        self.app_tracker_service = app_tracker_service
        self.audio_service = audio_service

        self.setWindowTitle("Battery Guard PRO")
        self.resize(1080, 720)
        self.setMinimumSize(900, 620)
        self.setStyleSheet("QMainWindow { background-color: #F9FAFB; }")

        # Set Window Icon
        self.icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'app_icon.png')
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))

        self.alarm_dialog = None
        self.is_quitting = False

        self.init_ui()
        self.init_tray()
        self.connect_signals()

    def init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(20)

        # Header Navbar
        header = QHBoxLayout()

        # Logo & Title
        logo_box = QLabel(self)
        logo_box.setFixedSize(44, 44)
        if os.path.exists(self.icon_path):
            logo_pix = QPixmap(self.icon_path).scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_box.setPixmap(logo_pix)
        else:
            logo_box.setStyleSheet("background-color: #10B981; border-radius: 12px; color: #FFFFFF; font-weight: 800; font-size: 20px;")
            logo_box.setText("🔋")
            logo_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title_lbl = QLabel("Battery Guard PRO", self)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #111827;")
        sub_lbl = QLabel("White & Emerald Green Edition", self)
        sub_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #059669;")
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)

        header.addWidget(logo_box)
        header.addLayout(title_box)
        header.addStretch()

        # Test Alarm Button
        test_btn = QPushButton("🔔 Test Alarm Popup", self)
        test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEF3C7;
                color: #D97706;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                border-radius: 12px;
                border: 1px solid #FDE68A;
            }
            QPushButton:hover {
                background-color: #FDE68A;
            }
        """)
        test_btn.clicked.connect(lambda: self.on_trigger_alarm(85))
        header.addWidget(test_btn)

        # Battery Live Pill
        self.battery_pill = QLabel("🔋 85% (On Battery)", self)
        self.battery_pill.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                color: #047857;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)
        header.addWidget(self.battery_pill)
        main_layout.addLayout(header)

        # Tabs Layout
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: #FFFFFF;
                color: #4B5563;
                font-weight: bold;
                font-size: 12px;
                padding: 10px 20px;
                margin-right: 8px;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
            QTabBar::tab:selected {
                background-color: #10B981;
                color: #FFFFFF;
                border: 1px solid #10B981;
            }
            QTabBar::tab:hover:!selected {
                background-color: #ECFDF5;
                color: #047857;
            }
        """)

        self.dashboard_tab = DashboardTab(self.storage, self)
        self.battery_tab = BatteryTab(self.storage, self)
        self.apps_tab = AppsTab(self.storage, self)
        self.history_tab = HistoryTab(self.storage, self)
        self.agent_tab = AgentTab(self.storage, self.app_tracker_service, self)
        self.settings_tab = SettingsTab(self.storage, self.audio_service, self)

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.battery_tab, "Battery Analytics")
        self.tabs.addTab(self.apps_tab, "App Usage")
        self.tabs.addTab(self.history_tab, "10-Day History")
        self.tabs.addTab(self.agent_tab, "🤖 AI Advisor Agents")
        self.tabs.addTab(self.settings_tab, "Settings")

        main_layout.addWidget(self.tabs)

    def init_tray(self):
        if os.path.exists(self.icon_path):
            self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path), self)
        else:
            pix = create_tray_icon_pixmap(85, False)
            self.tray_icon = QSystemTrayIcon(QIcon(pix), self)
            
        self.tray_icon.setToolTip("Battery Guard PRO")

        menu = QMenu()
        open_act = QAction("Open Battery Manager", self)
        open_act.triggered.connect(self.show_window)
        exit_act = QAction("Exit Application", self)
        exit_act.triggered.connect(self.quit_app)

        menu.addAction(open_act)
        menu.addSeparator()
        menu.addAction(exit_act)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def connect_signals(self):
        self.battery_service.battery_updated.connect(self.on_battery_updated)
        self.battery_service.trigger_alarm.connect(self.on_trigger_alarm)
        self.battery_service.stop_alarm.connect(self.on_stop_alarm)
        self.app_tracker_service.app_updated.connect(self.on_app_updated)

    def on_battery_updated(self, percent, is_charging):
        self.dashboard_tab.update_battery(percent, is_charging)
        st = "⚡ Charging" if is_charging else "🔋 On Battery"
        self.battery_pill.setText(f"{st}: {percent}%")
        self.tray_icon.setToolTip(f"Battery Guard: {percent}% ({st})")

    def on_app_updated(self, process_name, app_name):
        self.dashboard_tab.update_app(process_name, app_name)

    def on_trigger_alarm(self, percent):
        st = self.storage.get_setting('sound', 'digital')
        vol = int(self.storage.get_setting('volume', '80'))
        self.audio_service.play_alarm(st, vol)

        if not self.alarm_dialog or not self.alarm_dialog.isVisible():
            self.alarm_dialog = AlarmDialog(percent, self)
            self.alarm_dialog.dismissed.connect(self.on_stop_alarm)
            self.alarm_dialog.show()

    def on_stop_alarm(self):
        self.audio_service.stop_alarm()
        if self.alarm_dialog and self.alarm_dialog.isVisible():
            self.alarm_dialog.close()
            self.alarm_dialog = None

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def closeEvent(self, event):
        if not self.is_quitting:
            event.ignore()
            self.hide()
        else:
            event.accept()

    def quit_app(self):
        self.is_quitting = True
        self.battery_service.stop()
        self.app_tracker_service.stop()
        self.audio_service.stop_alarm()
        self.close()
