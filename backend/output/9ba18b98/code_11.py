# 更新分数和等级
if lines_to_clear:
    self.lines_cleared += len(lines_to_clear)
    self.score += [40, 100, 300, 1200][len(lines_to_clear) - 1] * self.level
    self.level = 1 + self.lines_cleared // 10
    self.fall_speed = max(100, 1000 - (self.level - 1) * 100)