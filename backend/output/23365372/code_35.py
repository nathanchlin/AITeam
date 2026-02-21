# alert_system/dashboard/alert_dashboard.py
from flask import Flask, jsonify, render_template
from .core.alert_manager import AlertManager, AlertLevel
from .core.alert_aggregation import AlertAggregator
import threading

class AlertDashboard:
    def __init__(self, alert_manager: AlertManager):
        self.app = Flask(__name__)
        self.alert_manager = alert_manager
        self.aggregator = AlertAggregator()
        self._setup_routes()
        self._start_background_task()
    
    def _setup_routes(self):
        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')
        
        @self.app.route('/api/alerts')
        def get_alerts():
            active_alerts = self.alert_manager.get_active_alerts()
            aggregated_alerts = self.aggregator.get_aggregated_alerts()
            
            all_alerts = active_alerts + aggregated_alerts
            return jsonify([alert.to_dict() for alert in all_alerts])
        
        @self.app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
        def resolve_alert(alert_id):
            self.alert_manager.resolve_alert(alert_id)
            return jsonify({"status": "resolved"})
    
    def _start_background_task(self):
        def update_aggregator():
            while True:
                for alert in self.alert_manager.get_active_alerts():
                    self.aggregator.add_alert(alert)
                time.sleep(60)  # 每分钟更新一次
        
        thread = threading.Thread(target=update_aggregator)
        thread.daemon = True
        thread.start()
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        self.app.run(host=host, port=port, debug=debug)