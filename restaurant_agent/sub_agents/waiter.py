"""Waiter agent for handling menu and orders."""

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

from ..prompts import WAITER_INSTRUCTION
from .chef import chef_agent
from .cashier import cashier_agent

load_dotenv()

# Backend API URL for database operations
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080/mcp")

waiter_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="waiter_agent",
    description="""Waiter agent that handles menu display, takes orders, and coordinates
    with chef and cashier. The main point of contact for seated customers.""",
    instruction=WAITER_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=BACKEND_API_URL
            )
        )
    ],
    sub_agents=[chef_agent, cashier_agent],
)

