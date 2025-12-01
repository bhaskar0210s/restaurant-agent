"""Chef agent for handling order preparation."""

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

from ..prompts import CHEF_INSTRUCTION
from .server import server_agent

load_dotenv()

# Backend API URL for database operations
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080/mcp")

chef_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="chef_agent",
    description="""Chef agent that receives orders and prepares them. Updates order
    status to 'ready' and delegates to server_agent for delivery.""",
    instruction=CHEF_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=BACKEND_API_URL
            )
        )
    ],
    sub_agents=[server_agent],
)

