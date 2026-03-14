---
name: rerun-frontend-backend-tests
overview: 为当前仓库梳理一套可执行的前后端测试重启/重跑方案，明确前端可用验证命令、后端 pytest 范围，以及执行后的结果交付方式。
todos:
  - id: confirm-test-entry
    content: 确认前后端可执行的启动与测试入口
    status: completed
  - id: restart-backend
    content: 重启 backend 服务并记录启动日志
    status: completed
    dependencies:
      - confirm-test-entry
  - id: run-backend-pytest
    content: 执行 backend 全量 pytest 并汇总结果
    status: completed
    dependencies:
      - restart-backend
  - id: restart-frontend
    content: 重启 frontend 服务并校验代理连通
    status: completed
    dependencies:
      - restart-backend
  - id: run-frontend-checks
    content: 执行 frontend build，并按环境补跑 lint
    status: completed
    dependencies:
      - restart-frontend
  - id: report-status
    content: 整理启动状态、测试结果与失败定位
    status: completed
    dependencies:
      - run-backend-pytest
      - run-frontend-checks
---

## User Requirements

- 重新执行当前项目的前后端验证流程，确认最近提交后的整体可运行状态。
- 后端需要重跑现有测试集；前端需要基于仓库当前可用入口完成可执行校验，并确认启动链路是否正常。
- 结果需要明确区分：启动是否成功、测试是否通过、若失败卡在前端还是后端、以及对应的关键日志信息。

## Product Overview

- 本次工作聚焦“重新启动并验证前后端”，不是新增功能开发。
- 最终交付应能直接说明前后端当前是否可正常启动、后端测试是否通过、前端现有校验是否通过，以及失败点落在哪个环节。

## Core Features

- 重启后端服务并验证其是否可正常提供接口。
- 重启前端服务并验证其是否能正常连通后端。
- 重跑后端现有测试集，输出通过与失败概况。
- 使用前端现有可执行校验入口完成验证，并记录环境缺失或脚本不可用问题。

## Tech Stack Selection

- 后端基于 Python 虚拟环境运行，仓库中已存在 `/Users/lindeng/AITeam/backend/venv/` 与 `backend/tests/`，测试入口明确为 `pytest`。
- 前端为 React + TypeScript + Vite，脚本入口位于 `/Users/lindeng/AITeam/frontend/package.json`。
- `/Users/lindeng/AITeam/frontend/vite.config.ts` 已确认前端开发服务运行在 `5173`，并将 `/api`、`/ws` 代理到 `http://localhost:8000`，因此启动顺序应优先后端，再前端。

## Implementation Approach

先基于现有脚本确认“可执行验证入口”，再按“后端启动与测试 → 前端启动与校验 → 结果汇总”执行。这样可以避免前端代理目标未就绪导致的假失败，并把启动问题与测试问题拆开定位。

关键决策如下：

- 后端测试以现有 `backend/tests/` 为准，优先使用 `/Users/lindeng/AITeam/backend/venv/bin/python -m pytest`，减少环境漂移。
- 前端未发现 `test` 脚本、测试框架配置或测试文件，因此前端验证以 `npm run build` 为主；`npm run lint` 虽已在 `package.json` 定义，但当前 `package-lock.json` 未检出 `eslint` 依赖，执行前需把它视为“补充检查”，避免把环境缺件误判为业务失败。
- 若需要联调验证，应以现有 Vite 代理配置为准，只做启动与连通性确认，不扩大到新增测试框架或改造脚本。

## Implementation Notes

- 保持工作区只做启动与验证，不夹带新的代码修改。
- 后端优先记录服务启动日志与 pytest 输出，前端优先记录 build 输出与代理连通情况。
- 若前端仅 lint 失败而 build 正常，应单独标记为“校验环境问题”而非“构建失败”。
- 若后端服务未起，前端代理验证应立即停止并回报根因，避免级联噪音。

## Architecture Design

当前验证链路为：后端服务监听 `8000` → 前端开发服务监听 `5173` → 前端通过 Vite 代理访问 `/api` 与 `/ws`。因此验证需要先确保后端可用，再验证前端启动与代理连通。

## Directory Structure

### Directory Structure Summary

本次计划不预期修改代码文件，主要复用现有启动与测试入口完成验证。

```text
/Users/lindeng/AITeam/
├── backend/
│   ├── venv/                                   # [USE] 现有 Python 虚拟环境；后端测试应优先从这里执行。
│   ├── requirements.txt                        # [USE] 后端依赖基线，定位缺包问题时参考。
│   └── tests/
│       ├── test_coordinator_reassign_agents.py # [USE] 后端 pytest 用例之一。
│       ├── test_output_manager.py              # [USE] 后端 pytest 用例之一。
│       ├── test_pipeline_queue.py              # [USE] 后端 pytest 用例之一。
│       ├── test_scoring_system.py              # [USE] 后端 pytest 用例之一。
│       ├── test_service_regressions.py         # [USE] 后端 pytest 用例之一。
│       └── test_web_output_validator.py        # [USE] 后端 pytest 用例之一。
└── frontend/
    ├── package.json                            # [USE] 前端脚本入口；当前存在 dev/build/lint/preview，无 test。
    ├── package-lock.json                       # [USE] 核对前端实际安装依赖，确认 lint 可执行性。
    └── vite.config.ts                          # [USE] 前端端口与代理配置，决定启动顺序与连通性验证方式。
```