class Objective:
    def __init__(self, description, condition, reward):
        self.description = description
        self.condition = condition
        self.reward = reward
        self.completed = False
        
    def check_completion(self, game_state):
        if not self.completed and self.condition(game_state):
            self.completed = True
            return self.reward
        return 0

# 示例目标
def destroy_half_aa_cannons(game_state):
    destroyed = game_state['destroyed_aa_cannons']
    total = game_state['total_aa_cannons']
    return destroyed >= total / 2

objective = Objective("摧毁至少一半的防空炮", destroy_half_aa_cannons, 500)