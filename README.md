# 🍽️ Restaurant Agent

A multi-agent restaurant management system built with Google ADK (Agent Development Kit) and MCP (Model Context Protocol).

## Overview

This project simulates a complete restaurant experience with multiple AI agents working together:

| Agent       | Role              | Responsibilities                                                          |
| ----------- | ----------------- | ------------------------------------------------------------------------- |
| **Captain** | Host/Orchestrator | Greets customers, manages reservations, assigns tables, coordinates staff |
| **Waiter**  | Service           | Presents menu, takes orders, recommends dishes based on history           |
| **Chef**    | Kitchen           | Prepares orders, updates cooking status                                   |
| **Server**  | Delivery          | Delivers food to tables, ensures customer satisfaction                    |
| **Cashier** | Payment           | Generates bills, processes payments, manages tabs                         |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Restaurant Agent System                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    delegates    ┌─────────┐                   │
│  │ Captain │ ──────────────► │ Waiter  │                   │
│  │ (root)  │                 └────┬────┘                   │
│  └────┬────┘                      │                        │
│       │                           ▼                        │
│       │ MCP            ┌─────────┐   ┌─────────┐          │
│       │                │  Chef   │──►│ Server  │          │
│       ▼                └─────────┘   └────┬────┘          │
│  ┌─────────┐                              │                │
│  │   MCP   │                              ▼                │
│  │ Server  │◄────────────────────┌─────────┐              │
│  │ (JSON)  │                     │ Cashier │              │
│  └─────────┘                     └─────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

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
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
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

Here's an example conversation flow:

```
You: Hi, I'd like to book a table.

Captain: Welcome to our restaurant! I'd be happy to help you with a table.
May I have your name and phone number please?

You: My name is John and my number is 555-0101.

Captain: Welcome back, John! I see you're a returning customer.
Let me check for available tables... I have a lovely table by the window
available. Shall I seat you there?

You: Yes please!

Captain: Excellent! You're now seated at Table 1. I'll have our waiter
assist you shortly.

Waiter: Hello John! Great to see you again. I noticed you've enjoyed our
Ribeye Steak in the past - would you like that again, or shall I show you
our menu?

You: Show me the menu please.

Waiter: Here's our menu:
**Appetizers:** Bruschetta ($8.99), Calamari ($12.99), Soup of the Day ($6.99)
**Mains:** Grilled Salmon ($24.99), Ribeye Steak ($34.99), Chicken Parmesan ($19.99)...

You: I'll have the Grilled Salmon and a Fresh Lemonade.

Waiter: Excellent choice! One Grilled Salmon and Fresh Lemonade coming up.
I'll send this to our chef right away.

Chef: Order received! I'm preparing your Grilled Salmon now...
Your order is ready!

Server: Here's your Grilled Salmon and Fresh Lemonade. Enjoy your meal!

You: I'm done, can I get the bill?

Cashier: Here's your bill:
- Grilled Salmon: $24.99
- Fresh Lemonade: $4.99
- Subtotal: $29.98
- Tax (8%): $2.40
- Total: $32.38

How would you like to pay? (cash, card, or add to tab)

You: Card please.

Cashier: Payment processed successfully! Thank you for dining with us, John.
We hope to see you again soon!
```

## Project Structure

```
restaurant/
├── restaurant_agent/
│   ├── __init__.py
│   ├── agent.py              # Root agent (Captain) with MCPToolset
│   ├── prompts.py            # Agent instructions
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
├── pyproject.toml            # Agent dependencies
├── env.example               # Environment template
└── README.md
```

## Backend Server Tools

The backend server exposes the following database operations:

| Tool                       | Description                                    |
| -------------------------- | ---------------------------------------------- |
| `get_customer`             | Get/Create customer by name and phone number   |
| `lookup_customer`          | Find customer by name or phone                 |
| `create_customer`          | Create new customer record                     |
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

- **Customers**: 3 sample customers with order history
- **Menu**: 15 items across appetizers, mains, desserts, and drinks
- **Tables**: 8 tables with various capacities (2-10 seats)
- **Reservations**: 2 sample reservations
- **Orders**: 3 sample past orders
- **Bills**: 1 sample paid bill

## License

Apache 2.0 - See [LICENSE](../LICENSE) for details.
