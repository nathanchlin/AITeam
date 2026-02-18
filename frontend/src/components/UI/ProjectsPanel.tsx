import { useState, useEffect } from 'react';
import { X, ExternalLink, Folder, RefreshCw, MessageCircle, ChevronRight } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, AGENT_LABELS } from '../../types';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000';

interface ProjectFile {
  name: string;
  size: number;
  modified: number;
}

interface DiscussionMessage {
  id: string;
  plan_id: string;
  agent_id: string;
  agent_name: string;
  agent_type: string;
  content: string;
  message_type: string;
  timestamp: string;
}

interface Project {
  id: string;
  title: string;
  path: string;
  files: ProjectFile[];
  file_count: number;
  total_size: number;
  has_preview: boolean;
  has_discussion: boolean;
  preview_url: string | null;
  modified: number;
}

export function ProjectsPanel() {
  const { projectsPanelOpen, toggleProjectsPanel } = useAgentStore();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [discussion, setDiscussion] = useState<DiscussionMessage[]>([]);
  const [discussionTitle, setDiscussionTitle] = useState('');
  const [loadingDiscussion, setLoadingDiscussion] = useState(false);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/projects/`);
      const data = await res.json();
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDiscussion = async (projectId: string) => {
    setLoadingDiscussion(true);
    try {
      const res = await fetch(`${API_BASE}/api/projects/${projectId}/discussion`);
      const data = await res.json();
      setDiscussion(data.discussion || []);
      setDiscussionTitle(data.title || projectId);
    } catch (error) {
      console.error('Failed to fetch discussion:', error);
      setDiscussion([]);
    } finally {
      setLoadingDiscussion(false);
    }
  };

  const handleViewDiscussion = async (project: Project) => {
    setSelectedProject(project);
    await fetchDiscussion(project.id);
  };

  const handleCloseDiscussion = () => {
    setSelectedProject(null);
    setDiscussion([]);
    setDiscussionTitle('');
  };

  useEffect(() => {
    if (projectsPanelOpen) {
      fetchProjects();
    }
  }, [projectsPanelOpen]);

  if (!projectsPanelOpen) return null;

  // Discussion view
  if (selectedProject) {
    return (
      <div className="absolute top-16 left-4 w-[450px] max-h-[700px] bg-gray-900/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between bg-gray-800">
          <div className="flex items-center gap-3">
            <button
              onClick={handleCloseDiscussion}
              className="p-1 hover:bg-gray-700 rounded transition-colors text-gray-400"
            >
              <ChevronRight size={16} className="rotate-180" />
            </button>
            <MessageCircle size={20} className="text-blue-400" />
            <div>
              <h2 className="text-white font-bold text-sm">群聊记录</h2>
              <p className="text-xs text-gray-400 truncate max-w-[280px]">{discussionTitle}</p>
            </div>
          </div>
          <button
            onClick={toggleProjectsPanel}
            className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
          >
            <X size={16} />
          </button>
        </div>

        {/* Discussion Content */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {loadingDiscussion ? (
            <div className="flex flex-col items-center justify-center h-32 text-gray-400">
              <RefreshCw size={24} className="animate-spin mb-2" />
              <p className="text-sm">加载群聊记录...</p>
            </div>
          ) : discussion.length > 0 ? (
            discussion.map((msg) => (
              <div
                key={msg.id}
                className={`p-3 rounded border-l-2 ${
                  msg.message_type === 'proposal' ? 'border-l-blue-500 bg-blue-500/10' :
                  msg.message_type === 'question' ? 'border-l-yellow-500 bg-yellow-500/10' :
                  msg.message_type === 'answer' ? 'border-l-green-500 bg-green-500/10' :
                  msg.message_type === 'agreement' ? 'border-l-purple-500 bg-purple-500/10' :
                  'border-l-gray-500 bg-gray-500/10'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                    style={{
                      backgroundColor: msg.agent_name === '系统' ? '#10B981' : (AGENT_COLORS[msg.agent_type as keyof typeof AGENT_COLORS]?.primary || '#888'),
                    }}
                  >
                    {msg.agent_name.charAt(0)}
                  </div>
                  <span className="text-sm font-medium text-white">{msg.agent_name}</span>
                  {msg.agent_name !== '系统' && (
                    <span className="text-xs text-gray-500">
                      {AGENT_LABELS[msg.agent_type as keyof typeof AGENT_LABELS] || msg.agent_type}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-300 whitespace-pre-wrap">{msg.content}</p>
                {/* Clickable links */}
                {msg.content.includes('http://') && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {msg.content.match(/http:\/\/[^\s]+/g)?.map((url, i) => (
                      <a
                        key={i}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-2 py-1 bg-blue-600/30 hover:bg-blue-600/50 rounded text-xs text-blue-300 transition-colors"
                      >
                        <ExternalLink size={12} />
                        打开网页
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center h-32 text-gray-400">
              <MessageCircle size={32} className="mb-2 opacity-30" />
              <p className="text-sm">暂无群聊记录</p>
            </div>
          )}
        </div>

        {/* Footer with actions */}
        {selectedProject.has_preview && (
          <div className="p-3 border-t border-gray-700 bg-gray-800/50">
            <a
              href={`${API_BASE}${selectedProject.preview_url}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded text-sm transition-colors"
            >
              <ExternalLink size={14} />
              打开项目预览
            </a>
          </div>
        )}
      </div>
    );
  }

  // Projects list view
  return (
    <div className="absolute top-16 left-4 w-[420px] max-h-[550px] bg-gray-900/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between bg-gray-800">
        <div className="flex items-center gap-3">
          <Folder size={20} className="text-yellow-400" />
          <h2 className="text-white font-bold">已生成的项目</h2>
          <span className="text-xs text-gray-400">({projects.length})</span>
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
              key={project.id}
              className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <h3 className="text-white text-sm font-medium truncate">
                    {project.title}
                  </h3>
                  <p className="text-gray-500 text-xs mt-1">
                    {project.file_count} 个文件 · {(project.total_size / 1024).toFixed(1)} KB
                  </p>
                </div>
                <div className="flex gap-2 ml-2">
                  {project.has_discussion && (
                    <button
                      onClick={() => handleViewDiscussion(project)}
                      className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs transition-colors whitespace-nowrap"
                      title="查看群聊记录"
                    >
                      <MessageCircle size={12} />
                      群聊
                    </button>
                  )}
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
              </div>

              {/* File list - only show if files are loaded */}
              {project.files && project.files.length > 0 && (
                <div className="mt-3 space-y-1 max-h-24 overflow-y-auto">
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
              )}
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
