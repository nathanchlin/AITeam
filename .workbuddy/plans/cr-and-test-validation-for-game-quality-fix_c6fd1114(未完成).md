---
name: cr-and-test-validation-for-game-quality-fix
overview: 对刚完成的游戏质量修复做一次复核，并补充/执行针对 `_reassign_agents()` 与代码块提取逻辑的测试验证，确认没有回归风险。
todos:
  - id: cr-call-chain
    content: 使用 [subagent:code-explorer] 复查重分配与提取调用链
    status: pending
  - id: cr-edge-cases
    content: 确认 `_reassign_agents` 与正则的边界行为
    status: pending
    dependencies:
      - cr-call-chain
  - id: add-regression-tests
    content: 新增 test_coordinator_reassign 与 test_output_manager 单测
    status: pending
    dependencies:
      - cr-edge-cases
  - id: run-targeted-pytest
    content: 运行定向 pytest 并输出 CR 结论与风险
    status: pending
    dependencies:
      - add-regression-tests
---

## 用户需求

- 对已完成的两处修复再做一次代码审查，确认没有遗漏的兼容性问题、边界缺陷或回归风险。
- 启动测试验证，但范围要聚焦，优先验证 Agent 重分配与代码块提取两个修复点，不做无必要的全量扩散。
- 输出应包含审查结论、测试结果和残余风险；若未发现新问题，应避免继续扩大改动。

## 产品概述

- 本轮关注的是平台恢复执行时的任务指派稳定性，以及生成结果中代码块提取的可靠性。
- 无新增界面，最终效果体现在恢复后的任务分配更稳定、代码保存更准确、验证结论更清晰。

## 核心功能

- 复查 `_reassign_agents()` 在历史 Plan 恢复、Agent 顺序、空候选集场景下的行为。
- 复查 `extract_code_blocks()` 对合法 fenced code block 和异常行内 fence 的处理是否符合预期。
- 通过定向单元测试和小范围回归测试验证修复点。

## Tech Stack Selection

- 后端：Python
- Web 服务：FastAPI
- 数据模型：Pydantic
- 测试方式：现有 `backend/tests/` 中使用 pytest 风格测试
- 已验证关键文件：`backend/app/services/coordinator.py`、`backend/app/services/output_manager.py`、`backend/app/api/pipeline.py`、`backend/app/core/tasks.py`、`backend/app/models/schemas.py`
- 已确认当前仓库下未发现 `pytest.ini`、`pyproject.toml`、`backend/conftest.py`，测试需沿用现有轻量模式

## Implementation Approach

先做一次只读 CR，围绕运行时调用链确认两个修复点是否与现有结构完全一致，再补充定向回归单测，最后只运行目标测试集并汇总结论。默认不继续改动生产代码；只有在 CR 发现可复现且确定的问题时，才做最小修复。

关键技术决策：

- `_reassign_agents()` 重点验证与 `_build_agents_by_type()` 的结构一致性，以及 `api/pipeline.py`、`core/tasks.py`、`coordinator._load_plans()` 三个入口的兼容性。
- `extract_code_blocks()` 重点验证“标准 fenced code block 正常提取、语言标识后空格/Tab 可接受、行内 fence 不误匹配”三类行为。
- 采用单元测试替代重型端到端验证，减少对 LLM、WebSocket、存储文件的耦合影响。

性能与可靠性：

- `_reassign_agents()` 的核心成本与任务数和 Agent 数线性相关，测试应覆盖多任务但避免构造重型对象。
- `extract_code_blocks()` 主要是一次正则扫描，测试应覆盖多段代码块和误匹配样例，避免超长样本文本。
- 使用 mock 和临时目录隔离外部依赖，避免污染真实 `plans` 或 `output` 数据。

## Implementation Notes

- 复用现有测试风格中的 `pytest`、`MagicMock`、`patch`。
- 对 `agent_manager.get_all_agents()` 做 mock，直接构造 `Plan` 与 `PlanTask`，避免依赖真实注册状态。
- 对 `OutputManager` 使用自定义临时 `base_dir`，避免写入真实输出目录。
- 回归范围保持在 `coordinator`、`output_manager` 及其直接调用链，不做无关重构。

## Architecture Design

本轮验证链路分为两条：

1. Plan 恢复链路：`coordinator._load_plans()` / `api.pipeline.resume_pipeline()` / `core.tasks.execute_pipeline_phase()` 调用 `_reassign_agents()`，目标是保证历史任务能拿到当前有效 Agent ID。
2. 代码落盘链路：任务结果进入 `OutputManager.extract_code_blocks()`，后续被 `save_task_output()` 与 `update_index_html()` 使用，目标是保证只提取合法代码块。

## Directory Structure

### Directory Structure Summary

本轮以“复查 + 定向验证”为主，优先新增回归测试；生产代码仅在 CR 确认存在确定性缺陷时再做最小修复。

- `/Users/lindeng/AITeam/backend/app/services/coordinator.py`  [MODIFY] 复查 `_reassign_agents()` 与 `_build_agents_by_type()` 的一致性；仅当 CR 发现确定性问题时做最小修补。
- `/Users/lindeng/AITeam/backend/app/services/output_manager.py`  [MODIFY] 复查 `extract_code_blocks()` 对下游 `save_task_output()`、`update_index_html()` 的影响；仅当 CR 发现误判场景时做最小修补。
- `/Users/lindeng/AITeam/backend/tests/test_coordinator_reassign.py`  [NEW] 为 `_reassign_agents()` 增加定向单测，覆盖用户选择顺序、未选择时回退、无候选 Agent 时不崩溃等场景。
- `/Users/lindeng/AITeam/backend/tests/test_output_manager.py`  [NEW] 为 `extract_code_blocks()` 增加定向单测，覆盖标准代码块、语言标识后空白、行内 fence 不误提取、多代码块提取顺序等场景。

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 扫描 `coordinator`、`output_manager` 及其调用链与测试缺口，辅助完成本轮 CR 范围确认
- Expected outcome: 明确需要补充的回归测试点，避免遗漏恢复入口和下游使用点