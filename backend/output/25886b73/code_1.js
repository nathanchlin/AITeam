class Calculator {
  constructor() {
    this.display = document.querySelector('.display');
    this.currentValue = '0';
    this.previousValue = '';
    this.operation = null;
    this.waitingForOperand = false;
    this.decimalAdded = false;
    
    this.updateDisplay();
  }
  
  inputDigit(digit) {
    if (this.waitingForOperand) {
      this.currentValue = digit;
      this.waitingForOperand = false;
    } else {
      this.currentValue = this.currentValue === '0' ? digit : this.currentValue + digit;
    }
    this.updateDisplay();
  }
  
  inputDecimal() {
    if (this.waitingForOperand) {
      this.currentValue = '0.';
      this.waitingForOperand = false;
    } else if (this.currentValue.indexOf('.') === -1) {
      this.currentValue += '.';
    }
    this.updateDisplay();
  }
  
  clear() {
    this.currentValue = '0';
    this.previousValue = '';
    this.operation = null;
    this.waitingForOperand = false;
    this.decimalAdded = false;
    this.updateDisplay();
  }
  
  clearEntry() {
    this.currentValue = '0';
    this.updateDisplay();
  }
  
  handleOperator(nextOperator) {
    const inputValue = parseFloat(this.currentValue);
    
    if (this.previousValue === '') {
      this.previousValue = inputValue;
    } else if (this.operation) {
      const currentValue = this.previousValue || 0;
      const newValue = this.performCalculation();
      
      this.currentValue = String(newValue);
      this.previousValue = newValue;
      this.updateDisplay();
    }
    
    this.waitingForOperand = true;
    this.operation = nextOperator;
  }
  
  performCalculation() {
    const prev = this.previousValue;
    const current = parseFloat(this.currentValue);
    
    switch (this.operation) {
      case '+':
        return prev + current;
      case '-':
        return prev - current;
      case '×':
        return prev * current;
      case '÷':
        if (current === 0) {
          alert('除数不能为零');
          return prev;
        }
        return prev / current;
      default:
        return current;
    }
  }
  
  equals() {
    if (this.operation) {
      const result = this.performCalculation();
      this.currentValue = String(result);
      this.previousValue = '';
      this.operation = null;
      this.waitingForOperand = true;
      this.decimalAdded = false;
      this.updateDisplay();
    }
  }
  
  updateDisplay() {
    this.display.textContent = this.currentValue;
  }
}

// 初始化计算器
const calculator = new Calculator();