"""文件操作工具 - 限于 Agent workspace 目录"""

import os
from typing import Optional, Dict, Any


def _safe_path(workspace_path: str, relative_path: str) -> Optional[str]:
    """安全拼接路径，防止路径遍历攻击"""
    # 标准化路径
    workspace_path = os.path.normpath(workspace_path)
    full_path = os.path.normpath(os.path.join(workspace_path, relative_path))

    # 检查是否在 workspace 内
    if not full_path.startswith(workspace_path):
        return None
    return full_path


async def read_file(path: str, _sandbox: Dict[str, Any] = None) -> str:
    """读取 workspace 中的文件内容

    Args:
        path: 文件相对路径
    """
    ws_path = _sandbox.get("workspace_path", "") if _sandbox else ""
    if not ws_path:
        return "错误：workspace 路径未配置"

    full_path = _safe_path(ws_path, path)
    if not full_path:
        return "错误：路径无效，不能访问 workspace 外的文件"

    if not os.path.exists(full_path):
        return f"错误：文件不存在 '{path}'"

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content[:4000]  # 截断
    except Exception as e:
        return f"读取文件失败: {str(e)}"


async def write_file(path: str, content: str, _sandbox: Dict[str, Any] = None) -> str:
    """向 workspace 写入文件

    Args:
        path: 文件相对路径
        content: 文件内容
    """
    ws_path = _sandbox.get("workspace_path", "") if _sandbox else ""
    if not ws_path:
        return "错误：workspace 路径未配置"

    full_path = _safe_path(ws_path, path)
    if not full_path:
        return "错误：路径无效，不能访问 workspace 外的文件"

    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"文件已写入: {path} ({len(content)} chars)"
    except Exception as e:
        return f"写入文件失败: {str(e)}"


async def list_directory(path: str = ".", _sandbox: Dict[str, Any] = None) -> str:
    """列出 workspace 目录内容

    Args:
        path: 目录相对路径（默认为根目录）
    """
    ws_path = _sandbox.get("workspace_path", "") if _sandbox else ""
    if not ws_path:
        return "错误：workspace 路径未配置"

    full_path = _safe_path(ws_path, path)
    if not full_path:
        return "错误：路径无效"

    if not os.path.exists(full_path):
        return f"错误：目录不存在 '{path}'"

    try:
        entries = os.listdir(full_path)
        result = []
        for entry in sorted(entries):
            entry_path = os.path.join(full_path, entry)
            if os.path.isdir(entry_path):
                result.append(f"📁 {entry}/")
            else:
                size = os.path.getsize(entry_path)
                result.append(f"📄 {entry} ({size}B)")
        return "\n".join(result) if result else "（空目录）"
    except Exception as e:
        return f"列出目录失败: {str(e)}"
