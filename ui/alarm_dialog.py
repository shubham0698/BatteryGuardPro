from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

class AlarmDialog(QDialog):
    dismissed = pyqtSignal()

    def __init__(self, percent=85, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(520, 360)

        # Main Outer Container with Drop Shadow
        self.init_ui(percent)

    def init_ui(self, percent):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Card Panel
        self.card = QLabel(self)
        self.card.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 2px solid #10B981;
                border-radius: 24px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(16, 185, 129, 100))
        shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(25, 20, 25, 25)

        # Top Header Bar (Badge + Top-Right X Close Button)
        top_bar = QHBoxLayout()
        badge = QLabel("⚡ BATTERY THRESHOLD ALERT", self.card)
        badge.setStyleSheet("""
            QLabel {
                background-color: #ECFDF5;
                color: #047857;
                font-weight: bold;
                font-size: 11px;
                padding: 4px 12px;
                border-radius: 12px;
                border: 1px solid #A7F3D0;
            }
        """)
        top_bar.addWidget(badge)
        top_bar.addStretch()

        close_btn = QPushButton("✕", self.card)
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #4B5563;
                border-radius: 16px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                color: #DC2626;
            }
        """)
        close_btn.clicked.connect(self.on_dismiss)
        top_bar.addWidget(close_btn)
        card_layout.addLayout(top_bar)

        card_layout.addStretch()

        # Center Percentage Display
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(f"Threshold Reached! {percent}%", self.card)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #065F46; border: none;")

        msg = QLabel("Your charger is connected and battery has reached your target limit.\nPlease unplug your power cable to protect battery health.", self.card)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 13px; color: #4B5563; border: none; margin-top: 6px;")

        center_layout.addWidget(title)
        center_layout.addWidget(msg)
        card_layout.addLayout(center_layout)

        card_layout.addStretch()

        # Bottom Center High-Contrast Dismiss Button
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dismiss_btn = QPushButton("🔔 DISMISS & MUTE ALARM", self.card)
        dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dismiss_btn.setFixedSize(280, 48)
        dismiss_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626);
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 800;
                border-radius: 16px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #DC2626, stop:1 #B91C1C);
            }
        """)
        dismiss_btn.clicked.connect(self.on_dismiss)
        btn_layout.addWidget(dismiss_btn)

        card_layout.addLayout(btn_layout)
        layout.addWidget(self.card)

    def on_dismiss(self):
        self.dismissed.emit()
        self.accept()
