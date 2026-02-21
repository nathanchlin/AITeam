# 添加CSS样式

**Agent**: coder

**Time**: 2026-02-17T18:56:23.929299

---

我来为计数器网页添加美观的CSS样式。下面是一个完整的HTML文件，包含了内联CSS样式，实现了现代化的计数器界面：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>计数器应用</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 400px;
            width: 100%;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }

        .container:hover {
            transform: translateY(-5px);
        }

        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 2.2rem;
            font-weight: 600;
        }

        .counter-display {
            background: linear-gradient(145deg, #f0f0f0, #e6e6e6);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 
                inset 5px 5px 10px #d1d1d1,
                inset -5px -5px 10px #ffffff;
        }

        .counter-value {
            font-size: 4rem;
            font-weight: 700;
            color: #667eea;
            line-height: 1;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }

        .counter-label {
            font-size: 1rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        .btn {
            background: linear-gradient(145deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 12px 25px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            min-width: 100px;
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }

        .btn:active {
            transform: translateY(0);
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
        }

        .btn-reset {
            background: linear-gradient(145deg, #f093fb, #f5576c);
            box-shadow: 0 5px 15px rgba(245, 87, 108, 0.3);
        }

        .btn-reset:hover {
            box-shadow: 0 8px 20px rgba(245, 87, 108, 0.4);
        }

        .btn:disabled {
            background: #cccccc;
            cursor: not-allowed;
            box-shadow: none;
        }

        .btn:disabled:hover {
            transform: none;
            box-shadow: none;
        }

        .message {
            margin-top: 20px;
            padding: 10px;
            border-radius: 10px;
            font-size: 0.9rem;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .message.show {
            opacity: 1;
        }

        .message.error {
            background-color: rgba(245, 87, 108, 0.2);
            color: #f5576c;
        }

        .message.success {
            background-color: rgba(102, 126, 234, 0.2);
            color: #667eea;
        }

        @media (max-width: 480px) {
            .container {
                padding: 30px 20px;
            }

            h1 {
                font-size: 1.8rem;
            }

            .counter-value {
                font-size: 3rem;
            }

            .buttons {
                flex-direction: column;
                gap: 10px;
            }

            .btn {
                width: 100%;
            }
        }

        /* 动画效果 */
        @keyframes pulse {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
            100% {
                transform: scale(1);
            }
        }

        .counter-value.pulse {
            animation: pulse 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>计数器应用</h1>
        
        <div class="counter-display">
            <div class="counter-value" id="counterValue">0</div>
            <div class="counter-label">当前计数</div>
        </div>
        
        <div class="buttons">
            <button class="btn" id="decreaseBtn">减少</button>
            <button class="btn" id="increaseBtn">增加</button>
        </div>
        
        <button class="btn btn-reset" id="resetBtn">重置</button>
        
        <div class="message" id="message"></div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const counterValue = document.getElementById('counterValue');
            const decreaseBtn = document.getElementById('decreaseBtn');
            const increaseBtn = document.getElementById('increaseBtn');
            const resetBtn = document.getElementById('resetBtn');
            const message = document.getElementById('message');
            
            let count = 0;
            
            // 更新计数器显示
            function updateCounter() {
                counterValue.textContent = count;
                counterValue.classList.add('pulse');
                setTimeout(() => {
                    counterValue.classList.remove('pulse');
                }, 300);
                
                // 禁用减少按钮当计数为0时
                decreaseBtn.disabled = count <= 0;
            }
            
            // 显示消息
            function showMessage(text, type) {
                message.textContent = text;
                message.className = `message show ${type}`;
                
                setTimeout(() => {
                    message.classList.remove('show');
                }, 3000);
            }
            
            // 增加计数
            increaseBtn.addEventListener('click', function() {
                count++;
                updateCounter();
                showMessage('计数已增加', 'success');
            });
            
            // 减少计数
            decreaseBtn.addEventListener('click', function() {
                if (count > 0) {
                    count--;
                    updateCounter();
                    showMessage('计数已减少', 'success');
                } else {
                    showMessage('计数不能小于0', 'error');
                }
            });
            
            // 重置计数
            resetBtn.addEventListener('click', function() {
                count = 0;
                updateCounter();
                showMessage('计数已重置', 'success');
            });
            
            // 初始化
            updateCounter();
        });
    </script>
</body>
</html>
```

### 样式设计说明：

1. **整体布局**：
   - 使用渐变背景（紫色到粉色）创造视觉吸引力
   - 居中布局，采用Flexbox实现响应式设计
   - 添加了毛玻璃效果（backdrop-filter）增强现代感

2. **计数器显示区域**：
   - 采用内嵌阴影设计，创造立体感
   - 大字体显示计数数值，使用醒目的紫色
   - 添加了脉冲动画效果，当数值变化时会有轻微缩放动画

3. **按钮样式**：
   - 圆角设计，符合现代UI趋势
   - 渐变背景色，增加按钮的视觉吸引力
   - 悬停效果：按钮上移并增强阴影
   - 点击效果：按钮下沉，模拟真实按钮按压感
   - 禁用状态：当计数为0时，减少按钮变为灰色且不可点击

4. **消息提示**：
   - 非侵入式设计，不使用alert
   - 淡入淡出动画效果
   - 不同类型消息使用不同颜色（错误为红色系，成功为蓝色系）

5. **响应式设计**：
   - 适配移动设备，在小屏幕上按钮垂直排列
   - 调整字体大小和间距，确保在各种屏幕尺寸下都有良好显示

6. **交互细节**：
   - 添加了悬停、点击和禁用状态的各种视觉反馈
   - 计数变化时有动画效果，提升用户体验

这个设计不仅满足了计数器的基本功能需求，还通过现代化的UI设计和流畅的交互体验，为用户提供了一个美观且易用的界面。