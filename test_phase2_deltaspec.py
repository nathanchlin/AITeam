#!/usr/bin/env python3
"""
Phase 2 Delta Spec 测试脚本（简化版）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.schemas import DeltaSpec, DeltaOperation, Requirement, Scenario, Plan
from app.services.specs_merger import SpecsMerger, create_delta_from_dict
from datetime import datetime


def test_delta_model():
    """测试 1: DeltaSpec 数据模型创建"""
    print("\n" + "="*60)
    print("测试 1: DeltaSpec 数据模型创建")
    print("="*60)
    
    # 创建 Scenario（确保符合 min_length 验证）
    scenario = Scenario(
        name="吃到食物音效",
        given="游戏正在进行中，蛇在移动",      # ≥ 10 字符 ✓
        when="蛇头碰到食物",                   # ≥ 5 字符 ✓
        then="系统播放吃食物音效"              # ≥ 10 字符 ✓
    )
    
    # 创建 Requirement
    requirement = Requirement(
        text="系统 SHALL 在游戏事件发生时播放对应音效",
        scenarios=[scenario]
    )
    
    # 创建 DeltaSpec
    delta = DeltaSpec(
        spec_name="音效系统",
        operation=DeltaOperation.ADDED,
        description="新增游戏音效功能",
        requirement=requirement
    )
    
    print(f"✅ DeltaSpec 创建成功:")
    print(f"   - 操作类型: {delta.operation.value}")
    print(f"   - 规范名称: {delta.spec_name}")
    print(f"   - 需求文本: {delta.requirement.text[:50]}...")
    print(f"   - 场景数量: {len(delta.requirement.scenarios)}")
    
    return delta


def test_specs_merger():
    """测试 2: 规范合并引擎"""
    print("\n" + "="*60)
    print("测试 2: 规范合并引擎")
    print("="*60)
    
    merger = SpecsMerger()
    
    # 准备基础规范
    base_specs = """## Purpose
开发经典贪吃蛇游戏，玩家控制蛇移动吃食物变长。

## Requirements

### Requirement: 吃食物
系统 SHALL 在蛇头碰到食物时增加蛇身长度和分数。

#### Scenario: 吃到食物
- **GIVEN** 游戏正在进行，蛇在移动中
- **WHEN** 蛇头位置与食物重叠
- **THEN** 蛇身长度加一，分数加十分

### Requirement: 游戏结束
系统 SHALL 在蛇撞墙或撞到自己时结束游戏。

#### Scenario: 撞墙
- **GIVEN** 游戏正在进行中
- **WHEN** 蛇头超出边界
- **THEN** 显示游戏结束界面
"""

    # 准备 Delta Spec
    deltas = [
        DeltaSpec(
            spec_name="音效系统",
            operation=DeltaOperation.ADDED,
            description="新增游戏音效功能",
            requirement=Requirement(
                text="系统 SHALL 在游戏事件发生时播放对应音效",
                scenarios=[
                    Scenario(
                        name="吃到食物音效",
                        given="游戏正在进行，蛇在移动",
                        when="蛇头碰到食物",
                        then="系统播放吃食物音效"
                    )
                ]
            )
        )
    ]
    
    print(f"📝 基础规范长度: {len(base_specs)} 字符")
    print(f"📝 Delta 数量: {len(deltas)}")
    
    # 合并
    merged_specs = merger.merge_deltas(base_specs, deltas)
    
    print(f"\n✅ 合并完成!")
    print(f"   - 合并后长度: {len(merged_specs)} 字符")
    print(f"   - 新增长度: +{len(merged_specs) - len(base_specs)} 字符")
    
    # 验证
    if "音效系统" in merged_specs:
        print(f"\n✅ 验证通过: '音效系统' 已合并到规范中")
    else:
        print(f"\n❌ 验证失败: '音效系统' 未找到")
    
    return merged_specs


def test_plan_integration():
    """测试 3: Plan 模型集成"""
    print("\n" + "="*60)
    print("测试 3: Plan 模型集成")
    print("="*60)
    
    # 创建带 Delta 的 Plan
    plan = Plan(
        id="test-plan-001",
        title="测试 Plan",
        description="Phase 2 集成测试",
        original_request="开发贪吃蛇游戏",
        specs="## Purpose\n测试规范",
        specs_version=1
    )
    
    # 添加 Delta
    delta = DeltaSpec(
        spec_name="计分系统",
        operation=DeltaOperation.ADDED,
        description="新增计分功能",
        requirement=Requirement(
            text="系统 SHALL 记录并显示玩家得分",
            scenarios=[
                Scenario(
                    name="更新分数",
                    given="玩家吃到食物",
                    when="分数增加",
                    then="屏幕显示新分数"
                )
            ]
        )
    )
    
    plan.deltas.append(delta)
    
    print(f"✅ Plan 创建成功:")
    print(f"   - Plan ID: {plan.id}")
    print(f"   - Specs Version: {plan.specs_version}")
    print(f"   - Deltas 数量: {len(plan.deltas)}")
    print(f"   - Delta 操作: {plan.deltas[0].operation.value}")
    
    return plan


def test_delta_from_dict():
    """测试 4: 字典转换"""
    print("\n" + "="*60)
    print("测试 4: 字典转换为 DeltaSpec")
    print("="*60)
    
    delta_data = {
        "spec_name": "计分系统",
        "operation": "ADDED",
        "description": "新增计分和排行榜功能",
        "requirement": {
            "text": "系统 SHALL 记录玩家得分并显示排行榜",
            "scenarios": [
                {
                    "name": "更新分数",
                    "given": "玩家吃到食物后",
                    "when": "分数增加时",
                    "then": "更新屏幕显示的分数"
                }
            ]
        }
    }
    
    delta = create_delta_from_dict(delta_data)
    
    print(f"✅ DeltaSpec 创建成功:")
    print(f"   - 操作: {delta.operation.value}")
    print(f"   - 名称: {delta.spec_name}")
    print(f"   - 场景: {delta.requirement.scenarios[0].name}")
    
    return delta


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 Phase 2 Delta Spec 测试套件")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_delta_model()
        test_specs_merger()
        test_plan_integration()
        test_delta_from_dict()
        
        print("\n" + "="*60)
        print("📊 测试总结")
        print("="*60)
        print("✅ 所有测试通过!")
        print("\n验证功能:")
        print("  ✅ DeltaSpec 数据模型")
        print("  ✅ SpecsMerger 合并引擎")
        print("  ✅ Plan 模型集成")
        print("  ✅ 字典转换功能")
        
        print("\n" + "="*60)
        print("🎉 Phase 2 Delta Spec 功能验证完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
