{
  _id: ObjectId, // 游戏记录ID
  roomId: String, // 房间ID
  players: [ // 参与玩家
    {
      playerId: String,
      username: String,
      finalSize: Number,
      rank: Number,
      survivalTime: Number,
      eatenCount: Number
    }
  ],
  mode: String, // 游戏模式
  map: String, // 地图
  startTime: Date, // 开始时间
  endTime: Date, // 结束时间
  duration: Number // 持续时间
}