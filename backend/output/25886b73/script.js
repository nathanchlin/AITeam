// 格式化显示数字（可选，用于添加千位分隔符等）
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// 验证输入是否为有效数字
function isValidNumber(num) {
    return !isNaN(num) && isFinite(num);
}

// 限制小数位数
function limitDecimalPlaces(num, maxDecimalPlaces = 8) {
    if (typeof num !== 'number') return num;
    
    const str = num.toString();
    if (str.includes('.')) {
        const [integer, decimal] = str.split('.');
        return `${integer}.${decimal.slice(0, maxDecimalPlaces)}`;
    }
    return num;
}