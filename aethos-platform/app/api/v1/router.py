from fastapi import APIRouter

# from app.api.v1 import auth, agents, tasks, storage

from app.api.v1 import agents

api_router = APIRouter()

# Include route modules
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(
    agents.router, prefix="/get-rai-metrics", tags=["RAI Agents"])
# api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
# api_router.include_router(storage.router, prefix="/storage", tags=["Storage"])
