import React, { useState, useEffect } from 'react';
import './AgentDashboard.css';

// 代理状态类型
const AGENT_STATUS = {
  IDLE: 'idle',
  BUSY: 'busy',
  OFFLINE: 'offline',
  ERROR: 'error'
};

// 代理数据类型
const Agent = {
  id: '',
  name: '',
  status: '',
  lastActive: '',
  currentTask: '',
  performance: 0,
  responseTime: 0
};

// 监控数据类型
const MonitoringData = {
  totalAgents: 0,
  activeAgents: 0,
  averageResponseTime: 0,
  tasksCompleted: 0,
  errorRate: 0
};

const AgentDashboard = () => {
  // 状态管理
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [monitoringData, setMonitoringData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 模拟数据获取
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 模拟代理数据
        const mockAgents = [
          { ...Agent, id: 'A001', name: 'Agent-1', status: AGENT_STATUS.BUSY, lastActive: '2023-05-15 10:30', currentTask: 'Processing Task #123', performance: 85, responseTime: 120 },
          { ...Agent, id: 'A002', name: 'Agent-2', status: AGENT_STATUS.IDLE, lastActive: '2023-05-15 10:25', currentTask: 'None', performance: 92, responseTime: 95 },
          { ...Agent, id: 'A003', name: 'Agent-3', status: AGENT_STATUS.OFFLINE, lastActive: '2023-05-15 09:15', currentTask: 'None', performance: 0, responseTime: 0 },
          { ...Agent, id: 'A004', name: 'Agent-4', status: AGENT_STATUS.BUSY, lastActive: '2023-05-15 10:28', currentTask: 'Processing Task #125', performance: 78, responseTime: 150 },
          { ...Agent, id: 'A005', name: 'Agent-5', status: AGENT_STATUS.ERROR, lastActive: '2023-05-15 10:20', currentTask: 'Error in Task #120', performance: 0, responseTime: 0 }
        ];
        
        // 模拟监控数据
        const mockMonitoringData = {
          ...MonitoringData,
          totalAgents: mockAgents.length,
          activeAgents: mockAgents.filter(a => a.status === AGENT_STATUS.BUSY).length,
          averageResponseTime: Math.round(mockAgents.reduce((sum, a) => sum + a.responseTime, 0) / mockAgents.length),
          tasksCompleted: 245,
          errorRate: 5.2
        };
        
        setAgents(mockAgents);
        setMonitoringData(mockMonitoringData);
      } catch (err) {
        setError('Failed to load data. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    
    // 模拟实时更新
    const interval = setInterval(() => {
      // 这里可以添加实时更新逻辑
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  // 选择代理
  const handleSelectAgent = (agent) => {
    setSelectedAgent(agent);
  };

  // 获取状态样式
  const getStatusClass = (status) => {
    switch (status) {
      case AGENT_STATUS.BUSY: return 'status-busy';
      case AGENT_STATUS.IDLE: return 'status-idle';
      case AGENT_STATUS.OFFLINE: return 'status-offline';
      case AGENT_STATUS.ERROR: return 'status-error';
      default: return '';
    }
  };

  // 获取状态文本
  const getStatusText = (status) => {
    switch (status) {
      case AGENT_STATUS.BUSY: return 'Busy';
      case AGENT_STATUS.IDLE: return 'Idle';
      case AGENT_STATUS.OFFLINE: return 'Offline';
      case AGENT_STATUS.ERROR: return 'Error';
      default: return 'Unknown';
    }
  };

  // 渲染代理状态面板
  const renderAgentStatusPanel = () => {
    if (loading) {
      return <div className="loading">Loading agents...</div>;
    }
    
    return (
      <div className="agent-status-panel">
        <h2>Agent Status</h2>
        <div className="agents-grid">
          {agents.map(agent => (
            <div 
              key={agent.id} 
              className={`agent-card ${getStatusClass(agent.status)} ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
              onClick={() => handleSelectAgent(agent)}
            >
              <div className="agent-header">
                <span className="agent-name">{agent.name}</span>
                <span className={`agent-status ${getStatusClass(agent.status)}`}>
                  {getStatusText(agent.status)}
                </span>
              </div>
              <div className="agent-details">
                <p><strong>Current Task:</strong> {agent.currentTask}</p>
                <p><strong>Last Active:</strong> {agent.lastActive}</p>
                <p><strong>Performance:</strong> {agent.performance}%</p>
                <p><strong>Response Time:</strong> {agent.responseTime}ms</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // 渲染选择结果展示区
  const renderSelectionResults = () => {
    if (!selectedAgent) {
      return (
        <div className="selection-results">
          <h2>Selected Agent</h2>
          <p>No agent selected. Click on an agent card to view details.</p>
        </div>
      );
    }
    
    return (
      <div className="selection-results">
        <h2>Selected Agent: {selectedAgent.name}</h2>
        <div className="selected-agent-details">
          <div className="detail-row">
            <span className="detail-label">ID:</span>
            <span className="detail-value">{selectedAgent.id}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Status:</span>
            <span className={`detail-value ${getStatusClass(selectedAgent.status)}`}>
              {getStatusText(selectedAgent.status)}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Current Task:</span>
            <span className="detail-value">{selectedAgent.currentTask}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Last Active:</span>
            <span className="detail-value">{selectedAgent.lastActive}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Performance:</span>
            <span className="detail-value">{selectedAgent.performance}%</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Response Time:</span>
            <span className="detail-value">{selectedAgent.responseTime}ms</span>
          </div>
        </div>
      </div>
    );
  };

  // 渲染监控数据仪表板
  const renderMonitoringDashboard = () => {
    if (loading) {
      return <div className="loading">Loading monitoring data...</div>;
    }
    
    return (
      <div className="monitoring-dashboard">
        <h2>Monitoring Data</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-title">Total Agents</div>
            <div className="metric-value">{monitoringData.totalAgents}</div>
          </div>
          <div className="metric-card">
            <div className="metric-title">Active Agents</div>
            <div className="metric-value">{monitoringData.activeAgents}</div>
          </div>
          <div className="metric-card">
            <div className="metric-title">Avg. Response Time</div>
            <div className="metric-value">{monitoringData.averageResponseTime}ms</div>
          </div>
          <div className="metric-card">
            <div className="metric-title">Tasks Completed</div>
            <div className="metric-value">{monitoringData.tasksCompleted}</div>
          </div>
          <div className="metric-card">
            <div className="metric-title">Error Rate</div>
            <div className="metric-value">{monitoringData.errorRate}%</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="agent-dashboard">
      <header className="dashboard-header">
        <h1>Agent Selection Dashboard</h1>
        <p>Monitor and select agents for task processing</p>
      </header>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="dashboard-content">
        <div className="left-panel">
          {renderAgentStatusPanel()}
          {renderSelectionResults()}
        </div>
        
        <div className="right-panel">
          {renderMonitoringDashboard()}
        </div>
      </div>
    </div>
  );
};

export default AgentDashboard;