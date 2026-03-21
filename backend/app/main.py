from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import agents, tasks, pipeline, projects, stats, group_chats
from app.api.ws import websocket_endpoint, ws_manager as websocket_manager
from app.services.agent_manager import agent_manager
from app.services.coordinator import coordinator
from app.services.pipeline_queue import pipeline_queue
from app.models.schemas import AgentType
from app.middleware.error_handler import setup_exception_handlers

# Create FastAPI app
app = FastAPI(
    title="AITeam API",
    description="Multi-Agent Visualization Collaboration System",
    version="1.0.0",
)

# Setup global exception handlers
setup_exception_handlers(app, debug=settings.debug)

# CORS middleware - parse origins from comma-separated string
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(group_chats.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "AITeam API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.api_route("/health", methods=["GET", "HEAD"])
@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)


@app.on_event("startup")
async def startup_event():
    # Initialize pipeline queue with coordinator and websocket manager
    pipeline_queue.set_coordinator(coordinator)
    pipeline_queue.set_websocket_manager(websocket_manager)
    print("[Startup] Pipeline queue initialized")

    # Only create default agents if no agents exist (first run)
    if len(agent_manager.get_all_agents()) > 0:
        print("[Startup] Agents loaded from storage, skipping default agent creation")
        return

    # Create default agents with Tester
    default_agents = [
        {
            "name": "CodeMaster",
            "type": AgentType.CODER,
            "description": "专业代码开发专家，擅长编写和调试代码",
            "position": {"x": -4, "y": 0, "z": 0},
        },
        {
            "name": "DataAnalyst",
            "type": AgentType.ANALYST,
            "description": "数据分析专家，擅长数据分析和报告生成",
            "position": {"x": -1.5, "y": 0, "z": 0},
        },
        {
            "name": "Coordinator",
            "type": AgentType.ASSISTANT,
            "description": "项目协调者，负责需求分析和任务分配",
            "position": {"x": 1.5, "y": 0, "z": 0},
        },
        {
            "name": "Tester",
            "type": AgentType.TESTER,
            "description": "测试工程师，负责测试和质量保证",
            "position": {"x": 4, "y": 0, "z": 0},
        },
    ]

    for agent_data in default_agents:
        agent_manager.create_agent(
            name=agent_data["name"],
            agent_type=agent_data["type"],
            description=agent_data["description"],
            position=agent_data["position"],
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
