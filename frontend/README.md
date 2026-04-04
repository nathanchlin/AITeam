# AITeam Frontend

多 Agent 可视化协作系统的前端界面，基于 React + Three.js + TypeScript 构建。

## 🎯 项目简介

AITeam Frontend 是一个 3D 可视化的多 Agent 协作平台前端，提供：

- **3D 空间界面**: 虚拟 3D 世界展示 Agent 协作
- **实时通信**: WebSocket 实时更新 Agent 状态
- **任务管理**: 创建、分配、跟踪任务进度
- **代码编辑**: 集成代码编辑器和语法高亮
- **Pipeline 可视化**: 直观展示工作流程
- **即时通讯**: 支持 IM 聊天和群组讨论

## 🎨 技术栈

### 核心框架
- **React** (18.2.0) - UI 框架
- **TypeScript** (5.2.2) - 类型安全
- **Vite** (5.0.0) - 构建工具

### 3D 可视化
- **Three.js** (0.158.0) - 3D 渲染引擎
- **React Three Fiber** (8.15.0) - React 的 Three.js 封装
- **React Three Drei** (9.88.0) - R3F 常用组件库

### 状态管理
- **Zustand** (4.4.0) - 轻量级状态管理

### UI 组件
- **TailwindCSS** (3.3.5) - 原子化 CSS
- **Lucide React** (0.294.0) - 图标库

## 📦 安装

### 前置要求
- Node.js 18+
- npm 或 yarn

### 快速开始

```bash
# 1. 进入项目目录
cd ~/AITeam/frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 浏览器访问
http://localhost:5173
```

### 构建生产版本

```bash
# 构建优化版本
npm run build

# 预览构建结果
npm run preview
```

## 🏛️ 项目结构

```
frontend/
├── src/
│   ├── main.tsx              # 应用入口
│   ├── App.tsx               # 根组件
│   ├── index.css             # 全局样式
│   ├── types/                # TypeScript 类型定义
│   │   └── index.ts
│   ├── stores/               # Zustand 状态管理
│   │   └── agentStore.ts     # Agent 状态
│   ├── components/           # React 组件
│   │   ├── UI/               # UI 组件
│   │   │   ├── AgentPanel.tsx        # Agent 管理面板
│   │   │   ├── TaskPanel.tsx         # 任务管理面板
│   │   │   ├── PipelinePanel.tsx     # Pipeline 面板
│   │   │   ├── ChatPanel.tsx         # 聊天面板
│   │   │   ├── AgentActivityPanel.tsx # Agent 活动日志
│   │   │   ├── VibeCodingPanel.tsx   # 代码编辑面板
│   │   │   ├── DashboardPanel.tsx    # 仪表板
│   │   │   ├── IMPanel.tsx           # 即时通讯
│   │   │   ├── GroupChatPanel.tsx    # 群聊
│   │   │   └── ...                   # 更多组件
│   │   └── Three/            # 3D 组件
│   │       ├── Scene.tsx             # 3D 场景
│   │       ├── Agent.tsx             # Agent 3D 模型
│   │       └── ...
│   ├── hooks/                # 自定义 Hooks
│   │   └── useWebSocket.ts   # WebSocket Hook
│   └── utils/                # 工具函数
│       ├── syntaxHighlight.tsx  # 语法高亮
│       ├── assetLoader.ts        # 资源加载
│       └── time.ts               # 时间处理
├── public/                   # 静态资源
├── index.html                # HTML 模板
├── package.json              # 依赖配置
├── vite.config.ts            # Vite 配置
├── tailwind.config.js        # TailwindCSS 配置
├── tsconfig.json             # TypeScript 配置
└── README.md                 # 本文件
```

## 🎮 核心功能

### 1. 3D Agent 展示

```tsx
// 3D 场景中的 Agent
<Canvas>
  <Agent 
    position={[-4, 0, 0]} 
    type="coder" 
    name="CodeMaster"
    status="working"
  />
  <Agent 
    position={[4, 0, 0]} 
    type="tester" 
    name="Tester"
    status="idle"
  />
</Canvas>
```

### 2. 实时状态更新

```tsx
// WebSocket 连接
const ws = useWebSocket('ws://localhost:8000/ws');

// 监听 Agent 状态
ws.onMessage((data) => {
  if (data.type === 'agent_status') {
    updateAgentStatus(data.agentId, data.status);
  }
});
```

### 3. 任务管理

```tsx
// 创建任务
<TaskPanel>
  <TaskCreateForm 
    onSubmit={(task) => {
      createTask(task);
      notifyAgent(task.assignedAgentId);
    }}
  />
</TaskPanel>
```

### 4. Pipeline 可视化

```tsx
// Pipeline 流程图
<PipelinePanel>
  <PipelineNode type="coder" label="编码" />
  <PipelineArrow />
  <PipelineNode type="tester" label="测试" />
</PipelinePanel>
```

## 🔧 开发指南

### 添加新组件

1. 在 `src/components/UI/` 创建组件：

```tsx
// CustomPanel.tsx
import React from 'react';

export const CustomPanel: React.FC = () => {
  return (
    <div className="custom-panel">
      {/* 组件内容 */}
    </div>
  );
};
```

2. 在 `App.tsx` 中使用：

```tsx
import { CustomPanel } from './components/UI/CustomPanel';

function App() {
  return (
    <div>
      <CustomPanel />
    </div>
  );
}
```

### 添加新的 3D 对象

1. 在 `src/components/Three/` 创建组件：

```tsx
// CustomObject.tsx
import { mesh } from '@react-three/fiber';

export const CustomObject: React.FC = () => {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="blue" />
    </mesh>
  );
};
```

2. 在场景中使用：

```tsx
<Canvas>
  <CustomObject />
</Canvas>
```

### 状态管理

使用 Zustand 管理全局状态：

```tsx
// stores/customStore.ts
import { create } from 'zustand';

interface CustomState {
  data: any[];
  setData: (data: any[]) => void;
}

export const useCustomStore = create<CustomState>((set) => ({
  data: [],
  setData: (data) => set({ data }),
}));

// 使用
const { data, setData } = useCustomStore();
```

## 🎨 样式指南

### TailwindCSS

```tsx
// 使用原子类
<div className="flex items-center justify-center bg-blue-500 text-white p-4 rounded-lg">
  内容
</div>

// 响应式设计
<div className="w-full md:w-1/2 lg:w-1/3">
  响应式布局
</div>
```

### 自定义主题

在 `tailwind.config.js` 中配置：

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
      },
    },
  },
};
```

## 🌐 API 集成

### 后端 API

```tsx
// 获取 Agent 列表
const fetchAgents = async () => {
  const response = await fetch('http://localhost:8000/api/agents');
  const agents = await response.json();
  return agents;
};

// 创建任务
const createTask = async (taskData) => {
  const response = await fetch('http://localhost:8000/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(taskData),
  });
  return response.json();
};
```

### WebSocket 连接

```tsx
// hooks/useWebSocket.ts
export const useWebSocket = (url: string) => {
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const websocket = new WebSocket(url);
    
    websocket.onopen = () => {
      console.log('WebSocket 连接成功');
    };
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // 处理消息
    };
    
    setWs(websocket);
    
    return () => websocket.close();
  }, [url]);

  return ws;
};
```

## 🧪 测试

```bash
# 运行测试
npm run test

# 测试覆盖率
npm run test:coverage
```

## 🐛 调试

### 开发工具

- **React DevTools**: 浏览器扩展
- **Redux DevTools** (如果使用 Redux)
- **Three.js Inspector**: 3D 场景调试

### 日志

```tsx
// 开发环境日志
if (import.meta.env.DEV) {
  console.log('Agent 状态:', agentStatus);
}
```

### 常见问题

1. **3D 模型加载失败**
   - 检查模型路径
   - 确认模型格式支持
   - 查看控制台错误

2. **WebSocket 连接断开**
   - 检查后端服务状态
   - 确认 WebSocket URL 正确
   - 实现自动重连机制

3. **样式不生效**
   - 检查 TailwindCSS 配置
   - 确认类名拼写正确
   - 清除浏览器缓存

## 📦 打包部署

### Docker

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "preview"]
```

### Nginx

```nginx
# nginx.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📝 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- GitHub: https://github.com/nathanchlin/AITeam
- Email: nathanchlin@gmail.com
