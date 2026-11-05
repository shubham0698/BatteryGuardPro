from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class HistoryTab(QWidget):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header Banner
        banner = QFrame(self)
        banner.setStyleSheet("background-color: #ECFDF5; border-radius: 16px; border: 1px solid #A7F3D0;")
        b_layout = QHBoxLayout(banner)
        b_layout.setContentsMargins(16, 12, 16, 12)
        b_text = QLabel("🧹 10-DAY AUTOMATED RETENTION POLICY: Records older than 10 days are deleted automatically every 24 hours.", banner)
        b_text.setStyleSheet("color: #047857; font-weight: bold; font-size: 12px;")
        b_layout.addWidget(b_text)
        layout.addWidget(banner)

        # Date Buttons
        dates_layout = QHBoxLayout()
        dates_layout.setSpacing(8)
        self.dates = self.storage.get_all_dates_with_data()
        self.selected_date = self.dates[0]

        for d_str in self.dates:
            btn = QPushButton(d_str, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #374151;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 6px 12px;
                    border-radius: 10px;
                    border: 1px solid #E5E7EB;
                }
                QPushButton:hover {
                    background-color: #D1FAE5;
                    color: #047857;
                }
            """)
            btn.clicked.connect(lambda _, d=d_str: self.select_date(d))
            dates_layout.addWidget(btn)
        dates_layout.addStretch()
        layout.addLayout(dates_layout)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Application Name", "Executable", "Time Spent"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #111827;
                border-radius: 16px;
                border: 1px solid #E5E7EB;
                gridline-color: #F3F4F6;
            }
            QTableWidget::item {
                color: #111827;
                background-color: #FFFFFF;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #D1FAE5;
                color: #047857;
            }
            QHeaderView::section {
                background-color: #F3F4F6;
                color: #111827;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
        """)
        layout.addWidget(self.table)
        self.select_date(self.selected_date)

    def select_date(self, date_str):
        self.selected_date = date_str
        apps = self.storage.get_app_usage_by_date(date_str)
        self.table.setRowCount(len(apps))
        text_color = QColor('#111827')
        for row, app in enumerate(apps):
            i0 = QTableWidgetItem(str(app[1]))
            i0.setForeground(text_color)
            self.table.setItem(row, 0, i0)

            i1 = QTableWidgetItem(str(app[0]))
            i1.setForeground(text_color)
            self.table.setItem(row, 1, i1)

            m = app[2] // 60
            i2 = QTableWidgetItem(f"{m} mins")
            i2.setForeground(text_color)
            self.table.setItem(row, 2, i2)

