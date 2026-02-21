// 根据分数调整游戏速度
function getGameSpeed() {
  const baseSpeed = 100; // 基础速度(毫秒)
  const speedIncrease = Math.floor(score / 5) * 10; // 每得5分增加10毫秒
  return Math.max(50, baseSpeed - speedIncrease); // 最低速度限制为50毫秒
}