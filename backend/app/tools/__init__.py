"""工具注册 - 在此注册所有可用工具"""

from app.tools.tool_registry import tool_registry
from app.tools.file_tools import read_file, write_file, list_directory
from app.tools.code_tools import check_syntax, analyze_code
from app.tools.web_tools import search_web, fetch_url
from app.tools.execution_tools import run_code
from app.tools.ui_design_tools import generate_design_system, search_ui_style, get_stack_guidelines


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

# === UI 设计工具（仅 custom 类型 = UI Designer 可用）===
tool_registry.register_tool(
    name="generate_design_system",
    description="生成完整的 UI 设计系统。根据产品类型和风格描述，自动生成专业的颜色方案、字体搭配、布局模式、样式推荐。这是 UI 设计的核心工具，应该在开始任何设计工作时首先调用。",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "设计需求描述，包含产品类型、行业、风格关键词。例如：'healthcare SaaS dashboard modern' 或 'beauty spa elegant luxury'"
            },
            "project_name": {
                "type": "string",
                "description": "项目名称（可选），用于设计系统标题"
            },
            "output_format": {
                "type": "string",
                "enum": ["markdown", "ascii"],
                "default": "markdown",
                "description": "输出格式，markdown 适合文档，ascii 适合终端显示"
            },
            "page": {
                "type": "string",
                "description": "页面名称（可选），用于生成页面特定的设计覆盖，如 'dashboard', 'checkout', 'settings'"
            }
        },
        "required": ["query"]
    },
    handler=generate_design_system,
    available_to=["custom"],  # 仅 UI Designer 可用
)

tool_registry.register_tool(
    name="search_ui_style",
    description="搜索 UI 设计资源。在特定领域（样式、颜色、字体、UX 等）搜索设计建议和最佳实践。用于补充设计系统或在特定主题上获取更多细节。",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索关键词，如 'glassmorphism', 'accessibility', 'dark mode'"
            },
            "domain": {
                "type": "string",
                "enum": ["product", "style", "typography", "color", "landing", "chart", "ux", "react", "web", "prompt"],
                "default": "style",
                "description": "搜索领域"
            },
            "max_results": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "default": 5,
                "description": "最大返回结果数"
            }
        },
        "required": ["query"]
    },
    handler=search_ui_style,
    available_to=["custom"],
)

tool_registry.register_tool(
    name="get_stack_guidelines",
    description="获取技术栈特定的 UI 实现指南。根据目标技术栈（React、Vue、Next.js、Tailwind 等）获取实现最佳实践。",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "查询主题，如 'layout responsive form', 'animation performance'"
            },
            "stack": {
                "type": "string",
                "enum": ["html-tailwind", "react", "nextjs", "vue", "svelte", "swiftui", "react-native", "flutter", "shadcn", "jetpack-compose"],
                "default": "html-tailwind",
                "description": "目标技术栈"
            }
        },
        "required": ["query"]
    },
    handler=get_stack_guidelines,
    available_to=["custom", "coder"],  # UI Designer 和 Coder 都可用
)

print(f"[Tools] Registered {len(tool_registry.list_tools())} tools: {', '.join(tool_registry.list_tools())}")
