"""
CodeMerger - 智能代码增量合并

支持将 LLM 输出的增量修改块合并到现有 HTML 代码中，而非完全替换。
"""

import re
import logging
from typing import List, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class Modification:
    """单个修改操作"""
    type: str  # "modify", "add", "delete", "css"
    target: str  # 函数名、选择器或位置标识
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

    # 最大扫描长度，防止无限循环
    MAX_SCAN_LENGTH = 100000

    # 修改块的标记模式 - 使用更严格的匹配
    MODIFY_PATTERN = re.compile(
        r'<<<MODIFY:\s*([^\s>][^>\n]*?)\s*>>>\s*\n(.*?)\n<<<END>>>',
        re.DOTALL
    )
    ADD_PATTERN = re.compile(
        r'<<<ADD:\s*(before|after):([^\s>][^>\n]*?)\s*>>>\s*\n(.*?)\n<<<END>>>',
        re.DOTALL
    )
    DELETE_PATTERN = re.compile(
        r'<<<DELETE:\s*([^\s>][^>\n]*?)\s*>>>\s*\n?<<<END>>>',
        re.DOTALL
    )
    CSS_PATTERN = re.compile(
        r'<<<CSS:\s*([^\s>][^>\n]*?)\s*>>>\s*\n(.*?)\n<<<END>>>',
        re.DOTALL
    )

    def parse_modifications(self, llm_response: str) -> List[Modification]:
        """解析 LLM 输出的修改块

        Args:
            llm_response: LLM 的完整响应文本

        Returns:
            解析出的修改操作列表
        """
        modifications = []

        # 解析 MODIFY 块
        for match in self.MODIFY_PATTERN.finditer(llm_response):
            func_name = match.group(1).strip()
            new_code = match.group(2).strip()
            if func_name:  # 验证非空
                modifications.append(Modification(
                    type="modify",
                    target=func_name,
                    new_code=new_code
                ))

        # 解析 ADD 块
        for match in self.ADD_PATTERN.finditer(llm_response):
            position = match.group(1).strip()  # before 或 after
            target = match.group(2).strip()
            new_code = match.group(3).strip()
            if target:  # 验证非空
                modifications.append(Modification(
                    type="add",
                    target=target,
                    new_code=new_code,
                    position=position
                ))

        # 解析 DELETE 块
        for match in self.DELETE_PATTERN.finditer(llm_response):
            func_name = match.group(1).strip()
            if func_name:  # 验证非空
                modifications.append(Modification(
                    type="delete",
                    target=func_name,
                    new_code=""
                ))

        # 解析 CSS 块
        for match in self.CSS_PATTERN.finditer(llm_response):
            selector = match.group(1).strip()
            new_rules = match.group(2).strip()
            if selector:  # 验证非空
                modifications.append(Modification(
                    type="css",
                    target=selector,
                    new_code=new_rules
                ))

        return modifications

    def merge_html(self, original: str, modifications: List[Modification]) -> MergeResult:
        """将修改合并到 HTML 中

        Args:
            original: 原始 HTML 代码
            modifications: 修改操作列表

        Returns:
            MergeResult 包含合并后的代码和状态信息
        """
        result = original
        applied = 0
        failed = []

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

            # 检查是否成功应用
            if result != original_result:
                applied += 1
            else:
                failed.append(f"{mod.type}:{mod.target}")

        return MergeResult(code=result, applied=applied, failed=failed)

    def _find_function_boundaries(self, code: str, func_name: str) -> Optional[tuple]:
        """找到 JavaScript 函数的起始和结束位置

        支持多种函数定义格式：
        - function name() {}
        - const name = () => {}
        - const name = function() {}
        - async function name() {}
        """
        # 模式1: 普通函数声明 function name(...) { ... }
        pattern1 = rf'(function\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{)'

        # 模式2: 箭头函数 const name = (...) => { ... }
        pattern2 = rf'((?:const|let|var)\s+{re.escape(func_name)}\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{{)'

        # 模式3: 函数表达式 const name = function(...) { ... }
        pattern3 = rf'((?:const|let|var)\s+{re.escape(func_name)}\s*=\s*function\s*\([^)]*\)\s*\{{)'

        # 模式4: async 函数声明 async function name(...) { ... }
        pattern4 = rf'(async\s+function\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{)'

        patterns = [pattern1, pattern4, pattern2, pattern3]

        for pattern in patterns:
            match = re.search(pattern, code, re.MULTILINE)
            if match:
                start_pos = match.start()
                brace_start = match.end() - 1  # 第一个 { 的位置

                # 计算匹配的 }，处理字符串和注释中的大括号
                brace_count = 1
                pos = brace_start + 1
                scan_start = pos

                while pos < len(code) and brace_count > 0:
                    # 防止无限循环
                    if pos - scan_start > self.MAX_SCAN_LENGTH:
                        logger.warning(f"Brace scanning exceeded limit for function '{func_name}'")
                        return None

                    # 跳过字符串字面量
                    if code[pos] in ('"', "'", '`'):
                        quote = code[pos]
                        pos += 1
                        while pos < len(code) and code[pos] != quote:
                            if code[pos] == '\\' and pos + 1 < len(code):
                                pos += 2  # 跳过转义字符
                            else:
                                pos += 1
                        pos += 1  # 跳过结束引号
                        continue

                    # 跳过单行注释
                    if code[pos:pos+2] == '//':
                        while pos < len(code) and code[pos] != '\n':
                            pos += 1
                        continue

                    # 跳过多行注释
                    if code[pos:pos+2] == '/*':
                        pos += 2
                        while pos < len(code) - 1 and code[pos:pos+2] != '*/':
                            pos += 1
                        pos += 2  # 跳过 */
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
        """替换 JavaScript 函数"""
        boundaries = self._find_function_boundaries(code, func_name)
        if boundaries:
            start, end = boundaries
            return code[:start] + new_code + code[end:]

        # 如果找不到函数，尝试追加到 <script> 标签内
        logger.warning(f"Function '{func_name}' not found, appending to script")
        script_match = re.search(r'</script>', code, re.IGNORECASE)
        if script_match:
            insert_pos = script_match.start()
            return code[:insert_pos] + "\n" + new_code + "\n" + code[insert_pos:]

        return code

    def _insert_code(self, code: str, target: str, new_code: str, position: str) -> str:
        """在指定位置插入代码"""
        boundaries = self._find_function_boundaries(code, target)
        if boundaries:
            start, end = boundaries
            insert_pos = end if position == "after" else start
            return code[:insert_pos] + "\n" + new_code + "\n" + code[insert_pos:]

        # 如果找不到目标函数，追加到 script 标签
        logger.warning(f"Target function '{target}' not found for insertion")
        script_match = re.search(r'</script>', code, re.IGNORECASE)
        if script_match:
            insert_pos = script_match.start()
            return code[:insert_pos] + "\n" + new_code + "\n" + code[insert_pos:]

        return code

    def _remove_function(self, code: str, func_name: str) -> str:
        """删除函数"""
        boundaries = self._find_function_boundaries(code, func_name)
        if boundaries:
            start, end = boundaries
            # 删除函数及其前后的空白
            while start > 0 and code[start-1] in ' \t\n':
                start -= 1
            return code[:start] + code[end:]

        logger.warning(f"Function '{func_name}' not found for deletion")
        return code

    @staticmethod
    def _escape_css_selector(selector: str) -> str:
        """转义 CSS 选择器用于正则匹配

        只转义正则元字符，保留 CSS 特殊字符（. #: 等）
        """
        result = []
        for char in selector:
            # 只转义正则元字符
            if char in r'\^$*+?()[]|':
                result.append('\\' + char)
            else:
                result.append(char)
        return ''.join(result)

    def _replace_css_rule(self, code: str, selector: str, new_rules: str) -> str:
        """替换 CSS 规则

        Args:
            code: HTML 代码
            selector: CSS 选择器（如 ".button", "#header", "body"）
            new_rules: 新的 CSS 规则内容（不含选择器和大括号）
        """
        # 使用自定义转义函数
        escaped_selector = self._escape_css_selector(selector)

        # 查找 CSS 规则: selector { ... }
        pattern = rf'({escaped_selector}\s*\{{)'

        match = re.search(pattern, code, re.IGNORECASE)
        if match:
            brace_start = match.end() - 1

            # 找到匹配的 }
            brace_count = 1
            pos = brace_start + 1
            while pos < len(code) and brace_count > 0:
                if code[pos] == '{':
                    brace_count += 1
                elif code[pos] == '}':
                    brace_count -= 1
                pos += 1

            if brace_count == 0:
                # 替换整个规则
                start = match.start()
                new_full_rule = f"{selector} {{\n{new_rules}\n}}"
                return code[:start] + new_full_rule + code[pos:]

        # 如果找不到规则，添加到 <style> 标签内
        logger.warning(f"CSS rule '{selector}' not found, appending to style")
        style_match = re.search(r'<style[^>]*>', code, re.IGNORECASE)
        if style_match:
            insert_pos = style_match.end()
            new_full_rule = f"\n{selector} {{\n{new_rules}\n}}"
            return code[:insert_pos] + new_full_rule + code[insert_pos:]

        return code

    def has_modifications(self, llm_response: str) -> bool:
        """检查响应中是否包含修改块"""
        return bool(
            self.MODIFY_PATTERN.search(llm_response) or
            self.ADD_PATTERN.search(llm_response) or
            self.DELETE_PATTERN.search(llm_response) or
            self.CSS_PATTERN.search(llm_response)
        )

    def extract_analysis_text(self, llm_response: str) -> str:
        """提取修改说明文本（第一个修改块之前的内容）"""
        # 找到第一个修改块的位置
        patterns = [
            self.MODIFY_PATTERN,
            self.ADD_PATTERN,
            self.DELETE_PATTERN,
            self.CSS_PATTERN
        ]

        first_match_pos = len(llm_response)
        for pattern in patterns:
            match = pattern.search(llm_response)
            if match and match.start() < first_match_pos:
                first_match_pos = match.start()

        if first_match_pos < len(llm_response):
            return llm_response[:first_match_pos].strip()

        return llm_response


# 单例实例
code_merger = CodeMerger()
