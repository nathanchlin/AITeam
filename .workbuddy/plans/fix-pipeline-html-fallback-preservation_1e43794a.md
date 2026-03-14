---
name: fix-pipeline-html-fallback-preservation
overview: 定位并修复 web-app 流水线在生成 HTML 校验失败后退化为默认空骨架 index.html 的问题，确保无效候选不会被静默替换成空页面，并补齐诊断信息。
todos:
  - id: trace-preview-chain
    content: 使用 [subagent:code-explorer] 复核预览退化链路与受影响文件
    status: completed
  - id: harden-output-manager
    content: 修复 `output_manager.py` 的占位页识别、失效候选保留和安全合成
    status: completed
    dependencies:
      - trace-preview-chain
  - id: improve-validation-diagnostics
    content: 强化 `web_output_validator.py` 的 JS 语法报错提取与报告内容
    status: completed
    dependencies:
      - trace-preview-chain
  - id: fix-preview-serving
    content: 调整 `coordinator.py` 和 `pipeline.py` 的预览保留与失败返回
    status: completed
    dependencies:
      - harden-output-manager
      - improve-validation-diagnostics
  - id: add-regression-tests
    content: 补充 `backend/tests` 回归用例覆盖 8f7cad32 与 6ed9abd6
    status: completed
    dependencies:
      - harden-output-manager
      - improve-validation-diagnostics
      - fix-preview-serving
---

## User Requirements

- 排查流水线输出中 `index.html` 退化成默认骨架的问题，确认真实原因不在接口传输，而在产物保存、校验、合成与预览链路。
- 重点覆盖已复现的异常目录 `8f7cad32` 和 `6ed9abd6`，定位“真实候选页已生成，但最终只显示空骨架”的具体触发路径。
- 给出可执行修复方案，避免后续再次出现“预览地址正常可打开，但页面内容被默认骨架掩盖”的误导性结果。

## Product Overview

- 预览输出需要正确区分三种状态：可正常预览、最新候选无效但仍保留最近可用版本、当前无可用预览但能明确说明失败原因。
- 页面展示效果应从“空白默认壳”改为“真实可用页面”或“明确诊断信息”，避免用户误判为接口或前端显示异常。

## Core Features

- 阻止默认骨架覆盖有效预览，或掩盖失效候选页面。
- 在候选页面校验失败时保留候选文件与错误信息，并向预览链路透出真实失败原因。
- 对历史异常目录和新生成目录都能稳定识别“占位页”与“真实页面”，保证预览结果可信。

## Tech Stack Selection

- 后端沿用现有 `FastAPI` 路由层与 `app/services` 服务层结构。
- 预览产物管理继续复用 `backend/app/services/output_manager.py`。
- HTML 与 JavaScript 校验继续复用 `backend/app/services/web_output_validator.py` 中的现有校验流程与 Node `--check`。
- 前端现有预览消费入口位于 `frontend/src/components/UI/PipelinePanel.tsx`，本次优先通过后端修复保证直链可用，尽量不扩大前端改动面。

## Implementation Approach

### 高层策略

采用“安全预览解析”替代“失败后回退默认骨架”的策略：把 `index.authoritative.html` 视为最后可用版本，把 `index.invalid.candidate.html` 视为最新失效候选，把校验报告视为诊断依据；任何失败都不再静默生成空骨架覆盖真实状态。

### 关键技术决策

- 在 `output_manager.py` 中增加统一的“预览状态判定”与“占位页识别”逻辑，识别当前 `index.html` 或 `index.authoritative.html` 是否只是 `_generate_basic_html()` 生成的默认骨架。
- 修正 `consolidate_web_app()` 的优先级：只有真实有效 HTML 才能成为预览源；若仅存在失效候选，不再生成或接受默认骨架。
- 修正历史兼容问题：对已经落盘的旧骨架文件，若同时存在 `index.invalid.candidate.html` 和失败校验报告，不能再把该骨架当作有效预览。
- 在 `pipeline.py` 中为 `files/index.html` 增加失效诊断分支：当无有效预览但存在失效候选时，返回明确诊断结果，而不是继续返回空骨架。
- 在 `coordinator.py` 中补强保存失败后的状态透出，避免任务完成但预览实际失效时仍对外表现为正常完成。

### 性能与可靠性

- 预览状态解析以文件存在性检查和小型 JSON 报告读取为主，常规路径时间复杂度为 O(1)。
- 仅在需要判断骨架页或生成诊断时读取 HTML 内容，避免对大 HTML 做重复遍历。
- 继续沿用“最新候选校验失败不覆盖最后可用版本”的思路，确保回归后预览链路具备明确的降级边界。
- 避免重复运行无意义合成：对“仅有失效候选”的目录直接返回失败或诊断，减少无价值的回退写入。

## Implementation Notes

- 保持健康链路兼容：已有正常的 `index.authoritative.html` 仍然优先作为预览源。
- 禁止任何路径把默认骨架写成新的权威预览，除非未来显式定义“空模板计划”且无候选无报错。
- 校验失败时必须保留 `index.invalid.candidate.html` 与 `web_validation_save.json`，并输出可定位的 JS 报错信息，而不是只留下 Node 版本号。
- API 诊断页或诊断返回应尽量基于现有文件即时生成，不再新增新的误导性静态产物。

## Architecture Design

### 当前确认的问题链路

1. coder 产出完整 HTML。
2. `update_index_html()` 校验失败后只保存 `index.invalid.candidate.html`，不更新 `index.html`。
3. `coordinator.py` 之后仍调用 `save_plan_output()` 和 `consolidate_web_app()`。
4. `consolidate_web_app()` 排除了失效候选，又在无有效 HTML 时调用 `_generate_basic_html()`。
5. 生成的默认骨架被写成 `index.html`，甚至在缺少权威文件时写成 `index.authoritative.html`。
6. `pipeline.py` 发现 `index.html` 已存在后直接返回，最终用户看到的是空骨架。

### 目标结构

- `OutputManager`：负责统一解析预览状态、识别占位页、保护最后可用版本、拒绝骨架覆盖。
- `WebOutputValidator`：负责输出可读、可定位的语法与结构错误。
- `Coordinator`：负责把“生成成功但预览保存失败”的状态明确传播到计划结果。
- `Pipeline API`：负责把预览、失效候选、诊断信息对外正确暴露。

## Directory Structure

### Directory Structure Summary

本次修改集中在后端预览产物保存、合成、诊断和回归测试，不做无关重构。

```text
/Users/lindeng/AITeam/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── pipeline.py                      # [MODIFY] 调整 index.html 访问逻辑；识别历史骨架页；在无有效预览时返回明确诊断，而不是静默返回空骨架。
│   │   └── services/
│   │       ├── coordinator.py                  # [MODIFY] 调整 web-app 产物保存失败后的状态透出与最终 output_url 生成条件，避免“任务完成但预览失效”被误判为成功。
│   │       ├── output_manager.py               # [MODIFY] 增加占位页识别、统一预览状态解析、安全合成策略；禁止默认骨架覆盖有效预览；兼容历史异常目录。
│   │       └── web_output_validator.py         # [MODIFY] 强化 JS 语法报错提取，保存可定位的错误上下文，避免报告只显示 Node 版本号。
│   └── tests/
│       ├── test_output_manager.py              # [MODIFY] 补充“失效候选存在时不生成骨架”“历史骨架不应被当作权威页”等回归用例。
│       ├── test_web_output_validator.py        # [MODIFY] 补充 Node `--check` 报错解析与错误信息持久化测试。
│       └── test_pipeline_output_api.py         # [NEW] 覆盖 `files/index.html` 访问场景，验证无有效预览时返回诊断而不是空骨架。
```

## Key Code Structures

- 可在 `output_manager.py` 中新增一个统一的预览状态描述方法，返回是否存在权威页、是否命中占位页、是否存在失效候选、最近校验报告与推荐预览行为，供 `coordinator.py` 和 `pipeline.py` 共同复用，避免重复判定逻辑。

## Agent Extensions

### SubAgent

- `code-explorer`
- Purpose: 复核 `output_manager.py`、`coordinator.py`、`pipeline.py` 与测试文件之间的调用链和回归影响面。
- Expected outcome: 精确锁定需要修改的保存、合成、预览与测试入口，避免遗漏历史骨架兼容场景。