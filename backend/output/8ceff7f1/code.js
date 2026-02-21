class CardMatchingGame {
    constructor() {
        this.cards = [];
        this.flippedCards = [];
        this.matchedPairs = 0;
        this.moves = 0;
        this.isProcessing = false;
        
        // 卡片内容 - 可以根据需要修改
        this.cardContents = ['🐑', '🐑', '🐐', '🐐', '🐮', '🐮', '🐷', '🐷', '🐶', '🐶', '🐱', '🐱'];
        
        this.init();
    }
    
    init() {
        // 初始化游戏
        this.createCards();
        this.renderCards();
        this.attachEventListeners();
        this.updateStats();
    }
    
    createCards() {
        // 创建卡片数组并打乱顺序
        const duplicatedContents = [...this.cardContents, ...this.cardContents];
        this.cards = duplicatedContents
            .map((content, index) => ({
                id: index,
                content: content,
                isFlipped: false,
                isMatched: false
            }))
            .sort(() => Math.random() - 0.5);
    }
    
    renderCards() {
        const cardGrid = document.getElementById('cardGrid');
        cardGrid.innerHTML = '';
        
        this.cards.forEach(card => {
            const cardElement = document.createElement('div');
            cardElement.className = 'card';
            cardElement.dataset.cardId = card.id;
            
            cardElement.innerHTML = `
                <div class="card-inner">
                    <div class="card-front">?</div>
                    <div class="card-back">${card.content}</div>
                </div>
            `;
            
            cardGrid.appendChild(cardElement);
        });
    }
    
    attachEventListeners() {
        // 卡片点击事件
        document.getElementById('cardGrid').addEventListener('click', (e) => {
            const cardElement = e.target.closest('.card');
            if (!cardElement || this.isProcessing) return;
            
            const cardId = parseInt(cardElement.dataset.cardId);
            this.handleCardClick(cardId);
        });
        
        // 重新开始按钮
        document.getElementById('restartBtn').addEventListener('click', () => {
            this.restart();
        });
    }
    
    handleCardClick(cardId) {
        const card = this.cards[cardId];
        
        // 如果卡片已经翻转或已匹配，则忽略点击
        if (card.isFlipped || card.isMatched) return;
        
        // 如果已经有两张卡片翻转，则忽略点击
        if (this.flippedCards.length >= 2) return;
        
        // 翻转卡片
        this.flipCard(cardId);
        
        // 如果翻转了两张卡片，检查是否匹配
        if (this.flippedCards.length === 2) {
            this.moves++;
            this.updateStats();
            this.checkForMatch();
        }
    }
    
    flipCard(cardId) {
        const card = this.cards[cardId];
        const cardElement = document.querySelector(`.card[data-card-id="${cardId}"]`);
        
        card.isFlipped = true;
        cardElement.classList.add('flipped');
        this.flippedCards.push(card);
    }
    
    checkForMatch() {
        this.isProcessing = true;
        
        const [card1, card2] = this.flippedCards;
        
        if (card1.content === card2.content) {
            // 匹配成功
            setTimeout(() => {
                this.handleMatch();
                this.isProcessing = false;
            }, 1000);
        } else {
            // 匹配失败
            setTimeout(() => {
                this.handleMismatch();
                this.isProcessing = false;
            }, 1000);
        }
    }
    
    handleMatch() {
        const [card1, card2] = this.flippedCards;
        
        // 标记卡片为已匹配
        card1.isMatched = true;
        card2.isMatched = true;
        
        // 添加匹配样式
        document.querySelector(`.card[data-card-id="${card1.id}"]`).classList.add('matched');
        document.querySelector(`.card[data-card-id="${card2.id}"]`).classList.add('matched');
        
        // 更新匹配计数
        this.matchedPairs++;
        this.updateStats();
        
        // 清空翻转卡片数组
        this.flippedCards = [];
        
        // 检查游戏是否结束
        if (this.matchedPairs === this.cardContents.length) {
            this.handleGameComplete();
        }
    }
    
    handleMismatch() {
        // 翻回卡片
        this.flipBackCards();
    }
    
    flipBackCards() {
        this.flippedCards.forEach(card => {
            card.isFlipped = false;
            const cardElement = document.querySelector(`.card[data-card-id="${card.id}"]`);
            cardElement.classList.remove('flipped');
        });
        
        this.flippedCards = [];
    }
    
    updateStats() {
        document.getElementById('moves').textContent = this.moves;
        document.getElementById('matches').textContent = this.matchedPairs;
    }
    
    handleGameComplete() {
        const message = document.getElementById('message');
        message.textContent = `恭喜！您用了 ${this.moves} 步完成了游戏！`;
        message.style.display = 'block';
    }
    
    restart() {
        // 重置游戏状态
        this.flippedCards = [];
        this.matchedPairs = 0;
        this.moves = 0;
        this.isProcessing = false;
        
        // 隐藏消息
        document.getElementById('message').style.display = 'none';
        
        // 重新初始化游戏
        this.init();
    }
}

// 启动游戏
document.addEventListener('DOMContentLoaded', () => {
    new CardMatchingGame();
});