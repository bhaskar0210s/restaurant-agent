# 🍽️ Restaurant Squad

A multi-agent restaurant management system built with Google ADK (Agent Development Kit) and MCP (Model Context Protocol).

## Overview

This project simulates a complete restaurant experience with multiple AI agents working together to handle everything from the first greeting to payment.

The agent is designed as a **concierge-style restaurant assistant**: it helps guests make reservations, select dishes, place orders, and pay their bill through a single natural‑language interface. Behind the scenes, the system coordinates several specialized agents and a shared restaurant database so that operations stay consistent and stateful across the whole visit.

This repository is also structured so it can be used as a **capstone submission** for the _Agents Intensive – Capstone Project_ competition: it includes a clear problem statement, architecture, runnable code, evaluation scripts, and deployment hooks.

| Agent       | Role              | Responsibilities                                                          |
| ----------- | ----------------- | ------------------------------------------------------------------------- |
| **Captain** | Host/Orchestrator | Greets customers, manages reservations, assigns tables, coordinates staff |
| **Waiter**  | Service           | Presents menu, takes orders, recommends dishes based on history           |
| **Chef**    | Kitchen           | Prepares orders, updates cooking status                                   |
| **Server**  | Delivery          | Delivers food to tables, ensures customer satisfaction                    |
| **Cashier** | Payment           | Generates bills, processes payments, manages tabs                         |

## Key Features

- **Multi-agent restaurant workflow**: Captain, Waiter, Chef, Server, and Cashier agents collaborate to mirror how a real full‑service restaurant operates.
- **Gemini-powered reasoning**: Each agent is implemented with Google ADK on top of Gemini models (Gemini 2.5 / 2.0 Flash Lite), which handle conversation, tool selection, and multi-step reasoning.
- **Tool-based backend integration**: Agents call tools exposed by a FastMCP backend server to manage customers, reservations, tables, menu items, orders, and bills as structured JSON data.
- **End-to-end happy-path evaluation**: The `eval/HappyFlow.evalset.json` scenario and pytest suite exercise the full journey from reservation through payment.
- **Deployment-ready variant**: A deployment-specific agent graph (`restaurant_agent/agent_deploy.py`) and scripts in `deployment/` allow you to publish the agent to Vertex AI Agent Engine.

## Architecture (Simplified)

```
┌─────────────────────────────────────────────────────────────┐
│                    Restaurant Squad System                  │
├─────────────────────────────────────────────────────────────┤
│  User (CLI / ADK Web UI)                                   │
│            │                                               │
│            ▼                                               │
│      ┌─────────┐    interacts    ┌─────────┐               │
│      │ Captain │ ──────────────► │ Waiter  │               │
│      │ (root)  │                 └────┬────┘               │
│      └─────────┘                      │                    │
│                                       │ interacts          │
│                    ┌──────────────────┴──────────────────┐ │
│                    │                                      │ │
│                    ▼                                      ▼ │
│              ┌─────────┐                          ┌─────────┐ │
│              │  Chef   │                          │ Cashier │ │
│              └────┬────┘                          └─────────┘ │
│                   │ interacts                                 │
│                   ▼                                           │
│              ┌─────────┐                                      │
│              │ Server  │                                      │
│              └─────────┘                                      │
│                                                               │
│  All agents call tools on:                                    │
│      ┌──────────────────────────────────────────────┐       │
│      │ FastMCP Backend Server (JSON data store)     │       │
│      │  customers / reservations / tables / menu    │       │
│      │  orders / bills                              │       │
│      └──────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Flow Image

![Flow Image](Flow.png)

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

1. **Clone and navigate to the project:**

```bash
cd restaurant
```

2. **Install uv (if not already installed):**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Configure environment variables:**

```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your API key
# Get a Gemini API key from: https://aistudio.google.com/apikey
```

4. **Install dependencies:**

```bash
# Install agent dependencies
uv sync

# Install backend server dependencies
cd backend-server && uv sync && cd ..
```

## Running the Agent

You need to start both the backend server and the agent.

### Step 1: Start the Backend Server

In a terminal, run:

```bash
uv run backend-server/server.py
```

You should see:

```
[INFO]: 🚀 Restaurant backend server starting on port 8080
```

### Step 2: Run the Agent

In a separate terminal, you can run the agent in different ways:

**Option A: Web Interface (Recommended)**

```bash
adk web --port 8000
```

Then open http://localhost:8000 in your browser and select `restaurant_agent`.

**Option B: Command Line**

```bash
adk run restaurant_agent
```

## Sample Interaction

Here's an example conversation flow from the Happy Flow evaluation, with backend function calls shown in _italics_:

```
You: hi

Captain: Hello! Welcome to our restaurant. Can I get your name and phone number, please?

You: My name is Bhaskar and my phone number is 12345.

*[Behind the scenes: get_customer(name="Bhaskar", phone="12345") → Customer found]*
*[Behind the scenes: get_reservations(customer_id="fba2e88e") → Reservation found]*

Captain: I found your reservation for today at 7:00 PM for 10 people.

You: ok

*[Behind the scenes: check_table_availability(party_size=10) → No tables available]*

Captain: Unfortunately, we don't have any tables available for a party of 10 at the moment.
Would you like to wait for a table to become available?

You: yes I'll wait

*[Behind the scenes: release_table(capacity=10) → Table 8 released]*
*[Behind the scenes: check_table_availability(party_size=10) → Table 8 available]*
*[Behind the scenes: assign_table(table_id="table08", customer_id="fba2e88e") → Table assigned]*

Captain: Please follow me to your table.

You: sure

*[Behind the scenes: transfer_to_agent(agent_name="waiter_agent")]*
*[Behind the scenes: get_customer_orders(customer_id="fba2e88e") → Past orders retrieved]*
*[Behind the scenes: get_menu() → Full menu retrieved]*

Waiter: Hello Bhaskar! Welcome. It's great to see you again. I see you've enjoyed our
Calamari and Fish and Chips in the past.

Here is our menu:

**Appetizers:**
*   Bruschetta: $8.99
*   Calamari: $12.99
*   Soup of the Day: $6.99

**Mains:**
*   Grilled Salmon: $24.99
*   Ribeye Steak: $34.99
*   Chicken Parmesan: $19.99
*   Vegetable Risotto: $17.99
*   Fish and Chips: $16.99

**Desserts:**
*   Tiramisu: $8.99
*   Chocolate Lava Cake: $9.99
*   Cheesecake: $8.49

**Drinks:**
*   Soft Drink: $2.99
*   Fresh Lemonade: $4.99
*   Coffee: $3.49
*   Iced Tea: $3.49

What would you like to order?

You: I'll have 2 Ribeye Steak, 1 Calamari, and 2 Bruschetta.

*[Behind the scenes: create_order(table_id="table08", customer_id="fba2e88e", items=[...]) → Order created]*

Waiter: Excellent choice! Would you like anything else?

You: that's it for now

*[Behind the scenes: transfer_to_agent(agent_name="chef_agent")]*
*[Behind the scenes: update_order_status(order_id="8cac1565", status="ready") → Order marked ready]*
*[Behind the scenes: transfer_to_agent(agent_name="server_agent")]*

Waiter: If you need anything else, please call me.

Chef: I have received your order. I will update the status to ready and then transfer it to the server.

Server: Here is your order. Hope you enjoy it!

*[Behind the scenes: transfer_to_agent(agent_name="waiter_agent")]*

You: sure

Waiter: If you need anything else, please call me.

You: I would like to have 5 Fresh Lemonade.

*[Behind the scenes: create_order(table_id="table08", customer_id="fba2e88e", items=[...]) → Order created]*

Waiter: Would you like anything else?

You: that's it, and get me the bill

*[Behind the scenes: generate_bill(customer_id="fba2e88e") → Bill generated with all orders]*

Waiter: Here is your bill:

Total Amount: $319.44

How would you like to pay?

You: cash

*[Behind the scenes: process_payment(bill_id="09c03cce", payment_method="cash") → Payment processed]*
*[Behind the scenes: release_table(capacity=10) → Table released]*

Waiter: Thank you for dining with us! Please visit again.
```

## Project Structure

```
restaurant/
├── restaurant_agent/
│   ├── __init__.py
│   ├── agent.py              # Root agent (Captain) with MCPToolset
│   ├── agent_deploy.py       # Deployment-ready agent graph
│   ├── prompts.py            # Agent instructions
│   ├── callbacks.py          # Agent callbacks
│   ├── tools.py              # Agent tools
│   └── sub_agents/
│       ├── __init__.py
│       ├── waiter.py         # Menu & orders
│       ├── chef.py           # Order preparation
│       ├── server.py         # Food delivery
│       └── cashier.py        # Billing & payments
├── backend-server/
│   ├── server.py             # FastMCP server with database tools
│   ├── pyproject.toml        # Backend server dependencies
│   └── data/
│       ├── customers.json    # Customer records
│       ├── reservations.json # Reservations
│       ├── orders.json       # Order history
│       ├── menu.json         # Menu items
│       ├── tables.json       # Table availability
│       └── bills.json        # Bills & payments
├── deployment/
│   ├── deploy.py             # Agent Engine deployment script
│   └── test_deployment.py    # Deployment testing script
├── eval/
│   ├── HappyFlow.evalset.json # Evaluation scenario
│   └── test_eval.py          # Evaluation test suite
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── pyproject.toml            # Agent dependencies
├── env.example               # Environment template
└── README.md
```

## Backend Server Tools

The backend server exposes the following database operations:

| Tool                       | Description                                    |
| -------------------------- | ---------------------------------------------- |
| `get_customer`             | Get/Create customer by name and phone number   |
| `get_reservations`         | Get reservations for customer/date             |
| `create_reservation`       | Make a new reservation                         |
| `check_table_availability` | Find available tables                          |
| `assign_table`             | Seat a customer at a table                     |
| `release_table`            | Free up a table by capacity                    |
| `get_menu`                 | Get menu items (with optional category filter) |
| `get_customer_orders`      | Get customer's order history                   |
| `create_order`             | Submit a new order                             |
| `get_order_status`         | Check order status                             |
| `update_order_status`      | Update order status                            |
| `generate_bill`            | Create bill for customer                       |
| `process_payment`          | Process payment                                |
| `add_to_tab`               | Add amount to customer's tab                   |

## Data Files

The backend server uses JSON files for persistent storage. Sample data is included for:

- **Customers**: 4 sample customers with order history
- **Menu**: 15 items across appetizers (3), mains (5), desserts (3), and drinks (4)
- **Tables**: 10 tables with various capacities (2-10 seats)
- **Reservations**: 3 sample reservations
- **Orders**: 29 sample orders (including past and current orders)
- **Bills**: 14 sample bills (including paid and pending bills)
