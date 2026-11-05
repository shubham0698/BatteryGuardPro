from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class BatteryTab(QWidget):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        title = QLabel("Battery Charge Analytics (Past 10 Days)", self)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #111827;")
        layout.addWidget(title)

        # Matplotlib Chart Frame
        chart_frame = QFrame(self)
        chart_frame.setStyleSheet("background-color: #FFFFFF; border-radius: 20px; border: 1px solid #E5E7EB;")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(15, 15, 15, 15)

        self.fig = Figure(figsize=(8, 3.5), facecolor='#FFFFFF')
        self.canvas = FigureCanvasQTAgg(self.fig)
        chart_layout.addWidget(self.canvas)
        layout.addWidget(chart_frame)

        # Log Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Date", "Battery %", "Power Status"])
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
        self.refresh_data()

    def refresh_data(self):
        logs = self.storage.get_battery_logs(limit=30)
        
        # Plot Matplotlib Area Chart
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#F9FAFB')

        if logs:
            reversed_logs = list(reversed(logs))
            times = [log[0].split()[1][:5] for log in reversed_logs]
            percents = [log[2] for log in reversed_logs]

            ax.plot(times, percents, color='#10B981', linewidth=2.5, marker='o', markersize=4)
            ax.fill_between(times, percents, color='#10B981', alpha=0.15)
            ax.set_ylim(0, 105)
            ax.set_ylabel('Battery %', color='#374151', fontsize=9)
            ax.tick_params(colors='#6B7280', labelsize=8)
            ax.grid(True, linestyle='--', alpha=0.5, color='#E5E7EB')
            for spine in ax.spines.values():
                spine.set_color('#E5E7EB')
        
        self.fig.tight_layout()
        self.canvas.draw()

        # Populate Table
        self.table.setRowCount(len(logs))
        text_color = QColor('#111827')
        for row, log in enumerate(logs):
            i0 = QTableWidgetItem(str(log[0]))
            i0.setForeground(text_color)
            self.table.setItem(row, 0, i0)

            i1 = QTableWidgetItem(str(log[1]))
            i1.setForeground(text_color)
            self.table.setItem(row, 1, i1)

            i2 = QTableWidgetItem(f"{log[2]}%")
            i2.setForeground(text_color)
            self.table.setItem(row, 2, i2)

            status = "⚡ AC Charger" if log[3] == 1 else "🔋 Battery"
            i3 = QTableWidgetItem(status)
            i3.setForeground(text_color)
            self.table.setItem(row, 3, i3)

