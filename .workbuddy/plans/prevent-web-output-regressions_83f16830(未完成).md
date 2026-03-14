---
name: prevent-web-output-regressions
overview: 分析 web 产物生成质量问题的根因，制定一套从提示约束、保存/合并、预测试验证到真实运行回归的防回归方案，避免再次生成出可打开但不可用的 HTML 页面。
todos:
  - id: unify-web-contract
    content: 用[subagent:code-explorer]统一 `coordinator.py` 与 `base.py` 的 Web 生成契约
    status: pending
  - id: build-validator-service
    content: 新增 `web_output_validator.py` 并接入 `output_manager.py` 的保存与合并链路
    status: pending
    dependencies:
      - unify-web-contract
  - id: wire-validation-gate
    content: 改造 `coordinator.py` 与 `quality_scorer.py`，让校验失败进入修复闭环
    status: pending
    dependencies:
      - build-validator-service
  - id: upgrade-smoke-flow
    content: 用[skill:agent-browser]设计 smoke 场景并接入 tester 验证上下文
    status: pending
    dependencies:
      - wire-validation-gate
  - id: add-regression-suite
    content: 补齐 `backend/tests` 回归用例，覆盖坏页与假成功场景
    status: pending
    dependencies:
      - build-validator-service
      - wire-validation-gate
      - upgrade-smoke-flow
---

## User Requirements

围绕现有 Web 产物生成链路，定位“为什么系统会生成出打不开、能打开但不能正常交互、提示与真实行为不一致”的问题来源，并给出一套可持续避免的改造方案。范围不是继续手工修单个页面，而是修生成机制、校验机制和测试闭环。

## Product Overview

当前需要把产物生成从“只要文件落盘就算完成”，改成“只有通过结构、运行和关键交互校验才算完成”。对外效果应是：预览页不再频繁出现坏页面，失败时能明确暴露问题类别和修复方向，而不是把异常结果当成已完成产物。

## Core Features

- 分析并收敛 Web 产物生成规范，避免所有页面被错误地套进同一类模板约束
- 在生成、合并、保存后的关键节点增加可运行性校验，尽早拦截坏产物
- 调整任务状态流转，校验失败时进入修复闭环，而不是直接标记完成
- 升级测试机制，覆盖脚本语法、页面初始化、核心交互、状态一致性等真实故障模式
- 为已暴露问题补回归，避免布局异常、交互假成功、自动状态修复失效等问题再次出现

## Tech Stack Selection

- 现有后端主链路：Python 服务，核心逻辑位于 `backend/app/services`
- 现有执行编排：`coordinator.py` 负责任务生成、执行、质量门禁与测试阶段串联
- 现有产物处理：`output_manager.py` 负责提取、合并、更新 `index.html`
- 现有质量评分：`quality_scorer.py` 负责静态质量评分
- 现有 Agent 提示词：`backend/app/agents/base.py`
- 现有测试：`backend/tests/test_output_manager.py`、`backend/tests/test_service_regressions.py`

## Implementation Approach

### 核心策略

本次改造采用“三层防线”方案：先纠正生成契约，再补落盘后的硬校验，最后把测试与状态流转接入闭环。这样可以同时解决“模型生成方向偏了”“合并修补把代码改坏了”“测试没真正执行页面”三类问题。

### 已确认的主要根因

1. `coordinator.py` 和 `base.py` 中的 Web 约束偏向 Canvas 游戏模板，容易把并非 Canvas 的页面也推向同一种生成范式。  
2. `update_index_html()` 会直接提取并覆盖 `index.html`，缺少保存前的运行校验。  
3. `consolidate_web_app()` 会做脚本抽取、去重、自动修补和重新注入，但没有配套验证修补后行为是否仍然正确。  
4. `pre_test_validation()` 主要是正则级静态检查，能拦截明显残缺，拦不住布局异常、点击链路失效、提示文案与真实状态不一致等运行问题。  
5. `coordinator.py` 当前在 Web 预测试失败时会直接跳过测试并结束流程，这会把坏产物留在“已完成”路径上。  
6. tester 阶段当前主要让 LLM 基于代码文本做评论式测试，不是真执行页面。

### 方案拆解

#### 方案一：统一生成契约

在 `coordinator.py` 与 `base.py` 中按产物类型区分约束，至少拆成“Canvas 游戏”“DOM 交互页/小游戏”“普通单页应用”三类，不再对所有 `web-app` 强制要求 Canvas、`getContext`、游戏循环。
同时统一增量修改契约：保留“输出完整最终 HTML”的规则，去掉可能干扰模型的冲突性描述。

#### 方案二：新增独立校验服务

新增 `backend/app/services/web_output_validator.py`，集中承接以下能力：

- HTML 结构与关键标签完整性检查
- 内联脚本提取后的 JS 语法检查
- DOM 引用与关键元素存在性检查
- 合并后脚本重注入一致性检查
- 轻量运行信号检查，例如初始化入口、事件可达性、关键状态更新钩子是否存在

之所以单独拆服务，而不是继续堆进 `output_manager.py`，是因为 `output_manager.py` 已承担提取、合并、归档、Godot 校验等多种职责；继续扩大会增加耦合和回归风险。

#### 方案三：把校验接入真正门禁

- `update_index_html()` 保存前先做轻量校验，避免明显坏 HTML 直接落盘
- `consolidate_web_app()` 合并后再次做最终校验，确保“修补”和“去重”没有引入新问题
- `quality_scorer.py` 改为消费结构化校验信号，而不是只靠静态正则评分
- `coordinator.py` 中若 Web 校验失败，不再把计划标记为完成，而是转入修复迭代或明确失败状态，并把错误摘要回灌给 coder/tester

#### 方案四：升级测试闭环

保留现有 tester 角色，但把 tester 的输入从“纯代码文本”升级为“代码文本 + 结构化校验报告 + smoke 结果摘要”。
测试分层建议：

- 运行时硬门禁：便宜、确定、超时可控的轻量校验
- 测试/CI 回归：针对真实故障模式执行更强的 smoke 验证

### Performance &amp; Reliability

- 静态校验和脚本提取复杂度基本为 O(n)，n 为 HTML 文本长度，适合在每次保存与最终合并后执行
- 较重的 smoke 校验只在最终 `index.html` 执行，避免对每个中间步骤重复放大成本
- 对校验结果按内容哈希做缓存可避免重复分析同一产物
- 日志只记录错误摘要、定位信息和失败类别，不打印整份 HTML，避免日志膨胀
- 若较重校验不可用，应保留轻量静态校验兜底，但不能静默跳过失败结果

## Implementation Notes

- 复用现有 `quality_scorer`、`pre_test_validation`、任务讨论消息与修复迭代机制，避免另起一套状态机
- 不做无关重构，重点收敛在 `coordinator.py`、`output_manager.py`、`quality_scorer.py` 与提示词契约
- 优先修正“预测试失败仍算完成”的状态流转问题，这是当前坏产物外溢的关键缺口
- 先上轻量硬门禁，再补更强 smoke 与更细粒度评分，降低首轮改造风险

## Architecture Design

### 改造后链路

1. Coder 依据更准确的 Web 产物类型约束生成完整 HTML  
2. `output_manager.py` 在保存与合并后调用 `web_output_validator.py`  
3. `quality_scorer.py` 消费校验结果，形成更可信的质量分  
4. `coordinator.py` 根据校验与评分决定：通过、进入修复迭代、或阻断完成态  
5. tester 基于机器校验结果补充逻辑与边界场景验证  
6. 回归测试把真实故障模式固化到 `backend/tests`

## Directory Structure

### Directory Structure Summary

本次改造聚焦现有 Web 产物生成主链路，新增一个独立校验服务，并在提示词、状态门禁和测试层建立闭环。

```text
/Users/lindeng/AITeam/backend/app/agents/base.py
  [MODIFY] Coder 系统提示词与增量修改约束。统一“完整 HTML 输出”规则，移除对所有 web-app 一刀切的 Canvas 倾向，减少提示词冲突。

/Users/lindeng/AITeam/backend/app/services/coordinator.py
  [MODIFY] 生成约束、修复迭代、质量门禁、预测试失败状态流转与 tester 输入编排。重点修复“校验失败却直接完成”的流程缺口。

/Users/lindeng/AITeam/backend/app/services/output_manager.py
  [MODIFY] 在 `update_index_html()` 与 `consolidate_web_app()` 后接入结构化校验，限制文本级自动修补的破坏面，并输出可消费的校验摘要。

/Users/lindeng/AITeam/backend/app/services/quality_scorer.py
  [MODIFY] 将静态规则评分升级为“静态规则 + 校验信号”混合评分，降低“像完整页面但实际不能用”的误判。

/Users/lindeng/AITeam/backend/app/services/web_output_validator.py
  [NEW] Web 产物独立校验服务。负责 HTML 结构、JS 语法、DOM 引用、初始化入口、合并后脚本一致性与轻量运行信号检查。

/Users/lindeng/AITeam/backend/tests/test_output_manager.py
  [MODIFY] 为 `update_index_html()`、`consolidate_web_app()` 与保存后校验链补单测，覆盖 HTML 提取、脚本重注入、坏内容拦截等场景。

/Users/lindeng/AITeam/backend/tests/test_service_regressions.py
  [MODIFY] 补充 Coordinator 与门禁回归，覆盖“预测试失败进入修复而非完成”“类型化约束”“坏页面不进入完成态”等流程问题。

/Users/lindeng/AITeam/backend/tests/test_web_output_validator.py
  [NEW] 为独立校验服务补专项回归，覆盖语法错误、DOM 缺失、初始化缺失、提示与状态不一致等真实故障模式。
```

## Key Code Structures

```python
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class WebOutputValidationResult:
    passed: bool
    stage: str
    errors: List[str]
    warnings: List[str]
    signals: Dict[str, Any]
    score_hint: Optional[float] = None

class WebOutputValidator:
    def validate_html_output(
        self,
        html_content: str,
        stage: str,
        requirements: str = ""
    ) -> WebOutputValidationResult:
        ...
```

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 复核 `coordinator.py`、`output_manager.py`、`quality_scorer.py` 之间的调用链和影响面
- Expected outcome: 给出完整的改造触点与回归范围，避免漏改门禁路径或状态分支

### Skill

- **agent-browser**
- Purpose: 为后续实现阶段设计并验证 Web 产物的浏览器级 smoke 场景
- Expected outcome: 形成可复用的页面加载、初始化、点击交互和状态变化检查样板，补足纯文本测试缺口