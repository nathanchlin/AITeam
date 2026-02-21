// 使用BigInt处理大数分数
class ScoreManager {
  constructor() {
    this.score = BigInt(0);
    this.multiplier = BigInt(1);
  }
  
  addScore(points) {
    this.score += BigInt(points) * this.multiplier;
  }
  
  getFormattedScore() {
    // 格式化显示分数
    return this.score.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  
  reset() {
    this.score = BigInt(0);
    this.multiplier = BigInt(1);
  }
}