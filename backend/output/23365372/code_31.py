# alert_system/core/alert_manager.py
from typing import Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime
import logging
import json
from abc import ABC, abstractmethod

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class Alert:
    def __init__(self, 
                 alert_id: str,
                 level: AlertLevel,
                 message: str,
                 source: str,
                 metadata: Optional[Dict] = None):
        self.alert_id = alert_id
        self.level = level
        self.message = message
        self.source = source
        self.timestamp = datetime.utcnow()
        self.status = AlertStatus.ACTIVE
        self.metadata = metadata or {}
        self.history = []
    
    def to_dict(self) -> Dict:
        return {
            "id": self.alert_id,
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "metadata": self.metadata
        }

class NotificationChannel(ABC):
    @abstractmethod
    def send(self, alert: Alert) -> bool:
        pass

class EmailChannel(NotificationChannel):
    def __init__(self, smtp_config: Dict, recipients: List[str]):
        self.smtp_config = smtp_config
        self.recipients = recipients
    
    def send(self, alert: Alert) -> bool:
        try:
            # 实现邮件发送逻辑
            logging.info(f"Sending email alert {alert.alert_id} to {self.recipients}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email alert: {str(e)}")
            return False

class SlackChannel(NotificationChannel):
    def __init__(self, webhook_url: str, channel: str):
        self.webhook_url = webhook_url
        self.channel = channel
    
    def send(self, alert: Alert) -> bool:
        try:
            # 实现Slack通知逻辑
            payload = {
                "channel": self.channel,
                "text": f"Alert: {alert.level.value.upper()} - {alert.message}",
                "attachments": [alert.to_dict()]
            }
            # 发送HTTP请求到Slack webhook
            logging.info(f"Sending Slack alert {alert.alert_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {str(e)}")
            return False

class AlertManager:
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.notification_channels: List[NotificationChannel] = []
        self.alert_rules: List[Dict] = []
        self.suppression_rules: List[Dict] = []
        self.alert_history: List[Dict] = []
    
    def add_notification_channel(self, channel: NotificationChannel):
        self.notification_channels.append(channel)
    
    def add_alert_rule(self, rule: Dict):
        self.alert_rules.append(rule)
    
    def add_suppression_rule(self, rule: Dict):
        self.suppression_rules.append(rule)
    
    def create_alert(self, 
                    level: AlertLevel,
                    message: str,
                    source: str,
                    metadata: Optional[Dict] = None) -> str:
        alert_id = f"{source}_{datetime.utcnow().timestamp()}"
        alert = Alert(alert_id, level, message, source, metadata)
        
        # 检查抑制规则
        if self._is_suppressed(alert):
            alert.status = AlertStatus.SUPPRESSED
            logging.info(f"Alert {alert_id} suppressed by rule")
        
        self.alerts[alert_id] = alert
        self.alert_history.append(alert.to_dict())
        
        # 发送通知
        if alert.status != AlertStatus.SUPPRESSED:
            self._send_notifications(alert)
        
        return alert_id
    
    def _is_suppressed(self, alert: Alert) -> bool:
        for rule in self.suppression_rules:
            if self._evaluate_rule(alert, rule):
                return True
        return False
    
    def _evaluate_rule(self, alert: Alert, rule: Dict) -> bool:
        # 实现规则评估逻辑
        # 示例: 检查源是否在抑制列表中
        if "source" in rule and alert.source in rule["source"]:
            return True
        
        # 检查级别是否低于抑制阈值
        if "min_level" in rule:
            min_level = AlertLevel(rule["min_level"])
            if alert.level.value < min_level.value:
                return True
        
        # 可以添加更多规则评估逻辑
        return False
    
    def _send_notifications(self, alert: Alert):
        for channel in self.notification_channels:
            try:
                channel.send(alert)
            except Exception as e:
                logging.error(f"Failed to send notification via {type(channel).__name__}: {str(e)}")
    
    def resolve_alert(self, alert_id: str):
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            self.alert_history.append(alert.to_dict())
            logging.info(f"Alert {alert_id} resolved")
    
    def get_active_alerts(self) -> List[Alert]:
        return [alert for alert in self.alerts.values() if alert.status == AlertStatus.ACTIVE]