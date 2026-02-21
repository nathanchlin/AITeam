# alert_system/core/alert_aggregation.py
from typing import Dict, List
from collections import defaultdict
from .alert_manager import Alert, AlertLevel

class AlertAggregator:
    def __init__(self, time_window: int = 300):  # 5分钟窗口
        self.time_window = time_window
        self.alert_buckets = defaultdict(list)
    
    def add_alert(self, alert: Alert):
        import time
        current_time = time.time()
        # 清理过期的告警
        self._cleanup_old_alerts(current_time)
        # 添加新告警
        self.alert_buckets[alert.alert_id].append((current_time, alert))
    
    def _cleanup_old_alerts(self, current_time: float):
        cutoff = current_time - self.time_window
        for alert_id in list(self.alert_buckets.keys()):
            self.alert_buckets[alert_id] = [
                (ts, alert) for ts, alert in self.alert_buckets[alert_id] 
                if ts > cutoff
            ]
            if not self.alert_buckets[alert_id]:
                del self.alert_buckets[alert_id]
    
    def get_aggregated_alerts(self) -> List[Alert]:
        """返回聚合后的告警列表"""
        aggregated = []
        for alert_id, alerts in self.alert_buckets.items():
            if len(alerts) > 1:
                # 创建聚合告警
                first_alert = alerts[0][1]
                aggregated_alert = Alert(
                    alert_id=f"aggregated_{alert_id}",
                    level=AlertLevel.WARNING,
                    message=f"Repeated alert: {first_alert.message} (occurred {len(alerts)} times)",
                    source=first_alert.source,
                    metadata={
                        "original_alert_id": alert_id,
                        "count": len(alerts),
                        "first_occurrence": alerts[0][0],
                        "last_occurrence": alerts[-1][0]
                    }
                )
                aggregated.append(aggregated_alert)
        return aggregated