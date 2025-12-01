"""Deployment-ready agent module for the restaurant agent system.

This module creates agents using regular function tools instead of MCPToolset,
which allows the agents to be serialized and deployed to Vertex AI Agent Engines.

Use this instead of agent.py for deployment.
"""

import logging
import os

from dotenv import load_dotenv
from google.adk.agents import Agent

from .tools import (
    # Customer Management
    get_customer,
    # Reservation Management
    get_reservations,
    create_reservation,
    # Table Management
    check_table_availability,
    assign_table,
    release_table,
    # Menu Management
    get_menu,
    # Order Management
    get_customer_orders,
    create_order,
    get_order_status,
    update_order_status,
    # Payment Management
    generate_bill,
    process_payment,
)
from .prompts import (
    CAPTAIN_INSTRUCTION,
    WAITER_INSTRUCTION,
    CHEF_INSTRUCTION,
    SERVER_INSTRUCTION,
    CASHIER_INSTRUCTION,
)

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

logger.info("🍽️ Initializing Restaurant Agent System (Deployment Mode)...")

# Server agent - delivers food
server_agent = Agent(
    model="gemini-2.0-flash-lite",
    name="server_agent",
    description="""Server agent that delivers prepared food to customers at their table.
    Updates order status to 'served' and transfers back to waiter.""",
    instruction=SERVER_INSTRUCTION,
    tools=[
        get_order_status,
        update_order_status,
    ],
)

# Chef agent - prepares orders
chef_agent = Agent(
    model="gemini-2.0-flash-lite",
    name="chef_agent",
    description="""Chef agent that receives orders and prepares them. Updates order
    status to 'ready' and delegates to server_agent for delivery.""",
    instruction=CHEF_INSTRUCTION,
    tools=[
        get_order_status,
        update_order_status,
    ],
    sub_agents=[server_agent],
)

# Cashier agent - handles billing
cashier_agent = Agent(
    model="gemini-2.0-flash-lite",
    name="cashier_agent",
    description="""Cashier agent that generates bills for customers.
    Transfers back to waiter with bill details.""",
    instruction=CASHIER_INSTRUCTION,
    tools=[
        generate_bill,
        process_payment,
    ],
)

# Waiter agent - main customer contact
waiter_agent = Agent(
    model="gemini-2.0-flash-lite",
    name="waiter_agent",
    description="""Waiter agent that handles menu display, takes orders, and coordinates
    with chef and cashier. The main point of contact for seated customers.""",
    instruction=WAITER_INSTRUCTION,
    tools=[
        get_menu,
        get_customer_orders,
        create_order,
        get_order_status,
    ],
    sub_agents=[chef_agent, cashier_agent],
)

# Captain (root agent) - orchestrates the restaurant
# Note: Callbacks removed for deployment compatibility
root_agent = Agent(
    model="gemini-2.0-flash-lite",
    name="captain_agent",
    description="The Captain (host) of the restaurant who greets customers, manages reservations and tables, and coordinates the dining experience.",
    instruction=CAPTAIN_INSTRUCTION,
    tools=[
        get_customer,
        get_reservations,
        create_reservation,
        check_table_availability,
        assign_table,
        release_table,
    ],
    sub_agents=[waiter_agent],
)

logger.info("✅ Restaurant Agent System initialized (Deployment Mode)!")

