// 菜单状态
class MenuState extends GameState {
  enter() {
    console.log('Entering menu state');
    // 初始化菜单UI
  }

  update(deltaTime) {
    // 处理菜单输入
  }

  exit() {
    console.log('Exiting menu state');
    // 清理菜单UI
  }
}

// 游戏状态
class PlayState extends GameState {
  enter() {
    console.log('Entering play state');
    // 初始化游戏
  }

  update(deltaTime) {
    // 更新游戏逻辑
  }

  exit() {
    console.log('Exiting play state');
    // 保存游戏状态
  }
}

// 暂停状态
class PauseState extends GameState {
  enter() {
    console.log('Entering pause state');
    // 显示暂停菜单
  }

  update(deltaTime) {
    // 处理暂停菜单输入
  }

  exit() {
    console.log('Exiting pause state');
    // 隐藏暂停菜单
  }
}