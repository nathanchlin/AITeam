"""UI 设计工具 - 封装 UI-UX-Pro-Max skill

为 UI Designer Agent 提供专业的设计系统能力
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Optional

# UI-UX-Pro-Max skill 路径
SKILL_PATH = Path(__file__).parent.parent.parent.parent / "frontend" / ".claude" / "skills" / "ui-ux-pro-max"


async def generate_design_system(
    query: str,
    project_name: Optional[str] = None,
    output_format: str = "markdown",
    persist: bool = False,
    page: Optional[str] = None,
    _sandbox: Optional[dict] = None
) -> str:
    """生成完整的 UI 设计系统
    
    根据产品类型和风格描述，生成包含颜色方案、字体搭配、布局模式、样式推荐的设计系统。
    
    Args:
        query: 设计需求描述
            - 产品类型: SaaS, e-commerce, dashboard, landing page, portfolio, etc.
            - 行业: healthcare, fintech, beauty, education, etc.
            - 风格关键词: minimal, luxury, playful, professional, dark mode, etc.
            示例: "healthcare SaaS dashboard modern", "beauty spa elegant"
        
        project_name: 项目名称，用于设计系统标题（可选）
        
        output_format: 输出格式
            - "markdown": Markdown 格式，适合文档（默认）
            - "ascii": ASCII 框格式，适合终端显示
        
        persist: 是否持久化到 design-system/ 目录（可选）
        
        page: 页面名称，用于生成页面特定覆盖（可选）
            示例: "dashboard", "checkout", "settings"
    
    Returns:
        完整的设计系统文档，包含：
        - Pattern: 页面布局模式
        - Style: UI 风格推荐
        - Colors: 颜色方案（主色、辅色、CTA、背景、文字）
        - Typography: 字体搭配（标题、正文、Google Fonts 链接）
        - Key Effects: 关键动效建议
        - Anti-patterns: 应避免的设计
        - Pre-delivery Checklist: 交付前检查清单
    """
    script_path = SKILL_PATH / "scripts" / "search.py"
    
    if not script_path.exists():
        return f"❌ UI-UX-Pro-Max skill 未找到\n路径: {script_path}\n请确保 skill 已正确安装。"
    
    # 构建命令
    cmd = ["python3", str(script_path), query, "--design-system", "-f", output_format]
    
    if project_name:
        cmd.extend(["-p", project_name])
    
    if persist:
        cmd.append("--persist")
    
    if page:
        cmd.extend(["--page", page])
    
    try:
        # 设置工作目录为 skill 目录，确保能找到 data 文件
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(SKILL_PATH / "scripts"),
            env=env
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"❌ 设计系统生成失败\n错误: {result.stderr}\n请检查查询参数是否正确。"
            
    except subprocess.TimeoutExpired:
        return "❌ 设计系统生成超时（30秒），请简化查询后重试。"
    except Exception as e:
        return f"❌ 执行错误: {str(e)}"


async def search_ui_style(
    query: str,
    domain: str = "style",
    max_results: int = 5,
    _sandbox: Optional[dict] = None
) -> str:
    """搜索 UI 设计资源
    
    在特定领域搜索设计建议、最佳实践和详细指南。
    
    Args:
        query: 搜索关键词
            示例: "glassmorphism", "accessibility animation", "real-time chart"
        
        domain: 搜索领域（默认 "style"）
            - "product": 产品类型推荐 (SaaS, e-commerce, healthcare, etc.)
            - "style": UI 风格 (glassmorphism, minimalism, brutalism, etc.)
            - "typography": 字体搭配
            - "color": 颜色方案
            - "landing": 落地页结构、CTA 策略
            - "chart": 图表类型推荐
            - "ux": UX 最佳实践、无障碍设计
            - "react": React/Next.js 性能优化
            - "web": Web 界面指南
            - "prompt": AI 提示词、CSS 关键词
        
        max_results: 最大返回结果数（1-10，默认 5）
    
    Returns:
        JSON 格式的搜索结果，包含匹配的设计建议
    """
    script_path = SKILL_PATH / "scripts" / "search.py"
    
    if not script_path.exists():
        return json.dumps({"error": "UI-UX-Pro-Max skill 未找到"}, ensure_ascii=False)
    
    cmd = [
        "python3", str(script_path),
        query,
        "--domain", domain,
        "-n", str(max_results)
    ]
    
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(SKILL_PATH / "scripts"),
            env=env
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return json.dumps({
                "error": "搜索失败",
                "details": result.stderr
            }, ensure_ascii=False)
            
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "搜索超时"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def get_stack_guidelines(
    query: str,
    stack: str = "html-tailwind",
    _sandbox: Optional[dict] = None
) -> str:
    """获取技术栈特定的 UI 指南
    
    根据目标技术栈获取实现特定的最佳实践。
    
    Args:
        query: 查询主题
            示例: "layout responsive form", "animation performance", "state management"
        
        stack: 技术栈（默认 "html-tailwind"）
            - "html-tailwind": Tailwind CSS，响应式，无障碍
            - "react": React 状态、hooks、性能模式
            - "nextjs": SSR、路由、图片优化
            - "vue": Composition API、Pinia、Vue Router
            - "svelte": Runes、stores、SvelteKit
            - "swiftui": SwiftUI 视图、状态、动画
            - "react-native": React Native 组件、导航、列表
            - "flutter": Widgets、状态、布局、主题
            - "shadcn": shadcn/ui 组件、主题、表单
            - "jetpack-compose": Composables、Modifiers、状态提升
    
    Returns:
        技术栈特定的最佳实践指南
    """
    script_path = SKILL_PATH / "scripts" / "search.py"
    
    if not script_path.exists():
        return json.dumps({"error": "UI-UX-Pro-Max skill 未找到"}, ensure_ascii=False)
    
    cmd = ["python3", str(script_path), query, "--stack", stack]
    
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(SKILL_PATH / "scripts"),
            env=env
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return json.dumps({
                "error": "获取指南失败",
                "details": result.stderr
            }, ensure_ascii=False)
            
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "获取超时"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# 工具元数据（供动态注册使用）
UI_TOOLS = [
    {
        "name": "generate_design_system",
        "description": "生成完整的 UI 设计系统。根据产品类型和风格描述，自动生成专业的颜色方案、字体搭配、布局模式、样式推荐。这是 UI 设计的核心工具，应该在开始任何设计工作时首先调用。",
        "parameters": {
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
        "handler": generate_design_system,
    },
    {
        "name": "search_ui_style",
        "description": "搜索 UI 设计资源。在特定领域（样式、颜色、字体、UX 等）搜索设计建议和最佳实践。用于补充设计系统或在特定主题上获取更多细节。",
        "parameters": {
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
        "handler": search_ui_style,
    },
    {
        "name": "get_stack_guidelines",
        "description": "获取技术栈特定的 UI 实现指南。根据目标技术栈（React、Vue、Next.js 等）获取实现最佳实践。",
        "parameters": {
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
        "handler": get_stack_guidelines,
    },
]
