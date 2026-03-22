/**
 * Pipeline 模板库
 * 提供常用场景的快速启动模板
 */

export interface PipelineTemplate {
  id: string;
  name: string;
  category: 'game' | 'web-app' | 'tool' | 'visualization' | 'learning';
  description: string;
  request: string;
  recommendedAgents: string[];
  icon: string;
}

export const pipelineTemplates: PipelineTemplate[] = [
  {
    id: 'snake-game',
    name: '贪吃蛇游戏',
    category: 'game',
    description: '经典贪吃蛇游戏，键盘控制',
    request: '我需要做一个贪吃蛇游戏，使用 Canvas 实现，键盘方向键控制蛇的移动，吃到食物得分并变长，撞墙或撞到自己游戏结束。',
    recommendedAgents: ['coder', 'tester'],
    icon: '🐍'
  },
  {
    id: 'breakout-game',
    name: '打砖块游戏',
    category: 'game',
    description: '经典打砖块游戏',
    request: '我需要做一个打砖块游戏，使用 Canvas 实现，底部有一个挡板用键盘左右移动，球反弹打掉上方的砖块，所有砖块消除后获胜。',
    recommendedAgents: ['coder', 'tester'],
    icon: '🧱'
  },
  {
    id: 'space-shooter',
    name: '太空射击游戏',
    category: 'game',
    description: '飞机射击游戏',
    request: '我需要做一个太空射击游戏，玩家控制底部飞机左右移动并发射子弹，敌方飞机从上方出现，被击中消灭，玩家被撞则损失生命。',
    recommendedAgents: ['coder', 'tester'],
    icon: '🚀'
  },
  {
    id: 'todo-app',
    name: '待办事项应用',
    category: 'web-app',
    description: '简洁的待办事项管理',
    request: '我需要做一个待办事项 Web 应用，可以添加、删除、标记完成任务，数据保存到 localStorage，界面简洁美观。',
    recommendedAgents: ['coder', 'assistant'],
    icon: '✅'
  },
  {
    id: 'calculator',
    name: '计算器',
    category: 'tool',
    description: '标准计算器功能',
    request: '我需要做一个计算器应用，支持加减乘除基本运算，有清除和退格按钮，显示当前计算过程和结果。',
    recommendedAgents: ['coder'],
    icon: '🔢'
  },
  {
    id: 'pomodoro-timer',
    name: '番茄钟',
    category: 'tool',
    description: '番茄工作法计时器',
    request: '我需要做一个番茄钟应用，25分钟工作时间 + 5分钟休息时间循环，显示剩余时间，支持暂停和重置。',
    recommendedAgents: ['coder'],
    icon: '🍅'
  },
  {
    id: 'markdown-editor',
    name: 'Markdown 编辑器',
    category: 'web-app',
    description: '实时预览的 Markdown 编辑器',
    request: '我需要做一个 Markdown 编辑器，左侧输入 Markdown 文本，右侧实时预览渲染效果，支持标题、列表、代码块、链接等常见语法。',
    recommendedAgents: ['coder', 'assistant'],
    icon: '📝'
  },
  {
    id: 'chart-visualizer',
    name: '数据可视化',
    category: 'visualization',
    description: '图表数据可视化工具',
    request: '我需要做一个数据可视化工具，可以输入 JSON 数据，生成柱状图、折线图、饼图，使用 Canvas 绘制。',
    recommendedAgents: ['coder', 'analyst'],
    icon: '📊'
  },
  {
    id: 'quiz-app',
    name: '问答测验',
    category: 'learning',
    description: '互动式问答测验应用',
    request: '我需要做一个问答测验应用，显示题目和选项，用户选择后显示对错和解析，最后统计得分。',
    recommendedAgents: ['coder', 'assistant'],
    icon: '❓'
  },
  {
    id: 'form-builder',
    name: '表单生成器',
    category: 'tool',
    description: '动态表单构建工具',
    request: '我需要做一个表单生成器，可以添加文本框、下拉选择、单选框、复选框等字段，生成可填写的表单并收集数据。',
    recommendedAgents: ['coder'],
    icon: '📋'
  }
];

export const templateCategories = [
  { id: 'game', name: '游戏', icon: '🎮' },
  { id: 'web-app', name: 'Web 应用', icon: '🌐' },
  { id: 'tool', name: '工具', icon: '🔧' },
  { id: 'visualization', name: '可视化', icon: '📈' },
  { id: 'learning', name: '学习', icon: '📚' }
];

export function getTemplatesByCategory(category: string): PipelineTemplate[] {
  return pipelineTemplates.filter(t => t.category === category);
}

export function getTemplateById(id: string): PipelineTemplate | undefined {
  return pipelineTemplates.find(t => t.id === id);
}
