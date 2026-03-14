---
name: diagnose-game-quality-drop
overview: 分析3月6日到3月7日之间的代码修改，找出导致游戏生产质量（可运行率）大幅降低的根本原因，并提出修复方案。
todos:
  - id: fix-reassign-agents
    content: 修复 coordinator.py 中 _reassign_agents() 方法的 agents_by_type 数据结构不一致问题，使其使用 _build_agents_by_type() 并适配 List 结构
    status: completed
  - id: fix-regex-extraction
    content: 收紧 output_manager.py 中 extract_code_blocks 的正则表达式，避免无换行时的误匹配
    status: completed
  - id: verify-base-prompt
    content: 验证 base.py 中 CoderAgent 的 system prompt 当前状态已正确回退，不含过载的代码质量规范
    status: completed
---

## 用户需求

用户反映：3月6日平台可以正常生产游戏，3月7日更新后游戏生产质量（可运行率）大幅降低。需要检查3月7日的代码修改，定位并修复导致问题的根因。

## 产品概述

AITeam 是一个多 Agent 可视化协作系统，核心功能是通过 Pipeline 编排多个 AI Agent（Coder、Analyst、Assistant、Tester）协同工作，生产 Web 游戏等应用。用户提交需求后，系统自动分析、讨论、规划并执行任务，由 CoderAgent 调用 GLM 大模型生成游戏代码。

## 核心问题

通过 git 日志分析，3月7日共有两个影响游戏生产质量的关键提交，需要逐一排查修复：

### 问题一：CoderAgent Prompt 过载（主因，已回退）

提交 `e9ed0f5` 在 CoderAgent 的 system prompt 中追加了约 45 行"代码质量规范"，包括过于严格的代码量限制（500-650行）、要求完整 5 状态生命周期、三种输入方式、复杂 UI 系统（10+ CSS变量、3-5个动画）、以及可选增强（音效/粒子/存档/教程），导致 LLM 在有限输出空间中试图满足所有约束，生成代码要么过于复杂易出bug，要么骨架式代码缺乏实现。此问题已在3月11日通过 `c1315a9` 回退。

### 问题二：coordinator.py 数据结构不一致（遗留 Bug，未修复）

提交 `d5fe253` 将 `agents_by_type` 的数据结构从 `Dict[str, Agent]` 改为 `Dict[str, List[Agent]]`，但 `_reassign_agents()` 方法（第209-244行）未同步更新，仍使用旧的单 Agent 赋值结构。这导致服务重启后加载历史 Plan 时，Agent 重新分配可能异常。

### 问题三：代码提取正则放宽（潜在风险）

提交 `67fd491` 将 `output_manager.py` 的代码块提取正则从 `\n` 改为 `\n?`，虽然意图是兼容语言标识后无换行的情况，但可能导致误匹配行内代码片段（如文本中的 ``` 标记），提取出非代码内容。

## 技术栈

- 后端：Python + FastAPI
- LLM：智谱 GLM-4/GLM-5（zhipuai SDK）
- 实时通信：WebSocket
- 数据存储：SQLite + JSON 文件持久化

## 根因分析与修复方案

### 问题一：CoderAgent Prompt 过载（已回退，需要优化重新引入）

**根因**：`e9ed0f5` 在 `backend/app/agents/base.py` 的 CoderAgent system prompt 末尾追加了 45 行代码质量规范，设定了过多且相互矛盾的约束：

1. **代码量限制过于精确**：要求 500-650 行，LLM 要么生成骨架代码凑行数，要么超出限制后截断
2. **功能要求过于宏大**：同时要求完整 5 态生命周期 + 三种输入方式 + 复杂 UI 系统 + 可选增强，远超单次生成的合理复杂度
3. **约束冲突**：KISS 原则（简单）与功能完整性（复杂）互相矛盾，LLM 陷入两难
4. **Prompt 膨胀**：原有 system prompt 已含完整模板和约束，追加 45 行规范导致 prompt 过长，稀释了核心指令的权重

**当前状态**：已通过 `c1315a9` 回退，不需要额外修改。

**后续优化建议**：如果需要重新引入代码质量规范，应遵循以下原则：

- 不超过 10 行，只保留最关键的 Bug 防护规则（如 script 标签分离、变量初始化）
- 去掉代码量限制和功能完整性的硬性要求
- 不列举"可选增强"，避免 LLM 误认为是必选

### 问题二：coordinator.py `_reassign_agents()` 数据结构不一致（需修复）

**根因**：`d5fe253` 将 `generate_plan()` 和 `_generate_iteration_plan()` 中的 `agents_by_type` 结构从 `Dict[str, Agent]` 改为 `Dict[str, List[Agent]]`，并新增了 `_build_agents_by_type()` 和 `_get_agent_for_task()` 辅助方法。但 `_reassign_agents()` 方法（第 209-244 行）**完全没有适配**，仍然使用：

```python
agents_by_type[agent_type] = agent  # 旧结构：单个 Agent
```

而其他方法都已改为：

```python
agents_by_type[agent_type] = [agent1, agent2, ...]  # 新结构：Agent 列表
```

**影响**：

- 服务重启后调用 `_reassign_agents()` 时，每种类型只保留第一个 Agent，多 Agent 轮询分配失效
- 虽然这不是游戏可运行率降低的直接原因（它影响的是 Agent 分配而非代码生成），但可能导致非预期的 Agent 被分配到不匹配的任务

**修复方案**：将 `_reassign_agents()` 改为使用 `_build_agents_by_type()` 构建新结构，并在重新分配时取列表中的第一个 Agent（保持与之前行为一致的同时兼容新结构）。

### 问题三：output_manager.py 代码提取正则放宽（建议收紧）

**根因**：`67fd491` 将正则从 `r'```(\w+)?\s*\n(.*?)```'` 改为 `r'```(\w+)?\s*\n?(.*?)```'`。

`\n` 变为 `\n?` 使得正则可以匹配没有换行的情况，如 `` ```htmlcode``` ``，这会错误地将语言标识后紧跟的文本也当作代码内容，例如把 `html` 后面的 `<` 直接截断当成代码开头。

**修复方案**：改用更精确的正则，既允许无换行也避免误匹配：`r'```(\w+)?[ \t]*\n(.*?)```'`，只允许语言标识后的空格/制表符，但换行仍是必须的。

## 实施说明

1. **优先级**：问题一已修复，问题二是活跃 Bug 需立即修复，问题三是改善性修复
2. **风险控制**：`_reassign_agents()` 的修复只在服务重启加载历史 Plan 时触发，不影响正在执行的 Pipeline
3. **向后兼容**：正则修复不影响格式正确的代码块（有换行的情况），只收紧了异常格式的匹配

## 目录结构

```
backend/app/
├── agents/
│   └── base.py                # [已修复] CoderAgent prompt 已回退，确认当前状态正确
├── services/
│   ├── coordinator.py         # [MODIFY] 修复 _reassign_agents() 数据结构不一致
│   └── output_manager.py      # [MODIFY] 收紧代码提取正则，避免误匹配
```