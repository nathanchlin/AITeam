"""FeedbackStore - Learning and storing error patterns for quality improvement.

This module provides a feedback learning system that:
1. Records errors encountered during code generation
2. Tracks common error patterns and their frequencies
3. Provides guidance based on similar past errors
4. Persists data to feedback.json for long-term learning
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter


class FeedbackStore:
    """Stores and retrieves error patterns for learning from mistakes."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize FeedbackStore with storage path.

        Args:
            storage_path: Path to feedback.json file. Defaults to backend/data/feedback.json
        """
        if storage_path is None:
            backend_root = Path(__file__).resolve().parent.parent.parent
            self.storage_path = backend_root / "data" / "feedback.json"
        else:
            self.storage_path = Path(storage_path)

        self._ensure_storage()
        self._data = self._load_data()

    def _ensure_storage(self):
        """Ensure storage directory and file exist."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._save_data({
                "errors": [],
                "error_patterns": {},
                "successful_fixes": {},
                "stats": {
                    "total_errors": 0,
                    "unique_patterns": 0,
                    "successful_fixes": 0
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })

    def _load_data(self) -> Dict[str, Any]:
        """Load feedback data from storage."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[FeedbackStore] Error loading data: {e}")
            return {
                "errors": [],
                "error_patterns": {},
                "successful_fixes": {},
                "stats": {
                    "total_errors": 0,
                    "unique_patterns": 0,
                    "successful_fixes": 0
                }
            }

    def _save_data(self, data: Dict[str, Any]):
        """Save feedback data to storage."""
        try:
            data["updated_at"] = datetime.now().isoformat()
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[FeedbackStore] Error saving data: {e}")

    def _hash_error(self, error_type: str, code_snippet: str) -> str:
        """Generate a unique hash for an error pattern."""
        normalized_code = ' '.join(code_snippet.split())[:500]
        content = f"{error_type}:{normalized_code}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def record_error(
        self,
        plan_id: str,
        error_type: str,
        description: str,
        code_snippet: str,
        fix_applied: Optional[str] = None,
        task_context: Optional[str] = None
    ) -> str:
        """Record an error for future learning.

        Args:
            plan_id: ID of the plan where error occurred
            error_type: Category of error (e.g., "empty_method", "undefined_variable")
            description: Human-readable error description
            code_snippet: The problematic code
            fix_applied: Description of how the error was fixed
            task_context: Additional context about what was being attempted

        Returns:
            Error pattern hash for reference
        """
        error_hash = self._hash_error(error_type, code_snippet)

        error_record = {
            "hash": error_hash,
            "plan_id": plan_id,
            "error_type": error_type,
            "description": description,
            "code_snippet": code_snippet[:500],
            "fix_applied": fix_applied,
            "task_context": task_context,
            "timestamp": datetime.now().isoformat()
        }

        # Add to errors list
        self._data["errors"].append(error_record)

        # Update error patterns counter
        if error_hash not in self._data["error_patterns"]:
            self._data["error_patterns"][error_hash] = {
                "error_type": error_type,
                "description": description,
                "count": 0,
                "first_seen": datetime.now().isoformat(),
                "examples": []
            }

        self._data["error_patterns"][error_hash]["count"] += 1
        self._data["error_patterns"][error_hash]["last_seen"] = datetime.now().isoformat()

        # Store example (max 5 per pattern)
        if len(self._data["error_patterns"][error_hash]["examples"]) < 5:
            self._data["error_patterns"][error_hash]["examples"].append({
                "code_snippet": code_snippet[:200],
                "plan_id": plan_id
            })

        # Record successful fix if provided
        if fix_applied:
            if error_hash not in self._data["successful_fixes"]:
                self._data["successful_fixes"][error_hash] = []
            self._data["successful_fixes"][error_hash].append({
                "fix": fix_applied,
                "timestamp": datetime.now().isoformat()
            })
            self._data["stats"]["successful_fixes"] += 1

        # Update stats
        self._data["stats"]["total_errors"] += 1
        self._data["stats"]["unique_patterns"] = len(self._data["error_patterns"])

        self._save_data(self._data)

        print(f"[FeedbackStore] Recorded error: {error_type} (hash: {error_hash})")
        return error_hash

    def get_common_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most common error patterns.

        Args:
            limit: Maximum number of patterns to return

        Returns:
            List of error patterns sorted by frequency
        """
        patterns = list(self._data["error_patterns"].values())
        patterns.sort(key=lambda x: x["count"], reverse=True)
        return patterns[:limit]

    def get_error_guidance(self, code_snippet: str, task_description: Optional[str] = None) -> Optional[str]:
        """Get guidance based on similar past errors.

        Analyzes the code snippet and task to find similar past errors
        and their successful fixes.

        Args:
            code_snippet: The code to analyze
            task_description: What task is being attempted

        Returns:
            Guidance string if similar errors found, None otherwise
        """
        guidance_parts = []

        # Check for common patterns in the code
        patterns_to_check = [
            ("empty_method", r'function\s+\w+\s*\([^)]*\)\s*\{\s*\}', "空方法体"),
            ("empty_method", r'\w+\s*\([^)]*\)\s*\{\s*\}', "空方法体"),
            ("todo", r'//\s*TODO|//\s*待实现|/\*.*TODO.*\*/', "TODO占位符"),
            ("ellipsis", r'\.\.\.(?:\s|$)', "省略号占位符"),
            ("undefined_ctx", r'ctx\.(fillRect|drawImage|fillText)', "未初始化的 ctx"),
            ("no_init", r'class\s+\w+.*\{', "检查是否有初始化"),
            ("external_ref", r'<script\s+src=|<link\s+[^>]*href=', "外部文件引用"),
        ]

        import re
        for pattern_type, regex, desc in patterns_to_check:
            if re.search(regex, code_snippet, re.IGNORECASE | re.DOTALL):
                # Check if we have fixes for this pattern
                matching_patterns = [
                    p for h, p in self._data["error_patterns"].items()
                    if p["error_type"] == pattern_type and p["count"] >= 2
                ]

                if matching_patterns:
                    # Get the most common fix
                    for pattern in matching_patterns:
                        error_hash = [h for h, p in self._data["error_patterns"].items()
                                      if p == pattern][0]
                        if error_hash in self._data["successful_fixes"]:
                            fixes = self._data["successful_fixes"][error_hash]
                            if fixes:
                                guidance_parts.append(f"⚠️ 检测到{desc}问题（已出现{pattern['count']}次）")
                                guidance_parts.append(f"   成功修复方案: {fixes[-1]['fix']}")
                                break

        # Get general guidance from common errors
        common_errors = self.get_common_errors(3)
        if common_errors and not guidance_parts:
            guidance_parts.append("⚠️ 常见错误提醒:")
            for err in common_errors:
                if err["count"] >= 3:
                    guidance_parts.append(f"   - {err['description']} (已出现{err['count']}次)")

        return '\n'.join(guidance_parts) if guidance_parts else None

    def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        return {
            **self._data["stats"],
            "top_error_types": self._get_top_error_types()
        }

    def _get_top_error_types(self) -> List[Dict[str, Any]]:
        """Get error types sorted by frequency."""
        type_counter = Counter()
        for pattern in self._data["error_patterns"].values():
            type_counter[pattern["error_type"]] += pattern["count"]

        return [
            {"type": t, "count": c}
            for t, c in type_counter.most_common(10)
        ]

    def mark_fix_successful(self, error_hash: str, fix_description: str):
        """Mark that a fix was successful for a given error pattern.

        Args:
            error_hash: Hash of the error pattern
            fix_description: Description of what fixed the issue
        """
        if error_hash not in self._data["successful_fixes"]:
            self._data["successful_fixes"][error_hash] = []

        self._data["successful_fixes"][error_hash].append({
            "fix": fix_description,
            "timestamp": datetime.now().isoformat()
        })

        self._data["stats"]["successful_fixes"] += 1
        self._save_data(self._data)

        print(f"[FeedbackStore] Marked fix successful for {error_hash}")

    def get_guidance_for_task(self, task_description: str) -> Optional[str]:
        """Get proactive guidance based on task description.

        Analyzes the task and provides warnings about common mistakes
        for similar tasks.

        Args:
            task_description: Description of the task

        Returns:
            Proactive guidance string if relevant patterns found
        """
        guidance = []

        # Task-specific warnings
        task_lower = task_description.lower()

        if any(kw in task_lower for kw in ["游戏", "game", "canvas", "动画"]):
            guidance.extend([
                "📝 游戏开发提醒:",
                "   - 必须有 window.onload 或 DOMContentLoaded 初始化",
                "   - 必须有 requestAnimationFrame 游戏循环",
                "   - ctx 必须在构造函数中初始化",
                "   - 所有绘制方法必须实际调用 ctx API"
            ])

        if any(kw in task_lower for kw in ["交互", "点击", "键盘", "控制"]):
            guidance.extend([
                "📝 交互功能提醒:",
                "   - 必须绑定事件监听器 (addEventListener)",
                "   - 检查事件对象是否正确使用"
            ])

        if any(kw in task_lower for kw in ["碰撞", "检测", "边界"]):
            guidance.extend([
                "📝 碰撞检测提醒:",
                "   - 检查边界条件 (x < 0, x >= width 等)",
                "   - 注意坐标系方向"
            ])

        # Add common errors from feedback
        common_errors = self.get_common_errors(3)
        if common_errors:
            guidance.append("\n⚠️ 该类任务常见错误:")
            for err in common_errors[:3]:
                guidance.append(f"   - {err['description']}")

        return '\n'.join(guidance) if guidance else None

    def clear_old_errors(self, days: int = 30):
        """Clear error records older than specified days.

        Args:
            days: Number of days to keep
        """
        cutoff = datetime.now()
        from datetime import timedelta
        cutoff = cutoff - timedelta(days=days)

        original_count = len(self._data["errors"])

        self._data["errors"] = [
            e for e in self._data["errors"]
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

        removed = original_count - len(self._data["errors"])
        if removed > 0:
            print(f"[FeedbackStore] Removed {removed} old error records")
            self._save_data(self._data)


# Global instance
feedback_store = FeedbackStore()
