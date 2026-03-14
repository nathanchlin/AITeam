from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import time

router = APIRouter(prefix="/projects", tags=["projects"])

OUTPUT_DIR = "output"
PLANS_STORAGE_FILE = Path(__file__).parent.parent.parent / "data" / "plans.json"

# Simple cache for project list
_projects_cache = {"data": None, "timestamp": 0, "ttl": 5}  # 5 second cache


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


def _get_project_info_fast(project_dir: str, plan_id_short: str) -> Dict[str, Any]:
    """Get project info with minimal I/O"""
    # Use scandir which is faster than listdir + stat
    has_preview = False
    has_discussion = False
    total_size = 0
    file_count = 0
    latest_mtime = 0

    try:
        with os.scandir(project_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    file_count += 1
                    try:
                        stat = entry.stat()
                        total_size += stat.st_size
                        if stat.st_mtime > latest_mtime:
                            latest_mtime = stat.st_mtime
                    except:
                        pass

                    name = entry.name.lower()
                    if name == "index.html":
                        has_preview = True
                    elif name == "discussion.json":
                        has_discussion = True
    except:
        pass

    # Get title from README (fast read, only first line)
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

    if not has_preview and os.path.exists(os.path.join(project_dir, "ts_app", "dist", "index.html")):
        has_preview = True

    return {
        "id": plan_id_short,
        "title": title,
        "path": project_dir,
        "files": [],  # Don't return files list - fetch on demand
        "file_count": file_count,
        "total_size": total_size,
        "has_preview": has_preview,
        "has_discussion": has_discussion,
        "preview_url": f"/api/projects/{plan_id_short}/preview" if has_preview else None,
        "modified": latest_mtime,
    }


@router.get("/")
async def list_projects():
    """List all generated projects from output directory"""
    global _projects_cache

    # Check cache
    current_time = time.time()
    if _projects_cache["data"] is not None and (current_time - _projects_cache["timestamp"]) < _projects_cache["ttl"]:
        return {"projects": _projects_cache["data"]}

    if not os.path.exists(OUTPUT_DIR):
        return {"projects": []}

    projects = []

    for plan_id_short in os.listdir(OUTPUT_DIR):
        project_dir = os.path.join(OUTPUT_DIR, plan_id_short)

        if not os.path.isdir(project_dir):
            continue

        project_info = _get_project_info_fast(project_dir, plan_id_short)
        projects.append(project_info)

    # Sort by modification time (newest first)
    projects.sort(key=lambda x: x["modified"], reverse=True)

    # Update cache
    _projects_cache["data"] = projects
    _projects_cache["timestamp"] = current_time

    return {"projects": projects}


@router.get("/{project_id}/files")
async def get_project_files(project_id: str):
    """Get file list for a specific project (on demand)"""
    project_dir = os.path.join(OUTPUT_DIR, project_id)

    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail="Project not found")

    files = []
    try:
        with os.scandir(project_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    try:
                        stat = entry.stat()
                        files.append({
                            "name": entry.name,
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                        })
                    except:
                        pass
    except:
        pass

    # Sort by modification time
    files.sort(key=lambda x: x["modified"], reverse=True)

    return {"project_id": project_id, "files": files[:20]}  # Return top 20 files


@router.get("/{project_id}/preview")
async def get_project_preview(project_id: str):
    """Get preview entry for a project."""
    project_dir = os.path.join(OUTPUT_DIR, project_id)
    index_path = os.path.join(project_dir, "index.html")
    ts_dist_path = os.path.join(project_dir, "ts_app", "dist", "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path)
    if os.path.exists(ts_dist_path):
        return FileResponse(ts_dist_path)

    raise HTTPException(status_code=404, detail="Preview not found")


@router.get("/{project_id}/files/{file_path:path}")
async def get_project_file(project_id: str, file_path: str):
    """Get a specific file from a project, including nested dist assets."""
    project_dir = os.path.join(OUTPUT_DIR, project_id)
    requested_path = os.path.normpath(file_path).lstrip("/")
    if requested_path.startswith(".."):
        raise HTTPException(status_code=400, detail="Invalid file path")

    filepath = os.path.abspath(os.path.join(project_dir, requested_path))
    project_root = os.path.abspath(project_dir)
    if filepath != project_root and not filepath.startswith(project_root + os.sep):
        raise HTTPException(status_code=400, detail="Invalid file path")

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
