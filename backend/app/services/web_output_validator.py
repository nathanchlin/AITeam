from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from app.services.ts_builder import ts_builder


@dataclass
class WebOutputValidationResult:
    passed: bool
    stage: str
    errors: List[str]
    warnings: List[str]
    signals: Dict[str, Any]
    score_hint: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WebOutputValidator:
    """Validate generated single-file web outputs before they become authoritative."""

    _EXTERNAL_SCRIPT_RE = re.compile(r'<script\s+src=["\']([^"\']+)["\']', re.IGNORECASE)
    _EXTERNAL_CSS_RE = re.compile(r'<link[^>]+href=["\']([^"\']+\.css)["\']', re.IGNORECASE)
    _INLINE_SCRIPT_RE = re.compile(r'<script[^>]*>([\s\S]*?)</script>', re.IGNORECASE)
    _DEFINED_ID_RE = re.compile(r'id=["\']([^"\']+)["\']', re.IGNORECASE)
    _GET_ID_RE = re.compile(r'getElementById\s*\(\s*["\']([^"\']+)["\']\s*\)')
    _QUERY_SELECTOR_ID_RE = re.compile(r'querySelector\s*\(\s*["\']#([^"\']+)["\']\s*\)')
    _TS_CSS_IMPORT_RE = re.compile(r'import\s+(?:[^"\']+from\s+)?["\']([^"\']+\.css)["\']\s*;?')
    _ELEMENT_ID_ASSIGN_RE = re.compile(r'\.id\s*=\s*["\']([^"\']+)["\']')
    _SET_ATTRIBUTE_ID_RE = re.compile(r'setAttribute\s*\(\s*["\']id["\']\s*,\s*["\']([^"\']+)["\']\s*\)')
    _INLINE_HANDLER_RE = re.compile(
        r'on(?:click|input|change|submit|keydown|keyup|pointerdown|pointerup|touchstart|touchend|mousedown|mouseup)=',
        re.IGNORECASE,
    )
    _EVENT_BINDING_RE = re.compile(
        r'addEventListener\s*\(\s*["\'](?:click|input|change|submit|keydown|keyup|pointerdown|pointerup|touchstart|touchend|mousedown|mouseup)',
        re.IGNORECASE,
    )
    _INTERACTIVE_ELEMENT_RE = re.compile(
        r'<(?:button|input|select|textarea|details|summary)\b|role=["\']button["\']|tabindex=',
        re.IGNORECASE,
    )

    def _infer_profile(self, html_content: str, requirements: str = "") -> str:
        source = f"{requirements}\n{html_content}".lower()
        if "<canvas" in source or "getcontext(" in source or "webgl" in source:
            return "canvas-game"

        canvas_keywords = [
            "canvas", "webgl", "shader", "particle", "physics", "platformer", "shooter",
            "bullet", "arcade", "racing", "flight", "pong", "breakout", "snake", "frame loop",
        ]
        dom_game_keywords = [
            "三消", "match-3", "match3", "2048", "sudoku", "棋盘", "board", "grid", "tile",
            "puzzle", "card", "memory", "inventory", "kanban", "calendar",
        ]
        spa_keywords = [
            "dashboard", "admin", "表单", "form", "settings", "landing", "portfolio", "saas",
            "管理台", "后台", "仪表盘", "博客", "官网", "工具页",
        ]

        if any(keyword in source for keyword in canvas_keywords):
            return "canvas-game"
        if any(keyword in source for keyword in dom_game_keywords):
            return "dom-interactive"
        if any(keyword in source for keyword in spa_keywords):
            return "single-page-app"
        return "dom-interactive"

    def _extract_inline_scripts(self, html_content: str) -> List[str]:
        return [match.strip() for match in self._INLINE_SCRIPT_RE.findall(html_content) if match.strip()]

    def _collect_defined_dom_ids(self, html_content: str) -> Set[str]:
        return set(self._DEFINED_ID_RE.findall(html_content))

    def _collect_referenced_dom_ids(self, html_content: str, js_code: str) -> Set[str]:
        referenced = set(self._GET_ID_RE.findall(js_code))
        referenced.update(self._QUERY_SELECTOR_ID_RE.findall(js_code))
        referenced.update(self._QUERY_SELECTOR_ID_RE.findall(html_content))
        return referenced

    def _collect_created_dom_ids_from_source(self, source: str) -> Set[str]:
        created = set(self._DEFINED_ID_RE.findall(source))
        created.update(self._ELEMENT_ID_ASSIGN_RE.findall(source))
        created.update(self._SET_ATTRIBUTE_ID_RE.findall(source))
        return created

    def _resolve_project_relative_import(self, source_path: str, import_path: str) -> Optional[str]:
        if not import_path.startswith('.'):
            return None
        return os.path.normpath(os.path.join(os.path.dirname(source_path), import_path)).replace('\\', '/')

    def _collect_ts_css_import_issues(self, files: Dict[str, str], ts_files: Dict[str, str]) -> List[str]:
        issues: List[str] = []

        for source_path, content in ts_files.items():
            for import_path in self._TS_CSS_IMPORT_RE.findall(content):
                resolved_path = self._resolve_project_relative_import(source_path, import_path)
                if not resolved_path or resolved_path in files:
                    continue

                alternate_path: Optional[str] = None
                if resolved_path.endswith('style.css'):
                    alternate_path = resolved_path[:-len('style.css')] + 'styles.css'
                elif resolved_path.endswith('styles.css'):
                    alternate_path = resolved_path[:-len('styles.css')] + 'style.css'

                if alternate_path and alternate_path in files:
                    issues.append(
                        f"{source_path} 引用了 {import_path}，但工程中存在 {alternate_path}；请统一使用 {alternate_path.split('/')[-1]}"
                    )
                else:
                    issues.append(f"{source_path} 引用了缺失的样式文件 {import_path}")

        return issues

    def _check_javascript_syntax(self, js_code: str) -> Tuple[bool, Optional[str], bool]:
        node_path = shutil.which("node")
        if not node_path:
            return True, "node 不可用，已跳过 JS 语法检查", False

        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(js_code)
            temp_path = temp_file.name

        try:
            result = subprocess.run(
                [node_path, "--check", temp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            return False, "JS 语法检查超时", True
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

        if result.returncode == 0:
            return True, None, True

        raw_output = (result.stderr or result.stdout or "未知语法错误").strip()
        lines = [line.rstrip() for line in raw_output.splitlines() if line.strip()]
        filtered_lines = [line for line in lines if not line.strip().startswith("Node.js v")]

        line_number = None
        code_line = None
        caret_line = None
        message_line = None

        for i, line in enumerate(filtered_lines):
            line_match = re.search(r':(\d+)$', line)
            if line_match and line_number is None:
                line_number = line_match.group(1)
                if i + 1 < len(filtered_lines):
                    code_line = filtered_lines[i + 1]
                if i + 2 < len(filtered_lines) and '^' in filtered_lines[i + 2]:
                    caret_line = filtered_lines[i + 2]

            if ("SyntaxError" in line or "Error:" in line) and message_line is None:
                message_line = line

        message_parts = []
        if line_number:
            message_parts.append(f"第 {line_number} 行")
        if code_line:
            message_parts.append(code_line)
        if caret_line:
            message_parts.append(caret_line)
        if message_line:
            message_parts.append(message_line)

        if message_parts:
            message = "\n".join(message_parts)
        elif filtered_lines:
            message = "\n".join(filtered_lines[:3])
        else:
            message = lines[-1] if lines else "未知语法错误"

        return False, message, True

    def _build_smoke_test_script(self, js_code: str, dom_ids: List[str]) -> str:
        serialized_js = json.dumps(js_code)
        serialized_ids = json.dumps(dom_ids)
        return f"""
const vm = require('vm');
const source = {serialized_js};
const knownIds = {serialized_ids};
class FakeClassList {{
  constructor() {{ this.set = new Set(); }}
  add(...tokens) {{ tokens.forEach(token => token && this.set.add(token)); }}
  remove(...tokens) {{ tokens.forEach(token => this.set.delete(token)); }}
  contains(token) {{ return this.set.has(token); }}
}}
class FakeElement {{
  constructor(tag = 'div', id = '') {{
    this.tagName = String(tag).toUpperCase();
    this.id = id;
    this.children = [];
    this.style = {{}};
    this.dataset = {{}};
    this.attributes = {{}};
    this.listeners = {{}};
    this.classList = new FakeClassList();
    this.textContent = '';
    this.innerHTML = '';
    this.value = '';
    this.disabled = false;
  }}
  appendChild(child) {{ this.children.push(child); return child; }}
  removeChild(child) {{ this.children = this.children.filter(item => item !== child); }}
  addEventListener(type, fn) {{ this.listeners[type] = fn; }}
  dispatchEvent(event) {{ const fn = this.listeners[event && event.type]; if (fn) return fn(event); return true; }}
  setAttribute(name, value) {{ this.attributes[name] = String(value); if (name === 'id') this.id = String(value); }}
  getAttribute(name) {{ return this.attributes[name]; }}
  querySelector(selector) {{ if (selector && selector.startsWith('#')) return document.getElementById(selector.slice(1)); return new FakeElement('div'); }}
  querySelectorAll() {{ return []; }}
  getContext() {{
    return {{
      clearRect() {{}}, fillRect() {{}}, beginPath() {{}}, arc() {{}}, fill() {{}}, stroke() {{}},
      drawImage() {{}}, save() {{}}, restore() {{}}, translate() {{}}, scale() {{}},
      fillText() {{}}, strokeText() {{}}, moveTo() {{}}, lineTo() {{}}, closePath() {{}},
      setTransform() {{}}, rect() {{}}, clip() {{}}, measureText() {{ return {{ width: 0 }}; }},
      createLinearGradient() {{ return {{ addColorStop() {{}} }}; }}
    }};
  }}
  getBoundingClientRect() {{ return {{ width: 640, height: 480, top: 0, left: 0, right: 640, bottom: 480 }}; }}
  focus() {{}}
}}
const elements = new Map(knownIds.map(id => [id, new FakeElement('div', id)]));
const document = {{
  body: new FakeElement('body', 'body'),
  head: new FakeElement('head', 'head'),
  documentElement: new FakeElement('html', 'html'),
  readyState: 'complete',
  createElement(tag) {{ return new FakeElement(tag); }},
  getElementById(id) {{ if (!elements.has(id)) elements.set(id, new FakeElement('div', id)); return elements.get(id); }},
  querySelector(selector) {{ if (selector && selector.startsWith('#')) return this.getElementById(selector.slice(1)); return new FakeElement('div'); }},
  querySelectorAll() {{ return []; }},
  addEventListener(type, fn) {{ if (type === 'DOMContentLoaded' || type === 'load') fn({{ type }}); }},
}};
const createStorage = () => {{
  const store = new Map();
  return {{
    getItem(key) {{ return store.has(key) ? store.get(key) : null; }},
    setItem(key, value) {{ store.set(key, String(value)); }},
    removeItem(key) {{ store.delete(key); }},
    clear() {{ store.clear(); }},
  }};
}};
const window = {{
  document,
  console,
  navigator: {{ userAgent: 'web-output-validator' }},
  location: {{ href: 'http://localhost/' }},
  addEventListener(type, fn) {{ if (type === 'load') fn({{ type }}); }},
  removeEventListener() {{}},
  requestAnimationFrame() {{ return 1; }},
  cancelAnimationFrame() {{}},
  setTimeout,
  clearTimeout,
  setInterval,
  clearInterval,
  localStorage: createStorage(),
  sessionStorage: createStorage(),
  Image: function Image() {{}},
  Audio: function Audio() {{}},
  performance: {{ now: () => 0 }},
}};
window.window = window;
window.self = window;
const context = {{
  window,
  document,
  console,
  navigator: window.navigator,
  location: window.location,
  setTimeout,
  clearTimeout,
  setInterval,
  clearInterval,
  requestAnimationFrame: window.requestAnimationFrame,
  cancelAnimationFrame: window.cancelAnimationFrame,
  localStorage: window.localStorage,
  sessionStorage: window.sessionStorage,
  Image: window.Image,
  Audio: window.Audio,
  HTMLElement: FakeElement,
  Node: FakeElement,
  Event: function Event(type) {{ return {{ type }}; }},
  CustomEvent: function CustomEvent(type, init) {{ return {{ type, detail: init && init.detail }}; }},
  performance: window.performance,
  globalThis: null,
}};
context.globalThis = context;
vm.createContext(context);
try {{
  vm.runInContext(source, context, {{ timeout: 2500 }});
  if (typeof window.onload === 'function') {{
    window.onload({{ type: 'load' }});
  }}
  console.log(JSON.stringify({{ passed: true, knownIds: knownIds.length }}));
}} catch (error) {{
  console.error(JSON.stringify({{ passed: false, error: String((error && error.stack) || error) }}));
  process.exit(1);
}}
"""

    def run_minimal_dom_smoke_test(self, html_content: str) -> Dict[str, Any]:
        js_code = "\n\n".join(self._extract_inline_scripts(html_content))
        if not js_code.strip():
            return {
                "passed": True,
                "skipped": True,
                "reason": "未检测到内联脚本，跳过最小 DOM smoke",
            }

        node_path = shutil.which("node")
        if not node_path:
            return {
                "passed": True,
                "skipped": True,
                "reason": "node 不可用，跳过最小 DOM smoke",
            }

        smoke_script = self._build_smoke_test_script(
            js_code,
            sorted(self._collect_defined_dom_ids(html_content)),
        )
        with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(smoke_script)
            temp_path = temp_file.name

        try:
            result = subprocess.run(
                [node_path, temp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "skipped": False,
                "error": "最小 DOM smoke 超时",
            }
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

        if result.returncode == 0:
            message = (result.stdout or "").strip().splitlines()[-1] if (result.stdout or "").strip() else ""
            payload = {"passed": True, "skipped": False}
            if message:
                try:
                    payload.update(json.loads(message))
                except json.JSONDecodeError:
                    payload["message"] = message
            return payload

        raw_error = ((result.stderr or result.stdout) or "最小 DOM smoke 失败").strip().splitlines()
        last_line = raw_error[-1] if raw_error else "最小 DOM smoke 失败"
        try:
            payload = json.loads(last_line)
            payload.setdefault("passed", False)
            payload.setdefault("skipped", False)
            return payload
        except json.JSONDecodeError:
            return {
                "passed": False,
                "skipped": False,
                "error": last_line,
            }

    def _collect_ts_project_files(self, project_dir: str) -> Dict[str, str]:
        project_path = Path(project_dir)
        files: Dict[str, str] = {}
        allowed_suffixes = {'.ts', '.tsx', '.js', '.jsx', '.css', '.html', '.json'}
        ignored_dirs = {'node_modules', 'dist', '.git', '.tsbuild-check'}

        if not project_path.exists():
            return files

        for path in sorted(project_path.rglob('*')):
            if not path.is_file():
                continue
            if any(part in ignored_dirs for part in path.parts):
                continue
            if path.suffix.lower() not in allowed_suffixes:
                continue
            rel_path = path.relative_to(project_path).as_posix()
            try:
                files[rel_path] = path.read_text(encoding='utf-8')
            except OSError:
                continue

        return files

    def _infer_ts_profile(self, files: Dict[str, str], requirements: str = "") -> str:
        source = requirements.lower() + "\n" + "\n".join(content.lower() for content in files.values())
        if any(keyword in source for keyword in ['canvas', 'getcontext(', 'requestanimationframe', 'tetromino', 'snake', 'game loop']):
            return 'canvas-game'
        if any(keyword in source for keyword in ['dashboard', 'admin', 'router', 'form', 'settings', 'portfolio', 'landing']):
            return 'single-page-app'
        return 'dom-interactive'

    def validate_ts_project(
        self,
        project_dir: str,
        stage: str,
        requirements: str = "",
    ) -> WebOutputValidationResult:
        files = self._collect_ts_project_files(project_dir)
        errors: List[str] = []
        warnings: List[str] = []
        signals: Dict[str, Any] = {
            'project_dir': project_dir,
            'file_count': len(files),
            'files': sorted(files.keys()),
        }

        if not files:
            return WebOutputValidationResult(
                passed=False,
                stage=stage,
                errors=['TypeScript 工程目录为空或未找到可校验文件'],
                warnings=[],
                signals=signals,
                score_hint=0.0,
            )

        ts_files = {path: content for path, content in files.items() if path.endswith(('.ts', '.tsx', '.js', '.jsx'))}
        css_files = {path: content for path, content in files.items() if path.endswith('.css')}
        html_files = {path: content for path, content in files.items() if path.endswith('.html')}
        main_entry = next((path for path in ('src/main.ts', 'src/main.tsx') if path in files), None)
        profile = self._infer_ts_profile(files, requirements)
        combined_source = "\n\n".join(ts_files.values())
        index_html = files.get('index.html', '')
        defined_dom_ids = self._collect_defined_dom_ids(index_html)
        created_dom_ids = self._collect_created_dom_ids_from_source(combined_source)
        referenced_dom_ids = self._collect_referenced_dom_ids('', combined_source)
        missing_dom_ids = sorted(referenced_dom_ids - defined_dom_ids - created_dom_ids)
        css_import_issues = self._collect_ts_css_import_issues(files, ts_files)

        signals['profile'] = profile
        signals['ts_file_count'] = len(ts_files)
        signals['css_file_count'] = len(css_files)
        signals['html_file_count'] = len(html_files)
        signals['has_main_entry'] = bool(main_entry)
        signals['has_styles'] = bool(css_files)
        signals['import_count'] = len(re.findall(r'\bimport\b', combined_source))
        signals['export_count'] = len(re.findall(r'\bexport\b', combined_source))
        signals['type_signal_count'] = len(re.findall(r'\b(interface|type|enum|implements|readonly)\b|:\s*[A-Z_a-z][A-Za-z0-9_<>, \[\]\|]*', combined_source))
        signals['placeholder_detected'] = bool(re.search(r'等待生成具体业务代码|代码生成尚未完成|TODO|FIXME|待实现', combined_source, re.IGNORECASE))
        signals['defined_dom_id_count'] = len(defined_dom_ids)
        signals['created_dom_id_count'] = len(created_dom_ids)
        signals['referenced_dom_id_count'] = len(referenced_dom_ids)
        signals['missing_dom_ids'] = missing_dom_ids
        signals['missing_css_imports'] = css_import_issues

        if not main_entry:
            errors.append('缺少 src/main.ts 或 src/main.tsx 入口文件')
        if len(ts_files) == 0:
            errors.append('未检测到任何 TypeScript/JavaScript 源文件')
        elif len(ts_files) == 1:
            warnings.append('当前工程只有一个脚本入口文件，模块化程度偏弱')

        if signals['placeholder_detected']:
            errors.append('工程中仍包含明显占位或待实现内容')
        if len(css_files) == 0:
            warnings.append('未检测到样式文件，界面可能仍较为粗糙')
        if signals['import_count'] == 0 and len(ts_files) > 1:
            warnings.append('检测到多个源码文件，但缺少明显的 import 依赖关系')
        if main_entry and not re.search(r'document\.(getElementById|querySelector)|new\s+\w+\(|render\(|mount\(|start\(', files.get(main_entry, '')):
            warnings.append('入口文件缺少明显的启动或挂载逻辑')
        if missing_dom_ids:
            errors.append(f"TypeScript 工程引用了模板或源码中不存在的 DOM id: {missing_dom_ids}")
        if css_import_issues:
            errors.extend([f"TypeScript 工程样式导入路径异常: {issue}" for issue in css_import_issues[:5]])

        compile_result = ts_builder.compile_check(project_dir)
        signals['compile_checked'] = True
        signals['compile_passed'] = compile_result.passed
        signals['compile_command'] = compile_result.command
        signals['compile_returncode'] = compile_result.returncode

        if not compile_result.passed:
            errors.extend([f'TypeScript 编译检查失败: {message}' for message in compile_result.errors[:8]])
        else:
            warnings.extend(compile_result.warnings[:5])

        score_hint = max(0.0, 100.0 - len(errors) * 15.0 - len(warnings) * 4.0)
        signals['score_hint'] = round(score_hint, 1)

        return WebOutputValidationResult(
            passed=not errors,
            stage=stage,
            errors=errors,
            warnings=warnings,
            signals=signals,
            score_hint=round(score_hint, 1),
        )

    def validate_html_output(
        self,
        html_content: str,
        stage: str,
        requirements: str = "",
    ) -> WebOutputValidationResult:
        html_content = html_content or ""
        errors: List[str] = []
        warnings: List[str] = []
        signals: Dict[str, Any] = {}

        profile = self._infer_profile(html_content, requirements)
        signals["profile"] = profile
        signals["html_length"] = len(html_content)
        signals["has_doctype"] = bool(re.search(r'<!DOCTYPE\s+html', html_content, re.IGNORECASE))
        signals["has_html_tag"] = bool(re.search(r'<html\b', html_content, re.IGNORECASE))
        signals["has_body_tag"] = bool(re.search(r'<body\b', html_content, re.IGNORECASE))
        signals["has_closing_html"] = bool(re.search(r'</html>', html_content, re.IGNORECASE))
        signals["has_closing_body"] = bool(re.search(r'</body>', html_content, re.IGNORECASE))
        signals["has_canvas"] = bool(re.search(r'<canvas\b', html_content, re.IGNORECASE))
        signals["has_canvas_context"] = bool(re.search(r'getContext\s*\(', html_content))

        if not signals["has_html_tag"] or not signals["has_body_tag"]:
            errors.append("缺少完整的 HTML/body 结构")
        if not signals["has_closing_html"] or not signals["has_closing_body"]:
            errors.append("HTML 或 body 未正确闭合")
        if not signals["has_doctype"]:
            warnings.append("缺少 DOCTYPE 声明")

        external_js = self._EXTERNAL_SCRIPT_RE.findall(html_content)
        external_css = self._EXTERNAL_CSS_RE.findall(html_content)
        signals["external_js"] = external_js
        signals["external_css"] = external_css
        if external_js:
            errors.append(f"存在外部 JS 引用: {external_js}")
        if external_css:
            errors.append(f"存在外部 CSS 引用: {external_css}")

        scripts = self._extract_inline_scripts(html_content)
        js_code = "\n\n".join(scripts)
        signals["inline_script_count"] = len(scripts)
        signals["has_inline_script"] = bool(scripts)

        syntax_ok, syntax_message, syntax_checked = self._check_javascript_syntax(js_code) if js_code else (True, None, False)
        signals["js_syntax_checked"] = syntax_checked
        signals["js_syntax_valid"] = syntax_ok
        if syntax_message and not syntax_checked:
            warnings.append(syntax_message)
        elif not syntax_ok:
            errors.append(f"JavaScript 语法检查失败: {syntax_message}")

        defined_dom_ids = self._collect_defined_dom_ids(html_content)
        referenced_dom_ids = self._collect_referenced_dom_ids(html_content, js_code)
        missing_dom_ids = sorted(referenced_dom_ids - defined_dom_ids)
        signals["defined_dom_id_count"] = len(defined_dom_ids)
        signals["referenced_dom_id_count"] = len(referenced_dom_ids)
        signals["missing_dom_ids"] = missing_dom_ids
        if missing_dom_ids:
            errors.append(f"引用了不存在的 DOM id: {missing_dom_ids}")

        has_inline_handlers = bool(self._INLINE_HANDLER_RE.search(html_content))
        has_event_binding = bool(self._EVENT_BINDING_RE.search(js_code))
        has_init = bool(re.search(r'window\.onload|DOMContentLoaded|document\.addEventListener\s*\(\s*["\']DOMContentLoaded["\']', js_code))
        has_bootstrap_instance = bool(re.search(r'new\s+\w+\s*\(', js_code))
        has_render_loop = bool(re.search(r'requestAnimationFrame|gameLoop|setInterval', js_code))
        has_state_update_signal = bool(re.search(r'\.textContent|\.innerHTML|\.replaceChildren|\.appendChild|\.classList|\.setAttribute|\.style\.|dataset\.|localStorage|sessionStorage', js_code))
        has_class_definitions = bool(re.search(r'\bclass\s+\w+', js_code))
        has_interactive_elements = bool(self._INTERACTIVE_ELEMENT_RE.search(html_content))

        signals["has_inline_handlers"] = has_inline_handlers
        signals["has_event_binding"] = has_event_binding or has_inline_handlers
        signals["has_init"] = has_init
        signals["has_bootstrap_instance"] = has_bootstrap_instance
        signals["has_render_loop"] = has_render_loop
        signals["has_state_update_signal"] = has_state_update_signal
        signals["has_class_definitions"] = has_class_definitions
        signals["has_interactive_elements"] = has_interactive_elements

        if has_class_definitions and not (has_init or has_bootstrap_instance):
            errors.append("存在类定义但缺少明确初始化入口")

        if profile == "canvas-game":
            if not signals["has_canvas"]:
                errors.append("Canvas/WebGL 游戏缺少 `<canvas>` 元素")
            if not signals["has_canvas_context"]:
                errors.append("Canvas/WebGL 游戏缺少渲染上下文初始化")
            if not has_render_loop:
                if signals["has_event_binding"]:
                    warnings.append("Canvas/WebGL 场景未检测到持续渲染循环，将按事件驱动模式处理")
                else:
                    errors.append("Canvas/WebGL 游戏缺少持续渲染或更新循环")
            if not signals["has_event_binding"]:
                warnings.append("Canvas/WebGL 游戏未检测到输入事件绑定")
        elif profile == "dom-interactive":
            if not has_interactive_elements:
                warnings.append("DOM 交互页未检测到明显的可交互元素")
            if js_code and not signals["has_event_binding"]:
                warnings.append("DOM 交互页未检测到显式事件绑定")
            if js_code and not has_state_update_signal:
                warnings.append("DOM 交互页未检测到明显的状态或视图更新信号")
        else:
            if js_code and not (signals["has_event_binding"] or has_state_update_signal):
                warnings.append("单页应用脚本缺少明显的交互或视图更新信号")

        score_hint = max(0.0, 100.0 - len(errors) * 18.0 - len(warnings) * 5.0)
        signals["score_hint"] = round(score_hint, 1)

        return WebOutputValidationResult(
            passed=not errors,
            stage=stage,
            errors=errors,
            warnings=warnings,
            signals=signals,
            score_hint=round(score_hint, 1),
        )


web_output_validator = WebOutputValidator()
