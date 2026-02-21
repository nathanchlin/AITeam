class GomokuSoundManager {
  constructor() {
    this.sounds = {
      place: null, // 落子音效
      win: null,   // 胜利音效
      undo: null,  // 悔棋音效
      invalid: null // 无效移动音效
    };
    this.soundEnabled = true;
    this.loadSounds();
  }

  // 加载音效文件
  loadSounds() {
    // 在实际应用中，这里会加载实际的音效文件
    // 这里我们使用占位符
    this.sounds.place = this.createBeepSound(440, 0.1); // A4音符
    this.sounds.win = this.createBeepSound(880, 0.5); // A5音符
    this.sounds.undo = this.createBeepSound(330, 0.1); // E4音符
    this.sounds.invalid = this.createBeepSound(220, 0.2); // A3音符
  }

  // 创建简单的蜂鸣音效（用于示例）
  createBeepSound(frequency, duration) {
    return {
      play: () => {
        if (!this.soundEnabled) return;
        
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.type = 'sine';
        oscillator.frequency.value = frequency;
        gainNode.gain.value = 0.1;
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + duration);
      }
    };
  }

  // 播放指定音效
  play(soundName) {
    if (this.sounds[soundName]) {
      this.sounds[soundName].play();
    }
  }

  // 切换音效开关
  toggleSound() {
    this.soundEnabled = !this.soundEnabled;
  }
}

// 在Gomoku类中集成音效管理器
class Gomoku {
  constructor() {
    // ... 其他初始化代码 ...
    this.soundManager = new GomokuSoundManager();
  }

  // 修改落子方法以包含音效
  makeMove(row, col) {
    if (this.isValidMove(row, col)) {
      // ... 原有代码 ...
      this.soundManager.play('place');
      return true;
    } else {
      this.soundManager.play('invalid');
      return false;
    }
  }

  // 修改胜利检测以包含音效
  checkWin(row, col) {
    const isWin = this.checkWinCondition(row, col);
    if (isWin && this.gameOver) {
      this.soundManager.play('win');
    }
    return isWin;
  }
}