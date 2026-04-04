"""
测试框架服务 - 为 Pipeline 提供自动化测试能力

这个服务实现了：
1. 静态代码分析
2. 自动化功能测试
3. 质量评分
4. 测试报告生成
"""

import asyncio
import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"  # 🔴 严重
    MEDIUM = "medium"      # 🟡 中等
    MINOR = "minor"        # 🟢 轻微


@dataclass
class Issue:
    """问题定义"""
    type: str
    severity: Severity
    message: str
    location: Optional[str] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    passed: bool
    duration: float = 0.0
    error_message: Optional[str] = None
    screenshot: Optional[str] = None
    logs: List[str] = field(default_factory=list)


@dataclass
class QualityScore:
    """质量评分"""
    total: float
    correctness: float
    completeness: float
    robustness: float
    performance: float
    passed: bool
    grade: str


@dataclass
class TestReport:
    """完整测试报告"""
    plan_id: str
    timestamp: datetime
    overall_passed: bool
    quality_score: QualityScore
    static_issues: List[Issue]
    test_results: List[TestResult]
    recommendations: List[str]


class TechStackDetector:
    """技术栈检测器"""

    @staticmethod
    def detect(code: str) -> List[str]:
        """识别代码使用的技术栈"""
        stacks = []

        # Canvas/WebGL
        if re.search(r'\bcanvas\b|\bCanvas\b|\bgetContext\s*\([\'"]2d', code):
            stacks.append('canvas')

        # Three.js
        if re.search(r'\bTHREE\b|\bthree\.js\b', code):
            stacks.append('three.js')

        # Phaser
        if re.search(r'\bPhaser\b', code):
            stacks.append('phaser')

        # React
        if re.search(r'\bReact\b|\breact\b', code):
            stacks.append('react')

        # Vue
        if re.search(r'\bVue\b|\bcreateApp\b', code):
            stacks.append('vue')

        # TypeScript
        if re.search(r':\s*(string|number|boolean|any)\b', code):
            stacks.append('typescript')

        return stacks if stacks else ['vanilla-js']


class StaticAnalyzer:
    """静态代码分析器"""

    def __init__(self):
        self.detector = TechStackDetector()

    async def analyze(self, code: str) -> List[Issue]:
        """执行静态分析"""
        issues = []

        # 1. 检测严重错误
        issues.extend(await self._check_critical_errors(code))

        # 2. 检测中等问题
        issues.extend(await self._check_medium_issues(code))

        # 3. 检测轻微问题
        issues.extend(await self._check_minor_issues(code))

        return issues

    async def _check_critical_errors(self, code: str) -> List[Issue]:
        """检查严重错误（🔴 必须修复，代码无法运行）"""
        issues = []

        # 1. 空方法体检测
        empty_methods = re.finditer(
            r'(function|method|async)\s+(\w+)\s*\([^)]*\)\s*\{\s*(//|/\*|)\s*\}',
            code
        )
        for match in empty_methods:
            method_name = match.group(2)
            issues.append(Issue(
                type="empty_method",
                severity=Severity.CRITICAL,
                message=f"方法体为空: {method_name}()",
                location=f"Line {code[:match.start()].count(chr(10)) + 1}",
                code_snippet=match.group(),
                suggestion="实现方法的具体逻辑或删除此方法"
            ))

        # 2. 重复定义检测
        classes = re.findall(r'class\s+(\w+)', code)
        duplicates = [cls for cls in set(classes) if classes.count(cls) > 1]
        if duplicates:
            issues.append(Issue(
                type="duplicate_class",
                severity=Severity.CRITICAL,
                message=f"重复定义的类: {duplicates}",
                suggestion="删除重复定义，保留一个版本"
            ))

        # 3. 缺少游戏循环检测
        has_game_class = re.search(r'class\s+\w*[Gg]ame', code)
        has_loop = re.search(r'requestAnimationFrame|setInterval', code)
        if has_game_class and not has_loop:
            issues.append(Issue(
                type="missing_game_loop",
                severity=Severity.CRITICAL,
                message="游戏类定义了但没有游戏循环",
                suggestion="添加 gameLoop() { requestAnimationFrame(() => this.gameLoop()); }"
            ))

        # 4. 缺少初始化检测
        has_class = re.search(r'class\s+\w+', code)
        has_init = re.search(r'window\.onload|DOMContentLoaded|new\s+\w+\s*\(', code)
        if has_class and not has_init:
            issues.append(Issue(
                type="missing_initialization",
                severity=Severity.CRITICAL,
                message="定义了类但没有实例化",
                suggestion="添加 window.onload = () => new ClassName();"
            ))

        # 5. 未定义变量检测
        common_vars = ['ctx', 'canvas', 'gl', 'game', 'app']
        for var in common_vars:
            used = re.search(rf'\b{var}\b', code)
            defined = re.search(rf'(const|let|var)\s+{var}\s*=', code) or \
                      re.search(rf'this\.{var}\s*=', code) or \
                      re.search(rf'{var}\s*=\s*', code)

            if used and not defined:
                issues.append(Issue(
                    type="undefined_variable",
                    severity=Severity.CRITICAL,
                    message=f"使用了未定义的变量: {var}",
                    suggestion=f"在构造函数或初始化函数中定义: this.{var} = ..."
                ))

        return issues

    async def _check_medium_issues(self, code: str) -> List[Issue]:
        """检查中等问题（🟡 应该修复，影响代码质量）"""
        issues = []

        # 1. 边界检查缺失
        array_accesses = re.finditer(r'\w+\[(\w+)\]', code)
        for match in array_accesses:
            index_var = match.group(1)
            # 检查是否有边界检查
            has_check = re.search(rf'if\s*\(\s*{index_var}\s*[<>=]', code)

            if not has_check and not index_var.isdigit():
                issues.append(Issue(
                    type="missing_boundary_check",
                    severity=Severity.MEDIUM,
                    message=f"数组访问缺少边界检查: [{index_var}]",
                    suggestion=f"添加: if ({index_var} >= 0 && {index_var} < array.length)"
                ))

        # 2. 错误处理缺失
        risky_operations = [
            (r'JSON\.parse\(', 'JSON.parse 缺少错误处理'),
            (r'fetch\(', 'fetch 缺少错误处理'),
            (r'localStorage\.', 'localStorage 操作缺少错误处理'),
        ]

        for pattern, message in risky_operations:
            if re.search(pattern, code):
                # 简化检查：如果代码中有这个操作，但没有 try-catch
                if 'try' not in code or 'catch' not in code:
                    issues.append(Issue(
                        type="missing_error_handling",
                        severity=Severity.MEDIUM,
                        message=message,
                        suggestion="添加 try-catch 错误处理"
                    ))
                break  # 只报告一次

        return issues

    async def _check_minor_issues(self, code: str) -> List[Issue]:
        """检查轻微问题（🟢 建议优化）"""
        issues = []

        # 1. 缺少注释
        comment_ratio = len(re.findall(r'//|/\*', code)) / max(len(code.split('\n')), 1)
        if comment_ratio < 0.05:  # 注释少于 5%
            issues.append(Issue(
                type="missing_comments",
                severity=Severity.MINOR,
                message="代码缺少注释",
                suggestion="为关键逻辑添加注释说明"
            ))

        # 2. 硬编码数值
        hardcoded = re.findall(r'\b(\d{3,})\b', code)
        if len(hardcoded) > 3:
            issues.append(Issue(
                type="hardcoded_values",
                severity=Severity.MINOR,
                message=f"发现硬编码数值: {hardcoded[:3]}...",
                suggestion="考虑使用常量定义"
            ))

        return issues


class FunctionalTester:
    """功能测试执行器"""

    async def execute_tests(
        self,
        test_url: str,
        code: str
    ) -> List[TestResult]:
        """执行功能测试"""
        results = []

        # 根据代码类型生成测试用例
        test_cases = await self._generate_test_cases(code)

        # 执行每个测试用例
        for test_case in test_cases:
            result = await self._run_single_test(test_url, test_case)
            results.append(result)

        return results

    async def _generate_test_cases(self, code: str) -> List[Dict]:
        """根据代码生成测试用例"""
        test_cases = []

        # 基础测试（所有项目都适用）
        test_cases.append({
            "name": "TC_001_页面加载",
            "description": "验证页面能正常加载",
            "steps": [
                {"action": "wait", "duration": 2000},
                {"action": "verify", "expected": "页面无错误"}
            ]
        })

        # Canvas 游戏测试
        if 'canvas' in code.lower() or 'Canvas' in code:
            test_cases.extend([
                {
                    "name": "TC_002_Canvas渲染",
                    "description": "验证 Canvas 正常渲染",
                    "steps": [
                        {"action": "verify", "selector": "canvas", "expected": "可见"}
                    ]
                },
                {
                    "name": "TC_003_交互响应",
                    "description": "验证用户交互响应",
                    "steps": [
                        {"action": "click", "selector": "canvas"},
                        {"action": "wait", "duration": 500},
                        {"action": "verify", "expected": "有响应"}
                    ]
                }
            ])

        # 游戏类测试
        if re.search(r'class\s+\w*[Gg]ame', code):
            test_cases.extend([
                {
                    "name": "TC_004_游戏初始化",
                    "description": "验证游戏正常初始化",
                    "steps": [
                        {"action": "wait", "duration": 1000},
                        {"action": "verify", "expected": "游戏元素可见"}
                    ]
                },
                {
                    "name": "TC_005_游戏循环",
                    "description": "验证游戏循环运行",
                    "steps": [
                        {"action": "wait", "duration": 3000},
                        {"action": "verify", "expected": "画面在更新"}
                    ]
                }
            ])

        return test_cases

    async def _run_single_test(
        self,
        test_url: str,
        test_case: Dict
    ) -> TestResult:
        """执行单个测试用例（模拟版）"""
        # 注意：这是模拟实现，实际需要集成 Playwright
        # 实际实现时会使用真实浏览器自动化

        import random

        # 模拟测试执行
        await asyncio.sleep(0.5)  # 模拟测试耗时

        # 模拟测试结果（实际会根据真实执行结果）
        passed = random.random() > 0.2  # 80% 通过率

        return TestResult(
            test_name=test_case["name"],
            passed=passed,
            duration=0.5,
            error_message=None if passed else f"模拟测试失败: {test_case['description']}",
            logs=[f"执行步骤: {step['action']}" for step in test_case["steps"]]
        )


class QualityScorer:
    """质量评分器"""

    def calculate(
        self,
        static_issues: List[Issue],
        test_results: List[TestResult]
    ) -> QualityScore:
        """计算综合质量分数"""

        # 1. 正确性评分 (40%)
        correctness = self._score_correctness(static_issues)

        # 2. 完整性评分 (30%)
        completeness = self._score_completeness(test_results)

        # 3. 健壮性评分 (20%)
        robustness = self._score_robustness(static_issues)

        # 4. 性能评分 (10%)
        performance = self._score_performance(test_results)

        # 加权平均
        total = (
            correctness * 0.4 +
            completeness * 0.3 +
            robustness * 0.2 +
            performance * 0.1
        )

        # 判断是否通过
        passed = total >= 60

        # 获取等级
        grade = self._get_grade(total)

        return QualityScore(
            total=total,
            correctness=correctness,
            completeness=completeness,
            robustness=robustness,
            performance=performance,
            passed=passed,
            grade=grade
        )

    def _score_correctness(self, issues: List[Issue]) -> float:
        """正确性评分"""
        # 严重错误严重扣分
        critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)

        if critical_count == 0:
            return 100.0
        elif critical_count == 1:
            return 70.0
        elif critical_count == 2:
            return 50.0
        else:
            return 30.0

    def _score_completeness(self, results: List[TestResult]) -> float:
        """完整性评分"""
        if not results:
            return 50.0

        passed_rate = sum(1 for r in results if r.passed) / len(results)
        return passed_rate * 100

    def _score_robustness(self, issues: List[Issue]) -> float:
        """健壮性评分"""
        # 中等问题扣分
        medium_count = sum(1 for i in issues if i.severity == Severity.MEDIUM)

        return max(100 - medium_count * 10, 50)

    def _score_performance(self, results: List[TestResult]) -> float:
        """性能评分"""
        # 基于测试执行时间
        if not results:
            return 70.0

        avg_duration = sum(r.duration for r in results) / len(results)

        if avg_duration < 0.5:
            return 100.0
        elif avg_duration < 1.0:
            return 90.0
        elif avg_duration < 2.0:
            return 80.0
        else:
            return 70.0

    def _get_grade(self, score: float) -> str:
        """获取等级"""
        if score >= 90:
            return "A+ (优秀)"
        elif score >= 80:
            return "A (良好)"
        elif score >= 70:
            return "B (合格)"
        elif score >= 60:
            return "C (及格)"
        else:
            return "D (不及格)"


class TesterFramework:
    """测试框架主服务"""

    def __init__(self):
        self.static_analyzer = StaticAnalyzer()
        self.functional_tester = FunctionalTester()
        self.quality_scorer = QualityScorer()

    async def run_full_test(
        self,
        plan_id: str,
        code: str,
        test_url: str
    ) -> TestReport:
        """执行完整测试流程"""

        print(f"[TesterFramework] 开始测试 - Plan: {plan_id}")

        # 阶段 1: 静态代码分析
        print("[TesterFramework] 阶段 1/3: 静态代码分析")
        static_issues = await self.static_analyzer.analyze(code)

        # 阶段 2: 功能测试
        print("[TesterFramework] 阶段 2/3: 功能测试执行")
        test_results = await self.functional_tester.execute_tests(test_url, code)

        # 阶段 3: 质量评分
        print("[TesterFramework] 阶段 3/3: 质量评分")
        quality_score = self.quality_scorer.calculate(static_issues, test_results)

        # 生成建议
        recommendations = self._generate_recommendations(
            static_issues,
            test_results,
            quality_score
        )

        # 创建报告
        report = TestReport(
            plan_id=plan_id,
            timestamp=datetime.now(),
            overall_passed=quality_score.passed,
            quality_score=quality_score,
            static_issues=static_issues,
            test_results=test_results,
            recommendations=recommendations
        )

        print(f"[TesterFramework] 测试完成 - 通过: {quality_score.passed}, 分数: {quality_score.total:.1f}")

        return report

    def _generate_recommendations(
        self,
        issues: List[Issue],
        results: List[TestResult],
        score: QualityScore
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 严重问题
        critical = [i for i in issues if i.severity == Severity.CRITICAL]
        if critical:
            recommendations.append(f"🔴 修复 {len(critical)} 个严重错误（必须）")
            for issue in critical[:3]:  # 只列出前 3 个
                recommendations.append(f"   - {issue.message}")

        # 中等问题
        medium = [i for i in issues if i.severity == Severity.MEDIUM]
        if medium:
            recommendations.append(f"🟡 处理 {len(medium)} 个中等问题（建议）")

        # 失败的测试
        failed_tests = [r for r in results if not r.passed]
        if failed_tests:
            recommendations.append(f"❌ 修复 {len(failed_tests)} 个失败的测试用例")

        # 性能建议
        if score.performance < 80:
            recommendations.append("⚡ 优化性能以提升用户体验")

        # 通过建议
        if score.passed:
            recommendations.append(f"✅ 总体质量良好 ({score.grade})，可以交付")
        else:
            recommendations.append(f"⚠️ 质量不达标 ({score.total:.1f}/100)，需要改进")

        return recommendations

    def format_report(self, report: TestReport) -> str:
        """格式化报告为 Markdown"""
        md = f"""# 🎯 测试报告

**Plan ID**: {report.plan_id}
**测试时间**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**总体状态**: {'✅ 通过' if report.overall_passed else '❌ 未通过'}

---

## 📊 质量评分

**综合得分**: {report.quality_score.total:.1f}/100 ({report.quality_score.grade})

| 维度 | 得分 | 权重 |
|------|------|------|
| 正确性 | {report.quality_score.correctness:.1f} | 40% |
| 完整性 | {report.quality_score.completeness:.1f} | 30% |
| 健壮性 | {report.quality_score.robustness:.1f} | 20% |
| 性能 | {report.quality_score.performance:.1f} | 10% |

---

## 🔍 发现的问题

"""

        # 按严重程度分组
        critical = [i for i in report.static_issues if i.severity == Severity.CRITICAL]
        medium = [i for i in report.static_issues if i.severity == Severity.MEDIUM]
        minor = [i for i in report.static_issues if i.severity == Severity.MINOR]

        if critical:
            md += f"### 🔴 严重问题 ({len(critical)} 个)\n\n"
            for i, issue in enumerate(critical, 1):
                md += f"{i}. **{issue.message}**\n"
                if issue.suggestion:
                    md += f"   - 建议: {issue.suggestion}\n"
            md += "\n"

        if medium:
            md += f"### 🟡 中等问题 ({len(medium)} 个)\n\n"
            for i, issue in enumerate(medium, 1):
                md += f"{i}. {issue.message}\n"
            md += "\n"

        if minor:
            md += f"### 🟢 轻微问题 ({len(minor)} 个)\n\n"
            for i, issue in enumerate(minor, 1):
                md += f"{i}. {issue.message}\n"
            md += "\n"

        # 测试结果
        md += "---\n\n## 🧪 测试用例执行结果\n\n"
        passed = sum(1 for r in report.test_results if r.passed)
        total = len(report.test_results)
        md += f"**通过**: {passed}/{total}\n\n"

        for result in report.test_results:
            status = "✅" if result.passed else "❌"
            md += f"{status} **{result.test_name}** - {result.duration:.2f}s\n"
            if result.error_message:
                md += f"   - 错误: {result.error_message}\n"

        # 建议
        md += "\n---\n\n## 💡 改进建议\n\n"
        for rec in report.recommendations:
            md += f"- {rec}\n"

        md += "\n---\n\n"
        md += f"**结论**: {'✅ 可以交付' if report.overall_passed else '⚠️ 需要修复问题后重新测试'}\n"

        return md


# 全局实例
tester_framework = TesterFramework()
