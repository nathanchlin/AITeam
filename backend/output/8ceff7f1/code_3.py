class SheepSheepGame:
    def __init__(self, difficulty=3):
        self.difficulty = difficulty
        self.card_generator = CardGenerator(difficulty)
        self.layout_optimizer = None
        self.cards = []
        self.selected_cards = []
        self.moves = 0
        self.score = 0
        
    def start_game(self):
        """开始新游戏"""
        # 生成卡片
        self.cards = self.card_generator.generate_cards()
        
        # 优化布局
        self.layout_optimizer = LayoutOptimizer(self.cards)
        self.cards = self.layout_optimizer.optimize_layout()
        
        # 重置游戏状态
        self.selected_cards = []
        self.moves = 0
        self.score = 0
        
        return self.cards
    
    def select_card(self, card_id):
        """选择卡片"""
        card = next((c for c in self.cards if c.id == card_id), None)
        if not card or card.is_removed:
            return False, "卡片已被消除或不存在"
            
        # 如果已经选择了两张卡片，先清除选择
        if len(self.selected_cards) >= 2:
            self.selected_cards = []
            
        # 添加到选中列表
        self.selected_cards.append(card)
        
        # 如果选择了两张卡片，检查是否匹配
        if len(self.selected_cards) == 2:
            return self._check_match()
            
        return True, "卡片已选中"
    
    def _check_match(self):
        """检查两张卡片是否匹配"""
        card1, card2 = self.selected_cards
        
        # 检查是否是同一类型
        if card1.type != card2.type:
            self.moves += 1
            return False, "卡片不匹配"
            
        # 检查是否可以消除(上层卡片或无遮挡)
        if not self._can_remove(card1) or not self._can_remove(card2):
            self.moves += 1
            return False, "卡片被遮挡，无法消除"
            
        # 消除卡片
        card1.is_removed = True
        card2.is_removed = True
        self.moves += 1
        self.score += 100
        
        # 清空选中列表
        self.selected_cards = []
        
        # 检查游戏是否结束
        if self._check_game_over():
            return True, "游戏胜利！"
            
        return True, "卡片匹配成功！"
    
    def _can_remove(self, card):
        """检查卡片是否可以消除"""
        # 顶层卡片总是可以消除
        if card.layer == self.difficulty - 1:
            return True
            
        # 检查上方是否有其他卡片遮挡
        for other in self.cards:
            if (other != card and not other.is_removed and 
                other.layer > card.layer and
                self._is_overlapping(other, card)):
                return False
                
        return True
    
    def _is_overlapping(self, upper_card, lower_card):
        """检查上层卡片是否遮挡下层卡片"""
        # 简单实现：基于位置和卡片大小
        size = 80  # 卡片大小
        ux, uy = upper_card.position
        lx, ly = lower_card.position
        
        # 计算中心点距离
        distance = ((ux - lx) ** 2 + (uy - ly) ** 2) ** 0.5
        
        # 如果距离小于卡片大小，认为遮挡
        return distance < size * 0.7
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        # 所有卡片都被消除
        remaining_cards = [c for c in self.cards if not c.is_removed]
        return len(remaining_cards) == 0