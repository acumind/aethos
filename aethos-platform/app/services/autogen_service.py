import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union

import autogen
from autogen.agentchat import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager
from pydantic import BaseModel, Field

from azure.identity import DefaultAzureCredential
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str
    agent_type: str = Field(...,
                            description="Type of agent: 'assistant', 'userproxy', 'groupchat'")
    system_message: Optional[str] = None
    description: Optional[str] = None
    human_input_mode: str = "NEVER"  # "ALWAYS", "NEVER", "TERMINATE"
    max_consecutive_auto_reply: Optional[int] = 10
    llm_config: Optional[Dict[str, Any]] = None
    is_termination_msg: Optional[bool] = None
    code_execution_config: Optional[Dict[str, Any]] = None
    members: Optional[List[str]] = None  # For group chat agents


class AgentResponse(BaseModel):
    """Response from an agent."""
    agent_id: str
    agent_name: str
    messages: List[Dict[str, Any]]
    status: str


class AgentStatus(BaseModel):
    """Status of an agent."""
    agent_id: str
    agent_name: str
    agent_type: str
    status: str
    created_at: str


class AgentExecutionResult(BaseModel):
    """Result of agent execution."""
    execution_id: str
    agent_id: str
    messages: List[Dict[str, Any]]
    status: str


class AutogenService:
    """Service for managing agents using Autogen."""

    def __init__(self, azure_openai_api_key: str = None, azure_openai_endpoint: str = None):
        """Initialize the service."""
        self.agents: Dict[str, Dict] = {}
        self.group_chats: Dict[str, Dict] = {}
        self.tasks: Dict[str, Dict] = {}

        # Configure Azure OpenAI
        self.azure_openai_config = self._get_azure_openai_config(
            azure_openai_api_key, azure_openai_endpoint
        )

    def _get_azure_openai_config(self, api_key: Optional[str] = None, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get Azure OpenAI configuration."""
        try:
            if not api_key:
                # Use DefaultAzureCredential if API key not provided
                credential = DefaultAzureCredential()
                token = credential.get_token(
                    "https://cognitiveservices.azure.com/.default")
                api_key = token.token

            # Default endpoint if not provided
            if not endpoint:
                endpoint = "https://api.cognitive.microsoft.com/openai/deployments"

            config = {
                "config_list": [
                    {
                        "model": "gpt-4",
                        "api_type": "azure",
                        "api_key": api_key,
                        "api_base": endpoint,
                        "api_version": "2023-07-01-preview"
                    }
                ],
                "temperature": 0.7,
                "cache_seed": 42  # For reproducibility
            }

            return config

        except Exception as e:
            logger.error(f"Error configuring Azure OpenAI: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error configuring Azure OpenAI: {str(e)}"
            )

    async def create_agent(self, config: AgentConfig) -> str:
        """
        Create a new agent.

        Args:
            config: Configuration for the agent

        Returns:
            str: ID of the created agent
        """
        try:
            agent_id = str(uuid.uuid4())

            # Set up LLM config if not provided
            if not config.llm_config and config.agent_type == "assistant":
                llm_config = self.azure_openai_config
            else:
                llm_config = config.llm_config or {}

            # Create agent based on type
            if config.agent_type == "assistant":
                agent = AssistantAgent(
                    name=config.name,
                    system_message=config.system_message or f"You are a helpful AI assistant named {config.name}.",
                    llm_config=llm_config
                )
            elif config.agent_type == "userproxy":
                code_execution_config = config.code_execution_config or {
                    "last_n_messages": 3, "work_dir": "workspace"}
                agent = UserProxyAgent(
                    name=config.name,
                    human_input_mode=config.human_input_mode,
                    max_consecutive_auto_reply=config.max_consecutive_auto_reply,
                    system_message=config.system_message,
                    code_execution_config=code_execution_config,
                    llm_config=llm_config if config.llm_config else False  # False if not provided
                )
            elif config.agent_type == "groupchat":
                # For group chats, we need to ensure the members exist
                if not config.members or len(config.members) < 2:
                    raise ValueError(
                        "Group chat requires at least 2 member agents")

                # Create a placeholder that will be properly set up when adding to a conversation
                agent = {"type": "groupchat", "name": config.name,
                         "members": config.members}
            else:
                raise ValueError(
                    f"Unsupported agent type: {config.agent_type}")

            # Store agent
            created_at = self._get_current_timestamp()
            self.agents[agent_id] = {
                "agent": agent,
                "config": config.dict(),
                "type": config.agent_type,
                "status": "created",
                "created_at": created_at
            }

            logger.info(f"Created agent: {config.name} (ID: {agent_id})")
            return agent_id

        except ValueError as e:
            logger.error(f"Invalid agent configuration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid agent configuration: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating agent: {str(e)}"
            )

    async def get_agent(self, agent_id: str) -> AgentStatus:
        """
        Get agent details.

        Args:
            agent_id: ID of the agent

        Returns:
            AgentStatus: Status of the agent
        """
        if agent_id not in self.agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )

        agent_info = self.agents[agent_id]
        return AgentStatus(
            agent_id=agent_id,
            agent_name=agent_info["config"]["name"],
            agent_type=agent_info["type"],
            status=agent_info["status"],
            created_at=agent_info["created_at"]
        )

    async def list_agents(self) -> List[AgentStatus]:
        """
        List all agents.

        Returns:
            List[AgentStatus]: List of all agents
        """
        return [
            AgentStatus(
                agent_id=agent_id,
                agent_name=agent_info["config"]["name"],
                agent_type=agent_info["type"],
                status=agent_info["status"],
                created_at=agent_info["created_at"]
            )
            for agent_id, agent_info in self.agents.items()
        ]

    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: ID of the agent to delete

        Returns:
            bool: True if successful
        """
        if agent_id not in self.agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )

        # Check if agent is used in a group chat
        for gc_id, gc_info in self.group_chats.items():
            if agent_id in gc_info.get("member_ids", []):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete agent as it is used in group chat {gc_id}"
                )

        # Delete agent
        del self.agents[agent_id]
        return True

    async def create_group_chat(
        self,
        name: str,
        agent_ids: List[str],
        system_message: Optional[str] = None,
        max_round: int = 10,
        speaker_selection_method: str = "auto"
    ) -> str:
        """
        Create a group chat.

        Args:
            name: Name of the group chat
            agent_ids: List of agent IDs to include
            system_message: System message for the group chat
            max_round: Maximum number of rounds
            speaker_selection_method: Method for selecting speakers

        Returns:
            str: ID of the created group chat
        """
        try:
            # Verify all agents exist
            for agent_id in agent_ids:
                if agent_id not in self.agents:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Agent with ID {agent_id} not found"
                    )

            # Create group chat ID
            group_chat_id = str(uuid.uuid4())

            # Store group chat
            created_at = self._get_current_timestamp()
            self.group_chats[group_chat_id] = {
                "name": name,
                "member_ids": agent_ids,
                "system_message": system_message,
                "max_round": max_round,
                "speaker_selection_method": speaker_selection_method,
                "created_at": created_at,
                "status": "created"
            }

            logger.info(f"Created group chat: {name} (ID: {group_chat_id})")
            return group_chat_id

        except Exception as e:
            logger.error(f"Error creating group chat: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating group chat: {str(e)}"
            )

    async def execute_agent(
        self,
        agent_id: str,
        message: str,
        wait_for_completion: bool = False
    ) -> Union[str, AgentResponse]:
        """
        Execute an agent with a message.

        Args:
            agent_id: ID of the agent to execute
            message: Message to send to the agent
            wait_for_completion: Whether to wait for completion or return task ID

        Returns:
            Union[str, AgentResponse]: Task ID or agent response if wait_for_completion=True
        """
        if agent_id not in self.agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )

        # Get agent
        agent_info = self.agents[agent_id]
        agent = agent_info["agent"]

        # Check agent type
        if agent_info["type"] == "groupchat":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot execute a group chat agent directly. Use execute_group_chat instead."
            )

        # Create task ID
        task_id = str(uuid.uuid4())

        # Set up task
        self.tasks[task_id] = {
            "agent_id": agent_id,
            "message": message,
            "status": "pending",
            "result": None
        }

        # Execute asynchronously
        asyncio.create_task(self._execute_agent_task(task_id, agent, message))

        # Return immediately or wait for completion
        if not wait_for_completion:
            return task_id

        # Wait for completion with timeout
        for _ in range(60):  # 30 second timeout (0.5s * 60)
            await asyncio.sleep(0.5)
            if self.tasks[task_id]["status"] != "pending":
                break

        # Check status
        if self.tasks[task_id]["status"] == "pending":
            # Still running, update to timeout but let it continue
            self.tasks[task_id]["status"] = "timeout"
            return AgentResponse(
                agent_id=agent_id,
                agent_name=agent_info["config"]["name"],
                messages=[],
                status="timeout"
            )

        # Return result
        result = self.tasks[task_id]["result"]
        return AgentResponse(
            agent_id=agent_id,
            agent_name=agent_info["config"]["name"],
            messages=result["messages"] if result else [],
            status=self.tasks[task_id]["status"]
        )

    async def execute_group_chat(
        self,
        group_chat_id: str,
        message: str,
        wait_for_completion: bool = False
    ) -> Union[str, AgentResponse]:
        """
        Execute a group chat with a message.

        Args:
            group_chat_id: ID of the group chat to execute
            message: Message to send to the group chat
            wait_for_completion: Whether to wait for completion or return task ID

        Returns:
            Union[str, AgentResponse]: Task ID or agent response if wait_for_completion=True
        """
        if group_chat_id not in self.group_chats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group chat with ID {group_chat_id} not found"
            )

        # Get group chat info
        gc_info = self.group_chats[group_chat_id]

        # Create task ID
        task_id = str(uuid.uuid4())

        # Set up task
        self.tasks[task_id] = {
            "group_chat_id": group_chat_id,
            "message": message,
            "status": "pending",
            "result": None
        }

        # Execute asynchronously
        asyncio.create_task(self._execute_group_chat_task(
            task_id, gc_info, message))

        # Return immediately or wait for completion
        if not wait_for_completion:
            return task_id

        # Wait for completion with timeout
        for _ in range(120):  # 60 second timeout (0.5s * 120)
            await asyncio.sleep(0.5)
            if self.tasks[task_id]["status"] != "pending":
                break

        # Check status
        if self.tasks[task_id]["status"] == "pending":
            # Still running, update to timeout but let it continue
            self.tasks[task_id]["status"] = "timeout"
            return AgentResponse(
                agent_id=group_chat_id,
                agent_name=gc_info["name"],
                messages=[],
                status="timeout"
            )

        # Return result
        result = self.tasks[task_id]["result"]
        return AgentResponse(
            agent_id=group_chat_id,
            agent_name=gc_info["name"],
            messages=result["messages"] if result else [],
            status=self.tasks[task_id]["status"]
        )

    async def get_task_status(self, task_id: str) -> AgentExecutionResult:
        """
        Get status of a task.

        Args:
            task_id: ID of the task

        Returns:
            AgentExecutionResult: Result of the task execution
        """
        if task_id not in self.tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )

        task = self.tasks[task_id]

        # Get agent info
        agent_id = task.get("agent_id") or task.get("group_chat_id", "unknown")

        return AgentExecutionResult(
            execution_id=task_id,
            agent_id=agent_id,
            messages=task["result"]["messages"] if task["result"] else [],
            status=task["status"]
        )

    async def _execute_agent_task(self, task_id: str, agent: Any, message: str):
        """
        Execute agent task.

        Args:
            task_id: ID of the task
            agent: Agent to execute
            message: Message to send
        """
        try:
            # Update status
            self.tasks[task_id]["status"] = "running"

            # Execute agent
            # The exact method depends on agent type
            if isinstance(agent, UserProxyAgent):
                # For user proxy, we need a different agent to chat with
                assist_agent = self._create_temp_assistant_agent()
                result = await agent.a_initiate_chat(assist_agent, message=message)
            else:
                # For assistant agent
                user_proxy = self._create_temp_user_proxy()
                result = await agent.a_generate_response(message)

            # Format results
            messages = []
            for msg in result.chat_history:
                messages.append({
                    "role": "assistant" if msg["role"] == "assistant" else "user",
                    "content": msg["content"]
                })

            # Update task
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["result"] = {
                "messages": messages
            }

        except Exception as e:
            logger.error(
                f"Error executing agent task: {str(e)}", exc_info=True)
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["result"] = {
                "error": str(e),
                "messages": []
            }

    async def _execute_group_chat_task(self, task_id: str, gc_info: Dict[str, Any], message: str):
        """
        Execute group chat task.

        Args:
            task_id: ID of the task
            gc_info: Group chat info
            message: Message to send
        """
        try:
            # Update status
            self.tasks[task_id]["status"] = "running"

            # Get agent instances
            agents = []
            for agent_id in gc_info["member_ids"]:
                if agent_id not in self.agents:
                    raise ValueError(f"Agent with ID {agent_id} not found")

                agent_info = self.agents[agent_id]
                agent = agent_info["agent"]

                if isinstance(agent, dict) and agent.get("type") == "groupchat":
                    raise ValueError(
                        f"Cannot include group chat agent {agent_id} in another group chat")

                agents.append(agent)

            # Create group chat
            group_chat = GroupChat(
                agents=agents,
                messages=[],
                max_round=gc_info["max_round"],
                speaker_selection_method=gc_info["speaker_selection_method"],
            )

            # Create group chat manager
            manager = GroupChatManager(
                groupchat=group_chat,
                llm_config=self.azure_openai_config
            )

            # Execute group chat
            result = await manager.a_chat(message)

            # Format results
            messages = []
            for msg in result:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "sender": msg.get("name", msg["role"])
                })

            # Update task
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["result"] = {
                "messages": messages
            }

        except Exception as e:
            logger.error(
                f"Error executing group chat task: {str(e)}", exc_info=True)
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["result"] = {
                "error": str(e),
                "messages": []
            }

    def _create_temp_assistant_agent(self) -> AssistantAgent:
        """Create a temporary assistant agent for interaction."""
        return AssistantAgent(
            name="TempAssistant",
            llm_config=self.azure_openai_config,
            system_message="You are a helpful AI assistant."
        )

    def _create_temp_user_proxy(self) -> UserProxyAgent:
        """Create a temporary user proxy agent for interaction."""
        return UserProxyAgent(
            name="TempUser",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0
        )

    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO format string."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
