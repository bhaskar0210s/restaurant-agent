"""HTTP tool wrappers for restaurant backend API calls.

This module provides serializable function wrappers around the restaurant backend tools.
These are used for deployment to Vertex AI Agent Engines where streaming toolsets cannot
be deep copied due to internal stream references.
"""

import os
from typing import Any

import httpx

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080/mcp")


def _call_backend_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call a backend tool via HTTP using JSON-RPC 2.0."""
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments,
        },
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            BACKEND_API_URL,
            json=request_body,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            raise RuntimeError(f"Backend API error: {result['error']}")

        return result.get("result", {})


# ============== Customer Management ==============


def get_customer(name: str, phone: str) -> dict[str, Any]:
    """Get a customer by name and phone number. Creates the customer if not found.

    Args:
        name: Customer's full name.
        phone: Customer's phone number.

    Returns:
        Customer record (either found or newly created).
    """
    return _call_backend_tool("get_customer", {"name": name, "phone": phone})


# ============== Reservation Management ==============


def get_reservations(customer_id: str = "", date: str = "") -> dict[str, Any]:
    """Get reservations for a customer or date.

    Args:
        customer_id: Customer ID to filter by.
        date: Date to filter by (YYYY-MM-DD format).

    Returns:
        List of matching reservations.
    """
    return _call_backend_tool("get_reservations", {"customer_id": customer_id, "date": date})


def create_reservation(
    customer_id: str, date: str, time: str, party_size: int
) -> dict[str, Any]:
    """Create a new reservation.

    Args:
        customer_id: ID of the customer making the reservation.
        date: Reservation date (YYYY-MM-DD).
        time: Reservation time (HH:MM).
        party_size: Number of guests.

    Returns:
        The created reservation record.
    """
    return _call_backend_tool(
        "create_reservation",
        {
            "customer_id": customer_id,
            "date": date,
            "time": time,
            "party_size": party_size,
        },
    )


# ============== Table Management ==============


def check_table_availability(party_size: int) -> dict[str, Any]:
    """Check available tables for a given party size.

    Args:
        party_size: Number of guests needing seats.

    Returns:
        List of available tables that can accommodate the party.
    """
    return _call_backend_tool("check_table_availability", {"party_size": party_size})


def assign_table(customer_id: str, table_id: str) -> dict[str, Any]:
    """Assign a table to a customer.

    Args:
        customer_id: ID of the customer.
        table_id: ID of the table to assign.

    Returns:
        Updated table status.
    """
    return _call_backend_tool(
        "assign_table", {"customer_id": customer_id, "table_id": table_id}
    )


def release_table(table_id: str) -> dict[str, Any]:
    """Release a table (mark as available).

    Args:
        table_id: ID of the table to release.

    Returns:
        Updated table status.
    """
    return _call_backend_tool("release_table", {"table_id": table_id})


# ============== Menu Management ==============


def get_menu(category: str = "") -> dict[str, Any]:
    """Get the restaurant menu.

    Args:
        category: Optional category to filter by (appetizers, mains, desserts, drinks).

    Returns:
        Menu items, optionally filtered by category.
    """
    return _call_backend_tool("get_menu", {"category": category})


# ============== Order Management ==============


def get_customer_orders(customer_id: str, limit: int = 5) -> dict[str, Any]:
    """Get a customer's previous orders.

    Args:
        customer_id: ID of the customer.
        limit: Maximum number of orders to return.

    Returns:
        List of customer's previous orders.
    """
    return _call_backend_tool(
        "get_customer_orders", {"customer_id": customer_id, "limit": limit}
    )


def create_order(
    customer_id: str, table_id: str, items: list[dict]
) -> dict[str, Any]:
    """Create a new order for a customer.

    Args:
        customer_id: ID of the customer.
        table_id: ID of the table.
        items: List of items with name and quantity, e.g., [{"name": "Burger", "quantity": 2}]

    Returns:
        The created order record.
    """
    return _call_backend_tool(
        "create_order",
        {"customer_id": customer_id, "table_id": table_id, "items": items},
    )


def get_order_status(order_id: str) -> dict[str, Any]:
    """Get the status of an order.

    Args:
        order_id: ID of the order.

    Returns:
        Order status and details.
    """
    return _call_backend_tool("get_order_status", {"order_id": order_id})


def update_order_status(order_id: str, status: str) -> dict[str, Any]:
    """Update the status of an order.

    Args:
        order_id: ID of the order.
        status: New status (pending, preparing, ready, served).

    Returns:
        Updated order record.
    """
    return _call_backend_tool("update_order_status", {"order_id": order_id, "status": status})


# ============== Payment Management ==============


def generate_bill(customer_id: str) -> dict[str, Any]:
    """Generate a bill for a customer's current orders.

    Args:
        customer_id: ID of the customer.

    Returns:
        Generated bill with itemized details.
    """
    return _call_backend_tool("generate_bill", {"customer_id": customer_id})


def process_payment(bill_id: str, payment_method: str) -> dict[str, Any]:
    """Process payment for a bill.

    Args:
        bill_id: ID of the bill to pay.
        payment_method: Payment method (cash, card, tab).

    Returns:
        Payment confirmation.
    """
    return _call_backend_tool(
        "process_payment", {"bill_id": bill_id, "payment_method": payment_method}
    )


def add_to_tab(customer_id: str, amount: float) -> dict[str, Any]:
    """Add an amount to customer's tab for later payment.

    Args:
        customer_id: ID of the customer.
        amount: Amount to add to tab.

    Returns:
        Updated tab balance.
    """
    return _call_backend_tool("add_to_tab", {"customer_id": customer_id, "amount": amount})


# Export all tools as a list for easy use with ADK agents
ALL_TOOLS = [
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
    add_to_tab,
]
