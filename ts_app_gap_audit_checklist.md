# ts-app 缺口审计与落地清单

## 执行摘要

本次先完成了协作流水线界面的最小可用修复：`frontend/src/components/UI/PipelinePanel.tsx` 已补上 `ts-app` 选项，用户现在可以直接在目标输出下拉框里选择“TS工程应用”。同时复核后端发现，`pipeline.py` 对 `ts-app` 的预览与下载接口已存在，因此这次前端补口后，主流程入口已打通。

进一步审计显示，`ts-app` 当前并不是“完全未实现”，而是“前端入口刚补齐，但质量保障链路仍不完整”。主要缺口集中在 `quality_scorer.py`、`web_output_validator.py`、`code_merger.py` 三处：它们仍以单文件 HTML/web-app 语义为中心，尚未为多文件 Vite + TypeScript 工程建立同等级的评分、校验和增量合并能力。

## 本次已完成的变更

### 1. 前端入口已补齐

已修改文件：`frontend/src/components/UI/PipelinePanel.tsx`

变更内容：在目标输出下拉框中新增：

```tsx
<option value="ts-app">TS工程应用</option>
```

当前下拉框顺序为：`web-app`、`ts-app`、`godot-game`、`api`、`report`、`documentation`。

### 2. 后端入口复核结果

后端已有能力，无需本次补改：

- `backend/app/api/pipeline.py` 已支持 `target_output="ts-app"` 启动计划
- 预览接口已支持 `ts_app/dist/index.html`
- 已存在 `GET /output/{plan_id}/ts-app`
- 已存在 `GET /output/{plan_id}/ts-app/download`

因此这次问题的直接根因就是：前端没有把 `ts-app` 暴露到选择器里。

## 审计范围

本次重点审计以下 3 个文件在 `ts-app` 场景下的能力缺口：

- `backend/app/services/quality_scorer.py`
- `backend/app/services/web_output_validator.py`
- `backend/app/services/code_merger.py`

并参考了以下调用链文件：

- `backend/app/services/coordinator.py`
- `backend/app/services/output_manager.py`
- `backend/app/services/ts_builder.py`

## 审计结论

### 1. quality_scorer.py

当前职责是对输出结果做质量评分，但它的规则明显围绕单文件 HTML/内联 JS 展开。`score_output(...)` 当前没有 `target_output` 或 `mode` 分支，仍默认按 web-app 语义工作。

主要问题：

- 完整性评分仍要求 `<!DOCTYPE html>`、`</html>`、`<style>`、`<canvas>` 等单文件 HTML 特征
- 正确性、可维护性、性能等多个维度依赖从 `<script>...</script>` 中提取 JS
- 对多文件 TypeScript 源码、`src/main.ts`、模块 import/export 几乎没有直接识别能力
- 如果未来拿 `dist/index.html` 去评分，还会把 Vite 正常输出的外链 JS/CSS 误判为问题

结论：`quality_scorer.py` 当前不能对 `ts-app` 做可靠评分，且存在系统性误伤风险。

### 2. web_output_validator.py

当前职责是对 HTML 产物做结构校验与最小运行校验。主入口 `validate_html_output(...)` 接收的是 `html_content: str`，本质上就是单文件页面校验器。

主要问题：

- 规则围绕 HTML/body/DOCTYPE 完整性展开，不适用于 TS 工程源码
- 会把外链 JS/CSS 当成错误，这与 Vite 构建产物天然冲突
- 语法检查走的是 `node --check`，适合 JS，不适合 TS
- smoke test 依赖“提取内联脚本 + fake DOM + vm.runInContext”，不适合 ES Module 多文件工程
- 没有针对 `src/main.ts`、入口模块、typecheck/build 结果的结构化 signals

结论：`web_output_validator.py` 目前不能直接承担 `ts-app` 的专属验证职责。

### 3. code_merger.py

当前职责是把 LLM 输出的增量修改块合并回 HTML 页面，核心是围绕 `<<<MODIFY>>> / <<<ADD>>> / <<<DELETE>>> / <<<CSS>>>` 等块，对函数和样式做增量修补。

主要问题：

- 入口是 `merge_html(...)`，能力中心是 HTML，不是工程目录
- `target` 语义目前更像“函数名/选择器”，不是“文件路径”
- 主要逻辑围绕 JS 函数边界、`</script>`、`<style>` 做 fallback，不适用于 TS 多文件项目
- `ts-app` 当前虽然有增量模式提示，但真正的“文件级增量合并器”并未落在这里

结论：`code_merger.py` 对 `ts-app` 目前基本处于未接入状态。

## 落地清单

### P0：必须优先完成

#### quality_scorer.py

- [ ] 给 `score_output(...)` 增加显式 `target_output` 或 `mode` 参数
- [ ] 新增 `ts-app` 专属评分分支，避免复用 HTML 单文件规则
- [ ] 为 `ts-app` 补充最小评分项：`src/main.ts`、入口挂载、样式入口、import/export 结构、基础交互与渲染
- [ ] 将 typecheck/build 结果作为 correctness 的核心输入，而不是继续依赖 `<script>` 提取
- [ ] 避免对 `ts-app` 或其 `dist` 产物误套“禁止外链 JS/CSS”的 web-app 规则

#### web_output_validator.py

- [ ] 保留 `validate_html_output(...)`，新增 `validate_ts_app_output(...)`
- [ ] 支持以项目目录或文件集合为输入，而非只接受 HTML 字符串
- [ ] 最小检查项至少覆盖：`src/main.ts` 是否存在、是否存在入口模块、是否存在挂载根节点、typecheck 是否通过、bundle/build 是否通过
- [ ] 增加 ts-app 专属 signals，例如 `has_src_main`、`typecheck_passed`、`bundle_passed`、`file_count`
- [ ] 不再把 Vite 构建产生的外链 JS/CSS 当成错误

#### code_merger.py

- [ ] 增加 `ts-app` 的文件级增量合并能力
- [ ] 支持按文件路径替换、新增、删除，例如 `src/main.ts`、`src/game.ts`、`src/styles.css`
- [ ] 路径范围与 `output_manager.extract_ts_app_files(...)` 对齐，只允许 `src/`、`public/`
- [ ] 去掉对 `</script>` / `<style>` fallback 的依赖，至少在 ts-app 分支中禁用

#### 打通 validator 与 scorer

- [ ] 让 `ts-app` validator 输出结构化结果，并被 `quality_scorer` 消费
- [ ] 复用已有 validation feedback 通道，把 typecheck/build 失败直接映射成降分与建议

### P1：建议第二阶段完成

- [ ] 为 `ts-app` validator 增加更丰富的 signals，例如样式导入、事件绑定、状态更新、缺失 import 候选
- [ ] 为 `code_merger.py` 增加文件内更细粒度的符号级修改能力，例如 `export function`、`export class`、类方法更新
- [ ] 增加基于构建产物的最小 runtime smoke，至少能发现启动阶段异常

### P2：中长期建设

- [ ] 引入 AST 级 TypeScript merge 能力，降低整文件覆盖带来的冲突
- [ ] 将 bundle 体积、构建警告、模块层级等纳入更真实的性能/可维护性评分
- [ ] 为 ts-app 建立更接近真实应用体验的 UX 评分规则

## 建议的下一步顺序

1. 先补 `quality_scorer.py` 的 `ts-app` 模式入口与基础评分规则。
2. 再补 `web_output_validator.py` 的 `validate_ts_app_output(...)`，并把 `ts_builder` 结果结构化输出。
3. 最后给 `code_merger.py` 增加最小“按文件路径合并”的能力，先不急着上 AST 级别复杂实现。

## 本次验证结果

- `PipelinePanel.tsx` 已成功写入 `ts-app` 选项
- 读取修改后代码确认下拉框已包含“TS工程应用”
- 对 `PipelinePanel.tsx` 读取诊断信息，未发现新增 lints

## 相关文件

- `frontend/src/components/UI/PipelinePanel.tsx`
- `backend/app/api/pipeline.py`
- `backend/app/services/quality_scorer.py`
- `backend/app/services/web_output_validator.py`
- `backend/app/services/code_merger.py`
- `backend/app/services/output_manager.py`
- `backend/app/services/ts_builder.py`
- `backend/app/services/coordinator.py`
