import logging
from typing import Dict, List, Optional
import httpx
from azure.identity import DefaultAzureCredential
from fastapi import HTTPException

from fastapi import FastAPI, HTTPException
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureAIService:
    """Service for interacting with Azure AI Agent Service."""

    def __init__(self):
        self.endpoint = settings.AZURE_AI_AGENT_SERVICE_ENDPOINT
        self.credential = DefaultAzureCredential()
        self.client = None

    async def _get_client(self):
        """Get or create the API client with token authentication."""
        if not self.client:
            token = await self._get_token()
            self.client = httpx.AsyncClient(
                base_url=self.endpoint,
                headers={"Authorization": f"Bearer {token}"}
            )
        return self.client

    async def _get_token(self) -> str:
        """Get an Azure AD token for the AI Agent Service."""
        try:
            token = self.credential.get_token(
                "https://cognitiveservices.azure.com/.default")
            return token.token
        except Exception as e:
            logger.error(f"Error getting Azure token: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to authenticate with Azure services")

    async def register_agent(
        self,
        name: str,
        description: str,
        capabilities: List[str]
    ) -> str:
        """
        Register a new agent with Azure AI Agent Service.

        Args:
            name: The name of the agent
            description: Description of the agent
            capabilities: List of agent capabilities

        Returns:
            The ID of the created agent in Azure
        """
        client = await self._get_client()

        payload = {
            "name": name,
            "description": description,
            "capabilities": capabilities,
        }

        try:
            response = await client.post("/agents", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["id"]
        except httpx.HTTPStatusError as e:
            logger.error(f"Error registering agent with Azure AI: {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to register agent with Azure AI: {e.response.text}"
            )

    async def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ) -> bool:
        """
        Update an existing agent in Azure AI Agent Service.

        Args:
            agent_id: ID of the agent to update
            name: New name for the agent
            description: New description for the agent
            capabilities: New capabilities for the agent

        Returns:
            True if successful
        """
        client = await self._get_client()

        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if capabilities is not None:
            payload["capabilities"] = capabilities

        try:
            response = await client.patch(f"/agents/{agent_id}", json=payload)
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Error updating agent in Azure AI: {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to update agent in Azure AI: {e.response.text}"
            )

    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent from Azure AI Agent Service.

        Args:
            agent_id: ID of the agent to delete

        Returns:
            True if successful
        """
        client = await self._get_client()

        try:
            response = await client.delete(f"/agents/{agent_id}")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Error deleting agent from Azure AI: {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to delete agent from Azure AI: {e.response.text}"
            )

    async def execute_agent_task(
        self,
        agent_id: str,
        task_data: Dict,
        callback_url: Optional[str] = None
    ) -> Dict:
        """
        Execute a task using an agent in Azure AI Agent Service.

        Args:
            agent_id: ID of the agent to use
            task_data: Task data to send to the agent
            callback_url: Optional URL for task completion callback

        Returns:
            Task execution result or task ID if async
        """
        client = await self._get_client()

        payload = {
            "taskData": task_data,
        }

        if callback_url:
            payload["callbackUrl"] = callback_url

        try:
            response = await client.post(f"/agents/{agent_id}/execute", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Error executing agent task in Azure AI: {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to execute agent task in Azure AI: {e.response.text}"
            )
