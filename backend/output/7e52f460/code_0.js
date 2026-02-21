// 替换ES6语法为ES5兼容代码
// 原代码：const canvas = document.getElementById('gameCanvas');
// 修复后：
var canvas = document.getElementById('gameCanvas');

// 替换箭头函数
// 原代码：const handleKeyDown = (e) => {
// 修复后：
function handleKeyDown(e) {
    // 函数内容保持不变
}

// 添加IE 11 flexbox兼容样式
.game-container {
    display: -ms-flexbox;
    display: -webkit-flex;
    display: flex;
    -ms-flex-direction: column;
    -webkit-flex-direction: column;
    flex-direction: column;
    -ms-flex-pack: center;
    -webkit-justify-content: center;
    justify-content: center;
    -ms-flex-align: center;
    -webkit-align-items: center;
    align-items: center;
    height: 100vh;
    background-color: #f0f0f0;
}