# OpenSpec 修复方案

> **诊断日期**: 2026-04-12  
> **状态**: 待实施  
> **影响文件**: `backend/app/services/coordinator.py`（主文件）

---

## 一、问题诊断

### 数据事实
| 指标 | 当前值 | 目标值 |
|------|--------|--------|
| Specs 生成率 | 18%（7/39） | ≥ 80% |
| Delta 合并次数 | 0 | 迭代时 100% 合并 |
| Specs 对 Agent 可见 | 否（0次注入） | 每次 Coder 任务可见 |

### 三个断点

```
[用户需求] → [讨论] → [Specs 生成] ✗ 82%没生成
                                    ↓
                               [Delta 合并] ✗ 从未触发
                                    ↓
                               [注入任务Prompt] ✗ Agent 不读 Specs
```

---

## 二、修复方案（3 个改动点，改动量最小化）

### 🔧 Fix 1: 降低 Specs 生成门槛

**文件**: `coordinator.py` 第 1367-1371 行  
**问题**: 条件 `not plan.skip_discussion and plan.discussion` 太严格，走快速模式的 Plan 全部跳过  
**改动**: 不依赖讨论阶段，直接从 `original_request` + `target_output` 生成

```python
# ---- 改前 (第 1367-1371 行) ----
if not plan.skip_discussion and plan.discussion:
    _pipeline_logger.info(f"[Specs] Generating specs for plan {plan_id}")
    plan.specs = await self._generate_specs(plan)
    self._save_plans()

# ---- 改后 ----
# 只要没生成过 specs 就生成（不依赖讨论阶段）
if not plan.specs:
    _pipeline_logger.info(f"[Specs] Generating specs for plan {plan_id}")
    plan.specs = await self._generate_specs(plan)
    self._save_plans()
```

**同步修改 `_generate_specs` 方法**（第 911-916 行），降低对 `plan.discussion` 的依赖：

```python
# ---- 改前 ----
if not plan.discussion:
    return ""

# ---- 改后 ----
if not plan.discussion and not plan.original_request:
    return ""
```

同时修改 prompt 构建（第 918-925 行），没有讨论时用 original_request 补充：

```python
# ---- 改前 ----
discussion_context = "\n".join([
    f"[{msg.agent_name}]: {msg.content[:300]}"
    for msg in plan.discussion[-6:]
])

# ---- 改后 ----
if plan.discussion:
    discussion_context = "\n".join([
        f"[{msg.agent_name}]: {msg.content[:300]}"
        for msg in plan.discussion[-6:]
    ])
else:
    discussion_context = f"项目需求：{plan.original_request}"
```

---

### 🔧 Fix 2: 将 Specs 注入 Coder 任务 Prompt

**文件**: `coordinator.py` 第 1897-1907 行  
**问题**: `task_description` 只包含 `discussion_context`，不包含 specs  
**改动**: 在 discussion_context 后追加 specs_context

```python
# ---- 在第 1904 行后追加（discussion_context 之后）----

# 注入 OpenSpec 规范文档（如果有）
specs_context = ""
if plan.specs and agent.type.value == "coder":
    specs_context = f"""

📋 **项目规范（必须遵循）：**
{plan.specs}

⚠️ 请严格按照以上规范实现功能。
"""

# ---- 然后修改 task_description（第 1907 行）----

# ---- 改前 ----
task_description = f"""任务：{task.title}

描述：{task.description or '无详细描述'}

原始需求上下文：{plan.original_request}
{discussion_context}{previous_tasks_context}{fix_context}{web_app_instructions}{ts_app_instructions}{godot_instructions}

请完成你的任务部分，提供详细的输出。"""

# ---- 改后 ----
task_description = f"""任务：{task.title}

描述：{task.description or '无详细描述'}

原始需求上下文：{plan.original_request}
{specs_context}{discussion_context}{previous_tasks_context}{fix_context}{web_app_instructions}{ts_app_instructions}{godot_instructions}

请完成你的任务部分，提供详细的输出。"""
```

**注意事项**: specs_context 放在 discussion_context 前面，因为规范比讨论摘要更有约束力。

---

### 🔧 Fix 3: 迭代时 Delta 生成兜底 + 归档保障

**问题**: 即使有迭代的 Plan（8个），Delta 也没有合并成功。原因可能是：
- `plan.specs` 为空导致跳过（Fix 1 已解决）
- `archive_iteration_deltas` 有异常但被静默吞掉了

**文件**: `coordinator.py` 第 4357-4363 行  
**改动**: 增加日志 + 兜底保障

```python
# ---- 改前 (第 4357-4363 行) ----
if plan.deltas:
    try:
        await self.archive_iteration_deltas(plan_id, iteration_round.round_number)
        _pipeline_logger.info(f"[DeltaSpec] Archived deltas for iteration {iteration_round.round_number}")
    except Exception as e:
        _pipeline_logger.error(f"[DeltaSpec] Failed to archive deltas: {e}")

# ---- 改后 ----
# Phase 2: Delta Spec 合并（迭代结束前）
if plan.deltas:
    _pipeline_logger.info(f"[DeltaSpec] Found {len(plan.deltas)} deltas to archive")
    try:
        await self.archive_iteration_deltas(plan_id, iteration_round.round_number)
        _pipeline_logger.info(f"[DeltaSpec] ✓ Archived deltas for iteration {iteration_round.round_number}")
    except Exception as e:
        _pipeline_logger.error(f"[DeltaSpec] Failed to archive deltas: {e}")
        # 兜底：即使归档失败，也保留 deltas 不丢失
        _pipeline_logger.warning(f"[DeltaSpec] Deltas preserved for manual recovery")
else:
    # 没有 deltas 但有 specs → 可能是 Delta 生成失败，记日志
    if plan.specs:
        _pipeline_logger.warning(
            f"[DeltaSpec] Iteration completed but no deltas generated "
            f"(specs exists: {len(plan.specs)} chars)"
        )
```

---

## 三、验证清单

修复后，用以下方式验证：

```bash
# 1. 启动后端
cd backend && uvicorn app.main:app --reload --port 8000

# 2. 创建一个新的 Plan（走快速模式，不讨论）
# 预期： Specs 应该自动生成（Fix 1）

# 3. 执行任务，观察 Coder 的 prompt
# 预期： prompt 中包含 "📋 **项目规范（必须遵循）**"（Fix 2）

# 4. 发起迭代
# 预期： 日志显示 "[DeltaSpec] Generating delta specs"
# 预期： 迭代完成后 specs_version 从 1 变为 2（Fix 3）
```

**日志关键词监控**:
```
[Specs]          → 规范生成
[DeltaSpec]      → Delta 生成/合并
specs_version    → 版本号变化
```

---

## 四、改动量估算

| Fix | 文件 | 改动行数 | 风险 |
|-----|------|----------|------|
| Fix 1 | coordinator.py | ~15 行 | 🟢 低 — 只放宽条件 |
| Fix 2 | coordinator.py | ~12 行 | 🟢 低 — 纯追加，不改现有逻辑 |
| Fix 3 | coordinator.py | ~10 行 | 🟢 低 — 增加日志和兜底 |
| **总计** | **1 个文件** | **~37 行** | |

> 遵循调试原则：**禁止大改结构，只改出错的那几行。**

---

## 五、可选优化（Phase 2，本次不做）

- [ ] Specs 缓存：相同类型的游戏复用规范模板
- [ ] 前端 DeltaSpecViewer 默认展开：当前默认折叠，用户看不到
- [ ] Specs 质量评分：用 LLM 自评规范质量
- [ ] 多轮 Delta 可视化：在 Plan 详情页显示规范演进时间线
