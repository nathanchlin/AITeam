{
  _id: ObjectId, // 游戏状态ID
  roomId: String, // 房间ID
  players: [ // 玩家状态
    {
      playerId: String,
      position: {
        x: Number,
        y: Number
      },
      size: Number,
      color: String,
      isAlive: Boolean,
      velocity: {
        x: Number,
        y: Number
      }
    }
  ],
  food: [ // 食物
    {
      id: String,
      position: {
        x: Number,
        y: Number
      },
      size: Number,
      type: String
    }
  ],
  obstacles: [ // 障碍物
    {
      id: String,
      position: {
        x: Number,
        y: Number
      },
      size: Number
    }
  ],
  startTime: Date, // 游戏开始时间
  endTime: Date, // 游戏结束时间
  duration: Number // 游戏持续时间
}