import { useState, useEffect } from 'react';
import { X, ExternalLink, Folder, RefreshCw } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000';

interface OutputProject {
  plan_id: string;
  title?: string;
  original_request?: string;
  output_dir: string;
  files: Array<{
    name: string;
    size: number;
    modified: number;
  }>;
  has_preview: boolean;
  preview_url?: string;
}

export function ProjectsPanel() {
  const { projectsPanelOpen, toggleProjectsPanel } = useAgentStore();
  const [projects, setProjects] = useState<OutputProject[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      // Get all plans
      const plansRes = await fetch(`${API_BASE}/api/pipeline/plans`);
      const plans = await plansRes.json();

      // Get output for each completed plan
      const projectPromises = plans
        .filter((p: { status: string }) => p.status === 'completed')
        .map(async (p: { id: string; title: string; original_request: string }) => {
          try {
            const outputRes = await fetch(`${API_BASE}/api/pipeline/output/${p.id}`);
            const outputData = await outputRes.json();

            const previewRes = await fetch(`${API_BASE}/api/pipeline/output/${p.id}/preview`);
            const previewData = await previewRes.json();

            return {
              plan_id: p.id,
              title: p.title,
              original_request: p.original_request,
              output_dir: outputData.output_dir,
              files: outputData.files || [],
              has_preview: previewData.has_preview,
              preview_url: previewData.preview_url,
            };
          } catch {
            return null;
          }
        });

      const results = await Promise.all(projectPromises);
      setProjects(results.filter(Boolean) as OutputProject[]);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectsPanelOpen) {
      fetchProjects();
    }
  }, [projectsPanelOpen]);

  if (!projectsPanelOpen) return null;

  return (
    <div className="absolute top-16 left-4 w-[400px] max-h-[500px] bg-gray-900/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between bg-gray-800">
        <div className="flex items-center gap-3">
          <Folder size={20} className="text-yellow-400" />
          <h2 className="text-white font-bold">已生成的项目</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchProjects}
            disabled={loading}
            className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
            title="刷新"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={toggleProjectsPanel}
            className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-32 text-gray-400">
            <RefreshCw size={24} className="animate-spin mb-2" />
            <p className="text-sm">加载中...</p>
          </div>
        ) : projects.length > 0 ? (
          projects.map((project) => (
            <div
              key={project.plan_id}
              className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <h3 className="text-white text-sm font-medium truncate">
                    {project.title || '未命名项目'}
                  </h3>
                  <p className="text-gray-500 text-xs mt-1">
                    {project.files.length} 个文件
                  </p>
                </div>
                {project.has_preview && (
                  <a
                    href={`${API_BASE}${project.preview_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 px-3 py-1.5 bg-green-600 hover:bg-green-500 text-white rounded text-xs transition-colors whitespace-nowrap"
                  >
                    <ExternalLink size={12} />
                    打开
                  </a>
                )}
              </div>

              {/* File list */}
              <div className="mt-3 space-y-1">
                {project.files.slice(0, 5).map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between text-xs"
                  >
                    <span className="text-gray-400 truncate">{file.name}</span>
                    <span className="text-gray-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                ))}
                {project.files.length > 5 && (
                  <div className="text-xs text-gray-500">
                    还有 {project.files.length - 5} 个文件...
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center h-32 text-gray-400">
            <Folder size={32} className="mb-2 opacity-30" />
            <p className="text-sm">暂无已完成的项目</p>
          </div>
        )}
      </div>
    </div>
  );
}
