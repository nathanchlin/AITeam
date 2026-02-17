from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import agents, tasks, pipeline
from app.api.ws import websocket_endpoint, ws_manager as websocket_manager
from app.services.agent_manager import agent_manager
from app.models.schemas import AgentType

# Create FastAPI app
app = FastAPI(
    title="AITeam API",
    description="Multi-Agent Visualization Collaboration System",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")


# WebSocket manager export for task executor
websocket_manager = websocket_manager


@app.get("/")
async def root():
    return {
        "message": "AITeam API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)


@app.on_event("startup")
async def startup_event():
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
