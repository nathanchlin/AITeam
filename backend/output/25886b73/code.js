class Calculator {
    constructor() {
        this.currentValue = '0';
        this.previousValue = '';
        this.operation = null;
        this.waitingForOperand = false;
    }

    // 输入数字
    inputDigit(digit) {
        if (this.waitingForOperand) {
            this.currentValue = digit;
            this.waitingForOperand = false;
        } else {
            this.currentValue = this.currentValue === '0' ? digit : this.currentValue + digit;
        }
    }

    // 输入小数点
    inputDecimal() {
        if (this.waitingForOperand) {
            this.currentValue = '0.';
            this.waitingForOperand = false;
            return;
        }

        if (this.currentValue.indexOf('.') === -1) {
            this.currentValue += '.';
        }
    }

    // 清除所有
    clear() {
        this.currentValue = '0';
        this.previousValue = '';
        this.operation = null;
        this.waitingForOperand = false;
    }

    // 删除最后一位
    delete() {
        if (this.waitingForOperand) {
            this.clear();
            return;
        }
        
        this.currentValue = this.currentValue.slice(0, -1) || '0';
    }

    // 设置操作符
    setOperation(nextOperation) {
        const inputValue = parseFloat(this.currentValue);

        if (this.previousValue === '') {
            this.previousValue = inputValue;
        } else if (this.operation) {
            const currentValue = this.previousValue || 0;
            const newValue = this.performCalculation();

            this.currentValue = String(newValue);
            this.previousValue = newValue;
        }

        this.waitingForOperand = true;
        this.operation = nextOperation;
    }

    // 执行计算
    performCalculation() {
        const prev = this.previousValue;
        const current = parseFloat(this.currentValue);

        if (prev === null || this.operation === null) {
            return current;
        }

        switch (this.operation) {
            case '+':
                return prev + current;
            case '-':
                return prev - current;
            case '*':
                return prev * current;
            case '/':
                return prev / current;
            default:
                return current;
        }
    }

    // 计算结果
    calculate() {
        const inputValue = parseFloat(this.currentValue);

        if (this.previousValue !== null && this.operation) {
            const newValue = this.performCalculation();
            this.currentValue = String(newValue);
            this.previousValue = null;
            this.operation = null;
            this.waitingForOperand = true;
        }
    }
}