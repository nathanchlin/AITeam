def set_key_mapping(self, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT):
       """自定义按键映射"""
       self.key_states = {
           left_key: False,
           right_key: False
       }