#!/usr/bin/env python3
"""
验证测试框架集成效果
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def verify_integration():
    """验证集成"""
    print("=" * 70)
    print("🔍 验证测试框架集成")
    print("=" * 70)
    print("")

    # 1. 检查文件存在
    print("1️⃣ 检查文件...")
    import os

    files = [
        "app/services/tester_framework.py",
        "app/services/tester_integration.py",
        "app/services/coordinator.py"
    ]

    for file in files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} 不存在")
            return False

    print("")

    # 2. 检查导入
    print("2️⃣ 检查导入...")
    try:
        from app.services.tester_framework import tester_framework, TestReport, QualityScore
        print("   ✅ tester_framework 模块导入成功")
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        return False

    print("")

    # 3. 检查方法存在
    print("3️⃣ 检查方法...")
    from app.services.coordinator import coordinator

    methods = [
        "_execute_test_phase",
        "_execute_fix_phase",
        "_format_issues_for_fix",
        "_format_failed_tests_for_fix",
        "_save_test_report"
    ]

    for method in methods:
        if hasattr(coordinator, method):
            print(f"   ✅ {method}")
        else:
            print(f"   ❌ {method} 不存在")
            return False

    print("")

    # 4. 测试静态分析器
    print("4️⃣ 测试静态分析器...")
    from app.services.tester_framework import StaticAnalyzer

    analyzer = StaticAnalyzer()

    # 测试代码
    test_code = """
class Game {
    constructor() {
        // TODO
    }

    update() {
    }

    render() {
        ctx.fillRect(0, 0, 100, 100);
    }
}
"""

    try:
        issues = await analyzer.analyze(test_code)
        print(f"   ✅ 静态分析成功，发现 {len(issues)} 个问题")

        for issue in issues[:3]:
            print(f"      • [{issue.severity.value}] {issue.message}")
    except Exception as e:
        print(f"   ❌ 静态分析失败: {e}")
        return False

    print("")

    # 5. 测试质量评分
    print("5️⃣ 测试质量评分...")
    from app.services.tester_framework import QualityScorer

    scorer = QualityScorer()
    score = scorer.calculate(issues, [])

    print(f"   ✅ 质量评分成功")
    print(f"      • 总分: {score.total:.1f}/100")
    print(f"      • 等级: {score.grade}")
    print(f"      • 通过: {'✅' if score.passed else '❌'}")

    print("")

    # 6. 测试报告生成
    print("6️⃣ 测试报告生成...")
    from app.services.tester_framework import TestReport
    from datetime import datetime

    report = TestReport(
        plan_id="test-verification",
        timestamp=datetime.now(),
        overall_passed=score.passed,
        quality_score=score,
        static_issues=issues,
        test_results=[],
        recommendations=["这是一个测试验证"]
    )

    md_report = tester_framework.format_report(report)

    print(f"   ✅ 报告生成成功 ({len(md_report)} 字符)")

    print("")

    # 7. 总结
    print("=" * 70)
    print("✅ 验证通过！测试框架集成成功")
    print("=" * 70)
    print("")

    print("📋 集成内容:")
    print("   • ✅ 测试框架服务")
    print("   • ✅ Coordinator 集成")
    print("   • ✅ 静态代码分析")
    print("   • ✅ 质量评分系统")
    print("   • ✅ 测试报告生成")
    print("")

    print("🚀 下一步:")
    print("   1. 重启 Backend:")
    print("      cd ~/AITeam/backend")
    print("      python -m app.main")
    print("")
    print("   2. 创建 Pipeline 测试:")
    print("      提交一个开发任务，观察测试阶段执行")
    print("")
    print("   3. 查看测试报告:")
    print("      检查 data/test_reports/ 目录")
    print("")

    return True


if __name__ == "__main__":
    import asyncio
    success = asyncio.run(verify_integration())
    sys.exit(0 if success else 1)
