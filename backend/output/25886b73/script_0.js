// 修复前
function divide(a, b) {
  return a / b;
}

// 修复后
function divide(a, b) {
  if (b === 0) {
    return "错误：除数不能为零";
  }
  const result = a / b;
  return parseFloat(result.toFixed(8));
}