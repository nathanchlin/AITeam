import { useState, useEffect } from 'react';
import {
  X, Archive, Download, Trash2, Undo2, CheckCircle, AlertCircle,
  FileCode, GitCompare, Loader2, Info, Plus, Save
} from 'lucide-react';
import type { ArchiveInfo, ArchiveDiffResult, ArchiveValidationResult } from '../../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

interface ArchivePanelProps {
  planId: string;
  onClose: () => void;
  onRestore: (roundNumber: number) => Promise<void>;
}

export function ArchivePanel({ planId, onClose, onRestore }: ArchivePanelProps) {
  const [archives, setArchives] = useState<ArchiveInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedArchive, setSelectedArchive] = useState<ArchiveInfo | null>(null);
  const [previewContent, setPreviewContent] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [validationResult, setValidationResult] = useState<ArchiveValidationResult | null>(null);
  const [validating, setValidating] = useState(false);
  const [diffResult, setDiffResult] = useState<ArchiveDiffResult | null>(null);
  const [diffLoading, setDiffLoading] = useState(false);
  const [diffFromRound, setDiffFromRound] = useState<number>(0);
  const [diffToRound, setDiffToRound] = useState<number>(0);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createName, setCreateName] = useState('');
  const [createDesc, setCreateDesc] = useState('');
  const [creating, setCreating] = useState(false);

  // Fetch archives
  const fetchArchives = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/archives/${planId}`);
      if (res.ok) {
        const data = await res.json();
        setArchives(data.archives || []);
        // Set default diff selections
        if (data.archives?.length >= 2) {
          setDiffFromRound(data.archives[0].round_number);
          setDiffToRound(data.archives[data.archives.length - 1].round_number);
        }
      }
    } catch (e) {
      console.error('Fetch archives error:', e);
      setError('Failed to load archives');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArchives();
  }, [planId]);

  // Preview archive content
  const handlePreview = async (archive: ArchiveInfo) => {
    setSelectedArchive(archive);
    setValidationResult(null);
    setDiffResult(null);
    setPreviewLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/archives/${planId}/content/${archive.round_number}`);
      if (res.ok) {
        const data = await res.json();
        setPreviewContent(data.content);
      } else {
        setPreviewContent(null);
        setError('Failed to load archive content');
      }
    } catch (e) {
      console.error('Preview error:', e);
      setPreviewContent(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  // Validate archive
  const handleValidate = async (roundNumber: number) => {
    setValidating(true);
    setValidationResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/archives/${planId}/validate/${roundNumber}`);
      if (res.ok) {
        const data = await res.json();
        setValidationResult(data);
      }
    } catch (e) {
      console.error('Validate error:', e);
    } finally {
      setValidating(false);
    }
  };

  // Download archive
  const handleDownload = async (archive: ArchiveInfo) => {
    setActionLoading(archive.round_number);
    try {
      const url = `${API_BASE}/api/pipeline/archives/${planId}/download/${archive.round_number}`;
      const link = document.createElement('a');
      link.href = url;
      link.download = `archive_${planId.slice(0, 8)}_${archive.archive_name}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      console.error('Download error:', e);
      setError('Failed to download archive');
    } finally {
      setActionLoading(null);
    }
  };

  // Delete archive
  const handleDelete = async (archive: ArchiveInfo) => {
    const label = archive.round_number === 0 ? '初始版本' : `迭代${archive.round_number}`;
    if (!confirm(`确定要删除${label}存档吗？此操作不可恢复。`)) return;

    setActionLoading(archive.round_number);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/archives/${planId}/${archive.round_number}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        await fetchArchives();
        if (selectedArchive?.round_number === archive.round_number) {
          setSelectedArchive(null);
          setPreviewContent(null);
        }
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || 'Failed to delete archive');
      }
    } catch (e) {
      console.error('Delete error:', e);
      setError('Failed to delete archive');
    } finally {
      setActionLoading(null);
    }
  };

  // Restore archive
  const handleRestore = async (roundNumber: number) => {
    setActionLoading(roundNumber);
    try {
      await onRestore(roundNumber);
    } finally {
      setActionLoading(null);
    }
  };

  // Compare archives
  const handleCompare = async () => {
    if (diffFromRound === diffToRound) {
      setError('Please select two different versions to compare');
      return;
    }
    setDiffLoading(true);
    setDiffResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/archives/${planId}/diff`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_round: diffFromRound, to_round: diffToRound }),
      });
      if (res.ok) {
        const data = await res.json();
        setDiffResult(data);
        setValidationResult(null);
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || 'Failed to compare archives');
      }
    } catch (e) {
      console.error('Diff error:', e);
      setError('Failed to compare archives');
    } finally {
      setDiffLoading(false);
    }
  };

  // Create manual archive
  const handleCreateArchive = async () => {
    setCreating(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/archives/${planId}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          custom_name: createName || undefined,
          description: createDesc || undefined,
        }),
      });
      if (res.ok) {
        await res.json(); // Consume response
        await fetchArchives(); // Refresh list
        setShowCreateModal(false);
        setCreateName('');
        setCreateDesc('');
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || 'Failed to create archive');
      }
    } catch (e) {
      console.error('Create archive error:', e);
      setError('Failed to create archive');
    } finally {
      setCreating(false);
    }
  };

  // Format file size
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  // Format date
  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get label for round
  const getRoundLabel = (roundNumber: number, customName?: string) => {
    if (customName) return customName;
    if (roundNumber === 0) return '初始版本';
    if (roundNumber >= 10000) {
      // 手动存档
      const originalRound = Math.floor((roundNumber - 10000) / 100);
      const suffix = (roundNumber - 10000) % 100;
      return `手动存档 ${originalRound > 0 ? `迭代${originalRound}` : '初始'}-${suffix}`;
    }
    return `迭代 ${roundNumber}`;
  };

  // Clear error after 3 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg w-[900px] max-w-[95vw] h-[700px] max-h-[85vh] flex flex-col border border-gray-700">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between bg-gray-800">
          <div className="flex items-center gap-3">
            <Archive size={20} className="text-blue-400" />
            <h2 className="text-white font-bold">存档管理</h2>
            <span className="text-xs text-gray-400">({archives.length} 个版本)</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-500 flex items-center gap-1"
            >
              <Plus size={14} />
              手动存档
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="px-4 py-2 bg-red-500/20 border-b border-red-500/30 flex items-center gap-2">
            <AlertCircle size={14} className="text-red-400" />
            <span className="text-sm text-red-300">{error}</span>
          </div>
        )}

        {/* Toolbar - Diff selector */}
        {archives.length >= 2 && (
          <div className="px-4 py-3 border-b border-gray-700 bg-gray-800/50 flex items-center gap-3">
            <GitCompare size={16} className="text-gray-400" />
            <span className="text-sm text-gray-300">版本对比:</span>
            <select
              value={diffFromRound}
              onChange={(e) => setDiffFromRound(Number(e.target.value))}
              className="px-2 py-1 bg-gray-700 rounded text-white text-sm border border-gray-600"
            >
              {archives.map((a) => (
                <option key={a.round_number} value={a.round_number}>
                  {getRoundLabel(a.round_number)}
                </option>
              ))}
            </select>
            <span className="text-gray-500">→</span>
            <select
              value={diffToRound}
              onChange={(e) => setDiffToRound(Number(e.target.value))}
              className="px-2 py-1 bg-gray-700 rounded text-white text-sm border border-gray-600"
            >
              {archives.map((a) => (
                <option key={a.round_number} value={a.round_number}>
                  {getRoundLabel(a.round_number)}
                </option>
              ))}
            </select>
            <button
              onClick={handleCompare}
              disabled={diffLoading || diffFromRound === diffToRound}
              className="px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-500 disabled:opacity-50 flex items-center gap-1"
            >
              {diffLoading ? <Loader2 size={12} className="animate-spin" /> : <GitCompare size={12} />}
              对比
            </button>
          </div>
        )}

        {/* Main content */}
        <div className="flex-1 flex min-h-0">
          {/* Left: Archive list */}
          <div className="w-1/3 border-r border-gray-700 flex flex-col">
            <div className="p-3 border-b border-gray-700 bg-gray-800/30">
              <span className="text-sm font-medium text-gray-300">版本列表</span>
            </div>
            <div className="flex-1 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <Loader2 size={20} className="animate-spin mr-2" />
                  加载中...
                </div>
              ) : archives.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <Archive size={32} className="mb-2 opacity-30" />
                  <p className="text-sm">暂无存档</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-700/50">
                  {archives.map((archive) => (
                    <div
                      key={archive.round_number}
                      className={`p-3 cursor-pointer transition-colors ${
                        selectedArchive?.round_number === archive.round_number
                          ? 'bg-blue-500/20 border-l-2 border-blue-500'
                          : 'hover:bg-gray-800/50'
                      }`}
                      onClick={() => handlePreview(archive)}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <FileCode size={14} className="text-blue-400" />
                        <span className="text-sm font-medium text-white">
                          {archive.custom_name || getRoundLabel(archive.round_number)}
                        </span>
                        {archive.checksum && (
                          <span title="已验证">
                            <CheckCircle size={12} className="text-green-400" />
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-400">
                        {formatDate(archive.modified_at)} · {formatSize(archive.size)}
                      </div>
                      {archive.description && (
                        <div className="text-xs text-gray-500 mt-1 truncate">
                          {archive.description}
                        </div>
                      )}
                      {/* Action buttons */}
                      <div className="flex gap-1 mt-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDownload(archive);
                          }}
                          disabled={actionLoading === archive.round_number}
                          className="p-1 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded disabled:opacity-50"
                          title="下载"
                        >
                          {actionLoading === archive.round_number ? (
                            <Loader2 size={12} className="animate-spin" />
                          ) : (
                            <Download size={12} />
                          )}
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleValidate(archive.round_number);
                          }}
                          disabled={validating}
                          className="p-1 text-gray-400 hover:text-green-400 hover:bg-gray-700 rounded"
                          title="验证"
                        >
                          <Info size={12} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRestore(archive.round_number);
                          }}
                          disabled={actionLoading === archive.round_number}
                          className="p-1 text-gray-400 hover:text-yellow-400 hover:bg-gray-700 rounded"
                          title="还原"
                        >
                          <Undo2 size={12} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(archive);
                          }}
                          disabled={actionLoading === archive.round_number}
                          className="p-1 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded"
                          title="删除"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right: Preview / Diff / Validation */}
          <div className="flex-1 flex flex-col min-h-0">
            {/* Validation result */}
            {validationResult && (
              <div className="p-4 border-b border-gray-700 bg-gray-800/30">
                <div className="flex items-center gap-2 mb-2">
                  {validationResult.valid ? (
                    <CheckCircle size={16} className="text-green-400" />
                  ) : (
                    <AlertCircle size={16} className="text-red-400" />
                  )}
                  <span className={`text-sm font-medium ${validationResult.valid ? 'text-green-400' : 'text-red-400'}`}>
                    验证{validationResult.valid ? '通过' : '失败'}
                  </span>
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center gap-2">
                    <span className={validationResult.file_exists ? 'text-green-400' : 'text-red-400'}>
                      {validationResult.file_exists ? '✓' : '✗'} 文件存在
                    </span>
                    <span className={validationResult.checksum_match ? 'text-green-400' : 'text-yellow-400'}>
                      {validationResult.checksum_match ? '✓' : '⚠'} 校验和{validationResult.checksum_match ? '匹配' : '不匹配'}
                    </span>
                  </div>
                  {validationResult.errors.length > 0 && (
                    <div className="text-red-300">
                      错误: {validationResult.errors.join(', ')}
                    </div>
                  )}
                  {validationResult.warnings.length > 0 && (
                    <div className="text-yellow-300">
                      警告: {validationResult.warnings.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Diff result */}
            {diffResult && (
              <div className="flex-1 flex flex-col min-h-0">
                <div className="p-3 border-b border-gray-700 bg-gray-800/30 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <GitCompare size={14} className="text-purple-400" />
                    <span className="text-sm text-gray-300">
                      {getRoundLabel(diffResult.from_round)} → {getRoundLabel(diffResult.to_round)}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-gray-400">
                      {formatSize(diffResult.from_size)} → {formatSize(diffResult.to_size)}
                    </span>
                    <span className="text-green-400">+{diffResult.additions}</span>
                    <span className="text-red-400">-{diffResult.deletions}</span>
                  </div>
                </div>
                <div className="flex-1 overflow-y-auto bg-gray-950 p-3 font-mono text-xs">
                  {diffResult.diff_lines.length > 0 ? (
                    diffResult.diff_lines.map((line, idx) => (
                      <div
                        key={idx}
                        className={`${
                          line.startsWith('+') && !line.startsWith('+++')
                            ? 'bg-green-500/20 text-green-300'
                            : line.startsWith('-') && !line.startsWith('---')
                            ? 'bg-red-500/20 text-red-300'
                            : line.startsWith('@@')
                            ? 'text-blue-400'
                            : 'text-gray-400'
                        } whitespace-pre`}
                      >
                        {line}
                      </div>
                    ))
                  ) : (
                    <div className="text-gray-500 text-center py-8">无差异</div>
                  )}
                </div>
              </div>
            )}

            {/* Preview content */}
            {!diffResult && (
              <div className="flex-1 flex flex-col min-h-0">
                {selectedArchive ? (
                  <>
                    <div className="p-3 border-b border-gray-700 bg-gray-800/30 flex items-center gap-2">
                      <FileCode size={14} className="text-blue-400" />
                      <span className="text-sm text-gray-300">
                        {selectedArchive.custom_name || getRoundLabel(selectedArchive.round_number)} - 预览
                      </span>
                    </div>
                    <div className="flex-1 overflow-y-auto bg-gray-950 p-3">
                      {previewLoading ? (
                        <div className="flex items-center justify-center h-full text-gray-500">
                          <Loader2 size={20} className="animate-spin mr-2" />
                          加载中...
                        </div>
                      ) : previewContent ? (
                        <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono">
                          {previewContent.slice(0, 10000)}
                          {previewContent.length > 10000 && (
                            <span className="text-gray-500">... (已截断，共 {previewContent.length} 字符)</span>
                          )}
                        </pre>
                      ) : (
                        <div className="flex flex-col items-center justify-center h-full text-gray-500">
                          <AlertCircle size={20} className="mb-2" />
                          <p className="text-sm">无法加载内容</p>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                    <FileCode size={32} className="mb-2 opacity-30" />
                    <p className="text-sm">选择存档查看预览</p>
                    <p className="text-xs text-gray-600 mt-1">或使用版本对比功能</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-gray-700 bg-gray-800/50 flex items-center justify-between">
          <div className="text-xs text-gray-500">
            点击存档项查看内容，使用按钮进行下载、验证、还原或删除操作
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors text-sm"
          >
            关闭
          </button>
        </div>
      </div>

      {/* Create Archive Modal */}
      {showCreateModal && (
        <div className="absolute inset-0 bg-black/60 flex items-center justify-center z-10">
          <div className="bg-gray-800 rounded-lg p-5 w-[400px] border border-gray-600">
            <div className="flex items-center gap-2 mb-4">
              <Save size={18} className="text-blue-400" />
              <h3 className="text-white font-medium">创建手动存档</h3>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">存档名称（可选）</label>
                <input
                  type="text"
                  value={createName}
                  onChange={(e) => setCreateName(e.target.value)}
                  placeholder="例如：修复Bug后的版本"
                  className="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">描述（可选）</label>
                <textarea
                  value={createDesc}
                  onChange={(e) => setCreateDesc(e.target.value)}
                  placeholder="描述这个版本的变更内容..."
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-white text-sm focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-5">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setCreateName('');
                  setCreateDesc('');
                }}
                className="px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 text-sm"
              >
                取消
              </button>
              <button
                onClick={handleCreateArchive}
                disabled={creating}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 text-sm flex items-center gap-1 disabled:opacity-50"
              >
                {creating ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    创建中...
                  </>
                ) : (
                  <>
                    <Save size={14} />
                    创建存档
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
