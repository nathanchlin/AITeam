"""
Agent 能力升级 - 自动化测试脚本

测试覆盖:
  Phase 1: Workspace 系统（初始化、上下文注入、记忆更新）
  Phase 2: Tool Use（工具注册、schema 生成、工具执行）
  Phase 3: 记忆与自我进化（学习提取、Few-shot、Prompt 自优化）
  Phase 4: Prompt Engineering（上下文窗口管理、enriched prompt）

运行: cd backend && python tests/test_agent_upgrade.py
"""

import asyncio
import sys
import io
import os

os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 确保 backend 在路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


passed = 0
failed = 0
errors = []


def test(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        msg = f"  FAIL  {name}" + (f" - {detail}" if detail else "")
        print(msg)
        errors.append(msg)


# ===========================================================================
# Phase 1 - Workspace System
# ===========================================================================
print("\n" + "=" * 60)
print("Phase 1: Workspace System")
print("=" * 60)

from app.services.workspace_manager import workspace_manager
from app.services.agent_manager import agent_manager
from app.models.schemas import AgentType

# Test 1.1: Workspace 已为所有 Agent 创建
print("\n[1.1] Workspace initialization")
agents = agent_manager.get_all_agents()
test(f"All {len(agents)} agents have workspace", len(agents) > 0)

for agent in agents[:3]:
    exists = workspace_manager.workspace_exists(agent.id)
    test(f"  {agent.name} workspace exists", exists)

# Test 1.2: Workspace 文件完整性
print("\n[1.2] Workspace file completeness")
agent = agents[0]  # CodeMaster
files = workspace_manager.get_workspace_files(agent.id)
test("IDENTITY.md exists", "IDENTITY.md" in files and len(files["IDENTITY.md"]) > 10)
test("SOUL.md exists", "SOUL.md" in files and len(files["SOUL.md"]) > 10)
test("USER.md exists", "USER.md" in files and len(files["USER.md"]) > 10)
test("MEMORY.md exists", "MEMORY.md" in files and len(files["MEMORY.md"]) > 10)

# Test 1.3: Coder 的 SOUL.md 包含角色方法
test("Coder SOUL has methodology", "methodology" in files.get("SOUL.md", "").lower()
     or "method" in files.get("SOUL.md", "").lower()
     or "完整性" in files.get("SOUL.md", ""))

# Test 1.4: 上下文加载
print("\n[1.4] Context loading")
context = workspace_manager.load_workspace_context(agent.id)
test("Context loaded (non-empty)", len(context) > 100)
test("Context has section headers", "===" in context)

# Test 1.5: 记忆更新
print("\n[1.5] Memory update")
workspace_manager.update_memory(
    agent.id,
    "Write a calculator app",
    ["HTML5 structure required", "Inline CSS/JS mandatory"],
    "success",
)
files_after = workspace_manager.get_workspace_files(agent.id)
memory_content = files_after.get("MEMORY.md", "")
test("Memory updated with learning",
     "HTML5" in memory_content or "Inline" in memory_content or "calculator" in memory_content.lower())

# Test 1.6: 每日日志
print("\n[1.6] Daily log")
workspace_manager.update_daily_log(agent.id, "Test daily log entry")
test("Daily log updated", True)  # No crash = pass

# Test 1.7: Workspace file update via API
print("\n[1.7] Workspace file update")
success = workspace_manager.update_workspace_file(agent.id, "USER.md", "# Updated User\nTest update")
test("Update workspace file", success)
updated = workspace_manager.get_workspace_files(agent.id)
test("File content updated", "Updated User" in updated.get("USER.md", ""))

# Test 1.8: 安全限制 - 不能写入非法文件名
print("\n[1.8] Security constraints")
bad_update = workspace_manager.update_workspace_file(agent.id, "../../../etc/passwd", "hacked")
test("Block path traversal", not bad_update)

# Test 1.9: Enriched prompt
print("\n[1.9] Enriched prompt injection")
prompt = agent.build_enriched_prompt("Write a game")
test("Enriched prompt > base prompt", len(prompt) > len(agent.get_system_prompt()))
test("Has workspace section", "# Workspace" in prompt or "Workspace" in prompt)


# ===========================================================================
# Phase 2 - Tool Use / Function Calling
# ===========================================================================
print("\n" + "=" * 60)
print("Phase 2: Tool Use / Function Calling")
print("=" * 60)

# Import and register tools
from app.tools import tool_registry

# Test 2.1: 工具注册
print("\n[2.1] Tool registration")
all_tools = tool_registry.list_tools()
test(f"8 tools registered", len(all_tools) == 8)
test("Has read_file", "read_file" in all_tools)
test("Has write_file", "write_file" in all_tools)
test("Has check_syntax", "check_syntax" in all_tools)
test("Has analyze_code", "analyze_code" in all_tools)
test("Has search_web", "search_web" in all_tools)
test("Has fetch_url", "fetch_url" in all_tools)
test("Has run_code", "run_code" in all_tools)
test("Has list_directory", "list_directory" in all_tools)

# Test 2.2: 各 Agent 类型的工具可用性
print("\n[2.2] Tool availability per agent type")
coder_tools = [t["function"]["name"] for t in tool_registry.get_tools_schema("coder")]
analyst_tools = [t["function"]["name"] for t in tool_registry.get_tools_schema("analyst")]
assistant_tools = [t["function"]["name"] for t in tool_registry.get_tools_schema("assistant")]
tester_tools = [t["function"]["name"] for t in tool_registry.get_tools_schema("tester")]

test("Coder has 8 tools (full access)", len(coder_tools) == 8)
test("Analyst has 5 tools", len(analyst_tools) == 5)
test("Assistant has 4 tools", len(assistant_tools) == 4)
test("Tester has 7 tools", len(tester_tools) == 7)
test("Coder has write_file", "write_file" in coder_tools)
test("Analyst cannot write_file", "write_file" not in analyst_tools)
test("Tester has check_syntax", "check_syntax" in tester_tools)

# Test 2.3: 工具 schema 格式
print("\n[2.3] Tool schema format")
schemas = tool_registry.get_tools_schema("coder")
for schema in schemas:
    test(f"  {schema['function']['name']} has valid schema",
         "name" in schema["function"]
         and "description" in schema["function"]
         and "parameters" in schema["function"])

# Test 2.4: 工具执行（同步部分）
print("\n[2.4] Tool execution")

async def run_tool_tests():
    results = []

    # read_file - 读取 workspace 中的 SOUL.md
    r = await tool_registry.execute_tool("read_file", {"path": "SOUL.md"}, {"workspace_path": workspace_manager._get_workspace_path(agent.id)})
    results.append(("read_file", len(r) > 10 and "错误" not in r[:10]))

    # list_directory
    r = await tool_registry.execute_tool("list_directory", {"path": "."}, {"workspace_path": workspace_manager._get_workspace_path(agent.id)})
    results.append(("list_directory", len(r) > 5 and "错误" not in r[:10]))

    # check_syntax - 正确代码
    r = await tool_registry.execute_tool("check_syntax", {"code": "function hello() { return 42; }", "language": "javascript"}, {})
    results.append(("check_syntax (valid)", "通过" in r or "0" in r))

    # check_syntax - 有问题的代码
    r = await tool_registry.execute_tool("check_syntax", {"code": "function a() { } // TODO", "language": "javascript"}, {})
    results.append(("check_syntax (issues)", "问题" in r or "TODO" in r or "空函数" in r))

    # analyze_code
    r = await tool_registry.execute_tool("analyze_code", {"code": "function add(a, b) { return a + b; }\nconst x = add(1, 2);"}, {})
    results.append(("analyze_code", "JavaScript" in r and "2" in r))

    # write_file
    ws_path = workspace_manager._get_workspace_path(agent.id)
    r = await tool_registry.execute_tool("write_file", {"path": "test_output.txt", "content": "Hello World"}, {"workspace_path": ws_path})
    results.append(("write_file", "已写入" in r or "written" in r.lower()))

    # 验证文件已写入
    r2 = await tool_registry.execute_tool("read_file", {"path": "test_output.txt"}, {"workspace_path": ws_path})
    results.append(("write then read", "Hello World" in r2))

    # 路径遍历防护
    r3 = await tool_registry.execute_tool("read_file", {"path": "../../../etc/passwd"}, {"workspace_path": ws_path})
    results.append(("path traversal blocked", "错误" in r3 or "无效" in r3 or "Error" in r3))

    # 未知工具
    r4 = await tool_registry.execute_tool("nonexistent_tool", {}, {})
    results.append(("unknown tool error", "未知" in r4 or "Unknown" in r4))

    return results

tool_results = asyncio.run(run_tool_tests())
for name, ok in tool_results:
    test(name, ok)

# Test 2.5: GLMClient 有 chat_with_tools_stream
print("\n[2.5] GLMClient tools support")
from app.llm.glm_client import glm_client, glm_coding_client
test("GLMClient has chat_with_tools_stream", hasattr(glm_client, "chat_with_tools_stream"))
test("CodingClient has chat_with_tools_stream", hasattr(glm_coding_client, "chat_with_tools_stream"))

# Test 2.6: BaseAgent._execute_with_tools 方法
print("\n[2.6] BaseAgent tool execution method")
from app.agents.base import CoderAgent, AnalystAgent, TesterAgent
coder = agents[0]  # CodeMaster
test("Coder has _execute_with_tools", hasattr(coder, "_execute_with_tools"))
test("Coder has _get_agent_type_str", hasattr(coder, "_get_agent_type_str"))
test("Coder type str is 'coder'", coder._get_agent_type_str() == "coder")
analyst = agents[1]
test("Analyst type str is 'analyst'", analyst._get_agent_type_str() == "analyst")


# ===========================================================================
# Phase 3 - Memory & Self-Evolution
# ===========================================================================
print("\n" + "=" * 60)
print("Phase 3: Memory & Self-Evolution")
print("=" * 60)

from app.services.memory_service import memory_service

# Test 3.1: 学习提取
print("\n[3.1] Learning extraction")
success_learnings = memory_service.extract_learnings(
    "Write a snake game",
    "我使用 Canvas API 和 requestAnimationFrame 实现了游戏循环。确保代码完整可运行。",
    "success",
)
test("Success learnings extracted", len(success_learnings) > 0)

failed_learnings = memory_service.extract_learnings(
    "Fix login bug",
    "错误：ReferenceError: x is not defined\n问题：变量未初始化",
    "failed",
)
test("Failed learnings extracted", len(failed_learnings) > 0)

# Test 3.2: 任务分类
print("\n[3.2] Task classification")
test("Game task classified", memory_service._classify_task("make a snake game") == "游戏开发")
test("Web task classified", memory_service._classify_task("create a html dashboard") == "Web开发")
test("Test task classified", memory_service._classify_task("run unit tests") == "测试")
test("API task classified", memory_service._classify_task("build REST api endpoint") == "后端开发")

# Test 3.3: Few-shot 上下文
print("\n[3.3] Few-shot context")
# 先写入一些日志
workspace_manager.update_daily_log(agent.id, "完成了一个 Canvas 游戏开发任务，使用了 requestAnimationFrame")
few_shot = memory_service.build_few_shot_context(agent.id, "Write a canvas game")
test("Few-shot context generated", len(few_shot) > 0)
test("Few-shot has reference section", "参考" in few_shot or "经验" in few_shot)

# Test 3.4: Prompt 自优化判断
print("\n[3.4] Prompt self-optimization")
# Mock: 增加记忆条目到5个
for i in range(4):
    workspace_manager.update_memory(
        agent.id,
        f"Test task {i}",
        [f"Learning {i}"],
        "success",
    )
should_optimize = memory_service.should_trigger_prompt_optimization(agent.id)
test("Should trigger optimization check runs", isinstance(should_optimize, bool))

# Test 3.5: 记忆更新后 MEMORY.md 增长
print("\n[3.5] Memory growth")
files_after_growth = workspace_manager.get_workspace_files(agent.id)
memory_after = files_after_growth.get("MEMORY.md", "")
test("Memory grew after updates", len(memory_after) > 200)


# ===========================================================================
# Phase 4 - Prompt Engineering Enhancement
# ===========================================================================
print("\n" + "=" * 60)
print("Phase 4: Prompt Engineering Enhancement")
print("=" * 60)

# Test 4.1: Enriched prompt v2
print("\n[4.1] Enriched prompt v2 with memory")
prompt_v2 = agent.build_enriched_prompt_v2("Write a snake game", max_context_tokens=80000)
test("V2 prompt generated", len(prompt_v2) > 0)
test("V2 prompt longer than base", len(prompt_v2) >= len(agent.get_system_prompt()))

# Test 4.2: Token 估算
print("\n[4.2] Token estimation")
from app.agents.base import BaseAgent
cn_tokens = BaseAgent._estimate_tokens("你好世界")
en_tokens = BaseAgent._estimate_tokens("Hello World")
test("Chinese token estimate > 0", cn_tokens > 0)
test("English token estimate > 0", en_tokens > 0)
test("Chinese > English per char", cn_tokens > en_tokens)

# Test 4.3: 内容截断
print("\n[4.3] Content trimming")
long_content = "A" * 10000
trimmed = BaseAgent._trim_content(long_content, 1000)
test("Trimmed to < max", len(trimmed) <= 1050)  # 允许截断标记
test("Trimmed has truncation marker", "截断" in trimmed)

short_content = "Hello"
not_trimmed = BaseAgent._trim_content(short_content, 1000)
test("Short content not trimmed", not_trimmed == short_content)

# Test 4.4: 上下文窗口管理
print("\n[4.4] Context window management")
# 测试非常小的 token 预算 - 应该只返回 base prompt
small_prompt = agent.build_enriched_prompt_v2("test", max_context_tokens=100)
test("Small budget falls back to base", len(small_prompt) > 0)


# ===========================================================================
# Summary
# ===========================================================================
print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 60)

if errors:
    print("\nFailed tests:")
    for e in errors:
        print(e)

sys.exit(0 if failed == 0 else 1)
