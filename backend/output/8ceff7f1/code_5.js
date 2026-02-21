class Card {
    constructor(type, id, position) {
        this.type = type;
        this.id = id;
        this.position = position;
        this.element = null;
        this.isSelected = false;
        this.isMatched = false;
        this.imageUrl = `assets/images/${type}.png`;
    }
    
    // 创建卡片DOM元素
    createElement() {
        const cardSize = DeviceDetector.getCardSize();
        const { spacing } = DeviceDetector.getLayoutParams();
        
        this.element = document.createElement('div');
        this.element.className = 'card';
        this.element.id = this.id;
        this.element.style.width = `${cardSize.width}px`;
        this.element.style.height = `${cardSize.height}px`;
        this.element.style.left = `${this.position.x * (cardSize.width + spacing)}px`;
        this.element.style.top = `${this.position.y * (cardSize.height + spacing)}px`;
        this.element.style.zIndex = this.position.y + 1;
        
        const img = document.createElement('img');
        img.src = this.imageUrl;
        img.alt = `Card ${this.type}`;
        
        this.element.appendChild(img);
        
        // 添加点击事件
        this.element.addEventListener('click', () => this.handleClick());
        
        return this.element;
    }
    
    // 处理卡片点击
    handleClick() {
        if (this.isMatched || this.isSelected) return;
        
        // 触发自定义事件
        const event = new CustomEvent('cardSelected', {
            detail: this,
            bubbles: true
        });
        this.element.dispatchEvent(event);
    }
    
    // 选中卡片
    select() {
        this.isSelected = true;
        this.element.classList.add('selected');
    }
    
    // 取消选中
    deselect() {
        this.isSelected = false;
        this.element.classList.remove('selected');
    }
    
    // 匹配卡片
    match() {
        this.isMatched = true;
        this.element.classList.add('matched');
        
        // 动画结束后移除元素
        setTimeout(() => {
            if (this.element && this.element.parentNode) {
                this.element.parentNode.removeChild(this.element);
            }
        }, 300);
    }
    
    // 检查两张卡片是否匹配
    static isMatch(card1, card2) {
        return card1.type === card2.type && card1.id !== card2.id;
    }
}

// 卡片布局算法
class CardLayout {
    constructor(rows, cols) {
        this.rows = rows;
        this.cols = cols;
        this.positions = [];
        this.generatePositions();
    }
    
    // 生成卡片位置
    generatePositions() {
        // 生成金字塔形布局
        const positions = [];
        
        // 底层最多卡片
        const maxCards = this.rows * this.cols;
        
        // 卡片类型列表
        const cardTypes = ['sheep', 'wolf', 'grass', 'water', 'mountain', 'tree'];
        
        // 计算每种卡片需要的数量
        const totalPairs = Math.floor(maxCards / 2);
        const cardsPerType = Math.floor(totalPairs / cardTypes.length);
        
        // 创建卡片数组
        let cards = [];
        cardTypes.forEach((type, index) => {
            const count = index === cardTypes.length - 1 
                ? totalPairs - (cardsPerType * (cardTypes.length - 1)) 
                : cardsPerType;
            
            for (let i = 0; i < count; i++) {
                cards.push(type, type); // 添加一对
            }
        });
        
        // 如果卡片总数不足，添加额外的随机卡片
        while (cards.length < maxCards) {
            const randomType = cardTypes[Math.floor(Math.random() * cardTypes.length)];
            cards.push(randomType);
        }
        
        // 确保有偶数个卡片
        if (cards.length % 2 !== 0) {
            cards.pop();
        }
        
        // 打乱卡片顺序
        cards = shuffleArray(cards);
        
        // 生成卡片位置
        let cardIndex = 0;
        for (let row = 0; row < this.rows && cardIndex < cards.length; row++) {
            const colsInRow = this.cols - Math.floor(row / 2);
            for (let col = 0; col < colsInRow && cardIndex < cards.length; col++) {
                positions.push({
                    x: col + Math.floor(row / 2),
                    y: row,
                    type: cards[cardIndex]
                });
                cardIndex++;
            }
        }
        
        this.positions = positions;
    }
    
    // 获取卡片位置
    getPositions() {
        return this.positions;
    }
}