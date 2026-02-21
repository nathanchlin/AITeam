# CSS样式设计

**Agent**: coder

**Time**: 2026-02-17T17:04:44.038804

---

# CSS样式设计 - 美化Hello World页面

我将为您的Hello World页面添加美观的CSS样式，确保基本的响应式设计。以下是完整的解决方案：

## HTML结构

首先，我们有一个基础的HTML页面：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello World</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1 class="greeting">Hello World</h1>
        <p class="subtitle">欢迎来到我的网页</p>
    </div>
</body>
</html>
```

## CSS样式 (styles.css)

```css
/* 基础样式重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* 全局样式 */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #6e8efb, #a777e3);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* 容器样式 */
.container {
    text-align: center;
    padding: 2rem;
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    max-width: 600px;
    width: 90%;
    animation: fadeIn 1s ease-out;
}

/* 标题样式 */
.greeting {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #2c3e50;
    text-transform: uppercase;
    letter-spacing: 2px;
    position: relative;
    display: inline-block;
}

.greeting::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 100px;
    height: 4px;
    background: linear-gradient(to right, #6e8efb, #a777e3);
    border-radius: 2px;
}

/* 副标题样式 */
.subtitle {
    font-size: 1.2rem;
    color: #7f8c8d;
    margin-top: 1rem;
}

/* 动画效果 */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 1.5rem;
        width: 95%;
    }
    
    .greeting {
        font-size: 2.5rem;
    }
    
    .subtitle {
        font-size: 1rem;
    }
}

@media (max-width: 480px) {
    .container {
        padding: 1rem;
    }
    
    .greeting {
        font-size: 2rem;
    }
    
    .subtitle {
        font-size: 0.9rem;
    }
}
```

## 设计说明

1. **布局与排版**：
   - 使用Flexbox实现居中布局
   - 容器采用圆角和阴影效果，增加层次感
   - 标题使用大号字体和下划线装饰，突出显示

2. **颜色方案**：
   - 背景使用渐变色（蓝紫色系）
   - 文字使用深灰色，确保可读性
   - 装饰元素使用与背景协调的渐变色

3. **响应式设计**：
   - 使用媒体查询适配不同屏幕尺寸
   - 在小屏幕上减小字体大小和内边距
   - 容器宽度根据屏幕大小调整

4. **动画效果**：
   - 页面加载时淡入动画
   - 标题下方有装饰性下划线

5. **可维护性**：
   - 使用CSS变量便于主题定制（如果需要）
   - 结构化的注释便于后续修改
   - 模块化的样式组织

这个设计既美观又实用，在各种设备上都能良好显示，同时保持了代码的清晰和可维护性。