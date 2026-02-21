class Card:
    def __init__(self, id, type, layer, position):
        self.id = id  # 唯一标识
        self.type = type  # 卡片类型(用于配对)
        self.layer = layer  # 所在层级(0为顶层)
        self.position = position  # 在层中的位置
        self.is_removed = False  # 是否已被消除