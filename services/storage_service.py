import sqlite3
import os
import datetime
from pathlib import Path

class StorageService:
    def __init__(self):
        app_data = Path(os.environ.get('APPDATA', os.path.expanduser('~'))) / 'BatteryManager'
        app_data.mkdir(parents=True, exist_ok=True)
        self.db_path = app_data / 'battery_manager.db'
        self._init_db()
        self.purge_old_data()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            # Battery logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS battery_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    date TEXT,
                    percent INTEGER,
                    is_charging INTEGER
                )
            ''')
            # App usage table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    process_name TEXT,
                    app_name TEXT,
                    duration_seconds INTEGER,
                    last_active TEXT,
                    UNIQUE(date, process_name)
                )
            ''')
            conn.commit()

            # Set default settings if not exist
            defaults = {
                'threshold': '80',
                'sound': 'digital',
                'volume': '80',
                'alarm_enabled': '1'
            }
            for k, v in defaults.items():
                cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (k, v))
            conn.commit()

    # 10-DAY AUTOMATED RETENTION CLEANUP
    def purge_old_data(self):
        today = datetime.date.today()
        cutoff_date = (today - datetime.timedelta(days=9)).strftime('%Y-%m-%d') # Keep today + 9 prior days = 10 days total

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM battery_logs WHERE date < ?', (cutoff_date,))
            cursor.execute('DELETE FROM app_usage WHERE date < ?', (cutoff_date,))
            conn.commit()

    def get_setting(self, key, default=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def set_setting(self, key, value):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
            conn.commit()

    def record_battery_log(self, percent, is_charging):
        now = datetime.datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        ts_str = now.strftime('%Y-%m-%d %H:%M:%S')

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO battery_logs (timestamp, date, percent, is_charging)
                VALUES (?, ?, ?, ?)
            ''', (ts_str, date_str, percent, 1 if is_charging else 0))
            conn.commit()

    def record_app_usage(self, process_name, app_name, duration_seconds=2):
        date_str = datetime.date.today().strftime('%Y-%m-%d')
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO app_usage (date, process_name, app_name, duration_seconds, last_active)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(date, process_name) DO UPDATE SET
                    duration_seconds = duration_seconds + ?,
                    last_active = ?
            ''', (date_str, process_name, app_name, duration_seconds, now_str, duration_seconds, now_str))
            conn.commit()

    def get_battery_logs(self, limit=100):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT timestamp, date, percent, is_charging FROM battery_logs ORDER BY id DESC LIMIT ?', (limit,))
            return cursor.fetchall()

    def get_app_usage_by_date(self, date_str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT process_name, app_name, duration_seconds, last_active FROM app_usage WHERE date = ? ORDER BY duration_seconds DESC', (date_str,))
            return cursor.fetchall()

    def get_all_dates_with_data(self):
        dates = []
        today = datetime.date.today()
        for i in range(10):
            d = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(d)
        return dates
