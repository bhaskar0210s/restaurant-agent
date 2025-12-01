"""Server agent for delivering food to customers."""

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

from ..prompts import SERVER_INSTRUCTION

load_dotenv()

# Backend API URL for database operations
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080/mcp")

server_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="server_agent",
    description="""Server agent that delivers prepared food to customers at their table.
    Updates order status to 'served' and transfers back to waiter.""",
    instruction=SERVER_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=BACKEND_API_URL
            )
        )
    ],
)

