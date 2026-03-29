"""工具注册 - 在此注册所有可用工具"""

from app.tools.tool_registry import tool_registry
from app.tools.file_tools import read_file, write_file, list_directory
from app.tools.code_tools import check_syntax, analyze_code
from app.tools.web_tools import search_web, fetch_url
from app.tools.execution_tools import run_code


# === 文件工具（所有 Agent 可用 ===
tool_registry.register_tool(
    name="read_file",
    description="读取 workspace 中的文件内容。可读取 IDENTITY.md、SOUL.md、MEMORY.md 等自身配置文件，或 workspace 下任何文件。",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件相对路径（相对于 workspace 根目录）"}
        },
        "required": ["path"]
    },
    handler=read_file,
)

tool_registry.register_tool(
    name="write_file",
    description="向 workspace 写入文件。可用于创建代码文件、记录笔记等。路径限制在 workspace 目录内。",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件相对路径"},
            "content": {"type": "string", "description": "文件内容"}
        },
        "required": ["path", "content"]
    },
    handler=write_file,
    available_to=["coder", "pua-coder", "custom"],
)

tool_registry.register_tool(
    name="list_directory",
    description="列出 workspace 目录中的文件和子目录。",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "目录相对路径（默认根目录）", "default": "."}
        },
        "required": []
    },
    handler=list_directory,
)

# === 代码工具 ===
tool_registry.register_tool(
    name="check_syntax",
    description="检查代码语法问题。支持 JavaScript、HTML、CSS、Python。可检测括号不匹配、空函数体、未闭合标签等问题。",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "待检查的代码"},
            "language": {"type": "string", "description": "编程语言 (javascript, html, css, python)", "default": "javascript"}
        },
        "required": ["code"]
    },
    handler=check_syntax,
    available_to=["coder", "pua-coder", "tester", "pua-tester"],
)

tool_registry.register_tool(
    name="analyze_code",
    description="分析代码结构和质量。统计行数、函数数量、注释比例等。",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "待分析的代码"}
        },
        "required": ["code"]
    },
    handler=analyze_code,
    available_to=["coder", "pua-coder", "analyst", "pua-analyst", "tester", "pua-tester"],
)

# === Web 工具 ===
tool_registry.register_tool(
    name="search_web",
    description="搜索 Web 获取信息。可用于查找 API 文档、技术方案、最佳实践等。",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"}
        },
        "required": ["query"]
    },
    handler=search_web,
)

tool_registry.register_tool(
    name="fetch_url",
    description="获取指定 URL 的页面内容。可用于读取文档、API 响应等。不允许访问内网地址。",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "目标 URL"}
        },
        "required": ["url"]
    },
    handler=fetch_url,
)

# === 执行工具 ===
tool_registry.register_tool(
    name="run_code",
    description="在沙箱中执行代码片段。支持 JavaScript (Node.js) 和 Python，5秒超时限制。可用于快速验证代码逻辑。",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "待执行的代码"},
            "language": {"type": "string", "description": "编程语言 (javascript, python)", "default": "javascript"}
        },
        "required": ["code"]
    },
    handler=run_code,
    available_to=["coder", "pua-coder", "tester", "pua-tester"],
)

print(f"[Tools] Registered {len(tool_registry.list_tools())} tools: {', '.join(tool_registry.list_tools())}")
