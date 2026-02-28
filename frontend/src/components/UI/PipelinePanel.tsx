import { useState, useRef, useEffect, useCallback } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, AGENT_LABELS, getAgentDisplayType } from '../../types';
import { X, Play, GitBranch, MessageCircle, CheckCircle, Loader2, Users, ExternalLink, Copy, Check, RotateCw, Trash2, RefreshCw, Layers, Archive, Undo2, Square } from 'lucide-react';
import { ArchivePanel } from './ArchivePanel';

const API_BASE = import.meta.env.PROD ? '' : `http://${window.location.hostname}:8000`;

// Default panel size
const DEFAULT_WIDTH = 900;
const DEFAULT_HEIGHT = 700;
const MIN_WIDTH = 600;
const MIN_HEIGHT = 400;
const MAX_WIDTH = 1400;
const MAX_HEIGHT = 900;

export function PipelinePanel() {
  const {
    pipelinePanelOpen,
    togglePipelinePanel,
    plans,
    currentPlanId,
    setCurrentPlan,
    streamContent,
    agents,
    updatePlan,
    setPlans,
    activeIterationTab,
    setActiveIterationTab,
  } = useAgentStore();

  const [request, setRequest] = useState('');
  const [targetOutput, setTargetOutput] = useState('web-app');
  const [selectedAgentIds, setSelectedAgentIds] = useState<string[]>([]);
  const [starting, setStarting] = useState(false);
  const [resuming, setResuming] = useState(false);
  const [restarting, setRestarting] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [restartMessage, setRestartMessage] = useState('');
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [iterating, setIterating] = useState(false);
  const [archives, setArchives] = useState<Array<{ round_number: number; label: string; archive_path: string; modified_at: string }>>([]);
  const [restoring, setRestoring] = useState(false);
  const [restoreMessage, setRestoreMessage] = useState('');
  const [showArchivePanel, setShowArchivePanel] = useState(false);
  const [godotProjectInfo, setGodotProjectInfo] = useState<any>(null);
  const [godotDownloading, setGodotDownloading] = useState(false);
  const [approving, setApproving] = useState(false);
  const [rejecting, setRejecting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pollingRef = useRef<number | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  // Panel size state with localStorage persistence
  const [panelSize, setPanelSize] = useState(() => {
    const saved = localStorage.getItem('pipelinePanelSize');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return { width: DEFAULT_WIDTH, height: DEFAULT_HEIGHT };
      }
    }
    return { width: DEFAULT_WIDTH, height: DEFAULT_HEIGHT };
  });

  // Resize handling
  const [isResizing, setIsResizing] = useState(false);
  const resizeStartRef = useRef({ x: 0, y: 0, width: 0, height: 0 });

  const handleResizeStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    resizeStartRef.current = {
      x: e.clientX,
      y: e.clientY,
      width: panelSize.width,
      height: panelSize.height,
    };
  }, [panelSize]);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      const deltaX = resizeStartRef.current.x - e.clientX;
      const deltaYS = resizeStartRef.current.y - e.clientY;

      const newWidth = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, resizeStartRef.current.width + deltaX));
      const newHeight = Math.min(MAX_HEIGHT, Math.max(MIN_HEIGHT, resizeStartRef.current.height + deltaYS));

      setPanelSize({ width: newWidth, height: newHeight });
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      // Save to localStorage
      localStorage.setItem('pipelinePanelSize', JSON.stringify(panelSize));
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, panelSize]);

  const currentPlan = plans.find((p) => p.id === currentPlanId);
  const currentStream = currentPlanId ? streamContent[currentPlanId] || '' : '';

  // Get discussion messages from current plan (they're stored in the plan itself)
  // 根据 activeIterationTab 显示不同轮次的讨论
  const getDisplayDiscussions = () => {
    if (!currentPlan) return [];
    if (activeIterationTab === 0) {
      // 初始版本：显示主讨论
      return currentPlan.discussion || [];
    } else {
      // 迭代轮次：显示对应迭代的讨论
      const iteration = currentPlan.iterations?.find(i => i.round_number === activeIterationTab);
      return iteration?.discussion || [];
    }
  };
  const planDiscussions = getDisplayDiscussions();

  // 获取当前显示的任务列表
  const getDisplayTasks = () => {
    if (!currentPlan) return [];
    if (activeIterationTab === 0) {
      // 初始版本：显示主任务
      return currentPlan.tasks || [];
    } else {
      // 迭代轮次：显示对应迭代的任务
      const iteration = currentPlan.iterations?.find(i => i.round_number === activeIterationTab);
      return iteration?.tasks || [];
    }
  };
  const displayTasks = getDisplayTasks();

  // 获取当前迭代的运行任务
  const getRunningTask = () => {
    const tasks = getDisplayTasks();
    return tasks.find(t => t.status === 'running');
  };
  const runningTask = getRunningTask();

  // 获取当前迭代的任务进度
  const completedTasksCount = displayTasks.filter(t => t.status === 'completed').length;
  const totalTasks = displayTasks.length;

  // 检查当前计划/迭代是否处于待确认状态
  const isPendingApproval = () => {
    if (!currentPlan) return false;
    if (activeIterationTab === 0) {
      return currentPlan.status === 'pending_approval';
    } else {
      const iteration = currentPlan.iterations?.find(i => i.round_number === activeIterationTab);
      return iteration?.status === 'pending_approval';
    }
  };

  // Fetch all plans
  const fetchPlans = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/plans`);
      if (res.ok) {
        const plansData = await res.json();
        setPlans(plansData);
      }
    } catch (e) {
      console.error('Fetch plans error:', e);
    }
  };

  // Fetch archives for current plan
  const fetchArchives = async () => {
    if (!currentPlanId) return;
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/archives/${currentPlanId}`);
      if (res.ok) {
        const data = await res.json();
        setArchives(data.archives || []);
      }
    } catch (e) {
      console.error('Fetch archives error:', e);
    }
  };

  // Fetch Godot project info
  const fetchGodotProjectInfo = async () => {
    if (!currentPlanId || currentPlan?.target_output !== 'godot-game') return;
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/output/${currentPlanId}/godot`);
      if (res.ok) {
        const data = await res.json();
        setGodotProjectInfo(data.project);
      }
    } catch (e) {
      console.error('Fetch Godot project info error:', e);
    }
  };

  // Download Godot project as zip
  const handleDownloadGodot = async () => {
    if (!currentPlanId || godotDownloading) return;
    setGodotDownloading(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/output/${currentPlanId}/godot/download`);
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `godot_project_${currentPlanId.slice(0, 8)}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || '下载失败');
      }
    } catch (e) {
      console.error('Download Godot project error:', e);
      alert('下载失败：' + (e instanceof Error ? e.message : '网络错误'));
    } finally {
      setGodotDownloading(false);
    }
  };

  // Restore to a specific archive
  const handleRestoreArchive = async (roundNumber: number) => {
    if (!currentPlanId || restoring) return;

    const confirmMsg = roundNumber === 0
      ? '确定要还原到初始版本吗？当前代码将被覆盖。'
      : `确定要还原到迭代${roundNumber}版本吗？当前代码将被覆盖。`;
    if (!confirm(confirmMsg)) return;

    setRestoring(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/archives/${currentPlanId}/restore/${roundNumber}`, {
        method: 'POST',
      });
      const data = await res.json().catch(() => ({}));

      if (res.ok) {
        const label = roundNumber === 0 ? '初始版本' : `迭代${roundNumber}`;
        setRestoreMessage(`已成功还原到${label}`);
        setTimeout(() => setRestoreMessage(''), 3000);
        console.log('Archive restored:', data);
      } else {
        const msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || '还原失败');
        alert(msg);
      }
    } catch (e) {
      console.error('Restore archive error:', e);
      alert('还原失败：' + (e instanceof Error ? e.message : '网络或服务器错误'));
    } finally {
      setRestoring(false);
    }
  };

  // Fetch archives when plan changes or completes
  useEffect(() => {
    if (currentPlanId && currentPlan?.status === 'completed') {
      fetchArchives();
    }
  }, [currentPlanId, currentPlan?.status]);

  // Also fetch archives when any iteration completes
  useEffect(() => {
    if (!currentPlan?.iterations) return;
    // Check if any iteration just completed (has archive_path)
    const completedIterations = currentPlan.iterations.filter(
      iter => iter.status === 'completed' && iter.archive_path
    );
    if (completedIterations.length > 0 && currentPlanId) {
      fetchArchives();
    }
  }, [currentPlan?.iterations?.map(i => `${i.round_number}:${i.status}:${i.archive_path}`).join(',')]);

  // Fetch Godot project info when plan completes
  useEffect(() => {
    if (currentPlanId && currentPlan?.status === 'completed' && currentPlan?.target_output === 'godot-game') {
      fetchGodotProjectInfo();
    }
  }, [currentPlanId, currentPlan?.status, currentPlan?.target_output]);

  // Poll for plan updates when plan is active
  // Also polls when WebSocket is disconnected (fallback sync)
  useEffect(() => {
    if (currentPlanId && currentPlan && !['completed', 'draft'].includes(currentPlan.status)) {
      const pollPlan = async () => {
        try {
          const res = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`);
          if (res.ok) {
            const plan = await res.json();
            updatePlan(currentPlanId, plan);
          }
        } catch (e) {
          console.error('Poll plan error:', e);
        }
      };

      // Poll every 3 seconds when active
      pollingRef.current = window.setInterval(pollPlan, 3000);
      // Also poll immediately
      pollPlan();

      return () => {
        if (pollingRef.current) clearInterval(pollingRef.current);
      };
    }
  }, [currentPlanId, currentPlan?.status, updatePlan]);

  // Fallback: periodic sync even when status appears stuck (e.g., missed WebSocket updates)
  useEffect(() => {
    if (!currentPlanId || !currentPlan) return;
    if (['completed', 'draft'].includes(currentPlan.status)) return;

    // Check every 10 seconds if we need to sync
    const fallbackSync = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`);
        if (res.ok) {
          const serverPlan = await res.json();
          // If server shows completed but local doesn't, sync it
          if (serverPlan.status === 'completed' && currentPlan.status !== 'completed') {
            console.log('[PipelinePanel] Fallback sync detected completed status');
            updatePlan(currentPlanId, serverPlan);
          }
          // If server shows different task status, sync it
          const localRunningTasks = currentPlan.tasks.filter(t => t.status === 'running');
          if (localRunningTasks.length > 0) {
            const serverTaskMap = new Map(serverPlan.tasks.map((t: { id: string; status: string }) => [t.id, t.status]));
            for (const task of localRunningTasks) {
              const serverStatus = serverTaskMap.get(task.id);
              if (serverStatus === 'completed' && task.status === 'running') {
                console.log('[PipelinePanel] Fallback sync detected task completion');
                updatePlan(currentPlanId, serverPlan);
                break;
              }
            }
          }
        }
      } catch (e) {
        console.error('[PipelinePanel] Fallback sync error:', e);
      }
    };

    const fallbackInterval = window.setInterval(fallbackSync, 10000);
    return () => clearInterval(fallbackInterval);
  }, [currentPlanId, currentPlan, updatePlan]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [planDiscussions.length, currentStream]);

  const handleStartPipeline = async () => {
    if (!request.trim() || starting) return;

    setStarting(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request: request.trim(),
          target_output: targetOutput,
          selected_agent_ids: selectedAgentIds,
        }),
      });
      const data = await res.json();
      console.log('Pipeline started:', data);
      setCurrentPlan(data.plan_id);
      setRequest('');
      setSelectedAgentIds([]);

      // Immediately fetch the new plan to refresh the list
      await fetchPlans();
    } catch (error) {
      console.error('Failed to start pipeline:', error);
    } finally {
      setStarting(false);
    }
  };

  const toggleAgentSelection = (agentId: string) => {
    setSelectedAgentIds(prev =>
      prev.includes(agentId)
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };

  const selectAllAgents = () => {
    setSelectedAgentIds(agents.map(a => a.id));
  };

  const clearAgentSelection = () => {
    setSelectedAgentIds([]);
  };

  const handleResumePipeline = async () => {
    if (!currentPlanId || resuming) return;
    setResuming(true);
    try {
      // 根据当前选中的 tab 决定恢复目标
      const isIteration = activeIterationTab > 0;
      const url = isIteration
        ? `${API_BASE}/api/pipeline/resume/${currentPlanId}/iteration/${activeIterationTab}`
        : `${API_BASE}/api/pipeline/resume/${currentPlanId}`;
      const res = await fetch(url, { method: 'POST' });
      if (res.ok) {
        await fetchPlans();
        const data = await res.json();
        console.log('Pipeline/Iteration resumed:', data);
      }
    } catch (e) {
      console.error('Resume pipeline error:', e);
    } finally {
      setResuming(false);
    }
  };

  const handleRestartPipeline = async () => {
    if (!currentPlanId || restarting) return;

    // 根据当前选中的 tab 决定重启目标
    const isIteration = activeIterationTab > 0;
    const confirmMsg = isIteration
      ? `确定要重启迭代${activeIterationTab}吗？将清空该迭代的任务与讨论，重新执行。`
      : '确定要重启该流水线吗？将清空当前任务与讨论，从需求分析重新开始。';
    if (!confirm(confirmMsg)) return;

    setRestarting(true);
    try {
      const url = isIteration
        ? `${API_BASE}/api/pipeline/restart/${currentPlanId}/iteration/${activeIterationTab}`
        : `${API_BASE}/api/pipeline/restart/${currentPlanId}`;
      const res = await fetch(url, { method: 'POST' });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        // 先刷新列表，再单独拉取当前计划，确保 UI 拿到最新状态
        await fetchPlans();
        const planRes = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`);
        if (planRes.ok) {
          const updatedPlan = await planRes.json();
          updatePlan(currentPlanId, updatedPlan);
          // 如果是迭代重启，切换到对应迭代 tab
          if (isIteration) {
            setActiveIterationTab(activeIterationTab);
          }
        }
        setRestartMessage(isIteration ? `迭代${activeIterationTab}已重启…` : '流水线已重启，正在重新分析需求…');
        setTimeout(() => setRestartMessage(''), 4000);
        console.log('Pipeline/Iteration restarted:', data);
      } else {
        const msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || '重启失败');
        alert(msg);
      }
    } catch (e) {
      console.error('Restart pipeline error:', e);
      alert('重启失败：' + (e instanceof Error ? e.message : '网络或服务器错误'));
    } finally {
      setRestarting(false);
    }
  };

  const handleStopIteration = async () => {
    if (!currentPlanId || stopping || activeIterationTab <= 0) return;

    if (!confirm(`确定要停止迭代${activeIterationTab}吗？`)) return;

    setStopping(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/stop/${currentPlanId}/iteration/${activeIterationTab}`, {
        method: 'POST',
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setRestartMessage(`已发送停止请求，迭代${activeIterationTab}将在当前任务完成后停止…`);
        setTimeout(() => setRestartMessage(''), 4000);
        console.log('Stop iteration requested:', data);
      } else {
        const msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || '停止失败');
        alert(msg);
      }
    } catch (e) {
      console.error('Stop iteration error:', e);
      alert('停止失败：' + (e instanceof Error ? e.message : '网络或服务器错误'));
    } finally {
      setStopping(false);
    }
  };

  const handleDeletePipeline = async () => {
    if (!currentPlanId || deleting) return;
    if (!confirm('确定要删除该流水线吗？删除后无法恢复。')) return;
    setDeleting(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`, { method: 'DELETE' });
      if (res.ok) {
        await fetchPlans();
        const remaining = plans.filter((p) => p.id !== currentPlanId);
        setCurrentPlan(remaining.length > 0 ? remaining[0].id : null);
        console.log('Pipeline deleted:', currentPlanId);
      } else {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || '删除失败');
      }
    } catch (e) {
      console.error('Delete pipeline error:', e);
      alert('删除失败');
    } finally {
      setDeleting(false);
    }
  };

  const handleIterate = async () => {
    if (!currentPlanId || !request.trim() || iterating) return;
    setIterating(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/iterate/${currentPlanId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ iteration_request: request.trim() }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setRequest(''); // 清空输入框
        // Poll for updates
        await fetchPlans();
        // 切换到新的迭代轮次 tab（在 plans 更新后）
        // 新轮次号 = 当前迭代数 + 1
        const planRes = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`);
        if (planRes.ok) {
          const updatedPlan = await planRes.json();
          updatePlan(currentPlanId, updatedPlan);
          // 设置新的迭代 tab
          if (updatedPlan.current_iteration_round) {
            setActiveIterationTab(updatedPlan.current_iteration_round);
          }
        }
        console.log('Iteration started:', data);
      } else {
        const msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || '迭代失败');
        alert(msg);
      }
    } catch (e) {
      console.error('Iterate error:', e);
      alert('迭代失败：' + (e instanceof Error ? e.message : '网络或服务器错误'));
    } finally {
      setIterating(false);
    }
  };

  const handleApprovePlan = async () => {
    if (!currentPlanId || approving) return;
    setApproving(true);
    try {
      const isIteration = activeIterationTab > 0;
      const url = isIteration
        ? `${API_BASE}/api/pipeline/plans/${currentPlanId}/iterations/${activeIterationTab}/approve`
        : `${API_BASE}/api/pipeline/plans/${currentPlanId}/approve`;
      const res = await fetch(url, { method: 'POST' });
      if (res.ok) {
        await fetchPlans();
        console.log('Plan approved');
      }
    } catch (e) {
      console.error('Approve plan error:', e);
    } finally {
      setApproving(false);
    }
  };

  const handleRejectPlan = async () => {
    if (!currentPlanId || rejecting) return;
    const feedback = prompt('请输入拒绝原因（可选）：') || '';
    setRejecting(true);
    try {
      const isIteration = activeIterationTab > 0;
      const url = isIteration
        ? `${API_BASE}/api/pipeline/plans/${currentPlanId}/iterations/${activeIterationTab}/reject?feedback=${encodeURIComponent(feedback)}`
        : `${API_BASE}/api/pipeline/plans/${currentPlanId}/reject?feedback=${encodeURIComponent(feedback)}`;
      const res = await fetch(url, { method: 'POST' });
      if (res.ok) {
        await fetchPlans();
        console.log('Plan rejected');
      }
    } catch (e) {
      console.error('Reject plan error:', e);
    } finally {
      setRejecting(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'text-gray-400',
      discussing: 'text-yellow-400',
      approved: 'text-blue-400',
      pending_approval: 'text-orange-400',
      executing: 'text-green-400',
      completed: 'text-green-500',
    };
    return colors[status] || 'text-gray-400';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      draft: '草稿',
      discussing: '讨论中',
      approved: '已批准',
      pending_approval: '待确认',
      executing: '执行中',
      completed: '已完成',
    };
    return labels[status] || status;
  };

  const getStatusBgColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-500',
      discussing: 'bg-yellow-500',
      approved: 'bg-blue-500',
      pending_approval: 'bg-orange-500',
      executing: 'bg-green-500',
      completed: 'bg-green-600',
    };
    return colors[status] || 'bg-gray-500';
  };

  const getPhaseInfo = (status: string) => {
    const phases = [
      { key: 'draft', label: '需求分析', icon: '📋' },
      { key: 'discussing', label: '团队讨论', icon: '💬' },
      { key: 'approved', label: '计划确认', icon: '✅' },
      { key: 'pending_approval', label: '待确认', icon: '⏳' },
      { key: 'executing', label: '执行开发', icon: '⚙️' },
      { key: 'completed', label: '完成交付', icon: '🎉' },
    ];
    const currentIndex = phases.findIndex(p => p.key === status);
    return { phases, currentIndex };
  };

  const getMessageTypeStyle = (type: string) => {
    const styles: Record<string, string> = {
      proposal: 'border-l-blue-500 bg-blue-500/10',
      question: 'border-l-yellow-500 bg-yellow-500/10',
      answer: 'border-l-green-500 bg-green-500/10',
      agreement: 'border-l-purple-500 bg-purple-500/10',
      comment: 'border-l-gray-500 bg-gray-500/10',
    };
    return styles[type] || styles.comment;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedUrl(true);
    setTimeout(() => setCopiedUrl(false), 2000);
  };

  if (!pipelinePanelOpen) return null;

  const { phases, currentIndex } = getPhaseInfo(currentPlan?.status || 'draft');
  // 显示链接的条件：web-app类型且有计划ID（不要求completed，只要有HTML就可能访问）
  const outputUrl = currentPlan?.id && currentPlan?.target_output === 'web-app'
    ? `${API_BASE}/api/pipeline/output/${currentPlan.id}/files/index.html`
    : null;

  return (
    <div
      ref={panelRef}
      className="absolute top-16 left-1/2 transform -translate-x-1/2 bg-gray-900/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700"
      style={{
        width: panelSize.width,
        height: panelSize.height,
        maxWidth: '95vw',
        maxHeight: '85vh',
      }}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between bg-gray-800">
        <div className="flex items-center gap-3">
          <GitBranch size={20} className="text-purple-400" />
          <h2 className="text-white font-bold">协作流水线</h2>
          <span className="text-xs text-gray-400">讨论 → 计划 → 执行</span>
        </div>
        <button
          onClick={togglePipelinePanel}
          className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
        >
          <X size={16} />
        </button>
      </div>

      {/* Input Section */}
      <div className="p-4 border-b border-gray-700 bg-gray-800/50">
        <div className="space-y-3">
          <textarea
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            placeholder={
              currentPlan?.status === 'completed'
                ? currentPlan?.target_output === 'godot-game'
                  ? "输入迭代需求，例如：添加关卡系统..."
                  : "输入迭代需求，例如：我想添加一个规则，当敌机穿过屏幕底部时，生命值减1..."
                : "输入你的需求，例如：我需要做一个贪吃蛇游戏..."
            }
            className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white text-sm border border-gray-600 focus:border-purple-500 focus:outline-none resize-none"
            rows={2}
            disabled={starting || iterating}
          />

          {/* Agent Selection */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">选择协作 Agent：</span>
              <div className="flex gap-2">
                <button
                  onClick={selectAllAgents}
                  className="text-xs text-purple-400 hover:text-purple-300"
                >
                  全选
                </button>
                <span className="text-gray-600">|</span>
                <button
                  onClick={clearAgentSelection}
                  className="text-xs text-gray-400 hover:text-gray-300"
                >
                  清除
                </button>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {agents.map((agent) => {
                const isSelected = selectedAgentIds.includes(agent.id);
                const agentColor = AGENT_COLORS[agent.type as keyof typeof AGENT_COLORS]?.primary || '#888';
                return (
                  <button
                    key={agent.id}
                    onClick={() => toggleAgentSelection(agent.id)}
                    className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-all ${
                      isSelected
                        ? 'ring-2 ring-offset-1 ring-offset-gray-800'
                        : 'opacity-60 hover:opacity-100'
                    }`}
                    style={{
                      backgroundColor: isSelected ? agentColor : `${agentColor}40`,
                      color: isSelected ? 'white' : '#ccc',
                    }}
                  >
                    <div
                      className="w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold"
                      style={{ backgroundColor: agentColor }}
                    >
                      {agent.name.charAt(0)}
                    </div>
                    <span>{agent.name}</span>
                    <span className="text-[10px] opacity-70">
                      ({getAgentDisplayType(agent)})
                    </span>
                    {isSelected && (
                      <Check size={12} className="ml-0.5" />
                    )}
                  </button>
                );
              })}
            </div>
            {selectedAgentIds.length === 0 && (
              <p className="text-xs text-yellow-500">
                未选择 Agent，将使用所有可用 Agent
              </p>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">目标输出：</span>
              <select
                value={targetOutput}
                onChange={(e) => setTargetOutput(e.target.value)}
                className="px-2 py-1 bg-gray-700 rounded text-white text-xs border border-gray-600"
              >
                <option value="web-app">Web应用</option>
                <option value="godot-game">Godot游戏</option>
                <option value="api">API服务</option>
                <option value="report">分析报告</option>
                <option value="documentation">文档</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              {/* 当有输出文件时，显示迭代按钮（不需要等到完成） */}
              {currentPlan && (outputUrl || currentPlan?.target_output === 'godot-game') && (
                <button
                  onClick={handleIterate}
                  disabled={!request.trim() || iterating}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  {iterating ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      迭代中...
                    </>
                  ) : (
                    <>
                      <RefreshCw size={16} />
                      开始迭代
                    </>
                  )}
                </button>
              )}
              <button
                onClick={handleStartPipeline}
                disabled={!request.trim() || starting}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                {starting ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    启动中...
                  </>
                ) : (
                  <>
                    <Play size={16} />
                    启动流水线
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content Section - Scrollable */}
      <div className="flex-1 overflow-y-auto flex flex-col">
        {currentPlan ? (
          <>
            {/* Progress Bar */}
            <div className="p-4 border-b border-gray-700 bg-gray-800/30">
              <div className="flex items-center justify-between mb-2">
                <span className={`text-sm font-medium ${getStatusColor(currentPlan.status)}`}>
                  {getStatusLabel(currentPlan.status)}
                </span>
                <div className="flex items-center gap-2 flex-wrap">
                  {totalTasks > 0 && (
                    <span className="text-xs text-gray-400">
                      任务进度: {completedTasksCount}/{totalTasks}
                    </span>
                  )}
                  {(() => {
                    // 根据当前 tab 获取正确的状态
                    if (activeIterationTab > 0) {
                      const iteration = currentPlan.iterations?.find(i => i.round_number === activeIterationTab);
                      return iteration?.status === 'executing' && completedTasksCount < totalTasks;
                    }
                    return currentPlan.status === 'executing' && completedTasksCount < totalTasks;
                  })() && (
                    <button
                      onClick={handleResumePipeline}
                      disabled={resuming}
                      className="px-3 py-1 text-xs font-medium rounded bg-amber-600 hover:bg-amber-500 text-white disabled:opacity-50 flex items-center gap-1"
                    >
                      {resuming ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                      {resuming ? '恢复中...' : '继续执行'}
                    </button>
                  )}
                  <button
                    onClick={handleRestartPipeline}
                    disabled={restarting}
                    title={activeIterationTab > 0 ? `清空迭代${activeIterationTab}的任务与讨论，重新执行` : "清空任务与讨论，从需求分析重新开始"}
                    className="px-3 py-1 text-xs font-medium rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 flex items-center gap-1"
                  >
                    {restarting ? <Loader2 size={12} className="animate-spin" /> : <RotateCw size={12} />}
                    {activeIterationTab > 0 ? `重启迭代${activeIterationTab}` : '重启流水线'}
                  </button>
                  {activeIterationTab > 0 && (() => {
                    const iteration = currentPlan.iterations?.find(i => i.round_number === activeIterationTab);
                    return iteration?.status === 'executing';
                  })() && (
                    <button
                      onClick={handleStopIteration}
                      disabled={stopping}
                      title={`强制停止迭代${activeIterationTab}`}
                      className="px-3 py-1 text-xs font-medium rounded bg-orange-600 hover:bg-orange-500 text-white disabled:opacity-50 flex items-center gap-1"
                    >
                      {stopping ? <Loader2 size={12} className="animate-spin" /> : <Square size={12} />}
                      {stopping ? '停止中...' : '停止迭代'}
                    </button>
                  )}
                  <button
                    onClick={handleDeletePipeline}
                    disabled={deleting}
                    title="删除该流水线，不可恢复"
                    className="px-3 py-1 text-xs font-medium rounded bg-red-600/80 hover:bg-red-500 text-white disabled:opacity-50 flex items-center gap-1"
                  >
                    {deleting ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
                    删除流水线
                  </button>
                </div>
              </div>

              {/* Phase Progress */}
              <div className="flex items-center gap-1 mb-3">
                {phases.map((phase, index) => (
                  <div key={phase.key} className="flex items-center flex-1">
                    <div
                      className={`flex items-center justify-center w-8 h-8 rounded-full text-sm transition-all ${
                        index <= currentIndex
                          ? `${getStatusBgColor(currentPlan.status)} text-white`
                          : 'bg-gray-700 text-gray-500'
                      } ${index === currentIndex ? 'ring-2 ring-white/30' : ''}`}
                    >
                      {index < currentIndex ? '✓' : phase.icon}
                    </div>
                    {index < phases.length - 1 && (
                      <div className={`flex-1 h-1 mx-1 rounded ${
                        index < currentIndex ? 'bg-green-500' : 'bg-gray-700'
                      }`} />
                    )}
                  </div>
                ))}
              </div>

              {/* Restart success hint */}
              {restartMessage && (
                <div className="flex items-center gap-2 p-2 bg-blue-500/10 rounded border border-blue-500/30">
                  <CheckCircle size={14} className="text-blue-400" />
                  <span className="text-sm text-blue-300">{restartMessage}</span>
                </div>
              )}
              {/* Plan Approval Banner */}
              {isPendingApproval() && (
                <div className="flex items-center gap-3 p-3 bg-orange-500/10 border border-orange-500/30 rounded">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-orange-300">⏳ 计划已生成，请确认后开始执行</div>
                    <div className="text-xs text-orange-400/70 mt-1">确认后将开始执行任务，拒绝后将返回讨论阶段</div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleRejectPlan}
                      disabled={rejecting}
                      className="px-3 py-1.5 bg-gray-600 hover:bg-gray-500 text-white rounded text-sm disabled:opacity-50 flex items-center gap-1"
                    >
                      {rejecting ? <Loader2 size={14} className="animate-spin" /> : null}
                      重新规划
                    </button>
                    <button
                      onClick={handleApprovePlan}
                      disabled={approving}
                      className="px-4 py-1.5 bg-green-600 hover:bg-green-500 text-white rounded text-sm disabled:opacity-50 flex items-center gap-1"
                    >
                      {approving ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} />}
                      确认执行
                    </button>
                  </div>
                </div>
              )}
              {/* Current Activity */}
              {runningTask && (
                <div className="flex items-center gap-2 p-2 bg-green-500/10 rounded border border-green-500/30">
                  <Loader2 size={14} className="animate-spin text-green-400" />
                  <span className="text-sm text-green-300">
                    正在执行: {runningTask.title}
                  </span>
                </div>
              )}
            </div>

            {/* Iteration Tabs */}
            {currentPlan && currentPlan.iterations && currentPlan.iterations.length > 0 && (
              <div className="px-4 py-2 border-b border-gray-700 bg-gray-800/20 flex items-center gap-2 overflow-x-auto">
                <Layers size={14} className="text-gray-400 flex-shrink-0" />
                <button
                  onClick={() => setActiveIterationTab(0)}
                  className={`px-3 py-1 rounded text-xs font-medium whitespace-nowrap transition-colors flex items-center gap-1 ${
                    activeIterationTab === 0
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  初始版本
                  {archives.some(a => a.round_number === 0) && (
                    <span title="已存档"><Archive size={10} className="text-blue-400 ml-1" /></span>
                  )}
                </button>
                {currentPlan.iterations.map((iteration) => {
                  const isActive = activeIterationTab === iteration.round_number;
                  const isCompleted = iteration.status === 'completed';
                  const isExecuting = iteration.status === 'executing';
                  const hasArchive = iteration.archive_path || archives.some(a => a.round_number === iteration.round_number);
                  return (
                    <div key={iteration.round_number} className="relative group">
                      <button
                        onClick={() => setActiveIterationTab(iteration.round_number)}
                        className={`px-3 py-1 rounded text-xs font-medium whitespace-nowrap transition-colors flex items-center gap-1 ${
                          isActive
                            ? 'bg-purple-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        {isCompleted && <CheckCircle size={10} className="text-green-400" />}
                        {isExecuting && <Loader2 size={10} className="animate-spin text-yellow-400" />}
                        迭代{iteration.round_number}
                        {hasArchive && (
                          <span title="已存档"><Archive size={10} className="text-blue-400 ml-1" /></span>
                        )}
                      </button>
                      {/* Restore dropdown for completed iterations with archive */}
                      {isCompleted && hasArchive && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRestoreArchive(iteration.round_number);
                          }}
                          disabled={restoring}
                          className="absolute -top-1 -right-1 w-5 h-5 bg-gray-600 hover:bg-blue-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                          title={`还原到迭代${iteration.round_number}版本`}
                        >
                          {restoring ? (
                            <Loader2 size={10} className="animate-spin text-white" />
                          ) : (
                            <Undo2 size={10} className="text-white" />
                          )}
                        </button>
                      )}
                    </div>
                  );
                })}
                {/* Restore message */}
                {restoreMessage && (
                  <div className="ml-auto flex items-center gap-1 px-2 py-1 bg-blue-500/20 rounded text-xs text-blue-300">
                    <CheckCircle size={12} />
                    {restoreMessage}
                  </div>
                )}
                {/* Archive management button */}
                {currentPlan?.status === 'completed' && archives.length > 0 && (
                  <button
                    onClick={() => setShowArchivePanel(true)}
                    className="ml-auto px-3 py-1 rounded text-xs font-medium whitespace-nowrap transition-colors flex items-center gap-1 bg-gray-700 text-gray-300 hover:bg-gray-600"
                  >
                    <Archive size={12} />
                    存档管理
                  </button>
                )}
              </div>
            )}

            {/* Archive Restore Section for Initial Version */}
            {currentPlan?.status === 'completed' && archives.length > 0 && activeIterationTab === 0 && archives.some(a => a.round_number === 0) && (
              <div className="px-4 py-2 border-b border-gray-700 bg-gray-800/10">
                <div className="flex items-center gap-2">
                  <Archive size={12} className="text-blue-400" />
                  <span className="text-xs text-gray-400">初始版本已存档</span>
                  <button
                    onClick={() => handleRestoreArchive(0)}
                    disabled={restoring}
                    className="ml-auto px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded flex items-center gap-1 disabled:opacity-50"
                  >
                    {restoring ? <Loader2 size={10} className="animate-spin" /> : <Undo2 size={10} />}
                    还原到此版本
                  </button>
                </div>
              </div>
            )}

            {/* Archive Restore Section for Iteration */}
            {currentPlan?.status === 'completed' && activeIterationTab > 0 && (() => {
              const iteration = currentPlan.iterations?.find(i => i.round_number === activeIterationTab);
              const hasArchive = iteration?.archive_path || archives.some(a => a.round_number === activeIterationTab);
              return hasArchive && iteration?.status === 'completed';
            })() && (
              <div className="px-4 py-2 border-b border-gray-700 bg-gray-800/10">
                <div className="flex items-center gap-2">
                  <Archive size={12} className="text-blue-400" />
                  <span className="text-xs text-gray-400">迭代{activeIterationTab}版本已存档</span>
                  <button
                    onClick={() => handleRestoreArchive(activeIterationTab)}
                    disabled={restoring}
                    className="ml-auto px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded flex items-center gap-1 disabled:opacity-50"
                  >
                    {restoring ? <Loader2 size={10} className="animate-spin" /> : <Undo2 size={10} />}
                    还原到此版本
                  </button>
                </div>
              </div>
            )}

            {/* Main Content Area - Split View */}
            <div className="flex-1 flex min-h-0">
              {/* Left: Group Chat */}
              <div className="w-1/2 flex flex-col border-r border-gray-700 min-h-0">
                <div className="p-3 border-b border-gray-700 bg-gray-800/50 flex items-center gap-2 flex-shrink-0">
                  <Users size={16} className="text-blue-400" />
                  <span className="text-sm font-medium text-white">
                    {activeIterationTab === 0 ? '团队群聊' : `迭代${activeIterationTab} 讨论`}
                  </span>
                  <span className="text-xs text-gray-500">({planDiscussions.length} 条消息)</span>
                </div>
                <div className="flex-1 overflow-y-auto p-3 space-y-2 min-h-0">
                  {planDiscussions.length > 0 ? (
                    planDiscussions.map((msg) => (
                      <div
                        key={msg.id}
                        className={`p-3 rounded border-l-2 ${getMessageTypeStyle(msg.message_type)}`}
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
                        {/* If message contains URL, make it clickable */}
                        {msg.content.includes('http://') && (
                          <div className="mt-2 flex gap-2">
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
                    <div className="flex flex-col items-center justify-center h-full text-gray-500">
                      <MessageCircle size={32} className="mb-2 opacity-30" />
                      <p className="text-sm">等待讨论开始...</p>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </div>

              {/* Right: Agent Work Panels */}
              <div className="w-1/2 flex flex-col min-h-0">
                <div className="p-3 border-b border-gray-700 bg-gray-800/50 flex items-center gap-2 flex-shrink-0">
                  <CheckCircle size={16} className="text-green-400" />
                  <span className="text-sm font-medium text-white">
                    {activeIterationTab === 0 ? '任务执行' : `迭代${activeIterationTab} 任务`}
                  </span>
                </div>
                <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
                  {/* Task List */}
                  {displayTasks.length > 0 ? (
                    <div className="space-y-2">
                      {displayTasks.map((task) => {
                        const assignedAgent = agents.find((a) => a.id === task.assigned_agent_id);
                        const isRunning = task.status === 'running';
                        const taskStream = streamContent[task.id] || '';

                        return (
                          <div
                            key={task.id}
                            className={`p-3 rounded border transition-all ${
                              isRunning
                                ? 'bg-green-500/10 border-green-500/50'
                                : task.status === 'completed'
                                ? 'bg-gray-700/30 border-gray-600'
                                : 'bg-gray-800/50 border-gray-700'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <div
                                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                                  task.status === 'completed'
                                    ? 'bg-green-500'
                                    : isRunning
                                    ? 'bg-yellow-500 animate-pulse'
                                    : 'bg-gray-600'
                                }`}
                              >
                                {task.status === 'completed' ? '✓' : task.order}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="text-sm text-white truncate">{task.title}</div>
                                {assignedAgent && (
                                  <div className="flex items-center gap-1 mt-1">
                                    <div
                                      className="w-4 h-4 rounded-full flex items-center justify-center text-[10px]"
                                      style={{ backgroundColor: AGENT_COLORS[assignedAgent.type]?.primary || '#888' }}
                                    >
                                      {assignedAgent.name.charAt(0)}
                                    </div>
                                    <span className="text-xs text-gray-400">{assignedAgent.name}</span>
                                  </div>
                                )}
                              </div>
                              <div
                                className={`text-xs px-2 py-1 rounded ${
                                  task.status === 'completed'
                                    ? 'bg-green-500/20 text-green-400'
                                    : isRunning
                                    ? 'bg-yellow-500/20 text-yellow-400'
                                    : 'bg-gray-600/50 text-gray-400'
                                }`}
                              >
                                {task.status === 'completed' ? '完成' : isRunning ? '执行中' : '等待'}
                              </div>
                            </div>

                            {/* Show stream content for running task */}
                            {isRunning && taskStream && (
                              <div className="mt-2 p-2 bg-gray-900/50 rounded text-xs text-gray-300 max-h-32 overflow-y-auto whitespace-pre-wrap border border-gray-700">
                                {taskStream.slice(-500)}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-gray-500">
                      <CheckCircle size={32} className="mb-2 opacity-30" />
                      <p className="text-sm">
                        {activeIterationTab > 0
                          ? '迭代计划生成中...'
                          : currentPlan.status === 'discussing'
                          ? '计划生成中...'
                          : '等待计划生成...'}
                      </p>
                      <p className="text-xs mt-1 text-gray-600">通常 1～2 分钟内完成，超时将自动使用兜底计划</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Final Result Section */}
            {currentPlan.status === 'completed' && (outputUrl || currentPlan.target_output === 'godot-game') && (
              <div className="p-4 border-t border-gray-700 bg-green-900/20 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center">
                      <CheckCircle size={20} className="text-white" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-white">
                        {currentPlan.target_output === 'godot-game' ? 'Godot 项目已完成' : '项目已完成'}
                      </div>
                      <div className="text-xs text-gray-400">
                        {currentPlan.target_output === 'godot-game'
                          ? '点击下载项目，用 Godot 4.3+ 打开运行'
                          : '点击下方链接查看结果，或在上方输入迭代需求'}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {/* Godot project buttons */}
                    {currentPlan.target_output === 'godot-game' && (
                      <>
                        {godotProjectInfo?.validation && (
                          <div className={`px-3 py-2 rounded text-sm flex items-center gap-2 ${
                            godotProjectInfo.validation.passed
                              ? 'bg-green-600/20 text-green-400'
                              : 'bg-yellow-600/20 text-yellow-400'
                          }`}>
                            {godotProjectInfo.validation.passed ? (
                              <>
                                <CheckCircle size={14} />
                                验证通过
                              </>
                            ) : (
                              <>
                                <span className="text-yellow-400">!</span>
                                {godotProjectInfo.validation.errors?.length || 0} 个问题
                              </>
                            )}
                          </div>
                        )}
                        <button
                          onClick={handleDownloadGodot}
                          disabled={godotDownloading}
                          className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-500 transition-colors flex items-center gap-2 text-sm disabled:opacity-50"
                        >
                          {godotDownloading ? (
                            <>
                              <Loader2 size={14} className="animate-spin" />
                              打包中...
                            </>
                          ) : (
                            <>
                              <Archive size={14} />
                              下载项目
                            </>
                          )}
                        </button>
                      </>
                    )}
                    {/* Web app buttons */}
                    {currentPlan.target_output !== 'godot-game' && (
                      <>
                        {archives.length > 0 && (
                          <button
                            onClick={() => setShowArchivePanel(true)}
                            className="px-3 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors flex items-center gap-2 text-sm"
                          >
                            <Archive size={14} />
                            存档管理
                          </button>
                        )}
                        <button
                          onClick={() => copyToClipboard(outputUrl || '')}
                          className="px-3 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors flex items-center gap-2 text-sm"
                        >
                          {copiedUrl ? <Check size={14} /> : <Copy size={14} />}
                          {copiedUrl ? '已复制' : '复制链接'}
                        </button>
                        <a
                          href={outputUrl || '#'}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-500 transition-colors flex items-center gap-2 text-sm"
                        >
                          <ExternalLink size={14} />
                          打开网页
                        </a>
                      </>
                    )}
                  </div>
                </div>
                {/* Godot validation warnings */}
                {currentPlan.target_output === 'godot-game' && godotProjectInfo?.validation?.warnings?.length > 0 && (
                  <div className="mt-3 p-2 bg-yellow-500/10 border border-yellow-500/30 rounded">
                    <div className="text-xs text-yellow-400 font-medium mb-1">注意事项：</div>
                    <ul className="text-xs text-yellow-300 space-y-1">
                      {godotProjectInfo.validation.warnings.slice(0, 3).map((w: string, i: number) => (
                        <li key={i}>- {w}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
            <GitBranch size={48} className="mb-4 opacity-30" />
            <p className="text-sm">输入需求开始协作</p>
            <p className="text-xs text-gray-500 mt-1">
              Agents 将自动讨论、制定计划并执行
            </p>
          </div>
        )}
      </div>

      {/* Plans List */}
      {plans.length > 0 && (
        <div className="p-3 border-t border-gray-700 bg-gray-800/50 flex-shrink-0">
          <div className="flex gap-2 overflow-x-auto">
            {plans.map((plan) => (
              <button
                key={plan.id}
                onClick={() => setCurrentPlan(plan.id)}
                className={`px-3 py-1.5 rounded text-xs whitespace-nowrap transition-colors flex items-center gap-2 ${
                  currentPlanId === plan.id
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${
                  plan.status === 'completed' ? 'bg-green-400' :
                  plan.status === 'executing' ? 'bg-yellow-400 animate-pulse' :
                  plan.status === 'discussing' ? 'bg-blue-400' : 'bg-gray-400'
                }`} />
                {plan.title.substring(0, 25)}...
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Resize Handle */}
      <div
        className={`absolute bottom-0 right-0 w-6 h-6 cursor-nwse-resize flex items-center justify-center select-none ${
          isResizing ? 'text-purple-400' : 'text-gray-500 hover:text-gray-300'
        } transition-colors`}
        onMouseDown={handleResizeStart}
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 12M12 7L7 12M12 12L12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      </div>

      {/* Archive Management Panel */}
      {showArchivePanel && currentPlanId && (
        <ArchivePanel
          planId={currentPlanId}
          onClose={() => setShowArchivePanel(false)}
          onRestore={async (roundNumber: number) => {
            await handleRestoreArchive(roundNumber);
            setShowArchivePanel(false);
          }}
        />
      )}
    </div>
  );
}
