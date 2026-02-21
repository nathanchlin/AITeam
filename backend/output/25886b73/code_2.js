// 全局变量
let currentOperation = '0';
let previousOperation = '';
let operation = undefined;
let resetScreen = false;

// 获取DOM元素
const currentOperationElement = document.getElementById('current-operation');
const previousOperationElement = document.getElementById('previous-operation');

// 更新显示屏
function updateDisplay() {
    currentOperationElement.textContent = currentOperation;
    previousOperationElement.textContent = previousOperation;
}

// 添加数字
function appendNumber(number) {
    if (currentOperation === '0' || resetScreen) {
        currentOperation = number;
        resetScreen = false;
    } else {
        currentOperation += number;
    }
    updateDisplay();
}

// 添加小数点
function appendDecimal() {
    if (resetScreen) {
        currentOperation = '0.';
        resetScreen = false;
    } else if (!currentOperation.includes('.')) {
        currentOperation += '.';
    }
    updateDisplay();
}

// 添加运算符
function appendOperator(op) {
    if (operation !== undefined) {
        calculate();
    }
    
    previousOperation = `${currentOperation} ${getOperatorSymbol(op)}`;
    operation = op;
    resetScreen = true;
    updateDisplay();
}

// 获取运算符符号
function getOperatorSymbol(op) {
    switch(op) {
        case '+': return '+';
        case '-': return '-';
        case '*': return '×';
        case '/': return '÷';
        default: return '';
    }
}

// 计算结果
function calculate() {
    if (operation === undefined || resetScreen) return;
    
    const prev = parseFloat(previousOperation);
    const current = parseFloat(currentOperation);
    let result;
    
    switch(operation) {
        case '+':
            result = prev + current;
            break;
        case '-':
            result = prev - current;
            break;
        case '*':
            result = prev * current;
            break;
        case '/':
            if (current === 0) {
                currentOperation = 'Error';
                operation = undefined;
                previousOperation = '';
                updateDisplay();
                return;
            }
            result = prev / current;
            break;
        default:
            return;
    }
    
    currentOperation = formatResult(result);
    previousOperation = '';
    operation = undefined;
    resetScreen = true;
    updateDisplay();
}

// 格式化结果
function formatResult(result) {
    // 处理大数或小数
    if (isNaN(result)) {
        return 'Error';
    }
    
    // 限制小数位数
    if (Number.isInteger(result)) {
        return result.toString();
    } else {
        return parseFloat(result.toFixed(8)).toString();
    }
}

// 清除当前输入
function clearEntry() {
    currentOperation = '0';
    updateDisplay();
}

// 清除全部
function clearAll() {
    currentOperation = '0';
    previousOperation = '';
    operation = undefined;
    resetScreen = false;
    updateDisplay();
}

// 键盘支持
document.addEventListener('keydown', (event) => {
    if (event.key >= '0' && event.key <= '9') {
        appendNumber(event.key);
    } else if (event.key === '.') {
        appendDecimal();
    } else if (event.key === '+' || event.key === '-' || event.key === '*' || event.key === '/') {
        appendOperator(event.key);
    } else if (event.key === 'Enter' || event.key === '=') {
        calculate();
    } else if (event.key === 'Escape') {
        clearAll();
    } else if (event.key === 'Backspace') {
        clearEntry();
    }
});