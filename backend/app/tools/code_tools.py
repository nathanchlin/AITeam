"""代码分析与语法检查工具"""

import re
from typing import Dict, Any


async def check_syntax(code: str, language: str = "javascript", _sandbox: Dict[str, Any] = None) -> str:
    """检查代码语法问题

    Args:
        code: 待检查的代码
        language: 编程语言 (javascript, html, css, python)
    """
    issues = []

    if language in ("javascript", "js", "typescript", "ts"):
        # 检查括号匹配
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces != close_braces:
            issues.append(f"花括号不匹配: {{ {open_braces} 个, }} {close_braces} 个")

        open_parens = code.count('(')
        close_parens = code.count(')')
        if open_parens != close_parens:
            issues.append(f"圆括号不匹配: ( {open_parens} 个, ) {close_parens} 个")

        # 检查空函数体
        empty_methods = re.findall(r'(function\s+\w+|async\s+\w+|\w+\s*\([^)]*\))\s*\{\s*(?://|/\*)?\s*\}', code)
        if empty_methods:
            issues.append(f"发现 {len(empty_methods)} 个空函数体")

        # 检查 TODO/FIXME
        todos = re.findall(r'(TODO|FIXME|HACK|XXX)', code, re.IGNORECASE)
        if todos:
            issues.append(f"发现 {len(todos)} 个 TODO/FIXME 标记")

    elif language == "html":
        # 检查基本 HTML 结构
        if "<html" not in code.lower():
            issues.append("缺少 <html> 标签")
        if "</html>" not in code.lower():
            issues.append("缺少 </html> 闭合标签")
        if "<body" not in code.lower():
            issues.append("缺少 <body> 标签")

        # 检查标签闭合
        open_tags = len(re.findall(r'<(div|span|p|section|main|header|footer)[>\s]', code, re.IGNORECASE))
        close_tags = len(re.findall(r'</(div|span|p|section|main|header|footer)>', code, re.IGNORECASE))
        if abs(open_tags - close_tags) > 2:
            issues.append(f"HTML 标签可能不匹配: 开标签 {open_tags}, 闭标签 {close_tags}")

    elif language == "python":
        # Python 缩进检查
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line and line[0] == ' ' and line.rstrip().endswith(':'):
                # 检查下一行是否缩进
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line and not next_line.startswith((' ', '\t', '#')):
                        if next_line.strip():
                            issues.append(f"第 {i+2} 行缩进可能错误")

    if issues:
        return f"发现 {len(issues)} 个问题:\n" + "\n".join(f"- {i}" for i in issues)
    return "语法检查通过，未发现问题"


async def analyze_code(code: str, _sandbox: Dict[str, Any] = None) -> str:
    """分析代码结构和质量

    Args:
        code: 待分析的代码
    """
    lines = code.split('\n')
    total_lines = len(lines)
    code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith(('//', '#', '/*')))
    comment_lines = sum(1 for l in lines if l.strip().startswith(('//', '#', '/*')))

    # 检测语言
    lang = "unknown"
    if '<html' in code.lower() or '<!doctype' in code.lower():
        lang = "HTML"
    elif 'def ' in code or 'import ' in code:
        lang = "Python"
    elif 'function ' in code or 'const ' in code or 'let ' in code:
        lang = "JavaScript"

    # 统计函数/方法
    func_pattern = r'function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\()'
    functions = re.findall(func_pattern, code)
    func_names = [f[0] or f[1] for f in functions if f[0] or f[1]]

    result = f"""代码分析结果:
- 语言: {lang}
- 总行数: {total_lines}
- 代码行: {code_lines}
- 注释行: {comment_lines}
- 函数数量: {len(func_names)}
- 函数列表: {', '.join(func_names[:20]) if func_names else '无'}"""

    return result
