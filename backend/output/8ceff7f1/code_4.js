// 设备检测
const DeviceDetector = {
    isMobile: () => /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
    isTablet: () => /iPad|Android/i.test(navigator.userAgent) && window.innerWidth > 768,
    isDesktop: () => !DeviceDetector.isMobile() && !DeviceDetector.isTablet(),
    
    // 获取设备类型
    getDeviceType: () => {
        if (DeviceDetector.isMobile()) return 'mobile';
        if (DeviceDetector.isTablet()) return 'tablet';
        return 'desktop';
    },
    
    // 获取卡片尺寸
    getCardSize: () => {
        const deviceType = DeviceDetector.getDeviceType();
        switch (deviceType) {
            case 'mobile':
                return { width: 50, height: 65 };
            case 'tablet':
                return { width: 60, height: 75 };
            default:
                return { width: 80, height: 100 };
        }
    },
    
    // 获取卡片布局参数
    getLayoutParams: () => {
        const deviceType = DeviceDetector.getDeviceType();
        switch (deviceType) {
            case 'mobile':
                return {
                    rows: 7,
                    cols: 9,
                    spacing: 5
                };
            case 'tablet':
                return {
                    rows: 8,
                    cols: 10,
                    spacing: 8
                };
            default:
                return {
                    rows: 9,
                    cols: 12,
                    spacing: 10
                };
        }
    }
};

// 格式化时间
const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

// 防抖函数
const debounce = (func, delay) => {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
};

// 随机打乱数组
const shuffleArray = (array) => {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
};

// 检查是否有解
const hasSolution = (cards) => {
    // 简化的解检查算法
    // 实际实现可能需要更复杂的逻辑
    const cardCounts = {};
    cards.forEach(card => {
        if (cardCounts[card.type]) {
            cardCounts[card.type]++;
        } else {
            cardCounts[card.type] = 1;
        }
    });
    
    // 检查每种卡片类型是否有偶数个
    for (const count of Object.values(cardCounts)) {
        if (count % 2 !== 0) {
            return false;
        }
    }
    
    return true;
};

// 生成卡片ID
const generateCardId = () => {
    return 'card-' + Math.random().toString(36).substr(2, 9);
};