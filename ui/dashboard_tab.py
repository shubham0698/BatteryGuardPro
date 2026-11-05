from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QBrush

class UltraCircularGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percent = 85
        self.is_charging = False
        self.setFixedSize(240, 240)

    def set_value(self, percent, is_charging):
        self.percent = percent
        self.is_charging = is_charging
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(20, 20, 200, 200)
        stroke_width = 18

        # 1. FAINT BASE TRACK (SOFT GREY)
        bg_pen = QPen(QColor(243, 244, 246), stroke_width, Qt.PenStyle.SolidLine)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect)

        # 2. FAINT EMERALD RING GLOW (360° FAINT CIRCLE TRACK)
        faint_pen = QPen(QColor(16, 185, 129, 30), stroke_width, Qt.PenStyle.SolidLine)
        painter.setPen(faint_pen)
        painter.drawEllipse(rect)

        # 3. GRADIENT ARC PROGRESS
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if self.is_charging:
            gradient.setColorAt(0.0, QColor(52, 211, 153))  # Emerald light
            gradient.setColorAt(1.0, QColor(5, 150, 105))   # Emerald deep
        else:
            gradient.setColorAt(0.0, QColor(56, 189, 248))  # Sky light
            gradient.setColorAt(1.0, QColor(3, 105, 161))   # Sky deep

        brush = QBrush(gradient)
        progress_pen = QPen(brush, stroke_width, Qt.PenStyle.SolidLine)
        progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)

        span_angle = int(- (self.percent / 100.0) * 360 * 16)
        painter.drawArc(rect, 90 * 16, span_angle)

        # 4. INNER CENTER PERCENTAGE DISPLAY
        painter.setPen(QColor(6, 95, 70))
        font = QFont("Plus Jakarta Sans", 36, QFont.Weight.ExtraBold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.percent}%")

class DashboardTab(QWidget):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Top Banner Alert (Hidden by default)
        self.alert_banner = QFrame(self)
        self.alert_banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FEF2F2, stop:1 #FEE2E2);
                border: 1.5px solid #FCA5A5;
                border-radius: 18px;
            }
        """)
        alert_layout = QHBoxLayout(self.alert_banner)
        alert_layout.setContentsMargins(20, 14, 20, 14)
        
        self.alert_text = QLabel("⚠️ Charging Threshold Reached! Unplug charger cable to preserve battery health.", self.alert_banner)
        self.alert_text.setStyleSheet("color: #991B1B; font-weight: 800; font-size: 13px; border: none;")
        alert_layout.addWidget(self.alert_text)
        self.alert_banner.hide()
        layout.addWidget(self.alert_banner)

        # Main Grid Layout
        grid = QHBoxLayout()
        grid.setSpacing(24)

        # Left Card: Circular Gauge with Drop Shadow
        gauge_card = QFrame(self)
        gauge_card.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 24px; border: 1px solid #E5E7EB; }")
        
        shadow1 = QGraphicsDropShadowEffect(self)
        shadow1.setBlurRadius(20)
        shadow1.setColor(QColor(0, 0, 0, 15))
        shadow1.setOffset(0, 6)
        gauge_card.setGraphicsEffect(shadow1)

        gauge_layout = QVBoxLayout(gauge_card)
        gauge_layout.setContentsMargins(24, 24, 24, 24)
        gauge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        gauge_title = QLabel("BATTERY LEVEL & POWER STATUS", gauge_card)
        gauge_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #6B7280; letter-spacing: 1.2px; border: none;")
        gauge_layout.addWidget(gauge_title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.gauge = UltraCircularGauge(gauge_card)
        gauge_layout.addWidget(self.gauge, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_pill = QLabel("🔋 On Battery Power", gauge_card)
        self.status_pill.setStyleSheet("""
            QLabel {
                background-color: #ECFDF5;
                color: #047857;
                font-weight: 800;
                font-size: 12px;
                padding: 8px 20px;
                border-radius: 14px;
                border: 1px solid #A7F3D0;
            }
        """)
        gauge_layout.addWidget(self.status_pill, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(gauge_card, 1)

        # Right Column: Threshold Slider (10% to 90%) & Active App
        right_col = QVBoxLayout()
        right_col.setSpacing(24)

        # Threshold Slider Card
        slider_card = QFrame(self)
        slider_card.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 24px; border: 1px solid #E5E7EB; }")
        
        shadow2 = QGraphicsDropShadowEffect(self)
        shadow2.setBlurRadius(20)
        shadow2.setColor(QColor(0, 0, 0, 15))
        shadow2.setOffset(0, 6)
        slider_card.setGraphicsEffect(shadow2)

        slider_layout = QVBoxLayout(slider_card)
        slider_layout.setContentsMargins(24, 24, 24, 24)

        st_header = QHBoxLayout()
        st_title = QLabel("Charging Threshold Settings", slider_card)
        st_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #111827; border: none;")
        self.val_label = QLabel("80%", slider_card)
        self.val_label.setStyleSheet("font-size: 22px; font-weight: 800; color: #10B981; border: none;")
        st_header.addWidget(st_title)
        st_header.addStretch()
        st_header.addWidget(self.val_label)
        slider_layout.addLayout(st_header)

        # Slider 10% to 90%
        self.slider = QSlider(Qt.Orientation.Horizontal, slider_card)
        self.slider.setRange(10, 90)
        curr_thresh = int(self.storage.get_setting('threshold', '80'))
        self.slider.setValue(curr_thresh)
        self.val_label.setText(f"{curr_thresh}%")
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 10px;
                background: #E5E7EB;
                border-radius: 5px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 #10B981);
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #047857;
                width: 22px;
                margin-top: -6px;
                margin-bottom: -6px;
                border-radius: 11px;
            }
        """)
        self.slider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.slider)

        # Presets
        presets_layout = QHBoxLayout()
        presets_label = QLabel("Quick Presets:", slider_card)
        presets_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #6B7280; border: none;")
        presets_layout.addWidget(presets_label)

        for val in [20, 50, 75, 80, 90]:
            btn = QPushButton(f"{val}%", slider_card)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F3F4F6;
                    color: #374151;
                    font-weight: 800;
                    font-size: 11px;
                    padding: 6px 12px;
                    border-radius: 10px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #D1FAE5;
                    color: #047857;
                }
            """)
            btn.clicked.connect(lambda _, v=val: self.set_threshold_val(v))
            presets_layout.addWidget(btn)
        presets_layout.addStretch()
        slider_layout.addLayout(presets_layout)

        right_col.addWidget(slider_card)

        # Active App Card
        app_card = QFrame(self)
        app_card.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 24px; border: 1px solid #E5E7EB; }")
        
        shadow3 = QGraphicsDropShadowEffect(self)
        shadow3.setBlurRadius(20)
        shadow3.setColor(QColor(0, 0, 0, 15))
        shadow3.setOffset(0, 6)
        app_card.setGraphicsEffect(shadow3)

        app_layout = QHBoxLayout(app_card)
        app_layout.setContentsMargins(24, 20, 24, 20)

        app_info = QVBoxLayout()
        app_badge = QLabel("ACTIVE FOREGROUND PROGRAM", app_card)
        app_badge.setStyleSheet("font-size: 10px; font-weight: 800; color: #10B981; border: none; letter-spacing: 1px;")
        self.app_name_lbl = QLabel("System Idle", app_card)
        self.app_name_lbl.setStyleSheet("font-size: 17px; font-weight: 800; color: #111827; border: none;")
        app_info.addWidget(app_badge)
        app_info.addWidget(self.app_name_lbl)

        app_layout.addLayout(app_info)
        app_layout.addStretch()
        right_col.addWidget(app_card)

        grid.addLayout(right_col, 2)
        layout.addLayout(grid)

    def on_slider_changed(self, value):
        self.val_label.setText(f"{value}%")
        self.storage.set_setting('threshold', str(value))

    def set_threshold_val(self, value):
        self.slider.setValue(value)
        self.on_slider_changed(value)

    def update_battery(self, percent, is_charging):
        self.gauge.set_value(percent, is_charging)
        if is_charging:
            self.status_pill.setText("⚡ Charger Connected")
            self.status_pill.setStyleSheet("background-color: #D1FAE5; color: #047857; font-weight: 800; border-radius: 14px; padding: 8px 20px;")
        else:
            self.status_pill.setText("🔋 On Battery Power")
            self.status_pill.setStyleSheet("background-color: #F3F4F6; color: #4B5563; font-weight: 800; border-radius: 14px; padding: 8px 20px;")

        thresh = int(self.storage.get_setting('threshold', '80'))
        if is_charging and percent >= thresh:
            self.alert_banner.show()
        else:
            self.alert_banner.hide()

    def update_app(self, process_name, app_name):
        self.app_name_lbl.setText(app_name)
