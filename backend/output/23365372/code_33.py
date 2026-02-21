# alert_system/example/usage_example.py
from alert_system.integration.test_agent_integration import TestAgentAlertSystem
from alert_system.core.alert_manager import AlertLevel
import json

# 配置告警系统
config = {
    "email": {
        "smtp": {
            "host": "smtp.example.com",
            "port": 587,
            "username": "alerts@example.com",
            "password": "password"
        },
        "recipients": ["admin@example.com", "dev-team@example.com"]
    },
    "slack": {
        "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        "channel": "#alerts"
    },
    "alert_rules": [
        {
            "name": "high_priority_alerts",
            "conditions": {
                "level": ["error", "critical"]
            },
            "actions": ["notify_all"]
        }
    ],
    "suppression_rules": [
        {
            "name": "maintenance_mode",
            "source": ["maintenance"],
            "min_level": "critical"
        }
    ]
}

# 初始化告警系统
alert_system = TestAgentAlertSystem(config)

# 模拟代理选择失败
try:
    # 这里是您的代理选择逻辑
    # raise Exception("Failed to connect to agent")
    pass
except Exception as e:
    alert_system.alert_agent_selection_failure(
        agent_id="agent-123",
        error_details={"error": str(e), "type": type(e).__name__}
    )

# 模拟性能下降
performance_metrics = {
    "response_time": 5000,  # 5秒
    "error_rate": 0.15,     # 15%
    "throughput": 10        # 10 req/s
}
alert_system.alert_agent_performance_degradation(
    agent_id="agent-456",
    metrics=performance_metrics
)

# 获取所有活跃告警
active_alerts = alert_system.alert_manager.get_active_alerts()
print(f"Active alerts: {len(active_alerts)}")
for alert in active_alerts:
    print(f"- {alert.alert_id}: {alert.message} ({alert.level.value})")