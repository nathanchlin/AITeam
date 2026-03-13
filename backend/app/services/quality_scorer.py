"""QualityScorer - Multi-dimensional quality scoring for generated code.

This module provides a comprehensive quality assessment system that evaluates:
1. Completeness - Are all required components present?
2. Correctness - Are there common errors or anti-patterns?
3. Maintainability - Is the code well-structured and readable?
4. Performance - Are there potential performance issues?
5. User Experience - Is the UI/UX properly implemented?
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class QualityScore:
    """Represents a quality score with details."""
    score: float
    max_score: float
    percentage: float
    checks: List[Dict[str, Any]]
    recommendations: List[str]


class QualityScorer:
    """Multi-dimensional quality scoring for web application code."""

    # Weight configuration for each dimension
    WEIGHTS = {
        "completeness": 0.35,   # 35% - Most important
        "correctness": 0.30,    # 30% - Critical for running
        "maintainability": 0.15, # 15% - Code quality
        "performance": 0.10,    # 10% - Efficiency
        "user_experience": 0.10  # 10% - UX quality
    }

    # Thresholds for quality grades
    GRADE_THRESHOLDS = {
        "A": 90,
        "B": 80,
        "C": 70,
        "D": 60,
        "F": 0
    }

    def __init__(self):
        """Initialize QualityScorer."""
        pass

    def score_output(
        self,
        code: str,
        requirements: str = "",
        validation_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform comprehensive quality scoring.

        Args:
            code: The HTML/JS code to evaluate
            requirements: Original requirements for context
            validation_result: Structured validation signals from WebOutputValidator

        Returns:
            Dictionary with scores, total, grade, and recommendations
        """
        completeness = self._score_completeness(code)
        correctness = self._score_correctness(code)
        maintainability = self._score_maintainability(code)
        performance = self._score_performance(code)
        ux = self._score_ux(code, requirements)

        scores = {
            "completeness": completeness,
            "correctness": correctness,
            "maintainability": maintainability,
            "performance": performance,
            "user_experience": ux,
        }

        profile = self._infer_profile(code, requirements, validation_result)
        self._rebalance_for_profile(scores, profile)
        self._apply_validation_feedback(scores, validation_result)

        total = sum(
            scores[dim].percentage * self.WEIGHTS[dim]
            for dim in scores
        )

        if validation_result and validation_result.get("score_hint") is not None:
            try:
                total = min(total, float(validation_result["score_hint"]))
            except (TypeError, ValueError):
                pass
        if validation_result and not validation_result.get("passed", True):
            total = min(total, 59.0)

        grade = self._get_grade(total)

        recommendations = []
        for dim, score_obj in scores.items():
            recommendations.extend(score_obj.recommendations)

        return {
            "scores": {
                dim: {
                    "score": score_obj.score,
                    "max_score": score_obj.max_score,
                    "percentage": round(score_obj.percentage, 1),
                    "checks": score_obj.checks,
                }
                for dim, score_obj in scores.items()
            },
            "total": round(total, 1),
            "grade": grade,
            "recommendations": recommendations[:10],
            "passed": total >= 60,
            "profile": profile,
            "validation": validation_result,
        }

    def _infer_profile(
        self,
        code: str,
        requirements: str = "",
        validation_result: Optional[Dict[str, Any]] = None,
    ) -> str:
        signals = (validation_result or {}).get("signals", {})
        profile = signals.get("profile")
        if profile:
            return profile

        source = f"{requirements}\n{code}".lower()
        if "<canvas" in source or "getcontext(" in source or "webgl" in source:
            return "canvas-game"
        if any(keyword in source for keyword in ["三消", "match-3", "match3", "2048", "棋盘", "board", "grid", "puzzle", "card"]):
            return "dom-interactive"
        if any(keyword in source for keyword in ["dashboard", "admin", "表单", "form", "landing", "portfolio", "管理台", "仪表盘", "工具页"]):
            return "single-page-app"
        return "dom-interactive"

    def _refresh_quality_score(self, score_obj: QualityScore) -> None:
        if score_obj.max_score > 0:
            score_obj.percentage = max(0.0, min(score_obj.score / score_obj.max_score * 100, 100))
        else:
            score_obj.percentage = 0

    def _rebalance_for_profile(self, scores: Dict[str, QualityScore], profile: str) -> None:
        if profile == "canvas-game":
            return

        canvas_only_checks = {"Canvas元素", "Canvas 2D上下文", "游戏循环", "游戏类定义"}
        completeness = scores["completeness"]
        for check in completeness.checks:
            if check["name"] in canvas_only_checks and not check.get("passed"):
                check["passed"] = True
                check["points"] = check.get("max_points", 0)
        completeness.score = sum(check.get("points", 0) for check in completeness.checks)
        completeness.recommendations = [
            rec for rec in completeness.recommendations
            if not any(name in rec for name in canvas_only_checks)
        ]
        completeness.checks.append({
            "name": f"按 {profile} 模式放宽 Canvas 专属要求",
            "passed": True,
            "points": 0,
            "max_points": 0,
        })
        self._refresh_quality_score(completeness)

        performance = scores["performance"]
        restored_points = 0
        for check in performance.checks:
            if check.get("name") == "建议使用requestAnimationFrame" and not check.get("passed", True):
                check["passed"] = True
                restored_points += 10
        if restored_points:
            performance.score = min(performance.max_score, performance.score + restored_points)
            performance.recommendations = [
                rec for rec in performance.recommendations
                if "requestAnimationFrame" not in rec
            ]
            performance.checks.append({
                "name": f"按 {profile} 模式取消 requestAnimationFrame 强制要求",
                "passed": True,
            })
            self._refresh_quality_score(performance)

    def _apply_validation_feedback(
        self,
        scores: Dict[str, QualityScore],
        validation_result: Optional[Dict[str, Any]],
    ) -> None:
        if not validation_result:
            return

        errors = validation_result.get("errors", []) or []
        warnings = validation_result.get("warnings", []) or []
        signals = validation_result.get("signals", {}) or {}
        penalty = min(45, len(errors) * 8 + len(warnings) * 2)

        correctness = scores["correctness"]
        if penalty:
            correctness.score = max(0, correctness.score - penalty)
            correctness.checks.append({
                "name": "结构化校验结果",
                "passed": not errors,
                "severity": "error" if errors else "warning",
                "penalty": penalty,
                "error_count": len(errors),
                "warning_count": len(warnings),
            })
            correctness.recommendations.insert(
                0,
                "结构化校验: " + ("; ".join(errors[:3]) if errors else "; ".join(warnings[:3]))
            )
            self._refresh_quality_score(correctness)

        if signals.get("js_syntax_valid") is False:
            completeness = scores["completeness"]
            completeness.score = max(0, completeness.score - 10)
            completeness.checks.append({
                "name": "JS 语法检查",
                "passed": False,
                "points": 0,
                "max_points": 10,
            })
            completeness.recommendations.insert(0, "缺少可通过的 JS 语法检查")
            self._refresh_quality_score(completeness)

    def _score_completeness(self, code: str) -> QualityScore:
        """Check for required components in the code."""
        checks = []
        score = 0
        max_score = 0

        # Required components for web games
        required_checks = [
            (r'<!DOCTYPE\s+html', "DOCTYPE声明", 10),
            (r'<canvas[^>]*>', "Canvas元素", 15),
            (r'getContext\s*\(\s*["\']2d["\']\s*\)', "Canvas 2D上下文", 15),
            (r'requestAnimationFrame|gameLoop|setInterval', "游戏循环", 15),
            (r'window\.onload|DOMContentLoaded|addEventListener\s*\(\s*["\']load["\']', "初始化代码", 15),
            (r'addEventListener\s*\(\s*["\'](?:keydown|keyup|click|touch)', "事件监听", 10),
            (r'class\s+\w+', "游戏类定义", 10),
            (r'<style>|<style\s', "CSS样式", 5),
            (r'</html>', "HTML正确闭合", 5),
        ]

        for pattern, name, points in required_checks:
            max_score += points
            passed = bool(re.search(pattern, code, re.IGNORECASE))
            if passed:
                score += points
            checks.append({
                "name": name,
                "passed": passed,
                "points": points if passed else 0,
                "max_points": points
            })

        recommendations = []
        for check in checks:
            if not check["passed"]:
                recommendations.append(f"缺少 {check['name']}")

        return QualityScore(
            score=score,
            max_score=max_score,
            percentage=(score / max_score * 100) if max_score > 0 else 0,
            checks=checks,
            recommendations=recommendations
        )

    def _score_correctness(self, code: str) -> QualityScore:
        """Check for common errors and anti-patterns."""
        checks = []
        score = 100  # Start with 100 and deduct for errors
        penalties = []

        # Extract JavaScript code
        js_match = re.search(r'<script[^>]*>([\s\S]*?)</script>', code)
        js_code = js_match.group(1) if js_match else ""

        # Error patterns with penalty points
        error_patterns = [
            # Critical errors
            (r'function\s+\w+\s*\([^)]*\)\s*\{\s*\}', "空函数体", 25, True),
            (r'\w+\s*\([^)]*\)\s*\{\s*/\*.*?\*/\s*\}', "只有注释的函数", 25, True),
            (r'//\s*TODO|//\s*FIXME|//\s*待实现', "TODO占位符", 20, True),
            (r'\.\.\.(?:\s|$|")', "省略号占位符", 20, True),
            (r'<script\s+src=["\'][^"\']+\.js["\']', "外部JS引用", 30, True),
            (r'<link[^>]+href=["\'][^"\']+\.css["\']', "外部CSS引用", 20, True),

            # Check for duplicate class definitions
            (None, "重复类定义", 25, True),  # Special handling

            # Warnings (less severe)
            (r'var\s+\w+\s*=', "使用var声明", 5, False),
            (r'==\s*[^=]|[^=]\s*==', "使用==而非===", 5, False),
        ]

        # Check standard patterns
        for pattern, name, penalty, is_error in error_patterns:
            if pattern is None:
                continue  # Skip special handling cases

            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                actual_penalty = penalty * min(len(matches), 3)  # Cap at 3x
                score -= actual_penalty
                checks.append({
                    "name": name,
                    "passed": False,
                    "severity": "error" if is_error else "warning",
                    "count": len(matches),
                    "penalty": actual_penalty
                })
                penalties.append(f"{name}: -{actual_penalty}分 ({len(matches)}处)")
            else:
                checks.append({
                    "name": name,
                    "passed": True,
                    "severity": "error" if is_error else "warning"
                })

        # Check for duplicate class definitions
        class_defs = re.findall(r'\bclass\s+(\w+)', js_code)
        class_counts = {}
        for cls in class_defs:
            class_counts[cls] = class_counts.get(cls, 0) + 1

        for cls, count in class_counts.items():
            if count > 1:
                penalty = 25 * (count - 1)
                score -= penalty
                checks.append({
                    "name": f"类 {cls} 重复定义",
                    "passed": False,
                    "severity": "error",
                    "count": count,
                    "penalty": penalty
                })
                penalties.append(f"类 {cls} 重复定义: -{penalty}分")

        # Check for undefined class usage
        defined_classes = set(class_defs)
        used_classes = set(re.findall(r'\bnew\s+(\w+)\s*\(', js_code))
        builtin_classes = {
            'Object', 'Array', 'String', 'Number', 'Boolean', 'Function',
            'Date', 'RegExp', 'Error', 'Map', 'Set', 'Promise', 'Image',
            'Audio', 'XMLHttpRequest', 'WebSocket', 'JSON', 'Math', 'Intl',
            'Proxy', 'Reflect', 'Animation', 'CanvasGradient', 'CanvasPattern',
            'Path2D', 'BigInt', 'ArrayBuffer', 'DataView', 'Int8Array',
            'Uint8Array', 'Uint8ClampedArray', 'Int16Array', 'Uint16Array',
            'Int32Array', 'Uint32Array', 'Float32Array', 'Float64Array'
        }
        undefined_classes = used_classes - defined_classes - builtin_classes

        if undefined_classes:
            penalty = 15 * len(undefined_classes)
            score -= penalty
            checks.append({
                "name": f"使用未定义的类: {undefined_classes}",
                "passed": False,
                "severity": "error",
                "penalty": penalty
            })
            penalties.append(f"未定义的类 {undefined_classes}: -{penalty}分")

        # Check for initialization
        has_class = bool(defined_classes)
        has_init = bool(re.search(r'window\.onload|DOMContentLoaded|new\s+\w+\s*\(\)', js_code))

        if has_class and not has_init:
            score -= 20
            checks.append({
                "name": "缺少初始化代码",
                "passed": False,
                "severity": "error",
                "penalty": 20
            })
            penalties.append("缺少初始化代码: -20分")

        score = max(0, score)  # Ensure non-negative

        return QualityScore(
            score=score,
            max_score=100,
            percentage=score,
            checks=checks,
            recommendations=penalties
        )

    def _score_maintainability(self, code: str) -> QualityScore:
        """Check code maintainability and structure."""
        checks = []
        score = 0
        max_score = 100

        # Extract JavaScript code
        js_match = re.search(r'<script[^>]*>([\s\S]*?)</script>', code)
        js_code = js_match.group(1) if js_match else ""

        # Good practices
        good_patterns = [
            (r'class\s+\w+\s*\{', "使用类封装", 20),
            (r'constructor\s*\(', "有构造函数", 15),
            (r'this\.\w+\s*=', "实例状态管理", 15),
            (r'function\s+\w+|=>\s*\{', "函数定义", 10),
            (r'const\s+\w+|let\s+\w+', "使用const/let", 10),
            (r'//.*|/\*[\s\S]*?\*/', "有注释", 10),
        ]

        for pattern, name, points in good_patterns:
            if re.search(pattern, js_code):
                score += points
                checks.append({"name": name, "passed": True, "points": points})
            else:
                checks.append({"name": name, "passed": False, "points": 0})

        # Check code length (reasonable size)
        lines = code.split('\n')
        if 50 <= len(lines) <= 500:
            score += 10
            checks.append({"name": "代码长度适中", "passed": True, "points": 10})
        elif len(lines) < 50:
            checks.append({"name": "代码可能过于简短", "passed": False, "points": 0})
        else:
            checks.append({"name": "代码可能过于冗长", "passed": False, "points": 0})

        # Check indentation consistency
        if re.search(r'^\s{2,4}\S', code, re.MULTILINE):
            score += 10
            checks.append({"name": "有一致的缩进", "passed": True, "points": 10})

        recommendations = []
        for check in checks:
            if not check.get("passed", True):
                recommendations.append(f"建议: {check['name']}")

        return QualityScore(
            score=min(score, max_score),
            max_score=max_score,
            percentage=min(score / max_score * 100, 100),
            checks=checks,
            recommendations=recommendations
        )

    def _score_performance(self, code: str) -> QualityScore:
        """Check for potential performance issues."""
        checks = []
        score = 100

        # Extract JavaScript code
        js_match = re.search(r'<script[^>]*>([\s\S]*?)</script>', code)
        js_code = js_match.group(1) if js_match else ""

        # Performance anti-patterns
        perf_issues = [
            (r'document\.querySelector|document\.getElementById(?=.*requestAnimationFrame|.*gameLoop)',
             "在游戏循环中查询DOM", 15),
            (r'new\s+Image\s*\(\)(?=.*requestAnimationFrame|.*gameLoop)',
             "在游戏循环中创建图片", 15),
            (r'\.bind\s*\((?=\s*\)(?=.*requestAnimationFrame|.*gameLoop))',
             "在游戏循环中使用bind", 10),
            (r'JSON\.parse\s*\((?=.*requestAnimationFrame|.*gameLoop)',
             "在游戏循环中解析JSON", 10),
        ]

        # Check if using requestAnimationFrame (good)
        if re.search(r'requestAnimationFrame', js_code):
            checks.append({"name": "使用requestAnimationFrame", "passed": True})
        else:
            score -= 10
            checks.append({"name": "建议使用requestAnimationFrame", "passed": False})

        # Check for potential issues
        for pattern, name, penalty in perf_issues:
            if re.search(pattern, js_code, re.DOTALL):
                score -= penalty
                checks.append({"name": name, "passed": False, "penalty": penalty})

        score = max(0, score)

        recommendations = []
        for check in checks:
            if not check.get("passed", True):
                recommendations.append(f"性能: {check['name']}")

        return QualityScore(
            score=score,
            max_score=100,
            percentage=score,
            checks=checks,
            recommendations=recommendations
        )

    def _score_ux(self, code: str, requirements: str = "") -> Dict[str, Any]:
        """Check user experience quality."""
        checks = []
        score = 0
        max_score = 100

        # UX indicators
        ux_patterns = [
            (r'id=["\']score["\']|class=["\']score["\']|得分|分数', "分数显示", 20),
            (r'gameOver|game.*over|游戏结束', "游戏结束状态", 20),
            (r'restart|重新开始|restartGame', "重新开始功能", 20),
            (r'addEventListener\s*\(\s*["\'](?:keydown|touch)', "输入响应", 15),
            (r'font-size|fontSize', "字体样式", 5),
            (r'color:|background:', "颜色样式", 5),
            (r'text-align|center|居中', "布局对齐", 5),
        ]

        for pattern, name, points in ux_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                score += points
                checks.append({"name": name, "passed": True, "points": points})
            else:
                checks.append({"name": name, "passed": False, "points": 0})

        # Check for responsive design
        if re.search(r'viewport|width.*%|max-width', code, re.IGNORECASE):
            score += 10
            checks.append({"name": "响应式设计", "passed": True, "points": 10})

        recommendations = []
        for check in checks:
            if not check.get("passed", True):
                recommendations.append(f"UX: 建议添加 {check['name']}")

        return QualityScore(
            score=min(score, max_score),
            max_score=max_score,
            percentage=min(score / max_score * 100, 100),
            checks=checks,
            recommendations=recommendations
        )

    def _get_grade(self, score: float) -> str:
        """Determine grade based on score."""
        if score >= self.GRADE_THRESHOLDS["A"]:
            return "A"
        elif score >= self.GRADE_THRESHOLDS["B"]:
            return "B"
        elif score >= self.GRADE_THRESHOLDS["C"]:
            return "C"
        elif score >= self.GRADE_THRESHOLDS["D"]:
            return "D"
        else:
            return "F"

    def quick_check(self, code: str) -> Dict[str, Any]:
        """Perform a quick quality check for immediate feedback.

        Args:
            code: The code to check

        Returns:
            Quick assessment with pass/fail and top issues
        """
        critical_issues = []

        # Check for critical issues
        if re.search(r'function\s+\w+\s*\([^)]*\)\s*\{\s*\}', code):
            critical_issues.append("有空函数体")

        if re.search(r'//\s*TODO|//\s*待实现|\.\.\.(?:\s|$)', code):
            critical_issues.append("有占位符代码")

        if re.search(r'<script\s+src=["\']', code):
            critical_issues.append("有外部JS引用")

        # Check for game essentials
        has_canvas = bool(re.search(r'<canvas', code, re.IGNORECASE))
        has_game_loop = bool(re.search(r'requestAnimationFrame|gameLoop', code))
        has_init = bool(re.search(r'window\.onload|DOMContentLoaded|new\s+\w+\s*\(\)', code))

        missing_essentials = []
        if has_canvas and not has_game_loop:
            missing_essentials.append("游戏循环")
        if re.search(r'class\s+\w+', code) and not has_init:
            missing_essentials.append("初始化代码")

        passed = len(critical_issues) == 0 and len(missing_essentials) == 0

        return {
            "passed": passed,
            "critical_issues": critical_issues,
            "missing_essentials": missing_essentials,
            "message": "代码检查通过" if passed else "发现需要修复的问题"
        }


# Global instance
quality_scorer = QualityScorer()
