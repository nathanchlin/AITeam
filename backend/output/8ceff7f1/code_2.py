class LayoutOptimizer:
    def __init__(self, cards):
        self.cards = cards
        
    def optimize_layout(self):
        """优化卡片布局，确保游戏可玩性"""
        # 1. 确保卡片不会重叠过多
        self._minimize_overlap()
        
        # 2. 确保底层卡片被上层卡片部分覆盖
        self._ensure_layer_coverage()
        
        # 3. 调整卡片位置使布局更自然
        self._naturalize_positions()
        
        return self.cards
    
    def _minimize_overlap(self):
        """最小化卡片重叠"""
        # 按层分组处理
        layers = defaultdict(list)
        for card in self.cards:
            layers[card.layer].append(card)
            
        # 对每层进行优化
        for layer in layers:
            self._optimize_layer(layers[layer])
    
    def _optimize_layer(self, layer_cards):
        """优化单层卡片布局"""
        # 简单实现：检测重叠并调整位置
        for i, card1 in enumerate(layer_cards):
            for card2 in layer_cards[i+1:]:
                if self._cards_overlap(card1, card2):
                    # 轻微调整位置减少重叠
                    offset_x = random.randint(-20, 20)
                    offset_y = random.randint(-20, 20)
                    card2.position = (
                        card2.position[0] + offset_x,
                        card2.position[1] + offset_y
                    )
    
    def _cards_overlap(self, card1, card2):
        """检查两张卡片是否重叠"""
        # 简单实现：基于位置和卡片大小
        size = 80  # 卡片大小
        x1, y1 = card1.position
        x2, y2 = card2.position
        
        # 计算中心点距离
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        
        # 如果距离小于卡片大小，认为重叠
        return distance < size * 0.8
    
    def _ensure_layer_coverage(self):
        """确保上层卡片覆盖下层卡片"""
        # 按层从上到下处理
        for layer in range(self.difficulty_level - 1, 0, -1):
            upper_cards = [c for c in self.cards if c.layer == layer]
            lower_cards = [c for c in self.cards if c.layer == layer - 1]
            
            # 确保上层卡片覆盖下层卡片
            for upper in upper_cards:
                # 随机选择一个下层卡片进行部分覆盖
                if lower_cards:
                    lower = random.choice(lower_cards)
                    self._adjust_coverage(upper, lower)
    
    def _adjust_coverage(self, upper_card, lower_card):
        """调整上下卡片位置实现覆盖效果"""
        # 简单实现：将上层卡片略微偏移到下层卡片上方
        x, y = upper_card.position
        upper_card.position = (x + random.randint(-20, 20), y - 10)
    
    def _naturalize_positions(self):
        """使卡片布局更自然"""
        # 按层分组处理
        layers = defaultdict(list)
        for card in self.cards:
            layers[card.layer].append(card)
            
        # 对每层进行微调
        for layer in layers:
            self._naturalize_layer(layers[layer])
    
    def _naturalize_layer(self, layer_cards):
        """使单层卡片布局更自然"""
        # 添加轻微随机偏移
        for card in layer_cards:
            x, y = card.position
            offset_x = random.randint(-15, 15)
            offset_y = random.randint(-15, 15)
            card.position = (x + offset_x, y + offset_y)