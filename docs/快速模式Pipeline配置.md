# 快速模式 Pipeline 配置

## 概述
跳过讨论阶段，直接从计划到编码，测试驱动开发。

## 核心配置
- `skip_discussion: true` - 跳过讨论
- `max_test_iterations: 2` - 最多测试2轮
- `auto_fix: true` - 自动修复

## 使用方式
创建 Pipeline 时设置：
```json
{
  "request": "开发球球作战游戏",
  "target_output": "web-app",
  "skip_discussion": true,
  "selected_agent_ids": ["coder-1"]
}
```

## 流程对比

### 标准模式（慢）
需求 → 讨论 → 计划 → 编码 → 测试 → 完成
时间：~15-30分钟

### 快速模式（快）
需求 → 计划 → 编码 → 测试 → 修复 → 完成
时间：~5-10分钟

## 测试框架集成
- ✅ 静态代码分析
- ✅ 自动修复机制
- ✅ 质量评分
- ✅ 测试报告

有问题随时改，无需讨论！
