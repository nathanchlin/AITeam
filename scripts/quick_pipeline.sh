#!/bin/bash
# 快速创建 Pipeline - 跳过讨论，直接开发

# 检查参数
if [ -z "$1" ]; then
    echo "使用方法: ./quick_pipeline.sh \"需求描述\" [输出类型]"
    echo ""
    echo "示例:"
    echo "  ./quick_pipeline.sh \"开发球球作战游戏\""
    echo "  ./quick_pipeline.sh \"开发登录功能\" web-app"
    echo ""
    echo "输出类型:"
    echo "  - web-app (默认)"
    echo "  - ts-app"
    echo "  - godot-game"
    exit 1
fi

REQUEST="$1"
TARGET="${2:-web-app}"

echo "🚀 快速模式 Pipeline"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 需求: $REQUEST"
echo "🎯 输出: $TARGET"
echo "⚡ 模式: 快速（跳过讨论）"
echo ""
echo "流程: 需求 → 计划 → 编码 → 测试 → 修复 → 完成"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 发送请求
curl -X POST http://localhost:8000/api/pipeline/start \
  -H "Content-Type: application/json" \
  -d "{
    \"request\": \"$REQUEST\",
    \"target_output\": \"$TARGET\",
    \"skip_discussion\": true
  }" | python3 -m json.tool

echo ""
echo "✅ Pipeline 已创建！"
echo ""
echo "🌐 查看进度: http://localhost:5173"
echo ""
