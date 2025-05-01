from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """Base schema for Agent with common attributes."""
    name: str
    description: Optional[str] = None
    agent_type: str = Field(...,
                            description="Type of agent (e.g., assistant, userproxy, custom)")
    capabilities: Optional[List[str]] = Field(
        default_factory=list, description="List of agent capabilities")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Agent configuration")


class AgentCreate(AgentBase):
    """Schema for creating a new Agent."""
    azure_agent_id: Optional[str] = None
    autogen_agent_id: Optional[str] = None
    owner_id: Optional[int] = None


class AgentUpdate(BaseModel):
    """Schema for updating an existing Agent."""
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[str] = None
    capabilities: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class Agent(BaseModel):
    """Schema representing an Agent."""
    id: int
    name: str
    description: Optional[str] = None
    azure_agent_id: str
    autogen_agent_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int


class AgentFilter(BaseModel):
    """Schema for filtering Agents."""
    name: Optional[str] = None
    agent_type: Optional[str] = None
    is_active: Optional[bool] = None
    capabilities: Optional[List[str]] = None
    owner_id: Optional[int] = None
