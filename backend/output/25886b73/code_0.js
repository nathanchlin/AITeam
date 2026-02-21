class Calculator {
  constructor() {
    this.currentInput = '0';
    this.previousInput = '';
    this.operation = null;
    this.waitingForOperand = false;
  }

  // 添加数字
  appendNumber(num) {
    if (this.waitingForOperand) {
      this.currentInput = String(num);
      this.waitingForOperand = false;
    } else {
      this.currentInput = this.currentInput === '0' ? String(num) : this.currentInput + num;
    }
  }

  // 添加小数点
  appendDecimal() {
    if (this.waitingForOperand) {
      this.currentInput = '0.';
      this.waitingForOperand = false;
    } else if (this.currentInput.indexOf('.') === -1) {
      this.currentInput += '.';
    }
  }

  // 选择运算符
  chooseOperation(op) {
    const inputValue = parseFloat(this.currentInput);

    if (this.previousInput === '') {
      this.previousInput = inputValue;
    } else if (this.operation) {
      const currentValue = this.previousInput || 0;
      const newValue = this.calculate(currentValue, inputValue, this.operation);

      this.currentInput = String(newValue);
      this.previousInput = newValue;
    }

    this.waitingForOperand = true;
    this.operation = op;
  }

  // 执行计算
  calculate(firstOperand, secondOperand, operation) {
    switch (operation) {
      case '+':
        return firstOperand + secondOperand;
      case '-':
        return firstOperand - secondOperand;
      case '×':
        return firstOperand * secondOperand;
      case '÷':
        if (secondOperand === 0) {
          return 'Error';
        }
        return firstOperand / secondOperand;
      default:
        return secondOperand;
    }
  }

  // 计算结果
  compute() {
    const inputValue = parseFloat(this.currentInput);

    if (this.previousInput !== '' && this.operation) {
      const currentValue = this.previousInput || 0;
      const newValue = this.calculate(currentValue, inputValue, this.operation);

      this.currentInput = String(newValue);
      this.previousInput = '';
      this.operation = null;
      this.waitingForOperand = true;
    }
  }

  // 清除所有
  clearAll() {
    this.currentInput = '0';
    this.previousInput = '';
    this.operation = null;
    this.waitingForOperand = false;
  }

  // 清除当前输入
  clearEntry() {
    this.currentInput = '0';
  }

  // 删除最后一个字符
  delete() {
    const { length } = this.currentInput;
    if (length === 1) {
      this.currentInput = '0';
    } else {
      this.currentInput = this.currentInput.substring(0, length - 1);
    }
  }

  // 处理表达式计算（支持连续运算）
  evaluateExpression(expression) {
    try {
      // 替换显示用的运算符为JavaScript运算符
      expression = expression.replace(/×/g, '*').replace(/÷/g, '/');
      
      // 使用Function构造函数安全地计算表达式
      const result = new Function(`return ${expression}`)();
      
      // 处理结果
      if (typeof result === 'number' && isFinite(result)) {
        this.currentInput = String(result);
        this.previousInput = '';
        this.operation = null;
        this.waitingForOperand = true;
      } else {
        throw new Error('Invalid result');
      }
    } catch (error) {
      this.currentInput = 'Error';
      this.clearAll();
    }
  }
}

// 示例使用
const calculator = new Calculator();

// 模拟用户输入
calculator.appendNumber(5);
calculator.appendNumber(0);
calculator.chooseOperation('+');
calculator.appendNumber(3);
calculator.chooseOperation('×');
calculator.appendNumber(2);
calculator.compute();

// 结果应为: 106 (50 + 3 * 2 = 50 + 6 = 56)
console.log(calculator.currentInput); // 输出: "56"

// 使用表达式计算
calculator.evaluateExpression('10 + 2 * 5 - 3 / 3');
// 结果应为: 19 (10 + 10 - 1 = 19)
console.log(calculator.currentInput); // 输出: "19"