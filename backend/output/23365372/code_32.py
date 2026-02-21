# alert_system/integration/test_agent_integration.py
from alert_system.core.alert_manager import AlertManager, AlertLevel, EmailChannel, SlackChannel

class TestAgentAlertSystem:
    def __init__(self, config: Dict):
        self.alert_manager = AlertManager()
        self._setup_channels(config)
        self._setup_rules(config)
    
    def _setup_channels(self, config: Dict):
        # 配置邮件通知
        if "email" in config:
            email_config = config["email"]
            email_channel = EmailChannel(
                smtp_config=email_config["smtp"],
                recipients=email_config["recipients"]
            )
            self.alert_manager.add_notification_channel(email_channel)
        
        # 配置Slack通知
        if "slack" in config:
            slack_config = config["slack"]
            slack_channel = SlackChannel(
                webhook_url=slack_config["webhook_url"],
                channel=slack_config["channel"]
            )
            self.alert_manager.add_notification_channel(slack_channel)
    
    def _setup_rules(self, config: Dict):
        # 设置告警规则
        if "alert_rules" in config:
            for rule in config["alert_rules"]:
                self.alert_manager.add_alert_rule(rule)
        
        # 设置抑制规则
        if "suppression_rules" in config:
            for rule in config["suppression_rules"]:
                self.alert_manager.add_suppression_rule(rule)
    
    def alert_agent_selection_failure(self, agent_id: str, error_details: Dict):
        """当代理选择失败时发送告警"""
        alert_id = self.alert_manager.create_alert(
            level=AlertLevel.ERROR,
            message=f"Agent selection failed for agent {agent_id}",
            source="test_agent_selection",
            metadata={
                "agent_id": agent_id,
                "error": error_details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        return alert_id
    
    def alert_agent_performance_degradation(self, agent_id: str, metrics: Dict):
        """当代理性能下降时发送告警"""
        alert_id = self.alert_manager.create_alert(
            level=AlertLevel.WARNING,
            message=f"Performance degradation detected for agent {agent_id}",
            source="test_agent_selection",
            metadata={
                "agent_id": agent_id,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        return alert_id
    
    def alert_system_overload(self, load_metrics: Dict):
        """当系统过载时发送告警"""
        alert_id = self.alert_manager.create_alert(
            level=AlertLevel.CRITICAL,
            message="System overload detected",
            source="test_agent_selection",
            metadata={
                "load_metrics": load_metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        return alert_id