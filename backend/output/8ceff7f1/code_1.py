import random
from collections import defaultdict

class CardGenerator:
    def __init__(self, difficulty_level=3):
        self.difficulty_level = difficulty_level  # 游戏难度(层数)
        self.card_types = []  # 卡片类型列表
        self.cards = []  # 所有卡片对象
        
    def generate_cards(self):
        """生成卡片布局"""
        self.cards = []
        card_id = 0
        
        # 计算每层卡片数量(底层最多，逐层减少)
        cards_per_layer = self._calculate_cards_per_layer()
        
        # 生成卡片类型(每种类型出现3次，确保可解)
        self._generate_card_types(cards_per_layer)
        
        # 从底层到顶层生成卡片
        for layer in range(self.difficulty_level):
            layer_cards = []
            positions = self._generate_positions(cards_per_layer[layer], layer)
            
            for i, pos in enumerate(positions):
                card = Card(
                    id=card_id,
                    type=self.card_types[card_id],
                    layer=layer,
                    position=pos
                )
                self.cards.append(card)
                layer_cards.append(card)
                card_id += 1
                
            # 随机打乱同层卡片顺序
            random.shuffle(layer_cards)
            
        # 确保顶层卡片有足够的可消除卡片
        self._ensure_top_layer_solvable()
        
        return self.cards
    
    def _calculate_cards_per_layer(self):
        """计算每层卡片数量"""
        # 简单实现：底层最多，逐层减少
        base_cards = 9  # 底层卡片数
        cards_per_layer = []
        
        for i in range(self.difficulty_level):
            # 底层最多，顶层最少
            cards = base_cards - i * 2
            cards_per_layer.append(max(cards, 4))  # 每层至少4张
            
        return cards_per_layer
    
    def _generate_card_types(self, cards_per_layer):
        """生成卡片类型，确保每种类型有3张"""
        total_cards = sum(cards_per_layer)
        # 确保卡片类型数量是3的倍数
        type_count = total_cards // 3
        
        self.card_types = []
        for i in range(type_count):
            # 每种类型添加3张
            self.card_types.extend([i] * 3)
            
        # 如果有余数，添加额外类型
        remainder = total_cards % 3
        if remainder > 0:
            self.card_types.extend([type_count] * remainder)
            
        # 打乱顺序
        random.shuffle(self.card_types)
    
    def _generate_positions(self, count, layer):
        """生成卡片在层中的位置"""
        # 简单实现：按行列排列
        cols = 3  # 每层3列
        positions = []
        
        for i in range(count):
            row = i // cols
            col = i % cols
            # 添加一些随机偏移，使布局更自然
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            positions.append((col * 100 + offset_x, row * 100 + offset_y))
            
        return positions
    
    def _ensure_top_layer_solvable(self):
        """确保顶层有足够的可消除卡片"""
        top_layer_cards = [c for c in self.cards if c.layer == self.difficulty_level - 1]
        
        # 统计顶层每种卡片类型的数量
        type_counts = defaultdict(int)
        for card in top_layer_cards:
            type_counts[card.type] += 1
            
        # 确保至少有一对卡片在顶层
        has_pair = any(count >= 2 for count in type_counts.values())
        if not has_pair and len(top_layer_cards) >= 2:
            # 随机选择两张卡片设为相同类型
            card1, card2 = random.sample(top_layer_cards, 2)
            card2.type = card1.type