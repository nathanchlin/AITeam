from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter(prefix="/projects", tags=["projects"])

OUTPUT_DIR = "output"


@router.get("/")
async def list_projects():
    """List all generated projects from output directory"""
    if not os.path.exists(OUTPUT_DIR):
        return {"projects": []}

    projects = []

    for plan_id_short in os.listdir(OUTPUT_DIR):
        project_dir = os.path.join(OUTPUT_DIR, plan_id_short)

        if not os.path.isdir(project_dir):
            continue

        # Check for index.html
        index_path = os.path.join(project_dir, "index.html")
        has_preview = os.path.exists(index_path)

        # Get file list (limited to top 10 files)
        files = []
        total_size = 0
        for f in os.listdir(project_dir):
            filepath = os.path.join(project_dir, f)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                total_size += size
                files.append({
                    "name": f,
                    "size": size,
                    "modified": os.path.getmtime(filepath),
                })

        # Sort by modification time and limit
        files.sort(key=lambda x: x["modified"], reverse=True)
        files_limited = files[:10]  # Only return top 10 files

        # Get project title from README or use directory name
        title = plan_id_short
        readme_path = os.path.join(project_dir, "README.md")
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if first_line.startswith('# '):
                        title = first_line[2:].strip()
            except:
                pass

        projects.append({
            "id": plan_id_short,
            "title": title,
            "path": project_dir,
            "files": files_limited,
            "file_count": len(files),
            "total_size": total_size,
            "has_preview": has_preview,
            "preview_url": f"/api/projects/{plan_id_short}/preview" if has_preview else None,
            "modified": os.path.getmtime(project_dir),
        })

    # Sort by modification time (newest first)
    projects.sort(key=lambda x: x["modified"], reverse=True)

    return {"projects": projects}


@router.get("/{project_id}/preview")
async def get_project_preview(project_id: str):
    """Get preview (index.html) for a project"""
    project_dir = os.path.join(OUTPUT_DIR, project_id)
    index_path = os.path.join(project_dir, "index.html")
    
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Preview not found")
    
    return FileResponse(index_path)


@router.get("/{project_id}/files/{filename}")
async def get_project_file(project_id: str, filename: str):
    """Get a specific file from a project"""
    project_dir = os.path.join(OUTPUT_DIR, project_id)
    filepath = os.path.join(project_dir, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(filepath)
