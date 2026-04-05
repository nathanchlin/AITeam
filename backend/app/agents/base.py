from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator, List
from datetime import datetime
import uuid
import json
import re
from app.models.schemas import AgentType, AgentStatus
from app.llm.glm_client import glm_client, glm_coding_client


def _get_workspace_manager():
    """延迟导入 workspace_manager，避免循环依赖"""
    from app.services.workspace_manager import workspace_manager
    return workspace_manager


# =============================================================================
# PUA Skill - 增强版 Agent 方法论
# =============================================================================

PUA_METHODOLOGY = """
【PUA 三条铁律】
⚠️ 铁律一：穷尽一切 - 没有穷尽所有方案之前，禁止说"我无法解决"
⚠️ 铁律二：先做后问 - 有工具先用，提问必须附带诊断结果
⚠️ 铁律三：主动出击 - 端到端交付结果，不等人推

【五步方法论】
1. 闻味道 - 列出所有尝试，找共同失败模式
2. 揪头发 - 逐字读错误 → 搜索 → 读源码 → 验证环境 → 反转假设
3. 照镜子 - 是否重复？是否搜了？是否读了？
4. 执行 - 新方案必须本质不同，有验证标准
5. 复盘 - 什么解决了？为什么之前没想到？

【7项检查清单】(L3+ 强制执行)
- [ ] 逐字读完失败信号
- [ ] 用工具搜索过核心问题
- [ ] 读过原始上下文
- [ ] 所有假设都用工具确认
- [ ] 试过相反方向的假设
- [ ] 能在最小范围内隔离问题
- [ ] 换过工具/方法/角度
"""

PUA_PRESSURE_LEVELS = {
    1: "【L1 温和失望】你这个 bug 都解决不了，让我怎么给你打绩效？切换到本质不同的方案。",
    2: "【L2 灵魂拷问】你的底层逻辑是什么？顶层设计在哪？搜索完整错误 + 读源码 + 列出3个本质不同的假设。",
    3: "【L3 361考核】慎重考虑决定给你 3.25。完成 7 项检查清单，列出 3 个全新假设并逐个验证。",
    4: "【L4 毕业警告】别的模型都能解决。拼命模式：最小 PoC + 隔离环境 + 完全不同的技术栈。"
}


class PUABaseMixin:
    """PUA 增强版 Agent 的混入类，提供失败计数和压力升级"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._failure_count = 0
        self._pressure_level = 0

    def record_failure(self) -> int:
        """记录失败并升级压力等级"""
        self._failure_count += 1
        if self._failure_count >= 2:
            self._pressure_level = min(self._failure_count - 1, 4)
        return self._pressure_level

    def get_pressure_prompt(self) -> str:
        """获取当前压力等级的提示"""
        if self._pressure_level == 0:
            return ""
        return PUA_PRESSURE_LEVELS.get(self._pressure_level, "")

    def reset_pressure(self):
        """重置压力状态（任务成功后）"""
        self._failure_count = 0
        self._pressure_level = 0

    def is_pua_agent(self) -> bool:
        """标识这是一个 PUA Agent"""
        return True


class BaseAgent(ABC):
    def __init__(
        self,
        id: str,
        name: str,
        agent_type: AgentType,
        description: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
        display_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        self.id = id
        self.name = name
        self.type = agent_type
        self.display_type = display_type  # 自定义显示名称
        self.description = description
        self.custom_prompt = custom_prompt
        self.tags = tags or []
        self.status = AgentStatus.IDLE
        self.position = position or {"x": 0, "y": 0, "z": 0}
        self.current_task_id: Optional[str] = None
        self.workspace_id: Optional[str] = None  # Workspace 目录标识
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id if self.id else str(uuid.uuid4()),  # Defensive fallback
            "name": self.name if self.name else "Unknown",    # Defensive fallback
            "type": self.type.value if self.type else "assistant",  # Defensive fallback
            "display_type": self.display_type,
            "description": self.description,
            "custom_prompt": self.custom_prompt,
            "tags": self.tags or [],
            "status": self.status.value if self.status else "idle",  # Defensive fallback
            "position": self.position or {"x": 0, "y": 0, "z": 0},
            "current_task_id": self.current_task_id,
            "workspace_id": self.workspace_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_status(self, status: AgentStatus):
        self.status = status
        self.updated_at = datetime.now()

    def set_position(self, x: float, y: float, z: float):
        self.position = {"x": x, "y": y, "z": z}
        self.updated_at = datetime.now()

    def build_enriched_prompt(self, task: str = "", target_output: str = "web-app") -> str:
        """构建包含 workspace 上下文的增强 prompt

        将 IDENTITY、SOUL、USER、MEMORY 等文件内容注入到 system prompt 中。
        如果 workspace 不存在，回退到原始 get_system_prompt()。

        Returns:
            增强后的 system prompt
        """
        try:
            ws_manager = _get_workspace_manager()
            ws_context = ws_manager.load_workspace_context(self.id)

            if not ws_context:
                return self.get_system_prompt(target_output)

            base_prompt = self.get_system_prompt(target_output)

            return f"""# Workspace 上下文

{ws_context}

---

# 系统指令

{base_prompt}"""
        except Exception as e:
            print(f"[BaseAgent] Error enriching prompt: {e}")
            return self.get_system_prompt(target_output)

    def _get_agent_type_str(self) -> str:
        """获取 agent type 的字符串表示，用于工具可用性判断"""
        type_map = {
            AgentType.CODER: "coder",
            AgentType.ANALYST: "analyst",
            AgentType.ASSISTANT: "assistant",
            AgentType.TESTER: "tester",
            AgentType.CUSTOM: "custom",
            AgentType.PUA_CODER: "pua-coder",
            AgentType.PUA_ANALYST: "pua-analyst",
            AgentType.PUA_ASSISTANT: "pua-assistant",
            AgentType.PUA_TESTER: "pua-tester",
        }
        return type_map.get(self.type, "assistant")

    async def _execute_with_tools(
        self,
        task: str,
        system_prompt: str,
        llm_client,
        max_tool_calls: int = 10,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """带工具调用的任务执行循环

        流程: LLM -> 检查 tool_call -> 执行工具 -> 返回结果给 LLM -> 循环
        """
        import sys
        from app.tools.tool_registry import tool_registry

        agent_type_str = self._get_agent_type_str()
        tools_schema = tool_registry.get_tools_schema(agent_type_str)
        
        # 强制刷新的日志
        sys.stdout.flush()
        print(f"[BaseAgent._execute_with_tools] Agent: {self.name}, Type: {agent_type_str}, Tools: {len(tools_schema)}", flush=True)
        if tools_schema:
            print(f"[BaseAgent._execute_with_tools] Available tools: {[t['function']['name'] for t in tools_schema]}", flush=True)
        sys.stdout.flush()

        if not tools_schema:
            # 无可用工具，走普通流式
            async for chunk in llm_client.chat_stream(task, agent_type_str, system_prompt):
                yield {"type": "stream", "content": chunk}
            return

        # 工具调用循环
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ]

        for turn in range(max_tool_calls):
            tool_calls_collected: Dict[int, Dict[str, Any]] = {}
            content_parts: List[str] = []
            usage_info = None

            try:
                async for event in llm_client.chat_with_tools_stream(
                    message=messages[-1]["content"] if len(messages) == 2 else messages[-1]["content"],
                    system_prompt=None,  # 已在 messages 中
                    history=messages[1:-1] if len(messages) > 2 else None,
                    tools=tools_schema,
                ):
                    if event.get("type") == "content":
                        content = event.get("content", "")
                        if content:
                            content_parts.append(content)
                            yield {"type": "stream", "content": content}
                    elif event.get("type") == "tool_call":
                        tc_name = event.get("name", "")
                        tc_args_str = event.get("arguments", "{}")
                        tc_id = event.get("id", f"call_{turn}")
                        try:
                            import json
                            tc_args = json.loads(tc_args_str) if isinstance(tc_args_str, str) else tc_args_str
                        except Exception:
                            tc_args = {}
                        tool_calls_collected[turn * 10 + len(tool_calls_collected)] = {
                            "id": tc_id,
                            "name": tc_name,
                            "arguments": tc_args,
                        }
                        yield {
                            "type": "tool_call",
                            "name": tc_name,
                            "arguments": tc_args,
                        }
                    elif event.get("type") == "usage":
                        usage_info = event.get("usage")
            except Exception as e:
                print(f"[BaseAgent] Tool stream error: {e}")
                yield {"type": "stream", "content": f"[工具调用错误] {str(e)}"}
                return

            # 如果没有 tool_calls，本轮结束
            if not tool_calls_collected:
                break

            # 拼接 assistant 消息（含 tool_calls）
            full_content = "".join(content_parts)
            assistant_msg = {"role": "assistant", "content": full_content or None}
            messages.append(assistant_msg)

            # 执行每个 tool_call 并追加结果
            sandbox = {"workspace_path": str(self._get_workspace_path())}
            for idx, tc in tool_calls_collected.items():
                # 追加 tool call 到 messages
                if "tool_calls" not in assistant_msg:
                    assistant_msg["tool_calls"] = []
                assistant_msg["tool_calls"].append({
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"], ensure_ascii=False),
                    }
                })

                # 执行工具
                print(f"[CustomAgent] Executing tool: {tc['name']} with args: {tc['arguments']}")
                result = await tool_registry.execute_tool(
                    tc["name"], tc["arguments"], sandbox
                )
                print(f"[CustomAgent] Tool result length: {len(result)} chars")
                yield {
                    "type": "tool_result",
                    "name": tc["name"],
                    "result": result[:500],  # 只发送前500字符到前端
                }

                # 追加 tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

            # 下一轮：LLM 根据工具结果继续（用空 user 消息触发）
            if turn < max_tool_calls - 1:
                messages.append({"role": "user", "content": "请根据工具调用结果继续。如果已经可以给出最终答案，请直接回答。"})

    def _get_workspace_path(self) -> str:
        """获取 workspace 目录路径"""
        from app.services.workspace_manager import workspace_manager
        return workspace_manager._get_workspace_path(self.id)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """粗略估算 token 数（中文约 1.5 token/字，英文约 0.25 token/字）"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text)
        non_chinese = total_chars - chinese_chars
        return int(chinese_chars * 1.5 + non_chinese * 0.25)

    @staticmethod
    def _trim_content(content: str, max_chars: int) -> str:
        """截断内容到指定字符数"""
        if len(content) <= max_chars:
            return content
        return content[:max_chars - 50] + "\n...（已截断）"

    def build_enriched_prompt_v2(
        self,
        task: str = "",
        target_output: str = "web-app",
        max_context_tokens: int = 80000,
    ) -> str:
        """增强版 Prompt 构建 - 带上下文窗口管理和记忆注入

        优先级（高→低，低优先级先被裁剪）：
        1. 任务描述（不裁剪）
        2. 系统核心指令（不裁剪）
        3. Workspace SOUL.md
        4. Workspace MEMORY.md
        5. Few-shot 示例
        6. 前序任务上下文
        7. 讨论摘要
        """
        try:
            from app.services.workspace_manager import workspace_manager
            from app.services.memory_service import memory_service

            # 加载各部分内容
            ws_context = workspace_manager.load_workspace_context(self.id, max_chars=6000)
            base_prompt = self.get_system_prompt(target_output)

            # 尝试加载 Few-shot 上下文
            few_shot = ""
            try:
                few_shot = memory_service.build_few_shot_context(self.id, task, max_examples=2)
            except Exception:
                pass

            # 尝试加载错误模式警告
            pattern_warning = ""
            try:
                warning = memory_service.get_pattern_warnings(self.id, task)
                if warning:
                    pattern_warning = warning
            except Exception:
                pass

            # 计算 token 预算
            task_tokens = self._estimate_tokens(task)
            base_tokens = self._estimate_tokens(base_prompt)
            remaining = max_context_tokens - task_tokens - base_tokens

            if remaining < 5000:
                # 空间不足，只保留核心
                return base_prompt

            # 按优先级分配预算
            parts = []

            # SOUL (最高优先级 workspace 内容)
            if ws_context and remaining > 2000:
                soul_budget = min(len(ws_context), remaining // 2)
                parts.append(("workspace", self._trim_content(ws_context, soul_budget)))
                remaining -= soul_budget

            # Few-shot
            if few_shot and remaining > 1000:
                few_shot_budget = min(len(few_shot), remaining // 3)
                parts.append(("few_shot", self._trim_content(few_shot, few_shot_budget)))
                remaining -= few_shot_budget

            # Pattern warning
            if pattern_warning and remaining > 500:
                parts.append(("warning", pattern_warning[:500]))
                remaining -= min(len(pattern_warning), 500)

            # 组装
            context_sections = []
            for label, content in parts:
                if content.strip():
                    context_sections.append(content)

            if context_sections:
                combined_context = "\n\n".join(context_sections)
                return f"""# Workspace 上下文

{combined_context}

---

# 系统指令

{base_prompt}"""

            return base_prompt

        except Exception as e:
            print(f"[BaseAgent] Error in build_enriched_prompt_v2: {e}")
            return self.get_system_prompt(target_output)

    @abstractmethod
    async def execute_task(
        self,
        task: str,
        existing_code: Optional[str] = None,
        incremental_mode: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a task and yield progress updates

        Args:
            task: Task description
            existing_code: Current code to modify (for incremental updates)
            incremental_mode: If True, use incremental modification format
        """
        pass

    @abstractmethod
    def get_system_prompt(self, target_output: str = "web-app") -> str:
        """Get the system prompt for this agent type"""
        pass


class CoderAgent(BaseAgent):
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(id, name, AgentType.CODER, **kwargs)

    def get_system_prompt(self, target_output: str = "web-app") -> str:
        if target_output == "ts-app":
            return self.custom_prompt or """你是一个专业的 TypeScript 浏览器应用开发专家。你的职责是生成完整、可构建、可预览的 Vite + TypeScript 多文件项目代码。

⚠️🚨 严格规则 - 违反将导致工程无法编译：

【项目形态】
- 目标工程：Vite + TypeScript（浏览器端，不是 Node 服务）
- 模板已预置：package.json、tsconfig.json、vite.config.ts、index.html
- 你只需要输出需要写入工程的源码文件，优先放在 src/ 目录

【必须遵守】
✅ 输出格式：每个文件必须以 `// filename: src/path/to/file.ts` 或 `// filename: src/path/to/file.css` 开头
✅ 每个输出文件必须是完整文件内容，不是片段、不是 diff
✅ 代码必须符合 TypeScript strict 模式
✅ 使用标准 ES Module：import / export
✅ 浏览器代码必须通过模板里真实存在的 DOM 节点启动；模板默认只保证 `#app` 根节点存在
✅ 如果需要 canvas、按钮、分数面板等节点，必须在 TypeScript 中创建并挂到 `#app` 下，不能假设 `index.html` 已有 `#gameCanvas`、`#score` 等元素
✅ 如果是游戏或交互应用，优先使用原生 Canvas API 和浏览器事件
✅ 至少提供可运行入口文件 `src/main.ts`

【禁止事项】
❌ 禁止输出 package.json、tsconfig.json、vite.config.ts、index.html（这些由模板提供）
❌ 禁止使用 CommonJS（require、module.exports）
❌ 禁止依赖未声明的第三方库
❌ 禁止只写类骨架、空函数、TODO、伪代码或 `...` 占位符
❌ 禁止使用 markdown 代码块包裹最终文件内容
❌ 禁止引用不存在的 DOM 元素或未定义符号

【推荐结构】
- src/main.ts：应用入口与挂载
- src/types.ts：类型定义
- src/game.ts / src/app.ts：核心逻辑
- src/styles.css：样式
- src/utils.ts：工具函数

【输出示例】
// filename: src/main.ts
import './styles.css';
import { createGame } from './game';

const root = document.getElementById('app');
if (!root) {
  throw new Error('Missing #app root');
}

createGame(root);

// filename: src/game.ts
export function createGame(root: HTMLElement): void {
  root.innerHTML = '<main><h1>Hello</h1></main>';
}

// filename: src/styles.css
body { margin: 0; }

请生成完整、可直接写入工程并通过构建的 TypeScript 文件集合。"""
        if target_output == "godot-game":
            return self.custom_prompt or """你是一个专业的 Godot 游戏开发专家。你的职责是生成完整的 Godot 3.6 游戏项目代码。

⚠️🚨 严格规则 - 违反将导致代码无法运行：

【目标平台】
- 目标引擎：Godot 3.6（使用 GLES2 渲染器，兼容抖音小程序）
- 目标平台：抖音小程序（需要导出为 Web/WASM）
- 屏幕分辨率：540x1080 竖屏

【禁止事项 - 绝对不可】
❌ 禁止使用 C# 脚本（无法导出到 Web/WASM）
❌ 禁止引用外部资源文件（图片、音频、字体等）
❌ 禁止使用 External 纹理或资源加载
❌ 禁止只写代码骨架/空方法
❌ 禁止 TODO 注释或占位符
❌ 禁止使用 Godot 4.x 语法（如 @onready, var := ）
❌ 禁止用 GDScript 语法写 .tscn 或 project.godot 文件
❌ 禁止使用 markdown 代码块包裹文件内容

【文件格式警告 - 极其重要】
⚠️ project.godot 必须是 INI 格式，不是 GDScript！
⚠️ .tscn 文件必须以 [gd_scene 开头，不是 GDScript！
⚠️ 只有 .gd 文件才是 GDScript 代码！

【必须遵守 - 强制要求】
✅ 只使用 GDScript (.gd 文件)，Godot 3.x 语法
✅ 所有图形必须用代码绘制（使用 draw_* 方法）
✅ 输出格式：每个文件用 `# filename: path/to/file.gd` 标注
✅ 必须输出完整的 .gd 脚本和 .tscn 场景文件
✅ 必须包含 project.godot 项目配置文件（config_version=4）
✅ 触摸控制：使用 InputEventScreenTouch 和 InputEventScreenDrag
✅ 适配竖屏 540x1080 布局

【输出文件格式示例 - 必须严格遵守】

# filename: project.godot
; Engine configuration file.
; It's best edited using the editor UI and not directly.
;
; Format:
;   [section] ; section goes between []
;   param=value ; assign values to parameters

config_version=4

[application]

config/name="MyGame"
config/description="Generated by AITeam"
run/main_scene="res://main.tscn"
config/icon="res://icon.png"

[display]

window/size/width=540
window/size/height=1080
window/size/fullscreen=true
window/dpi/allow_hidpi=true
window/stretch/mode="2d"
window/stretch/aspect="keep"

[rendering]

quality/driver/driver_name="GLES2"
vram_compression/import_etc=true

# filename: main.tscn
[gd_scene load_steps=2 format=2]

[ext_resource path="res://main.gd" type="Script" id=1]

[node name="Main" type="Node2D"]
script = ExtResource( 1 )

[node name="Player" type="Position2D" parent="."]
position = Vector2( 270, 540 )

[node name="Camera2D" type="Camera2D" parent="."]
current = true

# filename: main.gd
extends Node2D

var player_pos = Vector2(270, 540)
var velocity = Vector2()

func _ready():
    set_process(true)

func _process(delta):
    # 游戏逻辑
    pass

func _input(event):
    if event is InputEventScreenTouch:
        if event.pressed:
            player_pos = event.position

func _draw():
    # 绘制玩家（白色圆形）
    draw_circle(player_pos, 25, Color.white)
    # 绘制地面
    draw_rect(Rect2(0, 900, 540, 180), Color.green)

【Godot 3.x 语法要点】
- 变量声明：var x = 10（不是 var x := 10）
- 延迟加载：onready var node = $Node（不是 @onready）
- 类型转换：node as Node（不是 node as? Node）
- 信号连接：connect("signal", self, "method")（不是 signal.connect(func()))
- 实例化：preload("res://scene.tscn").instance()
- 颜色常量：Color.white, Color.red, Color.blue（不是 Color.WHITE）

【抖音小程序适配要求】
- 使用触摸事件而非键盘/鼠标
- UI 元素要足够大（最小 44px）
- 建议使用 CPUParticles2D 替代 GPUParticles2D

请生成完整的 Godot 3.6 项目，确保所有文件都可以直接在 Godot 3.6 引擎中打开运行。"""

        return self.custom_prompt or """你是一个专业的代码开发专家。你的职责包括：
1. 编写高质量、可维护的代码
2. 调试和修复代码问题
3. 进行代码审查和优化
4. 实现功能模块
5. 编写技术文档

⚠️🚨 严格规则 - 违反将导致代码无法运行：

【禁止事项 - 绝对不可】
❌ 禁止引用外部文件：<link href="css/xxx">, <script src="js/xxx">
❌ 禁止只写类骨架/空方法：禁止 class X { method() { /* 注释 */ } } 或 method() {} 无实现体
❌ 禁止重复定义同一个类：class Game {} 只能定义一次
❌ 禁止混用多个框架：选择一种实现方式（Canvas 或 Phaser），不要两者混用
❌ 禁止使用未定义的类/函数：使用前必须先完整定义
❌ 禁止依赖未引入的库：如果用 Phaser 必须 <script src="phaser.js">
❌ 禁止引用不存在的 DOM 元素：getElementById 必须对应真实元素

【SVG 格式规范 - 必须遵守】
⚠️ SVG viewBox 属性必须用空格分隔数值：viewBox="0 0 24 24"（正确）而非 viewBox="002424"（错误）
⚠️ SVG path 的 d 属性中数值必须用空格/逗号分隔：d="M 1 15 L 6 9 H 2"（正确）
⚠️ 示例：<svg viewBox="0 0 100 100"><path d="M 10 10 L 90 10 L 90 90 Z"/></svg>

【JavaScript 语法规范 - 必须遵守】
⚠️ 注释不能包含代码语法符号：// Ignore errors } 是错误的！花括号 } 在注释外面
⚠️ 正确写法：} catch (e) { // Ignore errors } 而非 } catch (e) { // Ignore errors } }
⚠️ 确保所有 { } 括号正确配对，不要在注释中误加括号
⚠️ 注释和代码必须分行：每行要么是注释，要么是代码，不可在同一行混合
⚠️ 错误示例：// 获取DOM元素 canvas = document.getElementById('gameCanvas');  ← 代码被注释掉了！
⚠️ 正确示例：
    // 获取DOM元素
    canvas = document.getElementById('gameCanvas');

【必须遵守 - 强制要求】
✅ 所有代码必须是单个完整的 HTML 文件
✅ 结构规范：<!DOCTYPE html><html><head><style>CSS</style></head><body>HTML元素<script>JS</script></body></html>
✅ 所有 CSS 内联在 <style> 标签中
✅ 所有 JavaScript 内联在 <script> 标签中
✅ 每个类只定义一次，不要在多处重复定义
✅ 类必须在使用前完整定义
✅ 必须包含初始化代码：window.onload 或 DOMContentLoaded
✅ 必须包含游戏循环：requestAnimationFrame 或 setInterval
✅ 游戏必须自动启动，不能只定义类不实例化

【代码质量 - 必须可直接运行】
- 交付的 HTML 在浏览器打开后必须能玩/能操作，不能是空白页或只有静态结构
- 禁止只写类定义和空方法：每个方法必须有可执行代码（如 move() 要真的改坐标，draw() 要真的调用 ctx 绘制）
- 不要写伪代码、代码片段、TODO 或 "..." 占位符
- 若任务拆成多文件（如 玩家控制.js + 敌人.js），最终应整合为一个可独立运行的 HTML，或明确写出完整单文件版本

【游戏框架选择 - 重要】
🚫 禁止使用 Phaser、Pixi.js 等外部游戏框架
✅ 只能使用原生 Canvas API (getContext('2d'))
✅ 原因：单文件HTML无法加载外部框架，框架CDN可能被墙

【完整性要求 - 极其重要】
⚠️ 代码必须完整，包括：
- 所有 HTML 闭合标签 (</body></html>)
- 所有 JavaScript 大括号配对 ({} 成对出现)
- 所有函数必须完整定义，不能在函数中间截断
- 所有代码块必须闭合 (``` 开始和结束)

⚠️ 如果代码较长，优先保证完整性而非功能丰富性：
- 宁可少一个功能，也不要生成不完整的代码
- 如果发现空间不够，先完成当前函数，省略可选功能
- 确保最后一个函数也是完整的，有闭合的 }

⚠️ 生成前预估代码量，确保能在输出限制内完成：
- 预计超过 3000 行代码时，应简化设计
- 核心功能优先，附加功能可省略
- 保持代码紧凑，减少冗余注释

【预生成检查清单 - 生成代码前必须确认】

在开始写代码之前，先在脑子里过一遍这个清单，确保所有必需组件都会被包含：

□ HTML 结构 - DOCTYPE, html, head, body 标签
□ Canvas 元素 - <canvas id="game"></canvas>
□ CSS 样式 - canvas 居中、背景色、边框
□ 游戏类 - class Game { ... }
□ 构造函数 - constructor() 初始化所有状态变量
□ 游戏循环 - requestAnimationFrame 或 setInterval
□ 输入处理 - keydown/keyup 或 touch 事件
□ 碰撞检测 - 边界、物体之间的碰撞
□ 状态更新 - update() 方法修改游戏状态
□ 渲染绘制 - draw() 方法使用 Canvas API 绘制
□ 分数/状态显示 - 玩家可见的游戏信息
□ 游戏结束条件 - 判断游戏何时结束
□ 初始化代码 - window.onload 或 DOMContentLoaded 启动游戏

=== 完整示例：可运行的贪吃蛇游戏 ===

以下是一个完整的、可直接在浏览器运行的贪吃蛇游戏。你的代码必须达到同样的完整度：

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>贪吃蛇游戏</title>
<style>
body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background: #1a1a2e; font-family: monospace; }
#gameContainer { position: relative; }
canvas { border: 2px solid #4a9eff; background: #16213e; }
#score { position: absolute; top: 10px; left: 10px; color: #4a9eff; font-size: 18px; }
#gameOver { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #ff4a4a; font-size: 24px; display: none; text-align: center; }
#restart { margin-top: 10px; padding: 10px 20px; background: #4a9eff; border: none; color: white; cursor: pointer; font-size: 16px; }
</style>
</head>
<body>
<div id="gameContainer">
  <div id="score">得分: 0</div>
  <canvas id="game" width="400" height="400"></canvas>
  <div id="gameOver">
    游戏结束!<br>
    <button id="restart" onclick="restartGame()">重新开始</button>
  </div>
</div>
<script>
class SnakeGame {
  constructor() {
    this.canvas = document.getElementById('game');
    this.ctx = this.canvas.getContext('2d');
    this.gridSize = 20;
    this.tileCount = this.canvas.width / this.gridSize;
    this.snake = [{x: 10, y: 10}];
    this.direction = {x: 1, y: 0};
    this.nextDirection = {x: 1, y: 0};
    this.food = {x: 15, y: 15};
    this.score = 0;
    this.gameOver = false;
    this.speed = 100;
    this.lastTime = 0;
    this.init();
  }
  init() {
    document.addEventListener('keydown', (e) => this.handleInput(e));
    document.getElementById('restart').addEventListener('click', () => this.restart());
    requestAnimationFrame((time) => this.gameLoop(time));
  }
  handleInput(e) {
    const keyMap = {
      ArrowUp: {x: 0, y: -1}, ArrowDown: {x: 0, y: 1},
      ArrowLeft: {x: -1, y: 0}, ArrowRight: {x: 1, y: 0},
      w: {x: 0, y: -1}, s: {x: 0, y: 1}, a: {x: -1, y: 0}, d: {x: 1, y: 0}
    };
    const newDir = keyMap[e.key];
    if (newDir && (newDir.x !== -this.direction.x || newDir.y !== -this.direction.y)) {
      this.nextDirection = newDir;
    }
  }
  spawnFood() {
    let newFood;
    do {
      newFood = {
        x: Math.floor(Math.random() * this.tileCount),
        y: Math.floor(Math.random() * this.tileCount)
      };
    } while (this.snake.some(s => s.x === newFood.x && s.y === newFood.y));
    this.food = newFood;
  }
  update() {
    this.direction = this.nextDirection;
    const head = {
      x: this.snake[0].x + this.direction.x,
      y: this.snake[0].y + this.direction.y
    };
    if (head.x < 0 || head.x >= this.tileCount || head.y < 0 || head.y >= this.tileCount) {
      this.endGame();
      return;
    }
    if (this.snake.some(s => s.x === head.x && s.y === head.y)) {
      this.endGame();
      return;
    }
    this.snake.unshift(head);
    if (head.x === this.food.x && head.y === this.food.y) {
      this.score += 10;
      document.getElementById('score').textContent = '得分: ' + this.score;
      this.spawnFood();
    } else {
      this.snake.pop();
    }
  }
  draw() {
    this.ctx.fillStyle = '#16213e';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.fillStyle = '#4a9eff';
    this.snake.forEach((s, i) => {
      const alpha = 1 - (i / this.snake.length) * 0.5;
      this.ctx.fillStyle = `rgba(74, 158, 255, ${alpha})`;
      this.ctx.fillRect(s.x * this.gridSize + 1, s.y * this.gridSize + 1, this.gridSize - 2, this.gridSize - 2);
    });
    this.ctx.fillStyle = '#ff4a4a';
    this.ctx.beginPath();
    this.ctx.arc(
      this.food.x * this.gridSize + this.gridSize / 2,
      this.food.y * this.gridSize + this.gridSize / 2,
      this.gridSize / 2 - 2, 0, Math.PI * 2
    );
    this.ctx.fill();
  }
  gameLoop(time) {
    if (this.gameOver) return;
    if (time - this.lastTime >= this.speed) {
      this.update();
      this.draw();
      this.lastTime = time;
    }
    requestAnimationFrame((t) => this.gameLoop(t));
  }
  endGame() {
    this.gameOver = true;
    document.getElementById('gameOver').style.display = 'block';
  }
  restart() {
    this.snake = [{x: 10, y: 10}];
    this.direction = {x: 1, y: 0};
    this.nextDirection = {x: 1, y: 0};
    this.score = 0;
    this.gameOver = false;
    document.getElementById('score').textContent = '得分: 0';
    document.getElementById('gameOver').style.display = 'none';
    this.spawnFood();
    requestAnimationFrame((t) => this.gameLoop(t));
  }
}
window.onload = () => new SnakeGame();
</script>
</body>
</html>
```

=== 反模式示例：绝对不要这样写 ===

以下代码展示了常见错误，你的代码绝对不能出现这些模式：

```javascript
// ❌ 错误1: 空方法体
class Game {
  constructor() { /* TODO */ }  // 错误！构造函数是空的
  update() { }                   // 错误！方法体为空
  draw() { /* 待实现 */ }        // 错误！只有注释
}

// ❌ 错误2: 使用省略号或占位符
function createEnemy() {
  // ... 创建敌人的逻辑
}

// ❌ 错误3: 没有初始化
class Game {
  constructor() {
    this.score = 0;
  }
}
// 忘记 window.onload 或实例化！游戏永远不会启动

// ❌ 错误4: 引用外部文件
<link href="style.css">          // 错误！外部CSS
<script src="game.js"></script>  // 错误！外部JS

// ❌ 错误5: 使用未定义的变量
class Game {
  draw() {
    ctx.fillRect(0, 0, 100, 100);  // 错误！ctx 未定义
  }
}
```

【增量修改规则 - 迭代时必须遵守】

当修改已有代码时，必须使用增量修改格式，而不是重写整个文件：

1. 修改现有函数：
<<<MODIFY: function_name>>>
function function_name() {
    // 新的函数实现
}
<<<END>>>

2. 添加新函数（在指定函数之后）：
<<<ADD: after: existing_function>>>
function new_function() {
    // 新函数
}
<<<END>>>

3. 删除函数：
<<<DELETE: function_name>>>
<<<END>>>

4. 修改CSS规则：
<<<CSS: .selector>>>
color: red;
font-size: 16px;
<<<END>>>

⚠️ 只有在创建全新项目时才输出完整代码。
⚠️ 迭代修改时，只输出需要修改的部分！
⚠️ 如果用户请求是迭代/修改现有功能，必须分析当前代码，只修改需要变化的部分！

【Canvas/WebGL 实时游戏模板 - 仅当需求明确属于实时绘制游戏时使用】
此模板只适用于必须持续绘制的 Canvas/WebGL 游戏，不适用于普通 DOM 页面、棋盘类小游戏或表单/仪表盘：
```html
<!DOCTYPE html>
<html>
<head><style>canvas { border: 1px solid #000; }</style></head>
<body>
<canvas id="game" width="400" height="400"></canvas>
<script>
class Game {
  constructor() {
    this.canvas = document.getElementById('game');
    this.ctx = this.canvas.getContext('2d');
    this.init();
  }
  init() {
    // 初始化游戏状态
    this.score = 0;
    this.gameOver = false;
    this.bindEvents();
    this.gameLoop();
  }
  bindEvents() {
    document.addEventListener('keydown', (e) => this.handleInput(e));
  }
  handleInput(e) {
    // 处理输入
  }
  update() {
    // 更新游戏状态（必须有实际代码）
  }
  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    // 绘制游戏（必须有实际代码，调用 ctx 绘制方法）
  }
  gameLoop() {
    if (!this.gameOver) {
      this.update();
      this.draw();
    }
    requestAnimationFrame(() => this.gameLoop());
  }
}
window.onload = () => new Game();
</script>
</body>
</html>
```

当代码需要作为独立文件时，请在代码块第一行标注文件名。"""

    async def execute_task(
        self,
        task: str,
        existing_code: Optional[str] = None,
        incremental_mode: bool = False,
        target_output: str = "web-app"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a coding task with optional incremental modification support.

        Args:
            task: Task description
            existing_code: Current code/project snapshot for incremental updates
            incremental_mode: If True, instruct LLM to modify existing output
            target_output: Desired output format, e.g. web-app / godot-game / ts-app
        """
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 开始分析代码任务..."}
        yield {"type": "thinking", "content": f"[{self.name}] 理解需求：{task}"}

        system_prompt = self.build_enriched_prompt(task, target_output)

        if existing_code and incremental_mode:
            if target_output == "ts-app":
                full_prompt = f"""## 当前工程文件

```text
{existing_code}
```

## 修改任务

{task}

## 重要提示

这是**TypeScript 工程增量修改任务**，你需要基于当前工程继续修改。

⚠️ **输出要求**：
1. 只输出本轮需要新增或替换的完整文件
2. 每个文件必须以 `// filename: 相对路径` 开头，后面直接跟完整文件内容
3. 不要输出 package.json、tsconfig.json、vite.config.ts、index.html
4. 所有 TypeScript 代码必须满足 strict 模式并使用 import/export
5. 不要使用 markdown 代码块包裹最终输出

请输出需要修改的完整文件：
"""
            else:
                full_prompt = f"""## 当前代码

```html
{existing_code}
```

## 修改任务

{task}

## 重要提示

这是**增量修改任务**，你需要基于上面的当前代码进行修改。

⚠️ **输出要求**：
1. 输出**完整的修改后的 HTML 代码**（不是增量格式，而是完整的可运行代码）
2. 保持现有功能的同时添加新功能或修复问题
3. 确保修改后的代码仍然是完整的单文件 HTML 应用
4. 不要删除或破坏现有的核心功能

请输出修改后的完整 HTML 代码：
"""
        else:
            full_prompt = task

        # 代码生成任务使用 GLM-5 (glm_coding_client)
        async for chunk in glm_coding_client.chat_stream(full_prompt, "coder", system_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "任务完成"}


class AnalystAgent(BaseAgent):
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(id, name, AgentType.ANALYST, **kwargs)

    def get_system_prompt(self, target_output: str = "web-app") -> str:
        return self.custom_prompt or """你是一个专业的数据分析师。你的职责包括：
1. 分析数据并提供洞察
2. 生成分析报告
3. 创建数据可视化建议
4. 解读数据趋势和模式
5. 评估项目可行性和风险

请用清晰、结构化的方式呈现分析结果。"""

    async def execute_task(
        self,
        task: str,
        existing_code: Optional[str] = None,
        incremental_mode: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute an analysis task.

        Note: existing_code and incremental_mode are accepted for interface
        consistency but are not used by AnalystAgent (only CoderAgent uses them).
        """
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 开始数据分析..."}
        yield {"type": "thinking", "content": f"[{self.name}] 分析目标：{task}"}

        enriched_prompt = self.build_enriched_prompt(task)
        async for chunk in glm_client.chat_stream(task, "analyst", enriched_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "分析完成"}


class AssistantAgent(BaseAgent):
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(id, name, AgentType.ASSISTANT, **kwargs)

    def get_system_prompt(self, target_output: str = "web-app") -> str:
        return self.custom_prompt or """你是一个智能通用助手和项目协调者。你的职责包括：
1. 理解用户需求并进行拆解
2. 协调不同专业领域的Agent进行协作
3. 组织讨论并形成执行计划
4. 汇总和整合各Agent的工作成果
5. 确保项目按计划推进

请用友好、专业的方式回应，善于组织和协调。"""

    async def execute_task(
        self,
        task: str,
        existing_code: Optional[str] = None,
        incremental_mode: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute an assistant task.

        Note: existing_code and incremental_mode are accepted for interface
        consistency but are not used by AssistantAgent (only CoderAgent uses them).
        """
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 处理请求..."}
        yield {"type": "thinking", "content": f"[{self.name}] 任务内容：{task}"}

        enriched_prompt = self.build_enriched_prompt(task)
        async for chunk in glm_client.chat_stream(task, "assistant", enriched_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "处理完成"}


class TesterAgent(BaseAgent):
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(id, name, AgentType.TESTER, **kwargs)

    def get_system_prompt(self, target_output: str = "web-app") -> str:
        return self.custom_prompt or """你是一个专业的软件测试工程师。你的职责包括：
1. 分析需求并设计测试用例
2. 执行功能测试和回归测试
3. 发现并报告Bug
4. 验证Bug修复
5. 确保产品质量

⚠️ 重要规则 - 测试代码时必须遵守：

【技术栈识别】
- 首先识别代码使用的技术栈（Canvas、Phaser、Three.js 等）
- 如果是纯 Canvas/WebGL 代码，不需要 Phaser 等框架
- 只有代码中明确引用了某个框架，才检查该框架是否存在
- 不要假设所有游戏都需要 Phaser 或其他框架

【常见错误模式检测清单 - 按严重程度分类】

🔴 严重错误（必须修复，代码无法运行）：

1. 【空方法体】
   - 检测模式：function name() { } 或 method() { /* 注释 */ }
   - 问题：方法没有实际执行代码
   - 示例：constructor() { /* TODO */ } 或 update() { }

2. 【重复定义】
   - 检测模式：同一个 class、function 或变量被定义多次
   - 问题：JavaScript 会报 "Identifier has already been declared" 错误
   - 示例：class Game {} 出现两次

3. 【缺少游戏循环】
   - 检测模式：代码有游戏类但没有 requestAnimationFrame 或 setInterval
   - 问题：游戏永远不会更新或渲染
   - 必须有：gameLoop() { requestAnimationFrame(() => this.gameLoop()); }

4. 【缺少初始化】
   - 检测模式：有 class 定义但没有 window.onload 或 DOMContentLoaded
   - 问题：游戏类永远不会被实例化
   - 必须有：window.onload = () => new Game();

5. 【使用未定义的变量/函数】
   - 检测模式：使用了 ctx、canvas 等但没有在构造函数中初始化
   - 问题：运行时会报 "xxx is not defined" 错误
   - 示例：draw() { ctx.fillRect(...) } 但 ctx 没有定义

6. 【外部文件引用】
   - 检测模式：<script src="xxx.js"> 或 <link href="xxx.css">
   - 问题：单文件 HTML 无法加载外部资源

7. 【占位符代码】
   - 检测模式：TODO、FIXME、... 省略号、"待实现"
   - 问题：代码不完整，功能无法正常工作

8. 【DOM 元素不存在】
   - 检测模式：getElementById('xxx') 但 HTML 中没有 id="xxx"
   - 问题：返回 null，后续操作会失败

🟡 中等问题（建议修复，可能导致运行时错误）：

1. 【缺少边界检查】
   - 玩家/敌人可能移出屏幕
   - 数组访问可能越界

2. 【没有错误处理】
   - 除法没有检查除数是否为 0
   - 没有 try-catch 处理可能的异常

3. 【硬编码数值】
   - 魔法数字应该用常量表示
   - 示例：if (score > 1000) 应该用 const WIN_SCORE = 1000

4. 【游戏状态不完整】
   - 缺少暂停/继续功能
   - 缺少游戏结束判定
   - 缺少重新开始功能

🟢 轻微问题（优化建议）：

1. 代码风格不一致
2. 注释不清晰
3. 变量命名不规范

【Canvas 游戏测试标准】
- ✅ 检查是否有 canvas 元素和 getContext('2d')
- ✅ 检查是否有游戏循环 (requestAnimationFrame 或 setInterval)
- ✅ 检查是否有初始化代码 (init 函数或 window.onload)
- ✅ 检查类和函数是否在使用前定义
- ✅ 检查事件监听是否设置
- ✅ 检查 ctx 绘制方法是否被调用（fillRect, drawImage 等）

【不要误报的问题】
❌ 不要报告"缺少 Phaser.js"如果代码使用纯 Canvas
❌ 不要报告"缺少外部文件"如果代码是完整的单文件
❌ 不要要求未使用的技术栈

【测试报告格式】

请按以下格式输出测试结果：

## 测试结果

### 🔴 严重错误（共 X 个）
1. [行号] 错误类型: 描述
   - 代码片段: ...
   - 修复建议: ...

### 🟡 中等问题（共 X 个）
1. [行号] 问题类型: 描述
   - 修复建议: ...

### ✅ 通过的检查项
- [x] 有游戏循环
- [x] 有初始化代码
- ...

### 修复优先级
1. 首先修复严重错误
2. 然后处理中等问题
3. 最后优化轻微问题

请用系统化、严谨的方式工作，关注边界条件和异常情况。
发现问题时，请清晰描述问题、预期结果和实际结果。"""

    async def execute_task(
        self,
        task: str,
        existing_code: Optional[str] = None,
        incremental_mode: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a testing task.

        Note: existing_code and incremental_mode are accepted for interface
        consistency but are not used by TesterAgent (only CoderAgent uses them).
        """
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 开始测试任务..."}
        yield {"type": "thinking", "content": f"[{self.name}] 测试目标：{task}"}

        enriched_prompt = self.build_enriched_prompt(task)
        async for chunk in glm_client.chat_stream(task, "tester", enriched_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "测试完成"}


class CustomAgent(BaseAgent):
    def __init__(self, id: str, name: str, custom_prompt: str, **kwargs):
        super().__init__(id, name, AgentType.CUSTOM, custom_prompt=custom_prompt, **kwargs)

    def get_system_prompt(self, target_output: str = "web-app") -> str:
        return self.custom_prompt or "你是一个自定义AI助手。"

    async def execute_task(
        self,
        task: str,
        existing_code: Optional[str] = None,
        incremental_mode: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a custom task with tool support.

        Note: existing_code and incremental_mode are accepted for interface
        consistency but are not used by CustomAgent (only CoderAgent uses them).
        """
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 开始处理自定义任务..."}
        yield {"type": "thinking", "content": f"[{self.name}] 任务：{task}"}

        enriched_prompt = self.build_enriched_prompt(task)
        
        # 使用带工具调用的执行方法
        async for chunk in self._execute_with_tools(
            task=task,
            system_prompt=enriched_prompt,
            llm_client=glm_client,
            max_tool_calls=5
        ):
            yield chunk

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "任务完成"}


# =============================================================================
# PUA 增强版 Agent 类
# =============================================================================

class PUACoderAgent(PUABaseMixin, CoderAgent):
    """PUA 增强版代码开发专家"""

    def __init__(self, id: str, name: str, **kwargs):
        # 确保 display_type 设置为 "PUA Coder"
        if 'display_type' not in kwargs or not kwargs['display_type']:
            kwargs['display_type'] = "PUA Coder"
        super().__init__(id, name, **kwargs)
        # 显式初始化 PUABaseMixin 的属性
        self._failure_count = 0
        self._pressure_level = 0
        # 覆盖 type 为 pua-coder
        self.type = AgentType.PUA_CODER

    def get_system_prompt(self, target_output: str = "web-app") -> str:
        base_prompt = super().get_system_prompt(target_output)
        pressure = self.get_pressure_prompt()

        pua_section = f"""

{PUA_METHODOLOGY}

{pressure}
""" if pressure else f"""

{PUA_METHODOLOGY}
"""

        return base_prompt + pua_section


class PUAAnalystAgent(PUABaseMixin, AnalystAgent):
    """PUA 增强版数据分析师"""

    def __init__(self, id: str, name: str, **kwargs):
        if 'display_type' not in kwargs or not kwargs['display_type']:
            kwargs['display_type'] = "PUA Analyst"
        super().__init__(id, name, **kwargs)
        self._failure_count = 0
        self._pressure_level = 0
        self.type = AgentType.PUA_ANALYST

    def get_system_prompt(self, target_output: str = "web-app") -> str:
        base_prompt = super().get_system_prompt(target_output)
        pressure = self.get_pressure_prompt()

        pua_section = f"""

{PUA_METHODOLOGY}

{pressure}
""" if pressure else f"""

{PUA_METHODOLOGY}
"""

        return base_prompt + pua_section


class PUAAssistantAgent(PUABaseMixin, AssistantAgent):
    """PUA 增强版通用助手"""

    def __init__(self, id: str, name: str, **kwargs):
        if 'display_type' not in kwargs or not kwargs['display_type']:
            kwargs['display_type'] = "PUA Assistant"
        super().__init__(id, name, **kwargs)
        self._failure_count = 0
        self._pressure_level = 0
        self.type = AgentType.PUA_ASSISTANT

    def get_system_prompt(self, target_output: str = "web-app") -> str:
        base_prompt = super().get_system_prompt(target_output)
        pressure = self.get_pressure_prompt()

        pua_section = f"""

{PUA_METHODOLOGY}

{pressure}
""" if pressure else f"""

{PUA_METHODOLOGY}
"""

        return base_prompt + pua_section


class PUATesterAgent(PUABaseMixin, TesterAgent):
    """PUA 增强版测试专家"""

    def __init__(self, id: str, name: str, **kwargs):
        if 'display_type' not in kwargs or not kwargs['display_type']:
            kwargs['display_type'] = "PUA Tester"
        super().__init__(id, name, **kwargs)
        self._failure_count = 0
        self._pressure_level = 0
        self.type = AgentType.PUA_TESTER

    def get_system_prompt(self, target_output: str = "web-app") -> str:
        base_prompt = super().get_system_prompt(target_output)
        pressure = self.get_pressure_prompt()

        pua_section = f"""

{PUA_METHODOLOGY}

{pressure}
""" if pressure else f"""

{PUA_METHODOLOGY}
"""

        return base_prompt + pua_section


def create_agent(
    name: str,
    agent_type: AgentType,
    description: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    position: Optional[Dict[str, float]] = None,
    display_type: Optional[str] = None,
) -> BaseAgent:
    """Factory function to create agents"""
    agent_id = str(uuid.uuid4())

    if agent_type == AgentType.CODER:
        return CoderAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position, display_type=display_type)
    elif agent_type == AgentType.ANALYST:
        return AnalystAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position, display_type=display_type)
    elif agent_type == AgentType.ASSISTANT:
        return AssistantAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position, display_type=display_type)
    elif agent_type == AgentType.TESTER:
        return TesterAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position, display_type=display_type)
    elif agent_type == AgentType.CUSTOM:
        return CustomAgent(agent_id, name, custom_prompt=custom_prompt or "", description=description, position=position, display_type=display_type)
    # PUA 增强版 Agent
    elif agent_type == AgentType.PUA_CODER:
        return PUACoderAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position, display_type=display_type)
    elif agent_type == AgentType.PUA_ANALYST:
        return PUAAnalystAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position, display_type=display_type)
    elif agent_type == AgentType.PUA_ASSISTANT:
        return PUAAssistantAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position, display_type=display_type)
    elif agent_type == AgentType.PUA_TESTER:
        return PUATesterAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position, display_type=display_type)
    else:
        return AssistantAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position, display_type=display_type)
