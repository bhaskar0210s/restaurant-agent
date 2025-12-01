"""Main agent module for the restaurant agent system."""

import logging
import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

from .prompts import CAPTAIN_INSTRUCTION
from .sub_agents import waiter_agent
from .callbacks import enforce_captain_workflow, track_captain_tools

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

# Backend API URL for database operations
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080/mcp")

logger.info("🍽️ Initializing Restaurant Agent System...")
logger.info(f"📡 Backend API URL: {BACKEND_API_URL}")

# Captain is the root agent that orchestrates the restaurant
# It has access to MCP tools for database operations and delegates to sub-agents
root_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="captain_agent",
    description="The Captain (host) of the restaurant who greets customers, manages reservations and tables, and coordinates the dining experience.",
    instruction=CAPTAIN_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=BACKEND_API_URL
            )
        )
    ],
    sub_agents=[waiter_agent],
    before_model_callback=enforce_captain_workflow,
    after_tool_callback=track_captain_tools,
)

logger.info("✅ Restaurant Agent System initialized successfully!")

