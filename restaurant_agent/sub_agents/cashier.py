"""Cashier agent for handling billing and payments."""

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

from ..prompts import CASHIER_INSTRUCTION

load_dotenv()

# Backend API URL for database operations
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080/mcp")

cashier_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="cashier_agent",
    description="""Cashier agent that generates bills for customers.
    Transfers back to waiter with bill details.""",
    instruction=CASHIER_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=BACKEND_API_URL
            )
        )
    ],
)

