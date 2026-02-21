class LODObject:
    def __init__(self):
        self.models = {
            'high': load_model("high_detail.obj"),
            'medium': load_model("medium_detail.obj"),
            'low': load_model("low_detail.obj")
        }
        self.current_model = self.models['high']
    
    def update_lod(self, camera_distance):
        if camera_distance < 10:
            self.current_model = self.models['high']
        elif camera_distance < 30:
            self.current_model = self.models['medium']
        else:
            self.current_model = self.models['low']