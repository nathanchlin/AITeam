from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter(prefix="/projects", tags=["projects"])

OUTPUT_DIR = "output"
PLANS_STORAGE_FILE = Path(__file__).parent.parent.parent / "data" / "plans.json"


def load_plans_data():
    """Load plans data from storage file"""
    try:
        if PLANS_STORAGE_FILE.exists():
            with open(PLANS_STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"plans": {}}


def find_plan_by_short_id(short_id: str):
    """Find a plan by its short ID (first 8 characters)"""
    data = load_plans_data()
    for plan_id, plan in data.get('plans', {}).items():
        if plan_id.startswith(short_id):
            return plan
    return None


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

        # Check for discussion history
        discussion_path = os.path.join(project_dir, "discussion.json")
        has_discussion = os.path.exists(discussion_path)

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
            "has_discussion": has_discussion,
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


@router.get("/{project_id}/discussion")
async def get_project_discussion(project_id: str):
    """Get discussion history for a project"""
    project_dir = os.path.join(OUTPUT_DIR, project_id)

    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail="Project not found")

    # Try to read from discussion.json first
    discussion_path = os.path.join(project_dir, "discussion.json")
    if os.path.exists(discussion_path):
        try:
            with open(discussion_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {"discussion": data.get("discussion", []), "title": data.get("title", project_id)}
        except:
            pass

    # Fallback: try to find from plans.json
    plan = find_plan_by_short_id(project_id)
    if plan:
        return {
            "discussion": plan.get("discussion", []),
            "title": plan.get("title", project_id)
        }

    return {"discussion": [], "title": project_id}
