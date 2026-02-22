import os
import json
import hashlib
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import re
import difflib


def _default_output_dir() -> str:
    """Return absolute path to backend/output, so path does not depend on process cwd."""
    try:
        # __file__ = .../backend/app/services/output_manager.py -> parent*3 = backend
        backend_root = Path(__file__).resolve().parent.parent.parent
        out = str(backend_root / "output")
        return out
    except Exception:
        return os.path.abspath("output")


class OutputManager:
    """Manages saving generated code and files from agent tasks"""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir if base_dir is not None else _default_output_dir()
        try:
            self.ensure_dir(self.base_dir)
        except OSError:
            pass  # 目录已存在或无权限时继续，后续读写再报错

    def ensure_dir(self, path: str):
        """Ensure directory exists"""
        if not os.path.exists(path):
            os.makedirs(path)

    def extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from markdown content"""
        blocks = []
        # Match ```language\ncode\n``` or ```\ncode\n```
        pattern = r'```(\w+)?\s*\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)

        for lang, code in matches:
            lang = lang or 'text'
            # Try to detect filename from first comment or content
            filename = self.detect_filename(code, lang)
            blocks.append({
                'language': lang,
                'filename': filename,
                'code': code.strip()
            })

        return blocks

    def detect_filename(self, code: str, lang: str) -> str:
        """Detect filename from code content"""
        # Check for filename in first line comment
        first_lines = code.strip().split('\n')[:5]
        for line in first_lines:
            # Check for filename patterns
            if 'filename:' in line.lower() or 'file:' in line.lower():
                match = re.search(r'(?:filename|file):\s*(\S+)', line, re.IGNORECASE)
                if match:
                    return match.group(1)
            # Check for HTML doctype
            if '<!doctype html' in line.lower() or '<html' in line.lower():
                return 'index.html'
            # Check for common patterns
            if 'function' in line and lang == 'javascript':
                return 'script.js'
            if lang == 'css':
                return 'style.css'
            if lang == 'html':
                return 'index.html'

        # Default extensions
        ext_map = {
            'javascript': 'js',
            'typescript': 'ts',
            'python': 'py',
            'html': 'html',
            'css': 'css',
            'json': 'json',
        }
        ext = ext_map.get(lang, lang)
        return f'code.{ext}'

    def save_task_output(
        self,
        plan_id: str,
        task_id: str,
        task_title: str,
        agent_type: str,
        content: str,
    ) -> List[str]:
        """Save task output to files, returns list of saved file paths"""
        plan_dir = os.path.join(self.base_dir, plan_id[:8])  # Use first 8 chars of UUID
        self.ensure_dir(plan_dir)

        saved_files = []
        code_counter = self._get_next_code_counter(plan_dir)

        # Extract code blocks
        code_blocks = self.extract_code_blocks(content)

        if code_blocks:
            for i, block in enumerate(code_blocks):
                filename = block['filename']

                # Always use numbered filenames to avoid overwriting
                base, ext = os.path.splitext(filename)
                if base in ['code', 'script', 'style', 'index']:
                    filepath = os.path.join(plan_dir, f"{base}_{code_counter + i}{ext}")
                else:
                    filepath = os.path.join(plan_dir, filename)
                    if os.path.exists(filepath):
                        filepath = os.path.join(plan_dir, f"{base}_{code_counter + i}{ext}")

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(block['code'])
                saved_files.append(filepath)

        # Also save full content as markdown
        task_slug = re.sub(r'[^\w\s-]', '', task_title.lower())[:30]
        task_slug = re.sub(r'[\s-]+', '-', task_slug)
        md_path = os.path.join(plan_dir, f"{task_slug}.md")

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {task_title}\n\n")
            f.write(f"**Agent**: {agent_type}\n\n")
            f.write(f"**Time**: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(content)

        saved_files.append(md_path)
        return saved_files

    def _get_next_code_counter(self, plan_dir: str) -> int:
        """Get the next available code counter for numbered files"""
        max_counter = -1
        for f in os.listdir(plan_dir):
            match = re.match(r'.+_(\d+)\.\w+$', f)
            if match:
                counter = int(match.group(1))
                max_counter = max(max_counter, counter)
        return max_counter + 1

    def consolidate_web_app(self, plan_id: str, plan_title: str) -> bool:
        """Consolidate code fragments into a working web application"""
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        if not os.path.exists(plan_dir):
            return False

        index_path = os.path.join(plan_dir, "index.html")

        # Collect all JS code from .js files (browser-compatible only)
        js_code = []
        js_files = []

        # Patterns that indicate Node.js/test code (not browser-compatible)
        # Use \b word boundary to avoid false matches like init(), describeGame()
        node_patterns = [
            r'module\.exports',
            r'\brequire\s*\(',
            r'import\s+.*from\s+["\']',
            r'@testing-library',
            r'jest\.mock',
            r'\bdescribe\s*\(',
            r'\bit\s*\(',
            r'\btest\s*\(',
            r'\bexpect\s*\(',
            # Server-side frameworks and libraries
            r'\bexpress\s*\(\)',
            r'\bsocket\.io\b',
            r'\bsocketIo\b',
            r'\bmongoose\b',
            r'\bredis\b',
            r'\bMongoClient\b',
            r'\bmongodb://',
            r'\bredis://',
            r'\bprocess\.env\b',
            r'\b__dirname\b',
            r'\b__filename\b',
            r'\bhttp\.createServer\b',
            r'\bapp\.listen\s*\(',
            r'\bserver\.listen\s*\(',
            r'\bcors\s*\(\)',
            r'\bjwt\.sign\b',
            r'\bjwt\.verify\b',
            # MongoDB schema patterns
            r'\bSchema\s*=\s*new\s+mongoose\.Schema',
            r'\bObjectId\b',
        ]

        for f in sorted(os.listdir(plan_dir)):
            if f.endswith('.js'):
                filepath = os.path.join(plan_dir, f)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='replace') as file:
                        content = file.read()
                    # Skip Node.js/test code
                    is_node_code = any(re.search(pattern, content) for pattern in node_patterns)
                    if content.strip() and not is_node_code:
                        js_files.append(f)
                        js_code.append(f"// From {f}\n{content}")
                except OSError:
                    continue

        # Collect all CSS
        css_code = []
        for f in sorted(os.listdir(plan_dir)):
            if f.endswith('.css'):
                filepath = os.path.join(plan_dir, f)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='replace') as file:
                        css_content = file.read()
                    if css_content.strip():
                        css_code.append(f"/* From {f} */\n{css_content}")
                except OSError:
                    pass

        # Find or create index.html（多个 index_*.html 时优先用编号最大的，通常最完整）
        html_content = None
        html_files = [f for f in os.listdir(plan_dir) if f.endswith('.html')]
        if html_files:
            def _index_num(fname: str) -> int:
                m = re.search(r'index_(\d+)\.html', fname)
                return int(m.group(1)) if m else (0 if fname == 'index.html' else -1)
            best = max(html_files, key=_index_num)
            filepath = os.path.join(plan_dir, best)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as file:
                html_content = file.read()

        if not html_content:
            # Create a basic HTML structure
            html_content = self._generate_basic_html(plan_title)

        # ALWAYS remove external script and CSS references - they won't work in single file
        html_content = re.sub(r'<script\s+src=["\'][^"\']*\.js["\']?\s*></script>', '', html_content)
        html_content = re.sub(r'<script\s+src=["\'][^"\']*\.js["\']?\s*/>', '', html_content)
        html_content = re.sub(r'<link[^>]*href=["\'][^"\']+\.css["\'][^>]*>', '', html_content)

        # Remove Phaser CDN - we enforce pure Canvas
        html_content = re.sub(r'<script\s+src=["\'][^"\']*phaser[^"\']*\.js["\']?\s*>\s*</script>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<script\s+src=["\'][^"\']*phaser[^"\']*["\']?\s*/>', '', html_content, flags=re.IGNORECASE)

        # Inject CSS if not already present (inline styles)
        if css_code and '<style>' not in html_content:
            combined_css = '\n'.join(css_code)
            html_content = html_content.replace('</head>', f'<style>\n{combined_css}\n</style>\n</head>')

        # Handle JavaScript consolidation - always merge JS files into HTML
        # This ensures all JS files are included, even if HTML already has some JS
        if js_code:
            combined_js = '\n'.join(js_code)
            # Find last script tag or inject before </body>
            if '</script>' in html_content and '<script' in html_content:
                # Insert after the last </script> to maintain code order
                last_script_pos = html_content.rfind('</script>')
                html_content = (
                    html_content[:last_script_pos + len('</script>')] +
                    f'\n<script>\n{combined_js}\n</script>' +
                    html_content[last_script_pos + len('</script>'):]
                )
            else:
                html_content = html_content.replace('</body>', f'<script>\n{combined_js}\n</script>\n</body>')

        # Validate and fix common issues
        html_content = self._validate_and_fix_html(html_content, plan_title)

        # Write consolidated index.html
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return True

    def _validate_and_fix_html(self, html_content: str, plan_title: str) -> str:
        """Validate and fix common issues in HTML content"""
        issues = []

        # Check for external file references that don't exist
        external_js = re.findall(r'<script\s+src=["\']([^"\']+\.js)["\']', html_content)
        if external_js:
            issues.append(f"外部 JS 引用: {external_js}")
            # Remove external references - they won't work
            for src in external_js:
                html_content = re.sub(rf'<script\s+src=["\']?{re.escape(src)}["\']?\s*></script>', '', html_content)
                html_content = re.sub(rf'<script\s+src=["\']?{re.escape(src)}["\']?\s*/>', '', html_content)

        external_css = re.findall(r'<link[^>]+href=["\']([^"\']+\.css)["\']', html_content)
        if external_css:
            issues.append(f"外部 CSS 引用: {external_css}")
            # Remove external references
            for href in external_css:
                html_content = re.sub(rf'<link[^>]+href=["\']?{re.escape(href)}["\']?[^>]*/>', '', html_content)

        # Extract all script content
        script_matches = list(re.finditer(r'<script[^>]*>([\s\S]*?)</script>', html_content))
        if script_matches:
            all_js = '\n'.join(m.group(1) for m in script_matches)

            # Check for duplicate class definitions
            class_defs = re.findall(r'\bclass\s+(\w+)', all_js)
            class_counts = {}
            for cls in class_defs:
                class_counts[cls] = class_counts.get(cls, 0) + 1

            duplicates = {cls: count for cls, count in class_counts.items() if count > 1}
            if duplicates:
                issues.append(f"重复定义的类: {duplicates}")
                # Try to keep only the last definition of each duplicate class
                for cls_name in duplicates:
                    # Find all class definitions
                    pattern = rf'(class\s+{cls_name}\s*\{{[\s\S]*?^(?:class\s|\Z))'
                    matches = list(re.finditer(rf'class\s+{cls_name}\s*\{{', all_js))
                    if len(matches) > 1:
                        # Keep only the most complete/largest definition
                        issues.append(f"  保留 {cls_name} 类的最大定义")

            # Check for framework mixing (Phaser + Canvas)
            has_phaser = bool(re.search(r'Phaser\.(Game|AUTO|Scene)', all_js))
            has_canvas = bool(re.search(r'getContext\s*\(\s*["\']2d["\']\s*\)', all_js))

            if has_phaser and has_canvas:
                issues.append("检测到混合框架代码 (Phaser + Canvas)，可能导致冲突")
                # Prefer Canvas code if no Phaser library is included
                if 'phaser.js' not in html_content.lower():
                    issues.append("  Phaser 库未加载，移除 Phaser 相关代码")
                    # Remove Phaser class definitions
                    html_content = re.sub(
                        r'class\s+\w+\s+extends\s+Phaser[^\{]*\{[\s\S]*?\n\s*\}',
                        '// Removed Phaser code - library not loaded',
                        html_content
                    )
                    html_content = re.sub(
                        r'new\s+Phaser\.Game\s*\([^)]*\)\s*;?',
                        '// Removed Phaser.Game - library not loaded',
                        html_content
                    )

            # Check for undefined classes (excluding built-ins and Phaser)
            defined_classes = set(re.findall(r'\bclass\s+(\w+)', all_js))  # 始终定义，供下方 undefined_funcs 使用
            if re.search(r'\bnew\s+\w+\(', all_js):
                used_classes = set(re.findall(r'\bnew\s+(\w+)\(', all_js))

                builtin_classes = {'Object', 'Array', 'String', 'Number', 'Boolean', 'Function',
                                   'Date', 'RegExp', 'Error', 'Map', 'Set', 'Promise', 'Image', 'Audio',
                                   'XMLHttpRequest', 'WebSocket', 'JSON', 'Math', 'Intl', 'Proxy', 'Reflect'}
                undefined_classes = used_classes - defined_classes - builtin_classes

                # Also exclude Phaser classes if library is loaded
                if 'phaser.js' in html_content.lower():
                    phaser_classes = {'Phaser', 'Game', 'Scene', 'Sprite', 'Text', 'Image', 'Graphics',
                                      'TileSprite', 'Container', 'Group', 'Physics'}
                    undefined_classes = undefined_classes - phaser_classes

                if undefined_classes:
                    issues.append(f"可能未定义的类: {undefined_classes}")

            # Check for undefined functions being called
            func_calls = set(re.findall(r'\b(\w+)\s*\(', all_js))
            func_defs = set(re.findall(r'function\s+(\w+)', all_js))
            method_defs = set(re.findall(r'(\w+)\s*\([^)]*\)\s*\{', all_js))

            # Common built-in functions
            builtin_funcs = {'console', 'document', 'window', 'Math', 'JSON', 'parseInt', 'parseFloat',
                             'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval', 'alert',
                             'confirm', 'prompt', 'fetch', 'require', 'define', 'addEventListener',
                             'getElementById', 'querySelector', 'querySelectorAll', 'createElement',
                             'requestAnimationFrame', 'cancelAnimationFrame'}

            undefined_funcs = func_calls - func_defs - method_defs - builtin_funcs - defined_classes
            # Filter out common patterns
            undefined_funcs = {f for f in undefined_funcs if not f.startswith('_') and len(f) > 2}

        # Check for missing initialization
        has_init = bool(re.search(r'(window\.onload|DOMContentLoaded|addEventListener.*load|\.\s*init\s*\()', html_content))
        has_game_loop = bool(re.search(r'(gameLoop|requestAnimationFrame|setInterval)', html_content))
        has_class_def = bool(re.search(r'class\s+\w+', html_content))

        if has_class_def and not has_init:
            issues.append("缺少初始化代码 (window.onload/DOMContentLoaded)")

        if has_class_def and has_game_loop and not has_init:
            # Add basic initialization wrapper
            init_wrapper = '''
<script>
// 自动添加的初始化代码
document.addEventListener('DOMContentLoaded', function() {
    // 尝试自动初始化游戏
    if (typeof Game !== 'undefined' && !window.game) {
        try {
            window.game = new Game();
        } catch(e) {
            console.log('自动初始化失败:', e.message);
        }
    }
});
</script>
'''
            html_content = html_content.replace('</body>', init_wrapper + '</body>')
            issues.append("已添加自动初始化包装器")

        if issues:
            print(f"[OutputManager] 代码验证发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"  - {issue}")

        return html_content

    def _generate_basic_html(self, title: str) -> str:
        """Generate a basic HTML template"""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <div id="app"></div>
</body>
</html>'''

    def save_plan_output(
        self,
        plan_id: str,
        plan_title: str,
        tasks: List[Dict[str, Any]],
    ) -> str:
        """Save plan summary and all task outputs"""
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        self.ensure_dir(plan_dir)

        # Create index.html for web projects
        index_path = os.path.join(plan_dir, "index.html")
        if not os.path.exists(index_path):
            # Check if there's any HTML content in tasks
            for task in tasks:
                if task.get('result') and '<html' in task['result'].lower():
                    # Extract and save the HTML
                    html_match = re.search(
                        r'(<(!DOCTYPE\s+)?html.*?</html>)',
                        task['result'],
                        re.IGNORECASE | re.DOTALL
                    )
                    if html_match:
                        with open(index_path, 'w', encoding='utf-8') as f:
                            f.write(html_match.group(1))
                        break

        # Try to consolidate web app
        self.consolidate_web_app(plan_id, plan_title)

        # Create README
        readme_path = os.path.join(plan_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {plan_title}\n\n")
            f.write(f"Generated by AITeam Pipeline\n\n")
            f.write(f"Plan ID: {plan_id}\n\n")
            f.write(f"## Tasks\n\n")
            for task in tasks:
                status = "✅" if task.get('status') == 'completed' else "⏳"
                f.write(f"- {status} {task.get('title', 'Unknown')}\n")

        return plan_dir

    def get_output_path(self, plan_id: str) -> str:
        """Get the output directory path for a plan"""
        return os.path.join(self.base_dir, plan_id[:8])

    def read_existing_code(self, plan_id: str, max_length: int = 20000) -> Optional[str]:
        """读取 plan 的现有 index.html 代码"""
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        index_path = os.path.join(plan_dir, "index.html")

        if not os.path.exists(index_path):
            return None

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 限制长度以避免超过 LLM 上下文
            if len(content) > max_length:
                # 优先保留 JavaScript 部分
                script_match = re.search(r'<script[^>]*>([\s\S]*?)</script>', content)
                if script_match:
                    js_content = script_match.group(1)
                    html_without_js = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', content)
                    # 保留 HTML 结构摘要 + 完整 JS
                    return f"{html_without_js[:5000]}\n\n<script>\n{js_content[:12000]}\n</script>"
                return content[:max_length]

            return content
        except Exception as e:
            print(f"[OutputManager] Error reading existing code: {e}")
            return None

    # ==================== Archive Management ====================

    def save_iteration_archive(self, plan_id: str, round_number: int, custom_name: Optional[str] = None, description: Optional[str] = None) -> Optional[str]:
        """保存当前 index.html 到存档目录

        Args:
            plan_id: 计划 ID
            round_number: 迭代轮次（0 表示初始版本）
            custom_name: 自定义名称（可选）
            description: 存档描述（可选）

        Returns:
            存档相对路径（如 "archive/initial" 或 "archive/iteration_1"），失败返回 None
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        index_path = os.path.join(plan_dir, "index.html")

        if not os.path.exists(index_path):
            print(f"[OutputManager] Archive failed: index.html not found for plan {plan_id[:8]}")
            return None

        # 确定存档目录名
        if round_number == 0:
            archive_name = "initial"
        else:
            archive_name = f"iteration_{round_number}"

        archive_dir = os.path.join(plan_dir, "archive", archive_name)
        self.ensure_dir(archive_dir)

        archive_path = os.path.join(archive_dir, "index.html")

        try:
            import shutil
            shutil.copy2(index_path, archive_path)

            # Calculate checksum and save metadata
            checksum = self._calculate_checksum(archive_path)
            metadata = {
                "round_number": round_number,
                "archive_name": archive_name,
                "created_at": datetime.now().isoformat(),
                "checksum": checksum,
                "custom_name": custom_name,
                "description": description,
            }
            self._save_archive_metadata(archive_dir, metadata)

            print(f"[OutputManager] Archive saved: {archive_path}")
            return f"archive/{archive_name}"
        except Exception as e:
            print(f"[OutputManager] Archive failed: {e}")
            return None

    def restore_iteration_archive(self, plan_id: str, round_number: int) -> bool:
        """从存档还原 index.html

        Args:
            plan_id: 计划 ID
            round_number: 迭代轮次（0 表示初始版本）

        Returns:
            是否还原成功
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])

        # 确定存档目录名
        if round_number == 0:
            archive_name = "initial"
        else:
            archive_name = f"iteration_{round_number}"

        archive_path = os.path.join(plan_dir, "archive", archive_name, "index.html")
        index_path = os.path.join(plan_dir, "index.html")

        if not os.path.exists(archive_path):
            print(f"[OutputManager] Restore failed: archive not found at {archive_path}")
            return False

        try:
            import shutil
            shutil.copy2(archive_path, index_path)
            print(f"[OutputManager] Restored from archive: {archive_path}")
            return True
        except Exception as e:
            print(f"[OutputManager] Restore failed: {e}")
            return False

    def list_archives(self, plan_id: str) -> List[Dict[str, Any]]:
        """列出所有存档版本

        Args:
            plan_id: 计划 ID

        Returns:
            存档列表，包含轮次、路径、创建时间等信息
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        archive_base_dir = os.path.join(plan_dir, "archive")

        archives = []

        if not os.path.exists(archive_base_dir):
            return archives

        try:
            for name in sorted(os.listdir(archive_base_dir)):
                archive_dir = os.path.join(archive_base_dir, name)
                if not os.path.isdir(archive_dir):
                    continue

                index_path = os.path.join(archive_dir, "index.html")
                if not os.path.exists(index_path):
                    continue

                # 解析轮次号
                if name == "initial":
                    round_number = 0
                    label = "初始版本"
                elif name.startswith("iteration_"):
                    round_number = int(name.split("_")[1])
                    label = f"迭代 {round_number}"
                else:
                    continue

                # 获取文件修改时间
                stat = os.stat(index_path)
                modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()

                # 加载元数据
                metadata = self._load_archive_metadata(archive_dir)

                archive_info = {
                    "round_number": round_number,
                    "label": label,
                    "archive_name": name,
                    "archive_path": f"archive/{name}",
                    "size": stat.st_size,
                    "modified_at": modified_time,
                    "custom_name": metadata.get("custom_name"),
                    "description": metadata.get("description"),
                    "checksum": metadata.get("checksum"),
                }

                archives.append(archive_info)
        except Exception as e:
            print(f"[OutputManager] List archives error: {e}")

        return archives

    def get_archive_content(self, plan_id: str, round_number: int) -> Optional[str]:
        """获取存档内容

        Args:
            plan_id: 计划 ID
            round_number: 迭代轮次

        Returns:
            存档的 HTML 内容，失败返回 None
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])

        if round_number == 0:
            archive_name = "initial"
        else:
            archive_name = f"iteration_{round_number}"

        archive_path = os.path.join(plan_dir, "archive", archive_name, "index.html")

        if not os.path.exists(archive_path):
            return None

        try:
            with open(archive_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[OutputManager] Read archive error: {e}")
            return None

    def _calculate_checksum(self, file_path: str) -> str:
        """计算文件的 MD5 校验和"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"[OutputManager] Checksum calculation error: {e}")
            return ""

    def _get_metadata_path(self, archive_dir: str) -> str:
        """获取存档元数据文件路径"""
        return os.path.join(archive_dir, "metadata.json")

    def _save_archive_metadata(self, archive_dir: str, metadata: Dict[str, Any]) -> bool:
        """保存存档元数据"""
        try:
            metadata_path = self._get_metadata_path(archive_dir)
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[OutputManager] Save metadata error: {e}")
            return False

    def _load_archive_metadata(self, archive_dir: str) -> Dict[str, Any]:
        """加载存档元数据"""
        metadata_path = self._get_metadata_path(archive_dir)
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[OutputManager] Load metadata error: {e}")
        return {}

    def validate_archive(self, plan_id: str, round_number: int) -> Dict[str, Any]:
        """验证存档完整性

        Args:
            plan_id: 计划 ID
            round_number: 迭代轮次

        Returns:
            验证结果字典
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])

        if round_number == 0:
            archive_name = "initial"
        else:
            archive_name = f"iteration_{round_number}"

        archive_dir = os.path.join(plan_dir, "archive", archive_name)
        archive_path = os.path.join(archive_dir, "index.html")

        result = {
            "round_number": round_number,
            "valid": True,
            "checksum_match": True,
            "file_exists": True,
            "errors": [],
            "warnings": [],
        }

        # Check if archive file exists
        if not os.path.exists(archive_path):
            result["valid"] = False
            result["file_exists"] = False
            result["errors"].append(f"存档文件不存在: {archive_path}")
            return result

        # Load metadata and verify checksum
        metadata = self._load_archive_metadata(archive_dir)
        if metadata and "checksum" in metadata:
            current_checksum = self._calculate_checksum(archive_path)
            if current_checksum != metadata["checksum"]:
                result["valid"] = False
                result["checksum_match"] = False
                result["warnings"].append("存档校验和不匹配，文件可能已被修改")
        else:
            result["warnings"].append("存档缺少校验和信息（可能是旧版本存档）")

        # Check file is readable
        try:
            with open(archive_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if len(content) < 100:
                result["warnings"].append("存档文件内容过小，可能不完整")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"无法读取存档文件: {str(e)}")

        return result

    def delete_archive(self, plan_id: str, round_number: int) -> bool:
        """删除存档

        Args:
            plan_id: 计划 ID
            round_number: 迭代轮次

        Returns:
            是否删除成功
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])

        if round_number == 0:
            archive_name = "initial"
        else:
            archive_name = f"iteration_{round_number}"

        archive_dir = os.path.join(plan_dir, "archive", archive_name)

        if not os.path.exists(archive_dir):
            print(f"[OutputManager] Delete failed: archive not found at {archive_dir}")
            return False

        try:
            import shutil
            shutil.rmtree(archive_dir)
            print(f"[OutputManager] Archive deleted: {archive_dir}")
            return True
        except Exception as e:
            print(f"[OutputManager] Delete archive error: {e}")
            return False

    def get_archive_as_zip(self, plan_id: str, round_number: int) -> Optional[str]:
        """将存档打包为 zip 文件

        Args:
            plan_id: 计划 ID
            round_number: 迭代轮次

        Returns:
            zip 文件路径，失败返回 None
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])

        if round_number == 0:
            archive_name = "initial"
        else:
            archive_name = f"iteration_{round_number}"

        archive_dir = os.path.join(plan_dir, "archive", archive_name)

        if not os.path.exists(archive_dir):
            return None

        try:
            # Create temp zip file
            temp_dir = tempfile.gettempdir()
            zip_filename = f"archive_{plan_id[:8]}_{archive_name}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(archive_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, archive_dir)
                        zipf.write(file_path, arcname)

            return zip_path
        except Exception as e:
            print(f"[OutputManager] Create zip error: {e}")
            return None

    def get_archive_diff(self, plan_id: str, from_round: int, to_round: int) -> Dict[str, Any]:
        """对比两个存档版本差异

        Args:
            plan_id: 计划 ID
            from_round: 起始轮次
            to_round: 目标轮次

        Returns:
            差异对比结果
        """
        from_content = self.get_archive_content(plan_id, from_round)
        to_content = self.get_archive_content(plan_id, to_round)

        result = {
            "from_round": from_round,
            "to_round": to_round,
            "from_size": len(from_content) if from_content else 0,
            "to_size": len(to_content) if to_content else 0,
            "additions": 0,
            "deletions": 0,
            "diff_lines": [],
        }

        if not from_content or not to_content:
            result["errors"] = []
            if not from_content:
                result["errors"].append(f"存档 round {from_round} 不存在或无法读取")
            if not to_content:
                result["errors"].append(f"存档 round {to_round} 不存在或无法读取")
            return result

        # Calculate diff
        from_lines = from_content.splitlines(keepends=True)
        to_lines = to_content.splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            from_lines,
            to_lines,
            fromfile=f"round_{from_round}",
            tofile=f"round_{to_round}",
            lineterm=''
        ))

        # Count additions and deletions
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                result["additions"] += 1
            elif line.startswith('-') and not line.startswith('---'):
                result["deletions"] += 1

        # Limit diff output to 500 lines for display
        result["diff_lines"] = diff[:500]
        if len(diff) > 500:
            result["diff_lines"].append(f"... ({len(diff) - 500} more lines)")

        return result

    def pre_test_validation(self, plan_id: str) -> Dict[str, Any]:
        """Pre-test validation to ensure code is complete and error-free"""
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        index_path = os.path.join(plan_dir, "index.html")

        result = {
            "passed": True,
            "errors": [],
            "warnings": [],
            "auto_fixed": [],
        }

        if not os.path.exists(index_path):
            result["passed"] = False
            result["errors"].append("index.html 不存在")
            return result

        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 1. Check for external file references
        external_js = re.findall(r'<script\s+src=["\']([^"\']+)["\']', html_content)
        external_css = re.findall(r'<link[^>]+href=["\']([^"\']+\.css)["\']', html_content)

        if external_js:
            result["errors"].append(f"外部 JS 引用: {external_js}")
            result["passed"] = False

        if external_css:
            result["errors"].append(f"外部 CSS 引用: {external_css}")
            result["passed"] = False

        # 2. Check for CDN dependencies (may be blocked)
        cdn_refs = re.findall(r'(https?://cdn[^"\']+)', html_content)
        if cdn_refs:
            result["warnings"].append(f"CDN 依赖: {cdn_refs[:3]}... (可能被墙)")

        # 3. Check for incomplete code patterns
        incomplete_patterns = [
            (r'//\s*TODO', 'TODO 注释'),
            (r'\.\.\.(?:\s|")', '省略号 ...'),
            (r'//\s*其他方法', '未实现的方法注释'),
            (r'//\s*待实现', '待实现注释'),
            (r'function\s+\w+\s*\(\s*\)\s*\{\s*\}', '空函数'),
        ]

        for pattern, desc in incomplete_patterns:
            if re.search(pattern, html_content):
                result["warnings"].append(f"可能不完整的代码: {desc}")

        # 4. Extract and validate JavaScript (all script tags)
        script_matches = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html_content)
        js_code = '\n'.join(script_matches)  # Combine all script contents

        if js_code:
            # Check for class definitions
            defined_classes = set(re.findall(r'\bclass\s+(\w+)', js_code))

            # Check for duplicate class definitions
            class_list = re.findall(r'\bclass\s+(\w+)', js_code)
            class_counts = {}
            for cls in class_list:
                class_counts[cls] = class_counts.get(cls, 0) + 1
            for cls, count in class_counts.items():
                if count > 1:
                    result["errors"].append(f"类 {cls} 被定义了 {count} 次")
                    result["passed"] = False

            # Check for undefined class usage
            used_classes = set(re.findall(r'\bnew\s+(\w+)\(', js_code))
            builtin_classes = {'Object', 'Array', 'String', 'Number', 'Boolean', 'Function',
                               'Date', 'RegExp', 'Error', 'Map', 'Set', 'Promise', 'Image', 'Audio',
                               'XMLHttpRequest', 'WebSocket', 'JSON', 'Math', 'Intl', 'Proxy', 'Reflect',
                               'Animation', 'CanvasGradient', 'CanvasPattern', 'Path2D', 'BigInt',
                               # Typed Arrays
                               'ArrayBuffer', 'DataView',
                               'Int8Array', 'Uint8Array', 'Uint8ClampedArray',
                               'Int16Array', 'Uint16Array', 'Int32Array', 'Uint32Array',
                               'Float32Array', 'Float64Array', 'BigInt64Array', 'BigUint64Array'}
            undefined_classes = used_classes - defined_classes - builtin_classes

            # Filter Phaser classes if CDN is included
            if any('phaser' in ref.lower() for ref in cdn_refs):
                phaser_classes = {'Phaser', 'Game', 'Scene', 'Sprite', 'Text', 'Image'}
                undefined_classes = undefined_classes - phaser_classes

            if undefined_classes:
                result["errors"].append(f"使用未定义的类: {undefined_classes}")
                result["passed"] = False

            # Check for undefined variable references (common patterns)
            undefined_var_patterns = [
                (r'\btextureCache\b', 'textureCache'),
                (r'\baudioCache\b', 'audioCache'),
                (r'\bbullets\s*=', 'bullets 数组'),
                (r'\bgetWorldVertices\b', 'getWorldVertices 函数'),
                (r'\bprojectPolygon\b', 'projectPolygon 函数'),
            ]
            for pattern, name in undefined_var_patterns:
                if re.search(pattern, js_code):
                    result["warnings"].append(f"可能未定义: {name}")

            # Check for Phaser usage without CDN
            if re.search(r'Phaser\.(Game|Scene|AUTO)', js_code):
                if not any('phaser' in ref.lower() for ref in cdn_refs):
                    result["errors"].append("使用了 Phaser 但未引入库")
                    result["passed"] = False

            # Check for initialization
            has_init = bool(re.search(r'(window\.onload|DOMContentLoaded|init\s*\(\)|addEventListener.*load)', js_code))
            has_class = bool(defined_classes)

            if has_class and not has_init:
                result["errors"].append("缺少初始化代码")
                result["passed"] = False

            # Check for game loop (if it's a game)
            has_game_loop = bool(re.search(r'(requestAnimationFrame|gameLoop|setInterval)', js_code))

            if has_class and not has_game_loop:
                result["warnings"].append("代码有类但没有游戏循环")

            # Check for Canvas (required for web games)
            has_canvas = bool(re.search(r'getContext\s*\(', html_content))
            has_canvas_element = bool(re.search(r'<canvas', html_content))

            if defined_classes and not has_canvas:
                result["warnings"].append("Web 游戏应该使用 Canvas 渲染")

        # 5. Check HTML structure
        if not re.search(r'<!DOCTYPE\s+html', html_content, re.IGNORECASE):
            result["warnings"].append("缺少 DOCTYPE 声明")
        if not re.search(r'</html>', html_content, re.IGNORECASE):
            result["errors"].append("HTML 未正确闭合")
            result["passed"] = False
        if '<style>' not in html_content and not external_css:
            result["warnings"].append("没有内联 CSS")

        # 6. Check DOM elements exist
        dom_ids = re.findall(r'getElementById\s*\(\s*["\']([^"\']+)["\']', html_content)
        for dom_id in dom_ids:
            if f'id="{dom_id}"' not in html_content and f"id='{dom_id}'" not in html_content:
                result["warnings"].append(f"DOM 元素 #{dom_id} 被引用但可能不存在")

        # Print summary
        if result["errors"] or result["warnings"]:
            print(f"[PreTestValidation] 验证结果:")
            for err in result["errors"]:
                print(f"  ❌ 错误: {err}")
            for warn in result["warnings"]:
                print(f"  ⚠️ 警告: {warn}")
        else:
            print(f"[PreTestValidation] ✅ 验证通过")

        return result

    # ==================== Godot Project Management ====================

    def extract_godot_files(self, content: str) -> List[Dict[str, str]]:
        """Extract Godot project files from LLM output

        Looks for file markers in format:
        # filename: path/to/file.gd
        # filename: path/to/scene.tscn
        """
        files = []

        # Pattern to match file markers and their content
        # Matches: # filename: some/path.gd\n<content until next marker or end>
        pattern = r'#\s*filename:\s*([^\n]+)\s*\n(.*?)(?=#\s*filename:|$)'
        matches = re.findall(pattern, content, re.DOTALL)

        for filepath, file_content in matches:
            filepath = filepath.strip()
            file_content = file_content.strip()

            if filepath and file_content:
                files.append({
                    'path': filepath,
                    'content': file_content
                })

        return files

    def save_godot_project(self, plan_id: str, task_title: str, content: str) -> List[str]:
        """Save Godot project files to godot_project/ directory

        Returns list of saved file paths
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        godot_dir = os.path.join(plan_dir, "godot_project")
        self.ensure_dir(godot_dir)

        files = self.extract_godot_files(content)
        saved_files = []

        for file_info in files:
            filepath = file_info['path']
            file_content = file_info['content']

            # Create subdirectories if needed
            full_path = os.path.join(godot_dir, filepath)
            self.ensure_dir(os.path.dirname(full_path))

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

            saved_files.append(full_path)

        return saved_files

    def consolidate_godot_project(self, plan_id: str, plan_title: str) -> bool:
        """Consolidate Godot project files from multiple tasks

        Creates a complete project.godot if not present
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        godot_dir = os.path.join(plan_dir, "godot_project")

        if not os.path.exists(godot_dir):
            return False

        # Check if project.godot exists, create default if not
        project_file = os.path.join(godot_dir, "project.godot")
        if not os.path.exists(project_file):
            default_project = f'''; Engine configuration file.
; It's best edited using the editor UI and not directly,
; since the parameters that go here are all auto-detected.

config_version=5

[application]

config/name="{plan_title}"
config/description="Generated by AITeam"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.3", "Forward Plus")
config/icon="res://icon.svg"

[display]

window/size/viewport_width=720
window/size/viewport_height=1280
window/size/resizable=true
window/size/window_width_override=720
window/size/window_height_override=1280
window/stretch/mode="canvas_items"
window/handheld/orientation=1

[rendering]

renderer/rendering_method="forward_plus"
'''
            with open(project_file, 'w', encoding='utf-8') as f:
                f.write(default_project)

        return True

    def pre_test_validation_godot(self, plan_id: str) -> Dict[str, Any]:
        """Validate Godot project completeness

        Checks:
        - project.godot exists
        - At least one .tscn scene file
        - At least one .gd script file
        - No C# code
        - No external resource references
        - No TODO or placeholder comments
        """
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        godot_dir = os.path.join(plan_dir, "godot_project")

        result = {
            "passed": True,
            "errors": [],
            "warnings": [],
            "files": [],
        }

        if not os.path.exists(godot_dir):
            result["passed"] = False
            result["errors"].append("godot_project 目录不存在")
            return result

        # List all files
        godot_files = []
        for root, dirs, files in os.walk(godot_dir):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), godot_dir)
                godot_files.append(rel_path)
        result["files"] = godot_files

        # 1. Check project.godot
        if not os.path.exists(os.path.join(godot_dir, "project.godot")):
            result["errors"].append("缺少 project.godot 文件")
            result["passed"] = False

        # 2. Check for .tscn files
        tscn_files = [f for f in godot_files if f.endswith('.tscn')]
        if not tscn_files:
            result["errors"].append("缺少场景文件 (.tscn)")
            result["passed"] = False

        # 3. Check for .gd files
        gd_files = [f for f in godot_files if f.endswith('.gd')]
        if not gd_files:
            result["errors"].append("缺少脚本文件 (.gd)")
            result["passed"] = False

        # 4. Check for C# files (not allowed for Web export)
        cs_files = [f for f in godot_files if f.endswith('.cs')]
        if cs_files:
            result["errors"].append(f"发现 C# 文件: {cs_files} (无法导出到 Web/WASM)")
            result["passed"] = False

        # 5. Check file contents for issues
        for filepath in godot_files:
            full_path = os.path.join(godot_dir, filepath)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for external resource references
                if re.search(r'ext_resource\s+path="res://[^"]+\.(png|jpg|wav|ogg|mp3|ttf|otf)"', content, re.IGNORECASE):
                    result["warnings"].append(f"{filepath}: 引用了外部资源文件")

                # Check for TODO/placeholder
                if re.search(r'\bTODO\b|\bFIXME\b|\.\.\.(?:\s|$)', content, re.IGNORECASE):
                    result["warnings"].append(f"{filepath}: 包含 TODO 或占位符")

                # Check for touchscreen input (warning if missing in main scene)
                if filepath == "main.tscn" or filepath.endswith("main.gd"):
                    if not re.search(r'InputEventScreenTouch|InputEventScreenDrag|touch', content, re.IGNORECASE):
                        result["warnings"].append(f"{filepath}: 未检测到触摸输入支持（抖音小程序需要）")

                # Check for known Godot 4.3 issues
                if re.search(r'PointLight2D|GPUParticles2D', content):
                    result["warnings"].append(f"{filepath}: 使用了 Godot 4.3 已知问题功能（点光源/GPU粒子）")

            except Exception as e:
                result["warnings"].append(f"{filepath}: 无法读取文件 - {str(e)}")

        # Print summary
        if result["errors"] or result["warnings"]:
            print(f"[GodotValidation] 验证结果:")
            for err in result["errors"]:
                print(f"  ❌ 错误: {err}")
            for warn in result["warnings"]:
                print(f"  ⚠️ 警告: {warn}")
        else:
            print(f"[GodotValidation] ✅ 验证通过")

        return result

    def get_godot_project_zip(self, plan_id: str) -> Optional[str]:
        """Package Godot project as zip for download"""
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        godot_dir = os.path.join(plan_dir, "godot_project")

        if not os.path.exists(godot_dir):
            return None

        try:
            temp_dir = tempfile.gettempdir()
            zip_filename = f"godot_project_{plan_id[:8]}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(godot_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, godot_dir)
                        zipf.write(file_path, arcname)

            return zip_path
        except Exception as e:
            print(f"[OutputManager] Create Godot zip error: {e}")
            return None

    def get_godot_project_info(self, plan_id: str) -> Dict[str, Any]:
        """Get Godot project info for display"""
        plan_dir = os.path.join(self.base_dir, plan_id[:8])
        godot_dir = os.path.join(plan_dir, "godot_project")

        if not os.path.exists(godot_dir):
            return {
                "exists": False,
                "files": [],
                "validation": None
            }

        # List all files
        godot_files = []
        for root, dirs, files in os.walk(godot_dir):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), godot_dir)
                full_path = os.path.join(root, f)
                godot_files.append({
                    "path": rel_path,
                    "size": os.path.getsize(full_path),
                    "type": os.path.splitext(f)[1]
                })

        return {
            "exists": True,
            "directory": godot_dir,
            "files": godot_files,
            "file_count": len(godot_files),
            "validation": self.pre_test_validation_godot(plan_id)
        }


# Global instance
output_manager = OutputManager()
