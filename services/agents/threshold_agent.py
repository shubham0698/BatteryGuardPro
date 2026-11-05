class DynamicThresholdAgent:
    def __init__(self, storage_service):
        self.storage = storage_service

    def analyze_and_suggest(self):
        logs = self.storage.get_battery_logs(limit=1000)
        if not logs:
            return 80, "Default threshold mode active. Collect more logs for smart adaptation."

        # Calculate AC power ratio (time plugged in vs battery)
        ac_count = sum(1 for log in logs if log[3] == 1)
        total_count = len(logs)
        ac_ratio = ac_count / total_count if total_count > 0 else 1.0

        if ac_ratio >= 0.75:
            return 75, "You spend 75%+ time on AC power. Recommended 75% limit to reduce cell voltage stress."
        elif ac_ratio <= 0.35:
            return 90, "High battery mobility detected. Recommended 90% limit for maximum unplugged screen time."
        else:
            return 80, "Balanced stationary & mobile usage detected. Recommended optimal 80% limit."
