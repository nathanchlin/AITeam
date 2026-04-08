"""
规范合并引擎（Specs Merger）- Phase 2

功能：
- 解析规范文档为树形结构
- 按顺序应用 Delta Spec（RENAMED → REMOVED → MODIFIED → ADDED）
- 重建规范文本
"""

import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

from app.models.schemas import DeltaSpec, DeltaOperation, Requirement, Scenario

logger = logging.getLogger(__name__)


@dataclass
class SpecNode:
    """规范节点"""
    type: str  # "section", "requirement", "scenario", "text"
    title: Optional[str] = None
    content: Optional[str] = None
    children: List['SpecNode'] = field(default_factory=list)
    level: int = 0
    line_start: int = 0
    line_end: int = 0


class SpecTree:
    """规范树结构"""
    
    def __init__(self):
        self.root = SpecNode(type="root", children=[])
        self.purpose: Optional[str] = None
        self.requirements: Dict[str, SpecNode] = {}  # requirement_name -> node
    
    def add_section(self, title: str, content: str, level: int = 2):
        """添加章节"""
        node = SpecNode(
            type="section",
            title=title,
            content=content,
            level=level
        )
        self.root.children.append(node)
        return node
    
    def add_requirement(self, name: str, content: str, scenarios: List[Dict] = None):
        """添加需求"""
        req_node = SpecNode(
            type="requirement",
            title=name,
            content=content,
            level=3
        )
        
        if scenarios:
            for scenario in scenarios:
                scenario_node = SpecNode(
                    type="scenario",
                    title=scenario.get("name", ""),
                    content=scenario.get("content", ""),
                    level=4
                )
                req_node.children.append(scenario_node)
        
        self.requirements[name] = req_node
        self.root.children.append(req_node)
        return req_node
    
    def remove_requirement(self, name: str) -> bool:
        """删除需求"""
        if name in self.requirements:
            node = self.requirements[name]
            if node in self.root.children:
                self.root.children.remove(node)
            del self.requirements[name]
            return True
        return False
    
    def rename_requirement(self, old_name: str, new_name: str) -> bool:
        """重命名需求"""
        if old_name in self.requirements:
            node = self.requirements[old_name]
            node.title = new_name
            del self.requirements[old_name]
            self.requirements[new_name] = node
            return True
        return False
    
    def update_requirement(self, name: str, new_content: str, new_scenarios: List[Dict] = None) -> bool:
        """更新需求内容"""
        if name in self.requirements:
            node = self.requirements[name]
            node.content = new_content
            
            if new_scenarios is not None:
                node.children = []
                for scenario in new_scenarios:
                    scenario_node = SpecNode(
                        type="scenario",
                        title=scenario.get("name", ""),
                        content=scenario.get("content", ""),
                        level=4
                    )
                    node.children.append(scenario_node)
            
            return True
        return False


class SpecsMerger:
    """规范合并引擎"""
    
    def __init__(self):
        self.log_prefix = "[SpecsMerger]"
    
    def parse_specs(self, specs: str) -> SpecTree:
        """解析规范为树形结构"""
        logger.info(f"{self.log_prefix} Parsing specs ({len(specs)} chars)")
        
        tree = SpecTree()
        if not specs or not specs.strip():
            return tree
        
        lines = specs.split('\n')
        current_section = None
        current_requirement = None
        current_scenario = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # ## Purpose 章节
            if line.startswith('## Purpose'):
                current_section = "purpose"
                i += 1
                content_lines = []
                while i < len(lines) and not lines[i].startswith('##'):
                    content_lines.append(lines[i])
                    i += 1
                tree.purpose = '\n'.join(content_lines).strip()
                continue
            
            # ## Requirements 章节
            elif line.startswith('## Requirements'):
                current_section = "requirements"
                i += 1
                continue
            
            # ### Requirement: 需求
            elif line.startswith('### Requirement:'):
                req_match = re.match(r'### Requirement:\s*(.+)', line)
                if req_match:
                    req_name = req_match.group(1).strip()
                    current_requirement = req_name
                    
                    i += 1
                    content_lines = []
                    scenarios = []
                    
                    while i < len(lines) and not lines[i].startswith('### Requirement:') and not lines[i].startswith('##'):
                        if lines[i].startswith('#### Scenario:'):
                            # 解析场景
                            scenario_match = re.match(r'#### Scenario:\s*(.+)', lines[i])
                            if scenario_match:
                                scenario_name = scenario_match.group(1).strip()
                                i += 1
                                scenario_content = []
                                while i < len(lines) and not lines[i].startswith('####') and not lines[i].startswith('###') and not lines[i].startswith('##'):
                                    scenario_content.append(lines[i])
                                    i += 1
                                scenarios.append({
                                    "name": scenario_name,
                                    "content": '\n'.join(scenario_content).strip()
                                })
                            continue
                        else:
                            content_lines.append(lines[i])
                            i += 1
                    
                    tree.add_requirement(
                        name=req_name,
                        content='\n'.join(content_lines).strip(),
                        scenarios=scenarios
                    )
                    current_requirement = None
                    continue
            
            i += 1
        
        logger.info(f"{self.log_prefix} Parsed {len(tree.requirements)} requirements")
        return tree
    
    def apply_rename(self, tree: SpecTree, delta: DeltaSpec) -> SpecTree:
        """应用重命名操作"""
        old_name = delta.old_name
        new_name = delta.new_name
        
        if not old_name or not new_name:
            logger.warning(f"{self.log_prefix} RENAMED delta missing old_name or new_name")
            return tree
        
        logger.info(f"{self.log_prefix} Applying RENAMED: '{old_name}' -> '{new_name}'")
        
        if tree.rename_requirement(old_name, new_name):
            logger.info(f"{self.log_prefix} ✓ Renamed requirement")
        else:
            logger.warning(f"{self.log_prefix} ✗ Requirement '{old_name}' not found")
        
        return tree
    
    def apply_remove(self, tree: SpecTree, delta: DeltaSpec) -> SpecTree:
        """应用删除操作"""
        spec_name = delta.spec_name
        
        logger.info(f"{self.log_prefix} Applying REMOVED: '{spec_name}'")
        logger.info(f"{self.log_prefix} Reason: {delta.reason or 'No reason provided'}")
        
        if tree.remove_requirement(spec_name):
            logger.info(f"{self.log_prefix} ✓ Removed requirement")
        else:
            logger.warning(f"{self.log_prefix} ✗ Requirement '{spec_name}' not found")
        
        return tree
    
    def apply_modify(self, tree: SpecTree, delta: DeltaSpec) -> SpecTree:
        """应用修改操作"""
        spec_name = delta.spec_name
        requirement = delta.requirement
        
        if not requirement:
            logger.warning(f"{self.log_prefix} MODIFIED delta missing requirement data")
            return tree
        
        logger.info(f"{self.log_prefix} Applying MODIFIED: '{spec_name}'")
        
        # 转换场景格式
        scenarios = []
        if requirement.scenarios:
            for scenario in requirement.scenarios:
                scenarios.append({
                    "name": scenario.name,
                    "content": f"- **GIVEN** {scenario.given}\n- **WHEN** {scenario.when}\n- **THEN** {scenario.then}"
                })
        
        if tree.update_requirement(spec_name, requirement.text, scenarios):
            logger.info(f"{self.log_prefix} ✓ Modified requirement")
        else:
            logger.warning(f"{self.log_prefix} ✗ Requirement '{spec_name}' not found")
        
        return tree
    
    def apply_add(self, tree: SpecTree, delta: DeltaSpec) -> SpecTree:
        """应用新增操作"""
        spec_name = delta.spec_name
        requirement = delta.requirement
        
        if not requirement:
            logger.warning(f"{self.log_prefix} ADDED delta missing requirement data")
            return tree
        
        logger.info(f"{self.log_prefix} Applying ADDED: '{spec_name}'")
        
        # 检查是否已存在
        if spec_name in tree.requirements:
            logger.warning(f"{self.log_prefix} ✗ Requirement '{spec_name}' already exists, skipping")
            return tree
        
        # 转换场景格式
        scenarios = []
        if requirement.scenarios:
            for scenario in requirement.scenarios:
                scenarios.append({
                    "name": scenario.name,
                    "content": f"- **GIVEN** {scenario.given}\n- **WHEN** {scenario.when}\n- **THEN** {scenario.then}"
                })
        
        tree.add_requirement(
            name=spec_name,
            content=requirement.text,
            scenarios=scenarios
        )
        
        logger.info(f"{self.log_prefix} ✓ Added new requirement")
        return tree
    
    def rebuild_specs(self, tree: SpecTree) -> str:
        """重建规范文本"""
        logger.info(f"{self.log_prefix} Rebuilding specs from tree")
        
        lines = []
        
        # Purpose
        if tree.purpose:
            lines.append("## Purpose")
            lines.append(tree.purpose)
            lines.append("")
        
        # Requirements
        if tree.requirements:
            lines.append("## Requirements")
            lines.append("")
            
            for req_node in tree.root.children:
                if req_node.type == "requirement":
                    lines.append(f"### Requirement: {req_node.title}")
                    if req_node.content:
                        lines.append(req_node.content)
                    lines.append("")
                    
                    # Scenarios
                    for scenario_node in req_node.children:
                        if scenario_node.type == "scenario":
                            lines.append(f"#### Scenario: {scenario_node.title}")
                            if scenario_node.content:
                                lines.append(scenario_node.content)
                            lines.append("")
        
        result = '\n'.join(lines).strip()
        logger.info(f"{self.log_prefix} Rebuilt specs ({len(result)} chars, {len(tree.requirements)} requirements)")
        
        return result
    
    def merge_deltas(
        self, 
        base_specs: str, 
        deltas: List[DeltaSpec]
    ) -> str:
        """将 Delta Spec 合并到主规范
        
        合并顺序（重要！）：
        1. RENAMED - 修改需求名称
        2. REMOVED - 删除需求
        3. MODIFIED - 修改需求内容
        4. ADDED - 新增需求
        
        Args:
            base_specs: 基础规范
            deltas: Delta 列表
        
        Returns:
            合并后的规范
        """
        if not deltas:
            logger.info(f"{self.log_prefix} No deltas to merge, returning base specs")
            return base_specs
        
        logger.info(f"{self.log_prefix} Merging {len(deltas)} deltas into base specs")
        
        # 1. 解析基础规范
        tree = self.parse_specs(base_specs)
        
        # 2. 按顺序应用 Delta
        # RENAMED
        renamed_deltas = [d for d in deltas if d.operation == DeltaOperation.RENAMED]
        logger.info(f"{self.log_prefix} Processing {len(renamed_deltas)} RENAMED deltas")
        for delta in renamed_deltas:
            tree = self.apply_rename(tree, delta)
        
        # REMOVED
        removed_deltas = [d for d in deltas if d.operation == DeltaOperation.REMOVED]
        logger.info(f"{self.log_prefix} Processing {len(removed_deltas)} REMOVED deltas")
        for delta in removed_deltas:
            tree = self.apply_remove(tree, delta)
        
        # MODIFIED
        modified_deltas = [d for d in deltas if d.operation == DeltaOperation.MODIFIED]
        logger.info(f"{self.log_prefix} Processing {len(modified_deltas)} MODIFIED deltas")
        for delta in modified_deltas:
            tree = self.apply_modify(tree, delta)
        
        # ADDED
        added_deltas = [d for d in deltas if d.operation == DeltaOperation.ADDED]
        logger.info(f"{self.log_prefix} Processing {len(added_deltas)} ADDED deltas")
        for delta in added_deltas:
            tree = self.apply_add(tree, delta)
        
        # 3. 重建规范文本
        merged_specs = self.rebuild_specs(tree)
        
        logger.info(f"{self.log_prefix} ✓ Merge completed")
        return merged_specs


# ==================== 辅助函数 ====================

def create_delta_from_dict(data: Dict[str, Any]) -> DeltaSpec:
    """从字典创建 DeltaSpec 对象"""
    # 解析 requirement
    requirement = None
    if data.get("requirement"):
        req_data = data["requirement"]
        scenarios = []
        if req_data.get("scenarios"):
            for scenario_data in req_data["scenarios"]:
                scenarios.append(Scenario(
                    name=scenario_data.get("name", ""),
                    given=scenario_data.get("given", ""),
                    when=scenario_data.get("when", ""),
                    then=scenario_data.get("then", "")
                ))
        
        requirement = Requirement(
            text=req_data.get("text", ""),
            scenarios=scenarios
        )
    
    return DeltaSpec(
        spec_name=data.get("spec_name", ""),
        operation=DeltaOperation(data.get("operation", "ADDED")),
        description=data.get("description", ""),
        requirement=requirement,
        old_name=data.get("old_name"),
        new_name=data.get("new_name"),
        reason=data.get("reason")
    )
