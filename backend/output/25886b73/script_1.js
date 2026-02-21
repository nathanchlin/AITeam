// 修复前
function handleOperator(operator) {
  currentOperator = operator;
  firstOperand = parseFloat(display.textContent);
  display.textContent = '';
}

// 修复后
function handleOperator(operator) {
  const inputValue = display.textContent;
  if (isNaN(parseFloat(inputValue))) {
    display.textContent = "错误：请输入有效数字";
    return;
  }
  currentOperator = operator;
  firstOperand = parseFloat(inputValue);
  display.textContent = '';
}

// 添加错误恢复功能
function clearError() {
  display.textContent = '';
  currentOperator = null;
  firstOperand = null;
  secondOperand = null;
}