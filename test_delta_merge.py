#!/usr/bin/env python3
"""
测试 Delta Spec 完整合并流程
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.schemas import DeltaSpec, DeltaOperation
from app.services.specs_merger import SpecsMerger
from datetime import datetime


def test_full_merge():
    """测试完整的 Delta 合并流程"""
    print("\n" + "="*70)
    print("🧪 Delta Spec 完整合并流程测试")
    print("="*70)
    
    # 娡拟初始规范
    base_specs = """## Purpose
开发一个简单的贪吃蛇游戏，玩家控制蛇吃食物变长。

## Requirements

### Requirement: 蛇的移动控制
系统 SHALL 允许玩家通过键盘方向键控制蛇移动。

#### Scenario: 向上移动
- **GIVEN** 游戏正在进行
- **WHEN** 玩家按上键
- **THEN** 蛇向上移动一格

#### Scenario: 向下移动
- **GIVEN** 游戏正在进行
- **WHEN** 玩家按上键
- **THEN** 蛇向下移动一格

### Requirement: 環撞检测
系统 SHALL 在蛇碰到边界或自身时结束游戏。

#### Scenario: 撞墙结束
- **GIVEN** 蛇头接近边界
- **WHEN** 蛇头超出边界
- **THEN** 显示游戏结束界面

### Requirement: 食物生成
系统 SHALL 在随机位置生成食物供蛇吃。

#### Scenario: 生成新食物
- **GIVEN** 蛇吃到食物
- **WHEN** 食物被吃掉
- **THEN** 在新的随机位置生成食物
"""
    
    print("\n[初始规范]")
    print(f"- 需求数量: 3")
    print(f- 规范长度: {len(base_specs)} 字符")
    
    # 准备 Delta Spec 列表
    deltas = [
        # Delta 1: ADDED - 新增音效系统
        DeltaSpec(
            spec_name="音效系统",
            operation=DeltaOperation.ADDED,
            description="新增游戏音效功能",
            created_at=datetime.now()
        ),
        # Delta 2: MODIFIED - 修改食物生成（添加音效触发）
        DeltaSpec(
            spec_name="食物生成",
            operation=DeltaOperation.MODIFIED,
            description="吃食物时播放音效",
            created_at=datetime.now()
        )
    ]
    
    print(f"\n[Delta Spec 列表]")
    print(f"- Delta 数量: {len(deltas)}")
    for i, d in enumerate(deltas, 1):
        print(f"  {i}. {d.operation.value}: {d.spec_name}")
    
    # 执行合并
    print(f"\n[执行合并]")
    merger = SpecsMerger()
    
    try:
        merged_specs = merger.merge_deltas(base_specs, deltas)
        
        print(f"\n✅ 合并成功!")
        print(f"   - 合并前: {len(base_specs)} 字符")
        print(f"   - 合并后: {len(merged_specs)} 字符")
        print(f"   - 差异: {len(merged_specs) - len(base_specs)} 字符")
        
        # 验证合并结果
        print(f"\n[验证合并结果]")
        
        # 检查新增的需求
        if "音效系统" in merged_specs:
            print(f"✅ 新增需求 '音效系统' 已添加")
        else:
            print(f"❌ 新增需求 '音效系统' 未找到")
            raise Exception("合并验证失败：音效系统未添加")
        
        # 检查原有的需求是否还在
        if "蛇的移动控制" in merged_specs:
            print(f"✅ 原有需求 '蛇的移动控制' 保留")
        else:
            print(f"❌ 原有需求 '蛇的移动控制' 丢失")
            raise Exception("合并验证失败：原有需求丢失")
        
        # 显示合并后的规范
        print(f"\n[合并后的规范预览]")
        print("-" * 70)
        print(merged_specs[:600])
        if len(merged_specs) > 600:
            print(f"\n... (还有 {len(merged_specs) - 600} 字符)")
        print("-" * 70)
        
        print(f"\n" + "="*70)
        print("🎉 完整合并流程测试通过!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 合并失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_merge()
    sys.exit(0 if success else 1)
