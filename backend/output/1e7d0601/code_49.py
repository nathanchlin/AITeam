class Level:
    def __init__(self, level_id, name, background_music, difficulty_multiplier=1.0):
        self.level_id = level_id
        self.name = name
        self.background_music = background_music
        self.difficulty_multiplier = difficulty_multiplier
        self.enemy_waves = []
        self.special_events = []
        self.objectives = []
        self.boss = None
        
    def add_enemy_wave(self, wave):
        self.enemy_waves.append(wave)
        
    def add_special_event(self, event):
        self.special_events.append(event)
        
    def add_objective(self, objective):
        self.objectives.append(objective)
        
    def set_boss(self, boss):
        self.boss = boss