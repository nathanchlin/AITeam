"""
CodeMerger - 智能代码增量合并

支持将 LLM 输出的增量修改块合并到现有 HTML 代码中，而非完全替换。
同时支持 ts-app 模式下按文件路径的多文件增量更新。
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


@dataclass
class Modification:
    """单个修改操作"""
    type: str  # "modify", "add", "delete", "css", "file", "delete_file"
    target: str  # 函数名、选择器或文件路径
    new_code: str  # 新代码
    position: str = ""  # "before:" 或 "after:" 用于 add 操作


@dataclass
class MergeResult:
    """合并结果"""
    code: str
    applied: int  # 成功应用的修改数
    failed: List[str]  # 失败的修改描述


class CodeMerger:
    """智能合并代码修改"""

    MAX_SCAN_LENGTH = 100000

    MODIFY_PATTERN = re.compile(
        r'<<<MODIFY:\s*([^\s>][^>\n]*?)\s*>>>\s*\n(.*?)\n<<<END>>>',
        re.DOTALL,
    )
    ADD_PATTERN = re.compile(
        r'<<<ADD:\s*(before|after):([^\s>][^>\n]*?)\s*>>>\s*\n(.*?)\n<<<END>>>',
        re.DOTALL,
    )
    DELETE_PATTERN = re.compile(
        r'<<<DELETE:\s*([^\s>][^>\n]*?)\s*>>>\s*\n?<<<END>>>',
        re.DOTALL,
    )
    CSS_PATTERN = re.compile(
        r'<<<CSS:\s*([^\s>][^>\n]*?)\s*>>>\s*\n(.*?)\n<<<END>>>',
        re.DOTALL,
    )
    FILE_PATTERN = re.compile(
        r'<<<FILE:\s*([^\s>][^>\n]*?)\s*>>>\s*\n(.*?)\n<<<END_FILE>>>',
        re.DOTALL,
    )
    DELETE_FILE_PATTERN = re.compile(
        r'<<<DELETE_FILE:\s*([^\s>][^>\n]*?)\s*>>>\s*\n?<<<END_FILE>>>',
        re.DOTALL,
    )
    SNAPSHOT_PATTERN = re.compile(
        r'(?:^|\n)\s*(?://|#)\s*filename:\s*([^\n]+)\n(.*?)(?=(?:\n\s*(?://|#)\s*filename:)|$)',
        re.DOTALL,
    )

    def parse_modifications(self, llm_response: str) -> List[Modification]:
        """解析 LLM 输出的修改块。"""
        modifications: List[Modification] = []

        for match in self.MODIFY_PATTERN.finditer(llm_response):
            func_name = match.group(1).strip()
            new_code = match.group(2).strip()
            if func_name:
                modifications.append(Modification(type="modify", target=func_name, new_code=new_code))

        for match in self.ADD_PATTERN.finditer(llm_response):
            position = match.group(1).strip()
            target = match.group(2).strip()
            new_code = match.group(3).strip()
            if target:
                modifications.append(Modification(type="add", target=target, new_code=new_code, position=position))

        for match in self.DELETE_PATTERN.finditer(llm_response):
            func_name = match.group(1).strip()
            if func_name:
                modifications.append(Modification(type="delete", target=func_name, new_code=""))

        for match in self.CSS_PATTERN.finditer(llm_response):
            selector = match.group(1).strip()
            new_rules = match.group(2).strip()
            if selector:
                modifications.append(Modification(type="css", target=selector, new_code=new_rules))

        for match in self.FILE_PATTERN.finditer(llm_response):
            filepath = self._normalize_ts_path(match.group(1))
            if filepath:
                modifications.append(Modification(type="file", target=filepath, new_code=match.group(2).strip()))

        for match in self.DELETE_FILE_PATTERN.finditer(llm_response):
            filepath = self._normalize_ts_path(match.group(1))
            if filepath:
                modifications.append(Modification(type="delete_file", target=filepath, new_code=""))

        return modifications

    def merge_html(self, original: str, modifications: List[Modification]) -> MergeResult:
        """将修改合并到 HTML 中。"""
        result = original
        applied = 0
        failed: List[str] = []

        for mod in modifications:
            original_result = result

            if mod.type == "modify":
                result = self._replace_function(result, mod.target, mod.new_code)
            elif mod.type == "add":
                result = self._insert_code(result, mod.target, mod.new_code, mod.position)
            elif mod.type == "delete":
                result = self._remove_function(result, mod.target)
            elif mod.type == "css":
                result = self._replace_css_rule(result, mod.target, mod.new_code)
            else:
                failed.append(f"{mod.type}:{mod.target}")
                continue

            if result != original_result:
                applied += 1
            else:
                failed.append(f"{mod.type}:{mod.target}")

        return MergeResult(code=result, applied=applied, failed=failed)

    def merge_ts_project(self, original: str, modifications: List[Modification]) -> MergeResult:
        """将 ts-app 文件级修改合并到现有工程快照中。"""
        files, order = self._parse_ts_snapshot(original)
        applied = 0
        failed: List[str] = []

        for mod in modifications:
            if mod.type == "file":
                path = self._normalize_ts_path(mod.target)
                content = mod.new_code.strip()
                if not path or not content:
                    failed.append(f"{mod.type}:{mod.target}")
                    continue

                previous = files.get(path)
                files[path] = content
                if path not in order:
                    order.append(path)
                if previous != content:
                    applied += 1
                else:
                    failed.append(f"{mod.type}:{mod.target}")
            elif mod.type == "delete_file":
                path = self._normalize_ts_path(mod.target)
                if not path or path not in files:
                    failed.append(f"{mod.type}:{mod.target}")
                    continue
                del files[path]
                order = [item for item in order if item != path]
                applied += 1

        return MergeResult(code=self._serialize_ts_snapshot(files, order), applied=applied, failed=failed)

    def _parse_ts_snapshot(self, snapshot: str) -> Tuple[Dict[str, str], List[str]]:
        files: Dict[str, str] = {}
        order: List[str] = []

        for match in self.SNAPSHOT_PATTERN.finditer(snapshot or ""):
            path = self._normalize_ts_path(match.group(1))
            if not path:
                continue
            content = match.group(2).strip()
            files[path] = content
            if path not in order:
                order.append(path)

        return files, order

    def _serialize_ts_snapshot(self, files: Dict[str, str], order: List[str]) -> str:
        chunks: List[str] = []
        for path in order:
            if path not in files:
                continue
            chunks.append(f"// filename: {path}\n{files[path].strip()}\n")
        return "\n".join(chunks).strip()

    def _normalize_ts_path(self, path: str) -> Optional[str]:
        normalized = path.strip().replace('\\', '/')
        while normalized.startswith('./'):
            normalized = normalized[2:]
        if not normalized:
            return None
        if normalized.startswith('/') or normalized.startswith('..') or '/../' in normalized:
            return None
        if not (normalized.startswith('src/') or normalized.startswith('public/')):
            return None
        return normalized

    def _find_function_boundaries(self, code: str, func_name: str) -> Optional[tuple]:
        """找到 JavaScript 函数的起始和结束位置。"""
        pattern1 = rf'(function\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{)'
        pattern2 = rf'((?:const|let|var)\s+{re.escape(func_name)}\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{{)'
        pattern3 = rf'((?:const|let|var)\s+{re.escape(func_name)}\s*=\s*function\s*\([^)]*\)\s*\{{)'
        pattern4 = rf'(async\s+function\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{)'
        patterns = [pattern1, pattern4, pattern2, pattern3]

        for pattern in patterns:
            match = re.search(pattern, code, re.MULTILINE)
            if match:
                start_pos = match.start()
                brace_start = match.end() - 1
                brace_count = 1
                pos = brace_start + 1
                scan_start = pos

                while pos < len(code) and brace_count > 0:
                    if pos - scan_start > self.MAX_SCAN_LENGTH:
                        logger.warning("Brace scanning exceeded limit for function '%s'", func_name)
                        return None

                    if code[pos] in ('"', "'", '`'):
                        quote = code[pos]
                        pos += 1
                        while pos < len(code) and code[pos] != quote:
                            if code[pos] == '\\' and pos + 1 < len(code):
                                pos += 2
                            else:
                                pos += 1
                        pos += 1
                        continue

                    if code[pos:pos + 2] == '//':
                        while pos < len(code) and code[pos] != '\n':
                            pos += 1
                        continue

                    if code[pos:pos + 2] == '/*':
                        pos += 2
                        while pos < len(code) - 1 and code[pos:pos + 2] != '*/':
                            pos += 1
                        pos += 2
                        continue

                    if code[pos] == '{':
                        brace_count += 1
                    elif code[pos] == '}':
                        brace_count -= 1
                    pos += 1

                if brace_count == 0:
                    return (start_pos, pos)
                break

        return None

    def _replace_function(self, code: str, func_name: str, new_code: str) -> str:
        """替换 JavaScript 函数。"""
        boundaries = self._find_function_boundaries(code, func_name)
        if boundaries:
            start, end = boundaries
            return code[:start] + new_code + code[end:]

        logger.warning("Function '%s' not found, appending to script", func_name)
        script_match = re.search(r'</script>', code, re.IGNORECASE)
        if script_match:
            insert_pos = script_match.start()
            return code[:insert_pos] + "\n" + new_code + "\n" + code[insert_pos:]

        return code

    def _insert_code(self, code: str, target: str, new_code: str, position: str) -> str:
        """在指定位置插入代码。"""
        boundaries = self._find_function_boundaries(code, target)
        if boundaries:
            start, end = boundaries
            insert_pos = end if position == "after" else start
            return code[:insert_pos] + "\n" + new_code + "\n" + code[insert_pos:]

        logger.warning("Target function '%s' not found for insertion", target)
        script_match = re.search(r'</script>', code, re.IGNORECASE)
        if script_match:
            insert_pos = script_match.start()
            return code[:insert_pos] + "\n" + new_code + "\n" + code[insert_pos:]

        return code

    def _remove_function(self, code: str, func_name: str) -> str:
        """删除函数。"""
        boundaries = self._find_function_boundaries(code, func_name)
        if boundaries:
            start, end = boundaries
            while start > 0 and code[start - 1] in ' \t\n':
                start -= 1
            return code[:start] + code[end:]

        logger.warning("Function '%s' not found for deletion", func_name)
        return code

    @staticmethod
    def _escape_css_selector(selector: str) -> str:
        """转义 CSS 选择器用于正则匹配。"""
        result = []
        for char in selector:
            if char in r'\^$*+?()[]|':
                result.append('\\' + char)
            else:
                result.append(char)
        return ''.join(result)

    def _replace_css_rule(self, code: str, selector: str, new_rules: str) -> str:
        """替换 CSS 规则。"""
        escaped_selector = self._escape_css_selector(selector)
        pattern = rf'({escaped_selector}\s*\{{)'
        match = re.search(pattern, code, re.IGNORECASE)
        if match:
            brace_start = match.end() - 1
            brace_count = 1
            pos = brace_start + 1
            while pos < len(code) and brace_count > 0:
                if code[pos] == '{':
                    brace_count += 1
                elif code[pos] == '}':
                    brace_count -= 1
                pos += 1

            if brace_count == 0:
                start = match.start()
                new_full_rule = f"{selector} {{\n{new_rules}\n}}"
                return code[:start] + new_full_rule + code[pos:]

        logger.warning("CSS rule '%s' not found, appending to style", selector)
        style_match = re.search(r'<style[^>]*>', code, re.IGNORECASE)
        if style_match:
            insert_pos = style_match.end()
            new_full_rule = f"\n{selector} {{\n{new_rules}\n}}"
            return code[:insert_pos] + new_full_rule + code[insert_pos:]

        return code

    def has_modifications(self, llm_response: str) -> bool:
        """检查响应中是否包含修改块。"""
        return bool(
            self.MODIFY_PATTERN.search(llm_response)
            or self.ADD_PATTERN.search(llm_response)
            or self.DELETE_PATTERN.search(llm_response)
            or self.CSS_PATTERN.search(llm_response)
            or self.FILE_PATTERN.search(llm_response)
            or self.DELETE_FILE_PATTERN.search(llm_response)
        )

    def extract_analysis_text(self, llm_response: str) -> str:
        """提取修改说明文本（第一个修改块之前的内容）。"""
        patterns = [
            self.MODIFY_PATTERN,
            self.ADD_PATTERN,
            self.DELETE_PATTERN,
            self.CSS_PATTERN,
            self.FILE_PATTERN,
            self.DELETE_FILE_PATTERN,
        ]

        first_match_pos = len(llm_response)
        for pattern in patterns:
            match = pattern.search(llm_response)
            if match and match.start() < first_match_pos:
                first_match_pos = match.start()

        if first_match_pos < len(llm_response):
            return llm_response[:first_match_pos].strip()

        return llm_response


code_merger = CodeMerger()
