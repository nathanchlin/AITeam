{
  _id: ObjectId, // 玩家ID
  userId: String, // 用户ID
  username: String, // 用户名
  avatar: String, // 头像URL
  level: Number, // 等级
  experience: Number, // 经验值
  coins: Number, // 金币
  gems: Number, // 钻石
  unlockedSkins: [String], // 解锁的皮肤
  currentSkin: String, // 当前皮肤
  achievements: [ // 成就
    {
      id: String,
      progress: Number,
      unlocked: Boolean,
      unlockedAt: Date
    }
  ],
  stats: { // 统计数据
    totalPlayTime: Number, // 总游戏时间
    totalEaten: Number, // 总吃球数
    totalDeaths: Number, // 总死亡次数
    largestSize: Number, // 最大尺寸
    rank: Number // 当前排名
  },
  createdAt: Date, // 创建时间
  updatedAt: Date // 更新时间
}