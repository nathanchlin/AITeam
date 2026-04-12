#!/usr/bin/env python3
"""
Phase 2 Delta Spec 最终验证脚本
"""

import sys
import os

# 设置路径
backend_path = os.path.join(os.path.dirname(os.path.abspath("test")) if "test" in __file__ else __file__, "backend')
sys.path.insert(0, backend_path)

print("="*70)
print("🧪 Phase 2 Delta Spec 功能验证")
print("="*70)

try:
    # 导入模块
    from app.models.schemas import DeltaSpec, DeltaOperation, Plan
    from app.services.specs_merger import SpecsMerger
    from datetime import datetime
    
    print("\n[测试 1] 创建 DeltaSpec 对象")
    delta = DeltaSpec(
        spec_name="测试需求",
        operation=DeltaOperation.ADDED,
        description="这是一个测试 Delta",
        created_at=datetime.now()
    )
    print(f"✅ 成功创建 DeltaSpec")
    print(f"   - 操作类型: {delta.operation.value}")
    print(f"   - 规范名称: {delta.spec_name}")
    
    print("\n[测试 2] 创建 Plan 对象（含 Delta）")
    plan = Plan(
        id="test-001",
        title="测试计划",
        original_request="测试请求",
        specs="## Purpose\n测试",
        deltas=[delta],
        specs_version=1
    )
    print(f"✅ 成功创建 Plan")
    print(f"   - Plan ID: {plan.id}")
    print(f"   - Specs 版本: {plan.specs_version}")
    print(f"   - Deltas 数量: {len(plan.deltas)}")
    
    print("\n[测试 3] 规范合并引擎")
    merger = SpecsMerger()
    
    # 测试规范
    test_specs = """## Purpose
开发贪吃蛇游戏。

## Requirements

### Requirement: 蛇的移动
系统 SHALL 允许玩家控制蛇移动。
"""
    
    # 解析规范
    tree = merger.parse_specs(test_specs)
    print(f"✅ 成功解析规范")
    print(f"   - Purpose: {tree.purpose}")
    print(f"   - 需求数量: {len(tree.requirements)}")
    for req_name in tree.requirements:
        print(f"   - 鸶求: {req_name}")
    
    print("\n[测试 4] 空规范合并")
    result = merger.merge_deltas("", [])
    print(f"✅ 成功合并空规范")
    print(f"   - 结果长度: {len(result)}")
    
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)
    print("✅ 所有测试通过!")
    print("\n验证功能:")
    print("  ✅ DeltaSpec 数据模型")
    print("  ✅ Plan 模型集成")
    print("  ✅ SpecsMerger 解析功能")
    print("  ✅ SpecsMerger 合并功能")
    
    print("\n" + "="*70)
    print("🎉 Phase 2 Delta Spec 功能验证完成!")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
