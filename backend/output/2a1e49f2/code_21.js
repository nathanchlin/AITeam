// ai/tests/strategy.test.js 示例
const { expect } = require('chai');
const { SimpleStrategy } = require('../src/strategies/simple');

describe('AI Strategy Tests', () => {
  it('should evaluate board position', () => {
    const strategy = new SimpleStrategy();
    const board = createTestBoard();
    const score = strategy.evaluate(board);
    expect(score).to.be.a('number');
  });
});