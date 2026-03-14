---
name: cr-and-test-validation-for-game-quality-fix
overview: 对刚完成的游戏质量修复做一次代码复核，并补充定向测试与最小回归验证，确认 `_reassign_agents()` 和代码块提取逻辑都没有引入回归。
todos:
  - id: cr-coordinator-path
    content: 使用 [subagent:code-explorer] 复核恢复与迭代恢复调用链，确认 `_reassign_agents()` 漏洞边界
    status: completed
  - id: fix-iteration-reassign
    content: 修复 `backend/app/services/coordinator.py`，让 `_reassign_agents()` 同时覆盖主任务与迭代任务
    status: completed
    dependencies:
      - cr-coordinator-path
  - id: add-coordinator-tests
    content: 新增 `backend/tests/test_coordinator_reassign_agents.py`，覆盖多 Agent、失效 ID 与迭代恢复场景
    status: completed
    dependencies:
      - fix-iteration-reassign
  - id: add-output-manager-tests
    content: 新增 `backend/tests/test_output_manager.py`，验证代码块提取合法与非法格式
    status: completed
    dependencies:
      - cr-coordinator-path
  - id: run-targeted-validation
    content: 运行定向 pytest 与相关回归验证，确认修复生效且无新回归
    status: completed
    dependencies:
      - add-coordinator-tests
      - add-output-manager-tests
---

## 用户需求

对已完成的两处修复再做一次代码评审，并启动测试验证，重点确认恢复/重启后的任务重新分配逻辑与 Markdown 代码块提取逻辑没有遗漏风险。

## 产品概述

本次工作聚焦后端服务稳定性，无新增界面。目标是让 Pipeline 在服务重启、计划恢复、迭代恢复时继续把任务分配给正确 Agent，同时保证从模型输出中提取代码块时只匹配合法 fenced code block。用户侧表现为恢复执行更稳定、代码落盘更准确。

## 核心功能

- 复核 `_reassign_agents()` 的完整影响链，确认主计划任务与迭代任务都能正确重绑 Agent
- 复核 `extract_code_blocks()` 的匹配边界，确认合法代码块可提取、非法行内格式不会误提取
- 增加定向自动化测试，覆盖本次修复点与关键边界场景
- 运行小范围回归验证，确认本次修复不会影响现有恢复与输出流程

## Tech Stack Selection

- 后端框架：Python 服务层（现有 `backend/app/services`）
- 数据模型：Pydantic schema（`Plan`、`PlanTask`、`IterationTask`）
- 测试体系：pytest（已在 `backend/tests` 使用）

## Implementation Approach

本轮以“先严格 CR，再做定向修复与验证”为策略，避免再次做大范围改动。根据已核实代码，`output_manager.py` 当前正则方向正确，主要风险点转移到 `coordinator.py`：`_reassign_agents()` 现在只遍历 `plan.tasks`，但 `resume_iteration` 也调用该方法后继续执行 `iteration.tasks`，因此迭代恢复场景仍可能保留旧的 `assigned_agent_id`。

关键决策：

- 在 `CoordinatorService._reassign_agents()` 内统一覆盖主计划任务和 `plan.iterations[*].tasks`，复用现有 `_build_agents_by_type()`，不引入新分配策略
- 保持“同类型取列表第一个 Agent”的兼容行为，不改动现有轮询分配逻辑 `_get_agent_for_task()`
- `extract_code_blocks()` 优先通过测试验证当前规则，不在没有失败证据前继续改正则，控制变更面

性能与可靠性：

- 任务重绑复杂度保持线性，约为 O(主任务数 + 迭代任务总数)，仅在加载/恢复时触发，不影响正常执行热路径
- 测试采用 mock/monkeypatch 隔离 `agent_manager.get_all_agents()`，避免真实存储和模型依赖
- 回归范围限定在修复点与其直接调用链，避免无关改动

## Implementation Notes

- `_reassign_agents()` 修复时需同时兼容 `selected_agent_ids` 为空、部分失效、同类型多个 Agent、任务类型不存在等场景
- 不要改动 `pipeline.py` / `tasks.py` 的调用入口，优先通过修复统一服务方法降低 blast radius
- `output_manager` 测试要覆盖：标准 fenced block、语言标识后空格/Tab、无语言标识、语言后无换行的非法格式
- 若测试暴露 `extract_code_blocks()` 兼容性问题，再做最小修补并复跑定向用例

## Architecture Design

当前影响链已确认：

- `backend/app/api/pipeline.py` 与 `backend/app/core/tasks.py` 在恢复路径中调用 `coordinator._reassign_agents(plan_id)`
- `backend/app/api/pipeline.py` 的迭代恢复路径随后继续执行 `iteration.tasks`
- `backend/app/services/output_manager.py` 的 `extract_code_blocks()` 被 `save_task_output()` 与 `update_index_html()` 复用

因此本轮应以 `CoordinatorService` 为主修复点，以 `OutputManager` 为主验证点。

## Directory Structure

## Directory Structure Summary

本次实现以服务层定向修复和回归测试为主，预计修改 1 个核心文件并新增 2 个测试文件。

/Users/lindeng/AITeam/
├── backend/app/services/coordinator.py  # [MODIFY] 修复 `_reassign_agents()` 仅处理 `plan.tasks` 的遗漏，扩展到迭代任务重绑；继续复用 `_build_agents_by_type()`，保持当前兼容行为。
├── backend/tests/test_coordinator_reassign_agents.py  # [NEW] 针对 `_reassign_agents()` 的单元测试。覆盖主任务、迭代任务、失效 selected_agent_ids、同类型多 Agent、缺失类型安全跳过等场景。
└── backend/tests/test_output_manager.py  # [NEW] 针对 `extract_code_blocks()` 的单元测试。覆盖标准 fenced block、语言后空白、无语言、非法无换行格式不提取等边界。

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 在执行阶段补充扫描恢复/迭代相关调用链与测试影响面，避免遗漏隐藏入口
- Expected outcome: 产出完整的影响文件列表与边界场景，支撑定向修复和测试覆盖