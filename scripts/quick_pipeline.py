#!/usr/bin/env python3
"""
快速创建 Pipeline - 跳过讨论，直接开发

使用方法:
    python quick_pipeline.py "开发球球作战游戏"
    python quick_pipeline.py "开发登录功能" --target ts-app
"""

import sys
import json
import argparse
import requests
from datetime import datetime


def create_quick_pipeline(request: str, target: str = "web-app"):
    """创建快速 Pipeline"""
    
    print("🚀 快速模式 Pipeline")
    print("━" * 70)
    print()
    print(f"📝 需求: {request}")
    print(f"🎯 输出: {target}")
    print(f"⚡ 模式: 快速（跳过讨论）")
    print()
    print("流程: 需求 → 计划 → 编码 → 测试 → 修复 → 完成")
    print()
    print("━" * 70)
    print()
    
    # 构造请求
    payload = {
        "request": request,
        "target_output": target,
        "skip_discussion": True,  # 关键：跳过讨论
        "selected_agent_ids": []  # 空 = 自动选择
    }
    
    # 发送请求
    try:
        response = requests.post(
            "http://localhost:8000/api/pipeline/start",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Pipeline 创建成功！")
            print()
            print(f"📋 Plan ID: {result.get('plan_id', 'N/A')}")
            print(f"📊 状态: {result.get('status', 'N/A')}")
            print()
            print("━" * 70)
            print()
            print("🌐 访问地址:")
            print(f"   本地: http://localhost:5173")
            print(f"   内网: http://192.168.0.46:5173")
            print(f"   Tailscale: http://100.67.202.43:5173")
            print()
            print("💡 提示:")
            print("   • 前端界面查看实时进度")
            print("   • 测试会自动执行")
            print("   • 有问题会自动修复")
            print()
            
            return result
        else:
            print(f"❌ 创建失败: {response.status_code}")
            print(f"   {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("   请确保 Backend 正在运行:")
        print("   cd ~/AITeam/backend && python -m app.main")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="快速创建 Pipeline（跳过讨论）"
    )
    parser.add_argument(
        "request",
        help="需求描述"
    )
    parser.add_argument(
        "--target",
        default="web-app",
        choices=["web-app", "ts-app", "godot-game"],
        help="输出类型（默认: web-app）"
    )
    
    args = parser.parse_args()
    
    create_quick_pipeline(args.request, args.target)


if __name__ == "__main__":
    main()
