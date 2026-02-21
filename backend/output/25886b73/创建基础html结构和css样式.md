# 创建基础HTML结构和CSS样式

**Agent**: coder

**Time**: 2026-02-17T18:06:13.161133

---

# 计算器网页实现

我将为您创建一个基础的计算器HTML结构和CSS样式，确保界面美观且响应式布局。

## HTML结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>简单计算器</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="calculator-container">
        <h1>简单计算器</h1>
        <div class="calculator">
            <div class="display">
                <div id="previous-operation"></div>
                <div id="current-operation">0</div>
            </div>
            <div class="buttons">
                <button class="btn btn-clear">C</button>
                <button class="btn btn-delete">DEL</button>
                <button class="btn btn-operation">÷</button>
                <button class="btn btn-operation">×</button>
                
                <button class="btn btn-number">7</button>
                <button class="btn btn-number">8</button>
                <button class="btn btn-number">9</button>
                <button class="btn btn-operation">-</button>
                
                <button class="btn btn-number">4</button>
                <button class="btn btn-number">5</button>
                <button class="btn btn-number">6</button>
                <button class="btn btn-operation">+</button>
                
                <button class="btn btn-number">1</button>
                <button class="btn btn-number">2</button>
                <button class="btn btn-number">3</button>
                <button class="btn btn-equals" rowspan="2">=</button>
                
                <button class="btn btn-number btn-zero">0</button>
                <button class="btn btn-number">.</button>
            </div>
        </div>
    </div>
    
    <script src="script.js"></script>
</body>
</html>
```

## CSS样式

```css
/* 全局样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Arial', sans-serif;
}

body {
    background-color: #f5f5f5;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
}

/* 计算器容器 */
.calculator-container {
    width: 100%;
    max-width: 400px;
    text-align: center;
}

h1 {
    color: #333;
    margin-bottom: 20px;
    font-size: 28px;
}

/* 计算器主体 */
.calculator {
    background-color: #333;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    overflow: hidden;
}

/* 显示区域 */
.display {
    background-color: #222;
    color: white;
    padding: 20px;
    text-align: right;
    min-height: 80px;
}

#previous-operation {
    font-size: 18px;
    color: #aaa;
    min-height: 24px;
}

#current-operation {
    font-size: 32px;
    min-height: 40px;
}

/* 按钮区域 */
.buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background-color: #444;
}

/* 按钮通用样式 */
.btn {
    background-color: #555;
    border: none;
    color: white;
    font-size: 20px;
    padding: 20px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.btn:hover {
    background-color: #666;
}

.btn:active {
    background-color: #777;
    transform: scale(0.98);
}

/* 数字按钮 */
.btn-number {
    background-color: #666;
}

.btn-number:hover {
    background-color: #777;
}

/* 运算符按钮 */
.btn-operation {
    background-color: #ff9500;
}

.btn-operation:hover {
    background-color: #ffb143;
}

/* 等号按钮 */
.btn-equals {
    background-color: #ff9500;
    grid-row: span 2;
}

.btn-equals:hover {
    background-color: #ffb143;
}

/* 特殊按钮 */
.btn-clear {
    background-color: #a55eea;
}

.btn-clear:hover {
    background-color: #b574f0;
}

.btn-delete {
    background-color: #ff6b6b;
}

.btn-delete:hover {
    background-color: #ff8787;
}

.btn-zero {
    grid-column: span 2;
}

/* 响应式设计 */
@media (max-width: 480px) {
    .calculator-container {
        max-width: 100%;
    }
    
    .btn {
        padding: 15px;
        font-size: 18px;
    }
    
    #current-operation {
        font-size: 24px;
    }
}

@media (max-width: 320px) {
    .btn {
        padding: 12px;
        font-size: 16px;
    }
    
    #current-operation {
        font-size: 20px;
    }
}
```

## 设计说明

1. **响应式布局**：
   - 使用Flexbox布局使计算器在页面中居中
   - 设置最大宽度确保在大屏幕上不会过大
   - 使用媒体查询适配不同屏幕尺寸

2. **视觉设计**：
   - 深色主题，减少视觉疲劳
   - 不同类型按钮使用不同颜色区分（数字、运算符、特殊功能）
   - 添加悬停和点击效果增强交互体验
   - 圆角和阴影效果提升现代感

3. **用户体验**：
   - 清晰的显示屏区域，显示当前操作和上一个操作
   - 按钮大小适中，便于触摸操作
   - 特殊按钮（清除、删除）使用醒目颜色
   - 零按钮跨两列，提高易用性

这个设计既美观又实用，在各种设备上都能良好显示。下一步可以添加JavaScript逻辑来实现计算器的功能。