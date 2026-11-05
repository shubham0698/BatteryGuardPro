import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class AppsTab(QWidget):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header Row with Search
        header = QHBoxLayout()
        title = QLabel("Application Usage Analytics Today", self)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #111827;")
        header.addWidget(title)
        header.addStretch()

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("🔍 Search process...")
        self.search_bar.setFixedWidth(200)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #111827;
                border: 1px solid #D1D5DB;
                border-radius: 10px;
                padding: 6px 12px;
                font-size: 12px;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_table)
        header.addWidget(self.search_bar)
        layout.addLayout(header)

        # Matplotlib Bar Chart
        chart_frame = QFrame(self)
        chart_frame.setStyleSheet("background-color: #FFFFFF; border-radius: 20px; border: 1px solid #E5E7EB;")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(15, 15, 15, 15)

        self.fig = Figure(figsize=(8, 3.2), facecolor='#FFFFFF')
        self.canvas = FigureCanvasQTAgg(self.fig)
        chart_layout.addWidget(self.canvas)
        layout.addWidget(chart_frame)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Application Name", "Executable", "Time Spent", "Last Active"])
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

    def format_sec(self, sec):
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        if h > 0: return f"{h}h {m}m"
        if m > 0: return f"{m}m {s}s"
        return f"{s}s"

    def refresh_data(self):
        today = datetime.date.today().strftime('%Y-%m-%d')
        apps = self.storage.get_app_usage_by_date(today)

        # Matplotlib Top Apps Bar Chart
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#F9FAFB')

        top_apps = apps[:6]
        if top_apps:
            names = [app[1][:12] for app in top_apps]
            mins = [round(app[2] / 60.0, 1) for app in top_apps]

            bars = ax.bar(names, mins, color='#10B981', width=0.5, edgecolor='#047857', linewidth=1)
            ax.set_ylabel('Minutes Spent', color='#374151', fontsize=9)
            ax.tick_params(colors='#6B7280', labelsize=8)
            ax.grid(axis='y', linestyle='--', alpha=0.5, color='#E5E7EB')
            for spine in ax.spines.values():
                spine.set_color('#E5E7EB')
        
        self.fig.tight_layout()
        self.canvas.draw()

        # Table
        self.all_apps_data = apps
        self.populate_table(apps)

    def populate_table(self, apps):
        self.table.setRowCount(len(apps))
        text_color = QColor('#111827')
        for row, app in enumerate(apps):
            i0 = QTableWidgetItem(str(app[1]))
            i0.setForeground(text_color)
            self.table.setItem(row, 0, i0)

            i1 = QTableWidgetItem(str(app[0]))
            i1.setForeground(text_color)
            self.table.setItem(row, 1, i1)

            i2 = QTableWidgetItem(self.format_sec(app[2]))
            i2.setForeground(text_color)
            self.table.setItem(row, 2, i2)

            i3 = QTableWidgetItem(str(app[3]))
            i3.setForeground(text_color)
            self.table.setItem(row, 3, i3)

    def filter_table(self, text):
        query = text.lower().strip()
        filtered = [a for a in getattr(self, 'all_apps_data', []) if query in a[0].lower() or query in a[1].lower()]
        self.populate_table(filtered)

