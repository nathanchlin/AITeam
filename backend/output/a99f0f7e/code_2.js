// 房间数据结构
{
  id: 'room_123',
  name: '游戏房间',
  maxPlayers: 10,
  players: [
    {
      id: 'player_1',
      name: 'Player1',
      x: 100,
      y: 100,
      radius: 20,
      color: '#FF0000'
    }
  ],
  foods: [
    {
      id: 'food_1',
      x: 200,
      y: 200,
      color: '#00FF00'
    }
  ],
  status: 'playing', // waiting, playing, ended
  startTime: Date.now()
}