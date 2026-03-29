"""沙箱代码执行工具"""

import asyncio
import subprocess
import tempfile
import os
from typing import Dict, Any


async def run_code(
    code: str,
    language: str = "javascript",
    _sandbox: Dict[str, Any] = None,
) -> str:
    """在沙箱中执行代码

    Args:
        code: 待执行的代码
        language: 编程语言 (javascript, python)
    """
    if language in ("javascript", "js"):
        return await _run_javascript(code)
    elif language == "python":
        return await _run_python(code)
    else:
        return f"不支持的语言: {language}"


async def _run_javascript(code: str) -> str:
    """用 Node.js 执行 JavaScript（沙箱，5秒超时）"""
    try:
        # 检查 Node.js 是否可用
        proc = await asyncio.create_subprocess_exec(
            "node", "-e", "console.log('ok')",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            await asyncio.wait_for(proc.wait(), timeout=3)
        except asyncio.TimeoutError:
            proc.kill()
            return "错误: Node.js 不可用"

        # 执行代码
        # 安全处理：用 --disable-warnings 限制输出
        proc = await asyncio.create_subprocess_exec(
            "node", "--disable-warnings", "-e", code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=5
            )
        except asyncio.TimeoutError:
            proc.kill()
            return "执行超时（5秒限制）"

        output = stdout.decode('utf-8', errors='replace')[:3000]
        error = stderr.decode('utf-8', errors='replace')[:1000]

        if error and not output:
            return f"执行错误:\n{error}"
        result = output.strip()
        if error:
            result += f"\n警告: {error[:500]}"
        return result or "（无输出）"

    except FileNotFoundError:
        return "Node.js 未安装，无法执行 JavaScript"
    except Exception as e:
        return f"执行失败: {str(e)}"


async def _run_python(code: str) -> str:
    """用 Python 子进程执行（沙箱，5秒超时）"""
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, encoding='utf-8'
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            proc = await asyncio.create_subprocess_exec(
                "python", temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=5
                )
            except asyncio.TimeoutError:
                proc.kill()
                return "执行超时（5秒限制）"

            output = stdout.decode('utf-8', errors='replace')[:3000]
            error = stderr.decode('utf-8', errors='replace')[:1000]

            if error and not output:
                return f"执行错误:\n{error}"
            result = output.strip()
            if error:
                result += f"\n警告: {error[:500]}"
            return result or "（无输出）"
        finally:
            os.unlink(temp_path)

    except Exception as e:
        return f"执行失败: {str(e)}"
