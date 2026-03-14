from app.services.quality_scorer import QualityScorer


def test_score_ts_output_rewards_modular_project_snapshot():
    scorer = QualityScorer()
    snapshot = """// filename: src/main.ts
import './styles.css';
import { Game } from './game';

const game = new Game();
game.start();

// filename: src/game.ts
export class Game {
  start(): void {
    document.getElementById('app')?.setAttribute('data-ready', 'true');
  }
}

// filename: src/types.ts
export interface GameState {
  score: number;
}

// filename: src/styles.css
#app { display: grid; background: #111; color: #fff; }
"""

    result = scorer.score_ts_output(snapshot, "做一个 TypeScript 小游戏")

    assert result["passed"] is True
    assert result["total"] >= 60
    assert result["profile"] == "ts-app"


def test_score_ts_output_penalizes_placeholders_and_missing_structure():
    scorer = QualityScorer()
    snapshot = """// filename: src/main.ts
const root = document.getElementById('app');
if (root) {
  root.textContent = '等待生成具体业务代码';
}
"""

    result = scorer.score_ts_output(snapshot, "做一个 TypeScript 应用")

    assert result["passed"] is False
    assert result["scores"]["correctness"]["percentage"] < 100
    assert any("占位" in item or "入口文件" in item for item in result["recommendations"])
