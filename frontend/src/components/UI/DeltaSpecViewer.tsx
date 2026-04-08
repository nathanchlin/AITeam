/**
 * Delta Spec Viewer - Phase 2
 * 
 * 功能：
 * - 显示待合并的 Delta 列表
 * - 可视化变更历史
 * - 显示主规范版本信息
 */

import React, { useState } from 'react';

interface Scenario {
  name: string;
  given: string;
  when: string;
  then: string;
}

interface Requirement {
  text: string;
  scenarios: Scenario[];
}

interface DeltaSpec {
  spec_name: string;
  operation: 'ADDED' | 'MODIFIED' | 'REMOVED' | 'RENAMED';
  description: string;
  requirement?: Requirement;
  old_name?: string;
  new_name?: string;
  reason?: string;
  created_at: string;
}

interface DeltaSpecViewerProps {
  deltas: DeltaSpec[];
  specsVersion: number;
  onMergePreview?: () => void;
}

const DeltaSpecViewer: React.FC<DeltaSpecViewerProps> = ({
  deltas,
  specsVersion,
  onMergePreview,
}) => {
  const [showDeltas, setShowDeltas] = useState(false);
  const [expandedDelta, setExpandedDelta] = useState<string | null>(null);

  // 操作类型配置
  const operationConfig = {
    ADDED: {
      emoji: '➕',
      color: 'bg-green-50 border-green-200 text-green-800',
      badge: 'bg-green-100 text-green-700',
    },
    MODIFIED: {
      emoji: '✏️',
      color: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      badge: 'bg-yellow-100 text-yellow-700',
    },
    REMOVED: {
      emoji: '➖',
      color: 'bg-red-50 border-red-200 text-red-800',
      badge: 'bg-red-100 text-red-700',
    },
    RENAMED: {
      emoji: '🔄',
      color: 'bg-blue-50 border-blue-200 text-blue-800',
      badge: 'bg-blue-100 text-blue-700',
    },
  };

  if (!deltas || deltas.length === 0) {
    return null;
  }

  return (
    <div className="mt-4">
      {/* Delta 列表切换按钮 */}
      <button
        onClick={() => setShowDeltas(!showDeltas)}
        className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <span className="text-lg">📝</span>
        <span>待合并的变更</span>
        <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-orange-100 text-orange-700">
          {deltas.length}
        </span>
        <span className="text-gray-400 text-xs">(v{specsVersion} → v{specsVersion + 1})</span>
        <span className="ml-auto">{showDeltas ? '▲' : '▼'}</span>
      </button>

      {/* Delta 列表 */}
      {showDeltas && (
        <div className="mt-3 space-y-3">
          {/* 摘要统计 */}
          <div className="flex items-center gap-4 px-3 py-2 text-xs text-gray-600 bg-gray-50 rounded">
            <span>
              ➕ {deltas.filter(d => d.operation === 'ADDED').length} 新增
            </span>
            <span>
              ✏️ {deltas.filter(d => d.operation === 'MODIFIED').length} 修改
            </span>
            <span>
              ➖ {deltas.filter(d => d.operation === 'REMOVED').length} 删除
            </span>
            <span>
              🔄 {deltas.filter(d => d.operation === 'RENAMED').length} 重命名
            </span>
          </div>

          {/* Delta 卡片 */}
          {deltas.map((delta, index) => {
            const config = operationConfig[delta.operation];
            const isExpanded = expandedDelta === delta.spec_name;

            return (
              <div
                key={index}
                className={`border-l-4 rounded-r-lg ${config.color}`}
              >
                {/* Delta 头部 */}
                <div
                  className="flex items-center justify-between p-3 cursor-pointer"
                  onClick={() => setExpandedDelta(isExpanded ? null : delta.spec_name)}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{config.emoji}</span>
                    <span className={`px-2 py-0.5 text-xs font-semibold rounded ${config.badge}`}>
                      {delta.operation}
                    </span>
                    <span className="font-medium">{delta.spec_name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">
                      {new Date(delta.created_at).toLocaleString('zh-CN')}
                    </span>
                    <span className="text-gray-400">{isExpanded ? '▲' : '▼'}</span>
                  </div>
                </div>

                {/* Delta 内容（展开后显示） */}
                {isExpanded && (
                  <div className="px-3 pb-3 border-t border-gray-200">
                    {/* 变更描述 */}
                    <div className="mt-2 text-sm">
                      <span className="font-medium text-gray-700">变更描述：</span>
                      <p className="mt-1 text-gray-600">{delta.description}</p>
                    </div>

                    {/* RENAMED 特殊显示 */}
                    {delta.operation === 'RENAMED' && delta.old_name && delta.new_name && (
                      <div className="mt-2 text-sm">
                        <span className="font-medium text-gray-700">名称变更：</span>
                        <p className="mt-1">
                          <span className="line-through text-red-600">{delta.old_name}</span>
                          <span className="mx-2">→</span>
                          <span className="text-green-600">{delta.new_name}</span>
                        </p>
                      </div>
                    )}

                    {/* REMOVED 原因 */}
                    {delta.operation === 'REMOVED' && delta.reason && (
                      <div className="mt-2 text-sm">
                        <span className="font-medium text-gray-700">删除原因：</span>
                        <p className="mt-1 text-red-600">{delta.reason}</p>
                      </div>
                    )}

                    {/* ADDED/MODIFIED 需求详情 */}
                    {delta.requirement && (
                      <div className="mt-3">
                        <div className="text-sm font-medium text-gray-700 mb-2">需求详情：</div>
                        <div className="bg-white p-3 rounded border border-gray-200">
                          <p className="text-sm text-gray-800">{delta.requirement.text}</p>

                          {/* 场景列表 */}
                          {delta.requirement.scenarios && delta.requirement.scenarios.length > 0 && (
                            <div className="mt-3 space-y-2">
                              {delta.requirement.scenarios.map((scenario, sIdx) => (
                                <div key={sIdx} className="text-xs bg-gray-50 p-2 rounded">
                                  <div className="font-medium text-gray-700 mb-1">
                                    场景：{scenario.name}
                                  </div>
                                  <div className="space-y-1">
                                    <div className="flex">
                                      <span className="font-semibold text-blue-600 mr-2">GIVEN</span>
                                      <span>{scenario.given}</span>
                                    </div>
                                    <div className="flex">
                                      <span className="font-semibold text-orange-600 mr-2">WHEN</span>
                                      <span>{scenario.when}</span>
                                    </div>
                                    <div className="flex">
                                      <span className="font-semibold text-green-600 mr-2">THEN</span>
                                      <span>{scenario.then}</span>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {/* 合并预览按钮 */}
          {onMergePreview && (
            <div className="mt-4 text-center">
              <button
                onClick={onMergePreview}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                🔍 预览合并结果
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DeltaSpecViewer;
