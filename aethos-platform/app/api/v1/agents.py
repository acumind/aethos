from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories.agent_repository import AgentRepository
from app.schemas.agent import Agent, AgentCreate, AgentUpdate
from app.core.security import get_current_user
from app.schemas.auth import User
from app.services.azure_ai_service import AzureAIService
from app.services.autogen_service import AutogenService
from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any

router = APIRouter()
ai_service = AzureAIService()
autogen_service = AutogenService()


@router.get("/", response_model=List[Agent])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve all agents belonging to the current user.
    """

    return [Agent(
        id=1,
        name="Test Agent",
        description="This is a test agent.",
        azure_agent_id="azure-123",
        autogen_agent_id="autogen-123",
        is_active=True,
        created_at="2023-10-01T00:00:00Z",
        updated_at="2023-10-01T00:00:00Z",
        owner_id=1
    )]


@router.get("/get-rai-metrics", response_model={})
async def get_rai_metrics(
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve all agents belonging to the current user.
    """

    return [{
        "raiScore": 0.5,
        "biasness": 0.2,
        "fairness": 0.8,
        "explainability": 0.9,
        "robustness": 0.7,
        "transparency": 0.6,
    }
    ]


@router.post("/get-rai-metrics", response_model={})
async def analyze_rai_metrics(request: Request):
    """
    Analyze RAI metrics by invoking various agents and collecting their results.
    """
    try:
        # Parse the incoming request data
        request_data = await request.json()
        input_type = request_data.get("type")
        input_value = request_data.get("value")

        if not input_type or not input_value:
            raise HTTPException(
                status_code=400, detail="Invalid input data. 'type' and 'value' are required.")

        # Simulate invoking various agents and collecting their results
        # Replace this with actual calls to your agents (e.g., Azure AI Agent Service, AutoGen Service, etc.)
        results = [
            {
                "raiScore": 0.5,
                "biasness": 0.2,
                "fairness": 0.8,
                "explainability": 0.9,
                "robustness": 0.7,
                "transparency": 0.6,
            }
        ]

        # Return the collected results
        return {"results": results}

    except Exception as e:
        # Log the error and return a 500 response
        print(f"Error analyzing RAI metrics: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while analyzing RAI metrics.")


@router.get("/", response_model=List[Agent])
async def get_agents(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """
        Retrieve all agents belonging to the current user.
        """
        repository = AgentRepository(db)
        return repository.get_multi_by_owner(owner_id=current_user.id, skip=skip, limit=limit)

    @router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
    async def create_agent(
        agent_in: AgentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """
        Create a new agent.
        """
        repository = AgentRepository(db)

        # Register agent with Azure AI Service
        azure_agent_id = await ai_service.register_agent(
            name=agent_in.name,
            description=agent_in.description,
            capabilities=agent_in.capabilities
        )

        # Create agent in AutoGen service
        autogen_agent_id = await autogen_service.create_agent(
            name=agent_in.name,
            agent_type=agent_in.agent_type,
            config=agent_in.config
        )

        # Save agent to database
        agent = repository.create(
            obj_in=AgentCreate(
                **agent_in.dict(),
                azure_agent_id=azure_agent_id,
                autogen_agent_id=autogen_agent_id,
                owner_id=current_user.id
            )
        )
        return agent

    @router.get("/{agent_id}", response_model=Agent)
    async def get_agent(
        agent_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """
        Get a specific agent by ID.
        """
        repository = AgentRepository(db)
        agent = repository.get(id=agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        if agent.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return agent

    @router.put("/{agent_id}", response_model=Agent)
    async def update_agent(
        agent_id: int,
        agent_in: AgentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """
        Update an agent.
        """
        repository = AgentRepository(db)
        agent = repository.get(id=agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        if agent.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Update in Azure AI Service if needed
        if any(field in agent_in.__fields_set__ for field in ['name', 'description', 'capabilities']):
            await ai_service.update_agent(
                agent_id=agent.azure_agent_id,
                name=agent_in.name if 'name' in agent_in.__fields_set__ else agent.name,
                description=agent_in.description if 'description' in agent_in.__fields_set__ else agent.description,
                capabilities=agent_in.capabilities if 'capabilities' in agent_in.__fields_set__ else agent.capabilities
            )

        # Update in AutoGen service if needed
        if any(field in agent_in.__fields_set__ for field in ['name', 'agent_type', 'config']):
            await autogen_service.update_agent(
                agent_id=agent.autogen_agent_id,
                name=agent_in.name if 'name' in agent_in.__fields_set__ else agent.name,
                agent_type=agent_in.agent_type if 'agent_type' in agent_in.__fields_set__ else agent.agent_type,
                config=agent_in.config if 'config' in agent_in.__fields_set__ else agent.config
            )

        # Update in database
        agent = repository.update(db_obj=agent, obj_in=agent_in)
        return agent

    @router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_agent(
        agent_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """
        Delete an agent.
        """
        repository = AgentRepository(db)
        agent = repository.get(id=agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        if agent.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Delete from Azure AI Service
        await ai_service.delete_agent(agent_id=agent.azure_agent_id)

        # Delete from AutoGen service
        await autogen_service.delete_agent(agent_id=agent.autogen_agent_id)

        # Delete from database
        repository.remove(id=agent_id)
        return None
    