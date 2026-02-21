class EventSystem:
    _listeners = {}
    
    @staticmethod
    def on(event_name, callback):
        """注册事件监听器"""
        if event_name not in EventSystem._listeners:
            EventSystem._listeners[event_name] = []
        EventSystem._listeners[event_name].append(callback)
    
    @staticmethod
    def emit(event_name, data=None):
        """触发事件"""
        if event_name in EventSystem._listeners:
            for callback in EventSystem._listeners[event_name]:
                callback(data)