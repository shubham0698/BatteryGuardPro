import sys
import os
import shutil
import winreg
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

def create_windows_shortcut(target_path, shortcut_path, icon_path=None, description="Battery Guard PRO Desktop App"):
    ps_cmd = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{shortcut_path}')
$s.TargetPath = '{target_path}'
$s.Description = '{description}'
$s.WorkingDirectory = '{os.path.dirname(target_path)}'
"""
    if icon_path and os.path.exists(icon_path):
        ps_cmd += f"\n$s.IconLocation = '{icon_path}'"
    ps_cmd += "\n$s.Save()"

    subprocess_script = f"powershell -NoProfile -ExecutionPolicy Bypass -Command \"{ps_cmd.replace(chr(10), '; ')}\""
    os.system(subprocess_script)

def register_uninstall_registry(install_dir, exe_path, icon_path):
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\BatteryGuardPro"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Battery Guard PRO")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Battery Guard Software")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path or exe_path)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{exe_path}" --uninstall')
    except Exception as e:
        print("Registry registration warning:", e)

class WelcomePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to Battery Guard PRO Setup Wizard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        banner = QFrame(self)
        banner.setStyleSheet("background-color: #ECFDF5; border-radius: 14px; border: 1px solid #A7F3D0;")
        b_layout = QHBoxLayout(banner)
        b_layout.setContentsMargins(16, 12, 16, 12)
        b_lbl = QLabel("🔋 Battery Guard PRO Setup", banner)
        b_lbl.setStyleSheet("color: #047857; font-weight: 800; font-size: 16px; border: none;")
        b_layout.addWidget(b_lbl)
        layout.addWidget(banner)

        msg = QLabel(
            "This wizard will install Battery Guard PRO on your computer's C: drive.\n\n"
            "Features included:\n"
            "  • Smart Battery Charging Threshold & 2-Minute Repeated Alarm\n"
            "  • Instant Sub-Second App Startup Performance\n"
            "  • 3 Built-in AI Battery & Energy Advisor Agents\n"
            "  • 10-Day Automated Data Retention Cleanup\n\n"
            "Click Next to continue."
        )
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 13px; color: #1F2937; line-height: 1.6; font-weight: 500;")
        layout.addWidget(msg)

class DirectoryPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Select Installation Directory on C: Drive")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        lbl = QLabel("Choose the destination folder where Battery Guard PRO will be installed:")
        lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #111827;")
        layout.addWidget(lbl)

        dir_layout = QHBoxLayout()
        local_app = Path(os.environ.get('LOCALAPPDATA', 'C:\\Users\\Default\\AppData\\Local')) / 'Programs' / 'BatteryGuardPro'
        self.path_edit = QLineEdit(str(local_app), self)
        self.path_edit.setStyleSheet("padding: 8px; font-size: 12px; color: #111827; background-color: #F9FAFB; border: 1px solid #D1D5DB; border-radius: 8px;")
        dir_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("Browse...", self)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setStyleSheet("background-color: #E5E7EB; color: #1F2937; font-weight: bold; padding: 8px 14px; border-radius: 8px;")
        browse_btn.clicked.connect(self.browse_dir)
        dir_layout.addWidget(browse_btn)

        layout.addLayout(dir_layout)

        self.shortcut_cb = QCheckBox("Create Desktop Shortcut (with transparent green battery icon)", self)
        self.shortcut_cb.setChecked(True)
        self.shortcut_cb.setStyleSheet("color: #111827; font-size: 13px; font-weight: 600; padding: 4px 0;")
        layout.addWidget(self.shortcut_cb)

        self.autostart_cb = QCheckBox("Add to Windows Start Menu Programs", self)
        self.autostart_cb.setChecked(True)
        self.autostart_cb.setStyleSheet("color: #111827; font-size: 13px; font-weight: 600; padding: 4px 0;")
        layout.addWidget(self.autostart_cb)

    def browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Install Folder", "C:\\")
        if d:
            self.path_edit.setText(os.path.join(d, "BatteryGuardPro"))

class PerformInstallPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Installing Battery Guard PRO")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.status_lbl = QLabel("Ready to install files to your C: drive...")
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #047857;")
        layout.addWidget(self.status_lbl)

    def initializePage(self):
        dir_page = self.wizard().page(1)
        dest_dir = dir_page.path_edit.text()
        
        try:
            os.makedirs(dest_dir, exist_ok=True)
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Copy --onedir app folder
            onedir_src = os.path.join(curr_dir, 'dist', 'BatteryGuardPro')
            exe_src = os.path.join(curr_dir, 'dist', 'BatteryGuardPro.exe')
            exe_dest = os.path.join(dest_dir, 'BatteryGuardPro.exe')

            if os.path.exists(onedir_src):
                # Copy entire folder for instant launch
                for item in os.listdir(onedir_src):
                    s = os.path.join(onedir_src, item)
                    d = os.path.join(dest_dir, item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
            elif os.path.exists(exe_src):
                shutil.copy2(exe_src, exe_dest)

            # Copy transparent green battery assets
            assets_src = os.path.join(curr_dir, 'assets')
            assets_dest = os.path.join(dest_dir, 'assets')
            if os.path.exists(assets_src):
                if os.path.exists(assets_dest):
                    shutil.rmtree(assets_dest)
                shutil.copytree(assets_src, assets_dest)

            icon_file = os.path.join(assets_dest, 'app_icon.ico') if os.path.exists(assets_dest) else exe_dest

            # Desktop Shortcut
            if dir_page.shortcut_cb.isChecked():
                desktop = Path(os.path.expanduser('~')) / 'Desktop'
                shortcut_file = desktop / 'Battery Guard PRO.lnk'
                create_windows_shortcut(exe_dest, str(shortcut_file), icon_file)

            # Start Menu Shortcut
            if dir_page.autostart_cb.isChecked():
                start_menu = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
                if start_menu.exists():
                    start_shortcut = start_menu / 'Battery Guard PRO.lnk'
                    create_windows_shortcut(exe_dest, str(start_shortcut), icon_file)

            # Windows Registry
            register_uninstall_registry(dest_dir, exe_dest, icon_file)

            self.status_lbl.setText("✅ Installation successfully completed on C: drive!\nInstant launch shortcut created on Desktop.")
            self.wizard().dest_exe = exe_dest
        except Exception as e:
            self.status_lbl.setText(f"Installation error: {e}")

class FinishPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Setup Completed Successfully")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        msg = QLabel("Battery Guard PRO is now installed on your laptop.")
        msg.setStyleSheet("font-size: 14px; font-weight: bold; color: #111827;")
        layout.addWidget(msg)

        self.launch_cb = QCheckBox("Launch Battery Guard PRO now", self)
        self.launch_cb.setChecked(True)
        self.launch_cb.setStyleSheet("color: #111827; font-size: 13px; font-weight: 600;")
        layout.addWidget(self.launch_cb)

    def validatePage(self):
        if self.launch_cb.isChecked() and hasattr(self.wizard(), 'dest_exe'):
            os.startfile(self.wizard().dest_exe)
        return True

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    wizard = QWizard()
    wizard.setWindowTitle("Battery Guard PRO Setup Wizard")
    wizard.resize(580, 420)
    wizard.setStyleSheet("""
        QWizard, QWizardPage {
            background-color: #FFFFFF;
            color: #111827;
        }
        QLabel {
            color: #111827;
            font-size: 13px;
        }
        QCheckBox {
            color: #111827;
            font-size: 13px;
            font-weight: 600;
        }
        QLineEdit {
            background-color: #F9FAFB;
            color: #111827;
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 12px;
        }
        QPushButton {
            background-color: #10B981;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 12px;
            padding: 8px 18px;
            border-radius: 8px;
            border: none;
        }
        QPushButton:hover {
            background-color: #059669;
        }
    """)

    wizard.addPage(WelcomePage(wizard))
    wizard.addPage(DirectoryPage(wizard))
    wizard.addPage(PerformInstallPage(wizard))
    wizard.addPage(FinishPage(wizard))

    wizard.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
