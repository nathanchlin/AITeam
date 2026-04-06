"""Godot 项目导出服务"""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import Optional


def export_godot_project(
    plan_id: str,
    output_dir: str = "/Users/lincheng/AITeam/backend/output"
) -> Optional[str]:
    """导出 Godot 项目为 ZIP 文件
    
    Args:
        plan_id: Pipeline 计划 ID
        output_dir: 输出目录
    
    Returns:
        ZIP 文件路径，如果失败返回 None
    """
    
    project_dir = os.path.join(output_dir, plan_id, "godot_project")
    
    if not os.path.exists(project_dir):
        print(f"[GodotExport] 项目目录不存在: {project_dir}")
        return None
    
    # 检查是否有 project.godot 文件
    project_file = os.path.join(project_dir, "project.godot")
    if not os.path.exists(project_file):
        print(f"[GodotExport] 不是有效的 Godot 项目")
        return None
    
    # 创建 ZIP 文件
    zip_path = os.path.join(output_dir, plan_id, f"godot_project_{plan_id[:8]}.zip")
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 保持相对路径
                    arcname = os.path.relpath(file_path, project_dir)
                    zipf.write(file_path, arcname)
        
        print(f"[GodotExport] 成功导出: {zip_path}")
        return zip_path
        
    except Exception as e:
        print(f"[GodotExport] 导出失败: {e}")
        return None


def get_godot_project_files(plan_id: str, output_dir: str = "/Users/lincheng/AITeam/backend/output") -> dict:
    """获取 Godot 项目的文件列表和统计信息
    
    Args:
        plan_id: Pipeline 计划 ID
        output_dir: 输出目录
    
    Returns:
        {
            "exists": bool,
            "files": [文件列表],
            "stats": {
                "total_files": int,
                "total_size": int,
                "file_types": {".gd": count, ...}
            },
            "zip_path": str (如果已导出)
        }
    """
    
    project_dir = os.path.join(output_dir, plan_id, "godot_project")
    
    result = {
        "exists": False,
        "files": [],
        "stats": {
            "total_files": 0,
            "total_size": 0,
            "file_types": {}
        },
        "zip_path": None
    }
    
    if not os.path.exists(project_dir):
        return result
    
    result["exists"] = True
    
    # 收集文件信息
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, project_dir)
            file_size = os.path.getsize(file_path)
            file_ext = Path(file).suffix
            
            result["files"].append({
                "path": rel_path,
                "size": file_size,
                "type": file_ext
            })
            
            result["stats"]["total_files"] += 1
            result["stats"]["total_size"] += file_size
            result["stats"]["file_types"][file_ext] = result["stats"]["file_types"].get(file_ext, 0) + 1
    
    # 检查是否已有 ZIP
    zip_path = os.path.join(output_dir, plan_id, f"godot_project_{plan_id[:8]}.zip")
    if os.path.exists(zip_path):
        result["zip_path"] = zip_path
        result["zip_size"] = os.path.getsize(zip_path)
    
    return result
