class BatteryHealthAgent:
    def __init__(self, storage_service):
        self.storage = storage_service

    def calculate_health_insights(self):
        logs = self.storage.get_battery_logs(limit=5000)
        threshold = int(self.storage.get_setting('threshold', '80'))

        if not logs:
            return {
                'score': 95,
                'status': 'Optimal Battery Health',
                'avoided_cycles': 0,
                'protected_hours': 0.0,
                'deep_discharges': 0,
                'months_gained': 0.5,
                'advice': f"Your charging threshold is active at <b>{threshold}%</b>. Capping charge level between 75%–85% prevents high-voltage cell degradation, extending overall pack lifespan."
            }

        total_logs = len(logs)
        charging_logs = [log for log in logs if log[3] == 1]
        charging_count = len(charging_logs)

        # Count safe charging logs (where percent <= max(threshold, 85))
        safe_charge_count = sum(1 for log in charging_logs if log[2] <= max(threshold, 85))
        overcharge_count = sum(1 for log in charging_logs if log[2] > 85)
        deep_discharges = sum(1 for log in logs if log[2] < 15)

        protected_hours = round((safe_charge_count * 1) / 60.0, 1)
        avoided_cycles = max(1 if safe_charge_count > 0 else 0, int(safe_charge_count / 15))
        months_gained = round(max(0.5, (safe_charge_count / 60.0) * 0.15), 1)

        score = 100
        if charging_count > 0:
            overcharge_ratio = overcharge_count / charging_count
            score -= int(overcharge_ratio * 25)
        if deep_discharges > 0:
            score -= min(20, deep_discharges * 5)
        score = max(65, min(100, score))

        if score >= 90:
            status = "Optimal Battery Health"
        elif score >= 75:
            status = "Good Battery Health"
        else:
            status = "High Cell Stress Level"

        if avoided_cycles > 0:
            advice = (
                f"Protected <b>{protected_hours} hrs</b> of charging under safe {threshold}% limit. "
                f"Avoided ~<b>{avoided_cycles} high-voltage stress cycles</b>, gaining approximately <b>+{months_gained} months</b> of pack lifespan."
            )
        else:
            advice = (
                f"Target threshold of <b>{threshold}%</b> active. "
                f"Keep your charger unplugged at {threshold}% to protect lithium-ion cell chemistry."
            )

        return {
            'score': score,
            'status': status,
            'avoided_cycles': avoided_cycles,
            'protected_hours': protected_hours,
            'deep_discharges': deep_discharges,
            'months_gained': months_gained,
            'advice': advice
        }

