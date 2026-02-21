// 全局变量定义
// currentOperation: 当前显示的数字或结果
// previousOperation: 上一次操作的表达式
// operation: 当前选择的运算符
// resetScreen: 是否需要重置显示屏的标志

// appendNumber(number) - 添加数字到当前操作
// 参数: number - 要添加的数字字符
// 功能: 将数字添加到当前操作中，处理初始状态和重置状态

// appendDecimal() - 添加小数点
// 功能: 向当前操作添加小数点，确保不重复添加

// appendOperator(op) - 添加运算符
// 参数: op - 运算符字符(+, -, *, /)
// 功能: 设置当前运算符，准备下一次计算

// calculate() - 执行计算
// 功能: 根据当前运算符和操作数进行计算，处理除零错误

// formatResult(result) - 格式化计算结果
// 参数: result - 计算结果数值
// 功能: 格式化结果，处理大数、小数和错误情况

// clearEntry() - 清除当前输入
// 功能: 重置当前操作为0

// clearAll() - 清除全部
// 功能: 重置计算器到初始状态

// 键盘事件监听
// 功能: 添加键盘支持，使用户可以通过键盘操作计算器