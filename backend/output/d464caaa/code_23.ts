// src/ai/aiPlayer.ts
import * as tf from '@tensorflow/tfjs'

export class TetrisAI {
  private model: tf.LayersModel | null = null
  
  constructor() {
    this.initializeModel()
  }
  
  private async initializeModel() {
    // 初始化神经网络模型
    this.model = tf.sequential({
      layers: [
        tf.layers.dense({ inputShape: [200], units: 128, activation: 'relu' }),
        tf.layers.dropout({ rate: 0.2 }),
        tf.layers.dense({ units: 64, activation: 'relu' }),
        tf.layers.dense({ units: 7, activation: 'softmax' }) // 7种可能的动作
      ]
    })
    
    this.model.compile({
      optimizer: 'adam',
      loss: 'categoricalCrossentropy',
      metrics: ['accuracy']
    })
  }
  
  // 训练模型的方法
  async train(trainingData: any[]) {
    if (!this.model) return
    
    const xs = tf.tensor2d(trainingData.map(d => d.state))
    const ys = tf.tensor2d(trainingData.map(d => d.action))
    
    await this.model.fit(xs, ys, {
      epochs: 10,
      batchSize: 32
    })
  }
  
  // 预测最佳动作
  predictBestMove(boardState: number[]): number {
    if (!this.model) return 0
    
    const input = tf.tensor2d([boardState])
    const prediction = this.model.predict(input) as tf.Tensor
    const action = prediction.argMax(-1).dataSync()[0]
    
    input.dispose()
    prediction.dispose()
    
    return action
  }
}