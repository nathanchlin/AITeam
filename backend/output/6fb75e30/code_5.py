class CharacterController:
    def __init__(self, character):
        self.character = character
        self.input_handler = InputHandler()
    
    def handle_input(self):
        """处理用户输入"""
        if self.input_handler.is_jump_pressed():
            self.character.jump()
        if self.input_handler.is_slide_pressed():
            self.character.slide()
    
    def update(self, delta_time):
        """更新控制器"""
        self.handle_input()
        self.character.update(delta_time)