# AITeam - Multi-Agent Visualization Collaboration System

A 3D visualization interface for managing multiple AI Agents working together, inspired by ralv.ai. Features cartoon-style characters representing different Agent types with real-time collaboration capabilities.

## Features

- **3D Space Interface**: Virtual 3D world with interactive agents
- **Multiple Agent Types**: Coder, Analyst, Assistant, and Custom agents
- **Real-time Communication**: WebSocket-based live updates
- **Task Management**: Create, assign, and track tasks
- **Thinking Process Visualization**: See agents' thought processes in real-time
- **GLM Integration**: Powered by Zhipu AI's GLM-4/5 models

## Tech Stack

### Backend
- FastAPI - Python Web Framework
- WebSocket - Real-time Communication
- GLM-4/GLM-5 - LLM Provider
- SQLite - Data Storage

### Frontend
- React + TypeScript + Vite
- React Three Fiber + Three.js - 3D Rendering
- Zustand - State Management
- TailwindCSS - Styling

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- GLM API Key (from https://open.bigmodel.cn/)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GLM_API_KEY

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application

Open http://localhost:5173 in your browser.

## Usage

1. **View Agents**: See your agents in the 3D space
2. **Create Agents**: Click "+" in the sidebar to create new agents
3. **Select Agent**: Click on a 3D character to select it
4. **Create Tasks**: Open the task panel and create new tasks
5. **Assign Tasks**: Select an agent when creating a task
6. **Start Tasks**: Click "Start" on pending tasks to begin execution
7. **Watch Progress**: See real-time thinking process and results

## Agent Types

| Type | Color | Description |
|------|-------|-------------|
| Coder | Blue | Code development and debugging |
| Analyst | Green | Data analysis and reporting |
| Assistant | Purple | General tasks and conversation |
| Custom | Orange | User-defined capabilities |

## Agent States

- **Idle**: Standing still, gentle floating animation
- **Working**: Active animation, progress indicator
- **Waiting**: Looking toward user
- **Error**: Warning indicator

## API Endpoints

### Agents
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/{id}/assign/{agent_id}` - Assign task to agent
- `POST /api/tasks/{id}/start` - Start task execution
- `POST /api/tasks/{id}/cancel` - Cancel task

### WebSocket
- `WS /ws` - WebSocket connection for real-time updates

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t aiteam-backend ./backend
docker build -t aiteam-frontend ./frontend
```

## Project Structure

```
AITeam/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── agents/       # Agent implementations
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   ├── llm/          # GLM integration
│   │   └── main.py       # Entry point
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Scene/    # 3D components
│   │   │   └── UI/       # UI components
│   │   ├── hooks/        # Custom hooks
│   │   ├── stores/       # Zustand stores
│   │   └── types/        # TypeScript types
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

## Configuration

### Backend (.env)
```
GLM_API_KEY=your_api_key_here
GLM_MODEL=glm-4
HOST=0.0.0.0
PORT=8000
DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./aiteam.db
```

## License

MIT License

## Acknowledgments

- Inspired by [ralv.ai](https://ralv.ai)
- Built with [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
- Powered by [Zhipu AI](https://open.bigmodel.cn/)
