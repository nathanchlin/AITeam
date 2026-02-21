// 添加历史记录数组
const history = [];

// 修改计算函数以保存历史记录
function calculate() {
  const inputValue = display.textContent;
  if (isNaN(parseFloat(inputValue))) {
    display.textContent = "错误：请输入有效数字";
    return;
  }
  
  secondOperand = parseFloat(inputValue);
  let result;
  
  switch(currentOperator) {
    case '+':
      result = add(firstOperand, secondOperand);
      break;
    case '-':
      result = subtract(firstOperand, secondOperand);
      break;
    case '×':
      result = multiply(firstOperand, secondOperand);
      break;
    case '÷':
      result = divide(firstOperand, secondOperand);
      break;
    default:
      return;
  }
  
  // 保存到历史记录
  history.push(`${firstOperand} ${currentOperator} ${secondOperand} = ${result}`);
  
  display.textContent = result;
  currentOperator = null;
  firstOperand = null;
  secondOperand = null;
}

// 添加显示历史记录的函数
function showHistory() {
  const historyElement = document.getElementById('history');
  historyElement.innerHTML = '<h3>历史记录</h3>';
  history.forEach(item => {
    const historyItem = document.createElement('div');
    historyItem.textContent = item;
    historyElement.appendChild(historyItem);
  });
}