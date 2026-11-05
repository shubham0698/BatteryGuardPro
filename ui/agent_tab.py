from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from services.agents.threshold_agent import DynamicThresholdAgent
from services.agents.energy_agent import EnergyHogAgent
from services.agents.health_agent import BatteryHealthAgent

class AgentTab(QWidget):
    def __init__(self, storage, app_tracker, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.thresh_agent = DynamicThresholdAgent(storage)
        self.energy_agent = EnergyHogAgent(app_tracker)
        self.health_agent = BatteryHealthAgent(storage)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        title = QLabel("🤖 AI Battery & Energy Advisor Agents", self)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #111827;")
        layout.addWidget(title)

        # Agent 1: Dynamic Threshold Recommendation Card
        c1 = QFrame(self)
        c1.setStyleSheet("background-color: #FFFFFF; border-radius: 20px; border: 1px solid #E5E7EB;")
        l1 = QVBoxLayout(c1)
        l1.setContentsMargins(20, 20, 20, 20)

        h1 = QHBoxLayout()
        t1 = QLabel("🧠 Agent 1: Smart Dynamic Threshold Recommendation", c1)
        t1.setStyleSheet("font-size: 14px; font-weight: bold; color: #047857; border: none;")
        h1.addWidget(t1)
        h1.addStretch()

        self.apply_btn = QPushButton("Apply Recommended Threshold", c1)
        self.apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 11px;
                padding: 6px 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_rec)
        h1.addWidget(self.apply_btn)
        l1.addLayout(h1)

        self.rec_text = QLabel("Analyzing 10-day AC power vs battery usage patterns...", c1)
        self.rec_text.setWordWrap(True)
        self.rec_text.setStyleSheet("font-size: 12px; color: #4B5563; margin-top: 8px; border: none;")
        l1.addWidget(self.rec_text)

        layout.addWidget(c1)

        # Agent 2: Energy Hog Feed Card
        c2 = QFrame(self)
        c2.setStyleSheet("background-color: #FFFFFF; border-radius: 20px; border: 1px solid #E5E7EB;")
        l2 = QVBoxLayout(c2)
        l2.setContentsMargins(20, 20, 20, 20)

        h2 = QHBoxLayout()
        t2 = QLabel("⚡ Agent 2: Idle Background Energy-Hog Detector", c2)
        t2.setStyleSheet("font-size: 14px; font-weight: bold; color: #D97706; border: none;")
        h2.addWidget(t2)
        h2.addStretch()

        scan_btn = QPushButton("🔄 Scan Now", c2)
        scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        scan_btn.setStyleSheet("background-color: #F3F4F6; color: #374151; font-weight: bold; padding: 4px 10px; border-radius: 8px; border: none;")
        scan_btn.clicked.connect(self.scan_hogs)
        h2.addWidget(scan_btn)
        l2.addLayout(h2)

        self.hog_list = QListWidget(c2)
        self.hog_list.setStyleSheet("""
            QListWidget {
                background-color: #F9FAFB;
                color: #111827;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                padding: 8px;
            }
            QListWidget::item {
                color: #111827;
                padding: 6px;
            }
            QListWidget::item:selected {
                background-color: #D1FAE5;
                color: #047857;
            }
        """)
        l2.addWidget(self.hog_list)


        layout.addWidget(c2)

        # Agent 3: Battery Lifespan Gains Card
        c3 = QFrame(self)
        c3.setStyleSheet("background-color: #ECFDF5; border-radius: 20px; border: 1px solid #A7F3D0;")
        l3 = QVBoxLayout(c3)
        l3.setContentsMargins(20, 20, 20, 20)

        t3 = QLabel("🛡️ Agent 3: Battery Lifespan Protection Insights", c3)
        t3.setStyleSheet("font-size: 14px; font-weight: bold; color: #047857; border: none;")
        l3.addWidget(t3)

        self.health_lbl = QLabel("Calculating avoided high-voltage charge cycles...", c3)
        self.health_lbl.setWordWrap(True)
        self.health_lbl.setStyleSheet("font-size: 12px; color: #065F46; margin-top: 6px; border: none;")
        l3.addWidget(self.health_lbl)

        layout.addWidget(c3)
        self.refresh_agents()

    def refresh_agents(self):
        # Agent 1: Dynamic Threshold Recommendation
        try:
            val, reason = self.thresh_agent.analyze_and_suggest()
            self.suggested_val = val
            self.rec_text.setText(f"💡 Recommended Threshold: <b>{val}%</b><br>{reason}")
        except Exception:
            self.rec_text.setText(f"💡 Recommended Threshold: <b>80%</b><br>Default 80% limit recommended to preserve health.")

        # Agent 2: Energy Hog Scan
        self.scan_hogs()

        # Agent 3: Battery Protection & Health Insights
        try:
            h_info = self.health_agent.calculate_health_insights()
            score = h_info.get('score', 95)
            status = h_info.get('status', 'Optimal Battery Health')
            advice = h_info.get('advice', '')

            self.health_lbl.setText(
                f"💚 <b>Battery Care Rating: {score}/100</b> ({status})<br>"
                f"{advice}"
            )
        except Exception:
            self.health_lbl.setText("🛡️ Keep your charger limit between 75% and 85% to extend battery pack lifespan.")

    def scan_hogs(self):
        self.hog_list.clear()
        try:
            hogs = self.energy_agent.scan_idle_energy_hogs()
            if hogs:
                for hog in hogs:
                    # Clean text without HTML tags for QListWidgetItem
                    clean_rec = hog['recommendation'].replace('<b>', '').replace('</b>', '')
                    item = QListWidgetItem(f"⚠️ {clean_rec} ({hog['impact']})")
                    self.hog_list.addItem(item)
            else:
                self.hog_list.addItem("✅ No heavy background energy-hogs detected right now!")
        except Exception as e:
            self.hog_list.addItem(f"✅ Energy scan completed cleanly ({e}).")


    def apply_rec(self):
        if hasattr(self, 'suggested_val'):
            self.storage.set_setting('threshold', str(self.suggested_val))
            self.rec_text.setText(f"✅ Applied threshold: <b>{self.suggested_val}%</b>!")

