import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import re


class OutputManager:
    """Manages saving generated code and files from agent tasks"""

    def __init__(self, base_dir: str = "output"):
        self.base_dir = base_dir
        self.ensure_dir(base_dir)

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
        node_patterns = [
            r'module\.exports',
            r'require\s*\(',
            r'import\s+.*from\s+["\']',
            r'@testing-library',
            r'jest\.mock',
            r'describe\s*\(',
            r'it\s*\(',
            r'test\s*\(',
            r'expect\s*\(',
        ]

        for f in sorted(os.listdir(plan_dir)):
            if f.endswith('.js'):
                filepath = os.path.join(plan_dir, f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()

                    # Skip Node.js/test code
                    is_node_code = any(re.search(pattern, content) for pattern in node_patterns)

                    if content.strip() and not is_node_code:
                        js_files.append(f)
                        js_code.append(f"// From {f}\n{content}")

        # Collect all CSS
        css_code = []
        for f in sorted(os.listdir(plan_dir)):
            if f.endswith('.css'):
                filepath = os.path.join(plan_dir, f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    css_content = file.read()
                    if css_content.strip():
                        css_code.append(f"/* From {f} */\n{css_content}")

        # Find or create index.html
        html_content = None
        for f in os.listdir(plan_dir):
            if f.endswith('.html'):
                filepath = os.path.join(plan_dir, f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                break

        if not html_content:
            # Create a basic HTML structure
            html_content = self._generate_basic_html(plan_title)

        # Check if HTML already has substantial inline JavaScript (more than just imports)
        # Look for actual function definitions or class definitions
        has_meaningful_js = bool(re.search(
            r'<script[^>]*>[\s\S]*(?:function\s+\w+|class\s+\w+|const\s+\w+\s*=)',
            html_content
        ))

        # Inject CSS if not already present (inline styles)
        if css_code and '<style>' not in html_content and '<link rel="stylesheet"' not in html_content:
            combined_css = '\n'.join(css_code)
            html_content = html_content.replace('</head>', f'<style>\n{combined_css}\n</style>\n</head>')

        # Handle JavaScript consolidation
        if js_code and not has_meaningful_js:
            combined_js = '\n'.join(js_code)

            # Remove external script references and inject inline script
            html_content = re.sub(r'<script\s+src=["\'][^"\']*\.js["\']?\s*></script>', '', html_content)
            html_content = re.sub(r'<script\s+src=["\'][^"\']*\.js["\']?\s*/>', '', html_content)

            # Inject the combined JS before </body>
            html_content = html_content.replace('</body>', f'<script>\n{combined_js}\n</script>\n</body>')

        # Write consolidated index.html
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return True

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


# Global instance
output_manager = OutputManager()
