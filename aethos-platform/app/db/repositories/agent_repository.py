from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import Agent as AgentModel
from app.schemas.agent import AgentCreate, AgentUpdate
from app.db.repositories.base import BaseRepository


class AgentRepository(BaseRepository[AgentModel, AgentCreate, AgentUpdate]):
    """
    Repository for Agent model operations.
    """

    def __init__(self, db: Session):
        super().__init__(db, AgentModel)

    def get_multi_by_owner(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentModel]:
        """
        Get multiple agents by owner ID.

        Args:
            owner_id: ID of the owner
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Agent models
        """
        return (
            self.db.query(self.model)
            .filter(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_azure_agent_id(self, azure_agent_id: str) -> Optional[AgentModel]:
        """
        Get an agent by Azure Agent ID.

        Args:
            azure_agent_id: Azure Agent ID

        Returns:
            Agent model if found, None otherwise
        """
        return (
            self.db.query(self.model)
            .filter(self.model.azure_agent_id == azure_agent_id)
            .first()
        )

    def get_by_autogen_agent_id(self, autogen_agent_id: str) -> Optional[AgentModel]:
        """
        Get an agent by AutoGen Agent ID.

        Args:
            autogen_agent_id: AutoGen Agent ID

        Returns:
            Agent model if found, None otherwise
        """
        return (
            self.db.query(self.model)
            .filter(self.model.autogen_agent_id == autogen_agent_id)
            .first()
        )

    def create_with_owner(
        self,
        obj_in: Union[AgentCreate, Dict[str, Any]],
        owner_id: int
    ) -> AgentModel:
        """
        Create a new agent with an owner.

        Args:
            obj_in: Agent creation data
            owner_id: ID of the owner

        Returns:
            Created Agent model
        """
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.dict(exclude_unset=True)

        obj_in_data["owner_id"] = owner_id
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_active_agents(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentModel]:
        """
        Get active agents.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active Agent models
        """
        return (
            self.db.query(self.model)
            .filter(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(
        self,
        agent_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentModel]:
        """
        Get agents by type.

        Args:
            agent_type: Type of agent
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Agent models matching the type
        """
        return (
            self.db.query(self.model)
            .filter(self.model.agent_type == agent_type)
            .offset(skip)
            .limit(limit)
            .all()
        )
