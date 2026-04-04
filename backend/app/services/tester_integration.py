"""
在 Pipeline 中集成测试框架的修改方案

这个文件展示了如何修改 Coordinator 的 execute_plan 方法，
在 Coder 完成后自动触发 Tester，并根据测试结果决定是否需要修复。
"""

# 在 app/services/coordinator.py 中添加以下代码

# === 1. 导入测试框架 ===
from app.services.tester_framework import tester_framework, TestReport

# === 2. 在 execute_plan 方法中添加测试阶段 ===

async def execute_plan(self, plan_id: str) -> str:
    """
    执行计划，包含测试阶段
    
    流程：
    1. 编码阶段（Coder）
    2. 测试阶段（Tester）← 新增
    3. 修复阶段（如果测试不通过）← 新增
    """
    plan = self.plans.get(plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")

    plan.status = PlanStatus.EXECUTING
    self._save_plans()

    # ... 现有的编码逻辑 ...

    # ===== 新增：测试阶段 =====
    max_test_iterations = 2  # 最多测试 2 轮
    test_iteration = 0

    while test_iteration < max_test_iterations:
        test_iteration += 1

        # 广播测试开始
        await self.broadcast({
            "type": "test_phase_started",
            "data": {
                "plan_id": plan_id,
                "iteration": test_iteration
            }
        })

        # 执行测试
        test_report = await self._execute_test_phase(plan_id)

        # 广播测试结果
        await self.broadcast({
            "type": "test_phase_completed",
            "data": {
                "plan_id": plan_id,
                "passed": test_report.overall_passed,
                "score": test_report.quality_score.total,
                "grade": test_report.quality_score.grade
            }
        })

        # 判断是否通过
        if test_report.overall_passed:
            # 测试通过，结束
            print(f"[Coordinator] 测试通过 - 分数: {test_report.quality_score.total:.1f}")
            break
        else:
            # 测试不通过，触发修复
            if test_iteration < max_test_iterations:
                print(f"[Coordinator] 测试未通过，触发修复 (迭代 {test_iteration}/{max_test_iterations})")

                # 广播修复开始
                await self.broadcast({
                    "type": "fix_phase_started",
                    "data": {
                        "plan_id": plan_id,
                        "iteration": test_iteration
                    }
                })

                # 执行修复
                await self._execute_fix_phase(plan_id, test_report)

                # 修复完成，重新测试
                continue
            else:
                # 达到最大测试轮次，仍然不通过
                print(f"[Coordinator] 达到最大测试轮次，测试仍未通过")
                # 可以选择：1. 继续交付（带风险提示） 2. 终止流程
                # 这里选择继续交付，但标记为"测试未通过"
                plan.metadata = plan.metadata or {}
                plan.metadata["test_failed"] = True
                plan.metadata["test_score"] = test_report.quality_score.total
                break

    # ... 现有的完成逻辑 ...


async def _execute_test_phase(self, plan_id: str) -> TestReport:
    """
    执行测试阶段

    Returns:
        TestReport: 完整的测试报告
    """
    plan = self.plans.get(plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")

    # 1. 获取代码输出
    if plan.target_output == "web-app":
        code = output_manager.read_existing_code(plan_id)
        test_url = f"http://localhost:8000/output/{plan_id}/index.html"
    elif plan.target_output == "ts-app":
        code = output_manager.read_existing_ts_code(plan_id)
        test_url = f"http://localhost:8000/output/{plan_id}/index.html"
    else:
        # 其他类型的输出，暂时跳过测试
        return TestReport(
            plan_id=plan_id,
            timestamp=datetime.now(),
            overall_passed=True,
            quality_score=QualityScore(
                total=100,
                correctness=100,
                completeness=100,
                robustness=100,
                performance=100,
                passed=True,
                grade="A+ (跳过测试)"
            ),
            static_issues=[],
            test_results=[],
            recommendations=["此类型输出暂不支持自动化测试"]
        )

    if not code:
        # 没有代码，测试失败
        return TestReport(
            plan_id=plan_id,
            timestamp=datetime.now(),
            overall_passed=False,
            quality_score=QualityScore(
                total=0,
                correctness=0,
                completeness=0,
                robustness=0,
                performance=0,
                passed=False,
                grade="D (无代码输出)"
            ),
            static_issues=[],
            test_results=[],
            recommendations=["未找到代码输出"]
        )

    # 2. 执行完整测试流程
    test_report = await tester_framework.run_full_test(
        plan_id=plan_id,
        code=code,
        test_url=test_url
    )

    # 3. 保存测试报告
    await self._save_test_report(plan_id, test_report)

    return test_report


async def _execute_fix_phase(self, plan_id: str, test_report: TestReport):
    """
    执行修复阶段

    根据测试报告的问题，让 Coder Agent 修复代码
    """
    plan = self.plans.get(plan_id)
    if not plan:
        return

    # 1. 生成修复任务描述
    fix_description = self._generate_fix_description(test_report)

    # 2. 找到 Coder Agent
    coder_agents = [
        agent for agent in agent_manager.get_all_agents()
        if agent.type.value in ["coder", "pua-coder"]
    ]

    if not coder_agents:
        print("[Coordinator] 没有找到 Coder Agent，无法修复")
        return

    coder = coder_agents[0]  # 使用第一个 Coder

    # 3. 广播修复开始
    await self.add_discussion_message(
        plan_id=plan_id,
        agent_id="system",
        agent_name="系统",
        agent_type="assistant",
        content=f"🔧 测试发现问题，触发自动修复 (分数: {test_report.quality_score.total:.1f}/100)",
        message_type="comment"
    )

    # 4. 执行修复任务
    fix_task = f"""修复测试发现的问题

**测试分数**: {test_report.quality_score.total:.1f}/100 ({test_report.quality_score.grade})

**发现的问题**:
{self._format_issues_for_fix(test_report.static_issues)}

**失败的测试用例**:
{self._format_failed_tests_for_fix(test_report.test_results)}

**改进建议**:
{chr(10).join(f'- {rec}' for rec in test_report.recommendations)}

请根据以上测试报告修复代码，确保所有严重问题都得到解决，测试用例能够通过。
"""

    # 执行修复
    coder.update_status(AgentStatus.WORKING)

    try:
        # 获取现有代码
        existing_code = output_manager.read_existing_code(plan_id)

        # 调用 Coder 修复
        full_response = ""
        async for update in coder.execute_task(
            fix_task,
            existing_code=existing_code,
            incremental_mode=True,
            target_output=plan.target_output
        ):
            full_response += update

            # 广播修复进度
            await self.broadcast({
                "type": "fix_progress",
                "data": {
                    "plan_id": plan_id,
                    "agent_id": coder.id,
                    "content": update
                }
            })

        # 保存修复后的代码
        if plan.target_output == "web-app":
            output_manager.write_code_output(plan_id, full_response)
        elif plan.target_output == "ts-app":
            output_manager.write_ts_code_output(plan_id, full_response)

        # 广播修复完成
        await self.add_discussion_message(
            plan_id=plan_id,
            agent_id=coder.id,
            agent_name=coder.name,
            agent_type=coder.type.value,
            content=f"✅ 修复完成，等待重新测试",
            message_type="comment"
        )

    except Exception as e:
        print(f"[Coordinator] 修复失败: {e}")
        await self.add_discussion_message(
            plan_id=plan_id,
            agent_id=coder.id,
            agent_name=coder.name,
            agent_type=coder.type.value,
            content=f"❌ 修复失败: {str(e)}",
            message_type="comment"
        )

    finally:
        coder.update_status(AgentStatus.IDLE)


def _generate_fix_description(self, test_report: TestReport) -> str:
    """生成修复描述"""
    desc = f"""测试报告摘要：

**总体得分**: {test_report.quality_score.total:.1f}/100
**通过状态**: {'✅ 通过' if test_report.overall_passed else '❌ 未通过'}

**发现的问题**:
"""
    for issue in test_report.static_issues:
        severity_emoji = {
            "critical": "🔴",
            "medium": "🟡",
            "minor": "🟢"
        }.get(issue.severity.value, "⚪")
        desc += f"{severity_emoji} {issue.message}\n"
        if issue.suggestion:
            desc += f"   建议: {issue.suggestion}\n"

    return desc


def _format_issues_for_fix(self, issues: list) -> str:
    """格式化问题列表用于修复"""
    if not issues:
        return "无问题"

    formatted = []
    for issue in issues:
        formatted.append(f"- [{issue.severity.value}] {issue.message}")
        if issue.suggestion:
            formatted.append(f"  修复建议: {issue.suggestion}")

    return "\n".join(formatted)


def _format_failed_tests_for_fix(self, results: list) -> str:
    """格式化失败的测试用例"""
    failed = [r for r in results if not r.passed]

    if not failed:
        return "所有测试用例通过"

    formatted = []
    for result in failed:
        formatted.append(f"- {result.test_name}")
        if result.error_message:
            formatted.append(f"  错误: {result.error_message}")

    return "\n".join(formatted)


async def _save_test_report(self, plan_id: str, report: TestReport):
    """保存测试报告"""
    import json
    from pathlib import Path

    # 创建报告目录
    report_dir = Path(f"data/test_reports/{plan_id}")
    report_dir.mkdir(parents=True, exist_ok=True)

    # 保存 JSON 格式
    report_data = {
        "plan_id": report.plan_id,
        "timestamp": report.timestamp.isoformat(),
        "overall_passed": report.overall_passed,
        "quality_score": {
            "total": report.quality_score.total,
            "correctness": report.quality_score.correctness,
            "completeness": report.quality_score.completeness,
            "robustness": report.quality_score.robustness,
            "performance": report.quality_score.performance,
            "passed": report.quality_score.passed,
            "grade": report.quality_score.grade
        },
        "static_issues": [
            {
                "type": issue.type,
                "severity": issue.severity.value,
                "message": issue.message,
                "suggestion": issue.suggestion
            }
            for issue in report.static_issues
        ],
        "test_results": [
            {
                "test_name": result.test_name,
                "passed": result.passed,
                "duration": result.duration,
                "error_message": result.error_message
            }
            for result in report.test_results
        ],
        "recommendations": report.recommendations
    }

    report_file = report_dir / "test_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    # 保存 Markdown 格式
    md_report = tester_framework.format_report(report)
    md_file = report_dir / "test_report.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_report)

    print(f"[Coordinator] 测试报告已保存: {report_dir}")


# === 3. 修改 broadcast 方法，添加测试相关消息 ===

# 在 broadcast 方法中添加测试相关的消息类型：
# - test_phase_started: 测试阶段开始
# - test_phase_completed: 测试阶段完成
# - fix_phase_started: 修复阶段开始
# - fix_progress: 修复进度
# - fix_phase_completed: 修复阶段完成


# === 4. 在 WebSocket 处理中添加测试相关事件 ===

# 在 app/api/ws.py 中添加：

async def handle_test_events(websocket: WebSocket, data: dict):
    """处理测试相关事件"""

    event_type = data.get("type")

    if event_type == "request_test":
        # 手动触发测试
        plan_id = data.get("plan_id")
        test_report = await coordinator._execute_test_phase(plan_id)

        await websocket.send_json({
            "type": "test_completed",
            "data": {
                "plan_id": plan_id,
                "passed": test_report.overall_passed,
                "score": test_report.quality_score.total,
                "report": tester_framework.format_report(test_report)
            }
        })

    elif event_type == "get_test_report":
        # 获取测试报告
        plan_id = data.get("plan_id")
        report_file = Path(f"data/test_reports/{plan_id}/test_report.md")

        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                report_md = f.read()

            await websocket.send_json({
                "type": "test_report",
                "data": {
                    "plan_id": plan_id,
                    "report": report_md
                }
            })
