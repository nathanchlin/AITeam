import { useState, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { 
  Gamepad2, 
  Rocket, 
  Sparkles, 
  ChevronRight,
  Smartphone,
  Monitor,
  Zap,
  Target,
  Palette
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

interface MobileEntryProps {
  onSwitchToFull: () => void;
}

export function MobileEntry({ onSwitchToFull }: MobileEntryProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [request, setRequest] = useState('');
  const [selectedType, setSelectedType] = useState<'web-app' | 'godot-game'>('web-app');
  const [recentProjects, setRecentProjects] = useState<any[]>([]);
  const { setPlans, setCurrentPlan, toggleVibeCodingPanel } = useAgentStore();

  // 加载最近项目
  useEffect(() => {
    const loadRecentProjects = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/pipeline/plans?limit=6`);
        const data = await res.json();
        const plansData = Array.isArray(data) ? data : data.plans || [];
        setPlans(plansData);
        setRecentProjects(plansData.slice(0, 6));
      } catch (error) {
        console.error('Failed to load recent projects:', error);
      }
    };
    loadRecentProjects();
  }, [setPlans]);

  const handleQuickCreate = async () => {
    if (!request.trim()) return;
    
    setIsCreating(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request: request.trim(),
          target_output: selectedType,
          skip_discussion: true
        })
      });
      
      const data = await res.json();
      
      if (data.plan_id) {
        setCurrentPlan(data.plan_id);
        toggleVibeCodingPanel();
        setRequest('');
      }
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('创建失败，请重试');
    } finally {
      setIsCreating(false);
    }
  };

  const gameTypeTemplates = [
    { icon: '🎮', name: '动作游戏', prompt: '制作一个动作游戏' },
    { icon: '🧩', name: '益智游戏', prompt: '制作一个益智游戏' },
    { icon: '🏃', name: '跑酷游戏', prompt: '制作一个跑酷游戏' },
    { icon: '👾', name: '射击游戏', prompt: '制作一个射击游戏' },
  ];

  const appTypeTemplates = [
    { icon: '📊', name: '数据仪表盘', prompt: '制作一个数据仪表盘' },
    { icon: '📝', name: '待办应用', prompt: '制作一个待办应用' },
    { icon: '🛒', name: '电商页面', prompt: '制作一个电商页面' },
    { icon: '📱', name: '落地页', prompt: '制作一个产品落地页' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white overflow-x-hidden">
      {/* 顶部栏 */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-lg border-b border-gray-700/50 px-4 py-3">
        <div className="flex items-center justify-between max-w-lg mx-auto">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
              <Gamepad2 size={18} className="text-white" />
            </div>
            <span className="font-semibold text-base">游戏工坊</span>
          </div>
          <button
            onClick={onSwitchToFull}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs font-medium transition-colors"
          >
            <Monitor size={14} />
            <span>全功能模式</span>
          </button>
        </div>
      </header>

      {/* 主内容 */}
      <main className="pt-16 pb-24 px-4 max-w-lg mx-auto">
        {/* 欢迎区域 */}
        <section className="mt-6 mb-6">
          <h1 className="text-2xl font-bold mb-1">创作你的游戏</h1>
          <p className="text-gray-400 text-sm">用 AI 快速生成游戏原型</p>
        </section>

        {/* 快速创建卡片 */}
        <section className="mb-6">
          <div className="bg-gradient-to-br from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={18} className="text-purple-400" />
              <span className="font-medium text-sm">快速创建</span>
            </div>
            
            {/* 类型选择 */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setSelectedType('web-app')}
                className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-medium transition-all ${
                  selectedType === 'web-app'
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-800/50 text-gray-300 border border-gray-700'
                }`}
              >
                <Smartphone size={14} className="inline mr-1.5" />
                Web 游戏
              </button>
              <button
                onClick={() => setSelectedType('godot-game')}
                className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-medium transition-all ${
                  selectedType === 'godot-game'
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-800/50 text-gray-300 border border-gray-700'
                }`}
              >
                <Gamepad2 size={14} className="inline mr-1.5" />
                Godot
              </button>
            </div>

            {/* 输入框 */}
            <textarea
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="描述你想做的游戏，例如：制作一个太空射击游戏，玩家控制飞机躲避敌机..."
              className="w-full bg-gray-900/50 border border-gray-700 rounded-xl p-3.5 text-sm placeholder-gray-500 resize-none h-24 mb-4 focus:outline-none focus:border-purple-500"
            />

            {/* 创建按钮 */}
            <button
              onClick={handleQuickCreate}
              disabled={!request.trim() || isCreating}
              className="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 disabled:from-gray-700 disabled:to-gray-700 text-white font-medium py-3.5 rounded-xl transition-all flex items-center justify-center gap-2"
            >
              {isCreating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>创建中...</span>
                </>
              ) : (
                <>
                  <Rocket size={16} />
                  <span>开始创建</span>
                </>
              )}
            </button>
          </div>
        </section>

        {/* 模板推荐 */}
        <section className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-base">热门模板</h2>
          </div>
          
          {selectedType === 'godot-game' ? (
            <div className="grid grid-cols-2 gap-3">
              {gameTypeTemplates.map((template, index) => (
                <button
                  key={index}
                  onClick={() => setRequest(template.prompt)}
                  className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4 text-left hover:border-purple-500/50 transition-all active:scale-95"
                >
                  <div className="text-2xl mb-2">{template.icon}</div>
                  <div className="font-medium text-sm">{template.name}</div>
                </button>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {appTypeTemplates.map((template, index) => (
                <button
                  key={index}
                  onClick={() => setRequest(template.prompt)}
                  className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4 text-left hover:border-purple-500/50 transition-all active:scale-95"
                >
                  <div className="text-2xl mb-2">{template.icon}</div>
                  <div className="font-medium text-sm">{template.name}</div>
                </button>
              ))}
            </div>
          )}
        </section>

        {/* 最近项目 */}
        {recentProjects.length > 0 && (
          <section className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold text-base">最近项目</h2>
              <button 
                onClick={() => toggleVibeCodingPanel()}
                className="text-purple-400 text-sm font-medium"
              >
                查看全部
              </button>
            </div>
            
            <div className="space-y-2">
              {recentProjects.slice(0, 4).map((project) => (
                <button
                  key={project.id}
                  onClick={() => {
                    setCurrentPlan(project.id);
                    toggleVibeCodingPanel();
                  }}
                  className="w-full bg-gray-800/50 border border-gray-700/50 rounded-xl p-4 text-left hover:border-purple-500/50 transition-all flex items-center justify-between"
                >
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate">
                      {project.original_request?.slice(0, 30) || '未命名项目'}
                      {project.original_request?.length > 30 && '...'}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5 flex items-center gap-2">
                      <span className={`px-1.5 py-0.5 rounded text-xs ${
                        project.target_output === 'godot-game' 
                          ? 'bg-orange-500/20 text-orange-400' 
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {project.target_output === 'godot-game' ? 'Godot' : 'Web'}
                      </span>
                      <span>{new Date(project.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <ChevronRight size={16} className="text-gray-500 flex-shrink-0" />
                </button>
              ))}
            </div>
          </section>
        )}

        {/* 功能特点 */}
        <section className="mt-8 mb-6">
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-gray-800/30 rounded-xl p-4 text-center">
              <Zap size={20} className="mx-auto mb-2 text-yellow-400" />
              <div className="text-xs text-gray-400">快速生成</div>
              <div className="text-xs text-gray-600 mt-0.5">分钟级原型</div>
            </div>
            <div className="bg-gray-800/30 rounded-xl p-4 text-center">
              <Target size={20} className="mx-auto mb-2 text-green-400" />
              <div className="text-xs text-gray-400">智能理解</div>
              <div className="text-xs text-gray-600 mt-0.5">自然语言描述</div>
            </div>
            <div className="bg-gray-800/30 rounded-xl p-4 text-center">
              <Palette size={20} className="mx-auto mb-2 text-purple-400" />
              <div className="text-xs text-gray-400">多种类型</div>
              <div className="text-xs text-gray-600 mt-0.5">游戏/应用</div>
            </div>
          </div>
        </section>
      </main>

      {/* 底部导航 */}
      <nav className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-lg border-t border-gray-700/50 px-4 py-2">
        <div className="flex items-center justify-around max-w-lg mx-auto">
          <button className="flex flex-col items-center py-2 px-4 text-purple-400">
            <Gamepad2 size={20} />
            <span className="text-xs mt-1">创建</span>
          </button>
          <button 
            onClick={() => toggleVibeCodingPanel()}
            className="flex flex-col items-center py-2 px-4 text-gray-400"
          >
            <Sparkles size={20} />
            <span className="text-xs mt-1">项目</span>
          </button>
          <button 
            onClick={onSwitchToFull}
            className="flex flex-col items-center py-2 px-4 text-gray-400"
          >
            <Monitor size={20} />
            <span className="text-xs mt-1">全功能</span>
          </button>
        </div>
      </nav>
    </div>
  );
}
