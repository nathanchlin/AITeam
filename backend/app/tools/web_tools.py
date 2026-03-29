"""Web 工具 - 搜索和 URL 获取"""

import re
from typing import Dict, Any


# 内网地址黑名单（SSRF 防护）
PRIVATE_IP_PATTERNS = [
    re.compile(r'^127\.'),
    re.compile(r'^10\.'),
    re.compile(r'^172\.(1[6-9]|2[0-9]|3[01])\.'),
    re.compile(r'^192\.168\.'),
    re.compile(r'^localhost'),
    re.compile(r'^0\.0\.0\.0'),
]


def _is_private_url(url: str) -> bool:
    """检查 URL 是否指向内网地址"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    for pattern in PRIVATE_IP_PATTERNS:
        if pattern.match(hostname):
            return True
    return False


async def search_web(query: str, _sandbox: Dict[str, Any] = None) -> str:
    """搜索 Web 信息

    Args:
        query: 搜索关键词
    """
    # 使用 httpx 进行搜索（简单实现）
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 使用 DuckDuckGo 的文本搜索 API（无需 API key）
            resp = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0 AITeam/1.0"},
            )
            if resp.status_code == 200:
                # 简单解析结果
                results = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
                snippets = [re.sub(r'<[^>]+>', '', r).strip() for r in results[:5]]
                if snippets:
                    return f"搜索 '{query}' 结果:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(snippets))
                return f"搜索 '{query}' 未找到相关结果"
            return f"搜索失败: HTTP {resp.status_code}"
    except Exception as e:
        return f"搜索 '{query}' 失败: {str(e)}"


async def fetch_url(url: str, _sandbox: Dict[str, Any] = None) -> str:
    """获取 URL 内容

    Args:
        url: 目标 URL
    """
    if _is_private_url(url):
        return "错误：不允许访问内网地址"

    try:
        import httpx
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 AITeam/1.0"})
            if resp.status_code == 200:
                content = resp.text
                # 截断
                if len(content) > 4000:
                    content = content[:3800] + "\n...（内容已截断）"
                return content
            return f"获取失败: HTTP {resp.status_code}"
    except Exception as e:
        return f"获取 URL 失败: {str(e)}"
