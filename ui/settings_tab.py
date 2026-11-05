from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QComboBox, QFrame, QMessageBox
from PyQt6.QtCore import Qt
from services.update_service import UpdateService, APP_VERSION

class SettingsTab(QWidget):
    def __init__(self, storage, audio_service, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.audio = audio_service
        self.update_service = UpdateService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        title = QLabel("Preferences & Application Settings", self)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #111827;")
        layout.addWidget(title)

        # Settings Card
        card = QFrame(self)
        card.setStyleSheet("background-color: #FFFFFF; border-radius: 20px; border: 1px solid #E5E7EB;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

        # Sound Selector
        s_row = QHBoxLayout()
        s_lbl = QLabel("Alarm Sound Tone:", card)
        s_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #374151;")
        self.sound_combo = QComboBox(card)
        self.sound_combo.addItems(["Digital Beep", "Urgent Siren", "Gentle Chime", "Pulse Warning"])
        self.sound_combo.setStyleSheet("""
            QComboBox {
                background-color: #F9FAFB;
                color: #111827;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-width: 140px;
            }
            QComboBox:hover {
                border-color: #10B981;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #111827;
                selection-background-color: #D1FAE5;
                selection-color: #047857;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 4px;
                outline: none;
            }
        """)
        curr_sound = self.storage.get_setting('sound', 'digital')
        sound_map = {'digital': 0, 'siren': 1, 'chime': 2, 'pulse': 3}
        self.sound_combo.setCurrentIndex(sound_map.get(curr_sound, 0))
        self.sound_combo.currentIndexChanged.connect(self.on_sound_changed)


        test_btn = QPushButton("▶ Test Sound", card)
        test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 14px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        test_btn.clicked.connect(self.test_sound)

        s_row.addWidget(s_lbl)
        s_row.addWidget(self.sound_combo)
        s_row.addWidget(test_btn)
        card_layout.addLayout(s_row)

        # Alarm Toggle
        t_row = QHBoxLayout()
        t_lbl = QLabel("Sound Alarm Enabled:", card)
        t_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #374151;")
        self.toggle_btn = QPushButton("ENABLED", card)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        is_on = self.storage.get_setting('alarm_enabled', '1') == '1'
        self.update_toggle_btn(is_on)
        self.toggle_btn.clicked.connect(self.toggle_alarm)
        t_row.addWidget(t_lbl)
        t_row.addStretch()
        t_row.addWidget(self.toggle_btn)
        card_layout.addLayout(t_row)

        # Auto-Update System Section
        u_row = QHBoxLayout()
        u_lbl = QLabel(f"Application Version (v{APP_VERSION}):", card)
        u_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #374151;")
        u_btn = QPushButton("🔄 Check for Updates", card)
        u_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        u_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 14px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        u_btn.clicked.connect(self.check_for_updates)
        u_row.addWidget(u_lbl)
        u_row.addStretch()
        u_row.addWidget(u_btn)
        card_layout.addLayout(u_row)

        # Purge Data Now
        p_row = QHBoxLayout()
        p_lbl = QLabel("10-Day Retention Data:", card)
        p_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #374151;")
        p_btn = QPushButton("🧹 Purge Older Data Now", card)
        p_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        p_btn.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #374151;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 14px;
                border-radius: 8px;
                border: 1px solid #D1D5DB;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                color: #DC2626;
            }
        """)
        p_btn.clicked.connect(self.purge_data)
        p_row.addWidget(p_lbl)
        p_row.addStretch()
        p_row.addWidget(p_btn)
        card_layout.addLayout(p_row)

        layout.addWidget(card)
        layout.addStretch()

    def on_sound_changed(self, idx):
        keys = ['digital', 'siren', 'chime', 'pulse']
        self.storage.set_setting('sound', keys[idx])

    def test_sound(self):
        keys = ['digital', 'siren', 'chime', 'pulse']
        st = keys[self.sound_combo.currentIndex()]
        self.audio.play_alarm(st)

    def toggle_alarm(self):
        curr = self.storage.get_setting('alarm_enabled', '1') == '1'
        new_val = '0' if curr else '1'
        self.storage.set_setting('alarm_enabled', new_val)
        self.update_toggle_btn(not curr)

    def update_toggle_btn(self, is_on):
        if is_on:
            self.toggle_btn.setText("ENABLED")
            self.toggle_btn.setStyleSheet("background-color: #D1FAE5; color: #047857; font-weight: bold; border-radius: 8px; padding: 6px 14px;")
        else:
            self.toggle_btn.setText("DISABLED")
            self.toggle_btn.setStyleSheet("background-color: #FEE2E2; color: #DC2626; font-weight: bold; border-radius: 8px; padding: 6px 14px;")

    def purge_data(self):
        self.storage.purge_old_data()

    def check_for_updates(self):
        has_update, latest_ver, notes, url = self.update_service.check_update_sync()
        if has_update:
            QMessageBox.information(self, "Update Available", f"A new version (v{latest_ver}) is available!\n\nRelease Notes:\n{notes}")
        else:
            QMessageBox.information(self, "Battery Guard PRO", f"You are running the latest version (v{APP_VERSION}).")
