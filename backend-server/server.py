"""Backend Server for Restaurant Database Operations."""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Restaurant Backend Server 🍽️")

# Data directory path
DATA_DIR = Path(__file__).parent / "data"


def _load_json(filename: str) -> dict | list:
    """Load JSON data from file."""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return [] if filename != "menu.json" else {"items": []}


def _save_json(filename: str, data: dict | list) -> None:
    """Save JSON data to file."""
    filepath = DATA_DIR / filename
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


# ============== Customer Management ==============

@mcp.tool()
def get_customer(name: str, phone: str) -> dict:
    """Get a customer by name and phone number. Creates the customer if not found.
    
    This function combines lookup and create operations - it first attempts to find
    an existing customer by phone number or name. If no customer is found, it creates
    a new customer record.
    
    Args:
        name: Customer's full name.
        phone: Customer's phone number.
    
    Returns:
        Customer record (either found or newly created).
    """
    logger.info(f"🔍 Getting customer: name={name}, phone={phone}")
    customers = _load_json("customers.json")
    
    # Try to find existing customer by phone or name
    for customer in customers:
        if phone and customer.get("phone") == phone:
            logger.info(f"✅ Found customer by phone: {customer}")
            return {"status": "found", "customer": customer}
        if name and name.lower() in customer.get("name", "").lower():
            logger.info(f"✅ Found customer by name: {customer}")
            return {"status": "found", "customer": customer}
    
    # Customer not found, create a new one
    logger.info(f"➕ Creating new customer: name={name}, phone={phone}")
    new_customer = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "phone": phone,
        "created_at": datetime.now().isoformat(),
        "total_visits": 0,
        "tab_balance": 0.0
    }
    
    customers.append(new_customer)
    _save_json("customers.json", customers)
    logger.info(f"✅ Created customer: {new_customer}")
    return {"status": "created", "customer": new_customer}


# ============== Reservation Management ==============

@mcp.tool()
def get_reservations(customer_id: str = "", date: str = "") -> dict:
    """Get reservations for a customer or date.
    
    Args:
        customer_id: Customer ID to filter by.
        date: Date to filter by (YYYY-MM-DD format).
    
    Returns:
        List of matching reservations.
    """
    logger.info(f"📅 Getting reservations: customer_id={customer_id}, date={date}")
    reservations = _load_json("reservations.json")
    
    results = []
    for res in reservations:
        if customer_id and res.get("customer_id") != customer_id:
            continue
        if date and res.get("date") != date:
            continue
        results.append(res)
    
    logger.info(f"✅ Found {len(results)} reservations")
    return {"status": "success", "reservations": results}


@mcp.tool()
def create_reservation(
    customer_id: str,
    date: str,
    time: str,
    party_size: int
) -> dict:
    """Create a new reservation.
    
    Args:
        customer_id: ID of the customer making the reservation.
        date: Reservation date (YYYY-MM-DD).
        time: Reservation time (HH:MM).
        party_size: Number of guests.
    
    Returns:
        The created reservation record.
    """
    logger.info(f"📝 Creating reservation: customer={customer_id}, date={date}, time={time}, size={party_size}")
    reservations = _load_json("reservations.json")
    
    new_reservation = {
        "id": str(uuid.uuid4())[:8],
        "customer_id": customer_id,
        "date": date,
        "time": time,
        "party_size": party_size,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    reservations.append(new_reservation)
    _save_json("reservations.json", reservations)
    logger.info(f"✅ Created reservation: {new_reservation}")
    return {"status": "created", "reservation": new_reservation}


# ============== Table Management ==============

@mcp.tool()
def check_table_availability(party_size: int) -> dict:
    """Check available tables for a given party size.
    
    Args:
        party_size: Number of guests needing seats.
    
    Returns:
        List of available tables that can accommodate the party.
    """
    logger.info(f"🪑 Checking table availability for party of {party_size}")
    tables = _load_json("tables.json")
    
    available = [
        t for t in tables 
        if t.get("status") == "available" and t.get("capacity") >= party_size
    ]
    
    logger.info(f"✅ Found {len(available)} available tables")
    return {
        "status": "success",
        "available_tables": available,
        "count": len(available)
    }


@mcp.tool()
def assign_table(customer_id: str, table_id: str) -> dict:
    """Assign a table to a customer.
    
    Args:
        customer_id: ID of the customer.
        table_id: ID of the table to assign.
    
    Returns:
        Updated table status.
    """
    logger.info(f"🪑 Assigning table {table_id} to customer {customer_id}")
    tables = _load_json("tables.json")
    
    for table in tables:
        if table.get("id") == table_id:
            if table.get("status") != "available":
                return {"status": "error", "message": "Table is not available"}
            table["status"] = "occupied"
            table["customer_id"] = customer_id
            table["seated_at"] = datetime.now().isoformat()
            _save_json("tables.json", tables)
            logger.info(f"✅ Table {table_id} assigned to customer {customer_id}")
            return {"status": "success", "table": table}
    
    return {"status": "error", "message": "Table not found"}


@mcp.tool()
def release_table(capacity: int) -> dict:
    """Release a table (mark as available).
    
    Args:
        capacity: Capacity of the table to release (finds first occupied table with this capacity).
    
    Returns:
        Updated table status.
    """
    logger.info(f"🪑 Releasing table with capacity {capacity}")
    tables = _load_json("tables.json")
    
    for table in tables:
        if table.get("capacity") == capacity and table.get("status") == "occupied":
            table["status"] = "available"
            table["customer_id"] = None
            table["seated_at"] = None
            _save_json("tables.json", tables)
            logger.info(f"✅ Table {table.get('id')} (capacity {capacity}) released")
            return {"status": "success", "table": table}
    
    return {"status": "error", "message": f"No occupied table found with capacity {capacity}"}


# ============== Menu Management ==============

@mcp.tool()
def get_menu(category: str = "") -> dict:
    """Get the restaurant menu.
    
    Args:
        category: Optional category to filter by (appetizers, mains, desserts, drinks).
    
    Returns:
        Menu items, optionally filtered by category.
    """
    logger.info(f"📋 Getting menu: category={category}")
    menu = _load_json("menu.json")
    
    items = menu.get("items", [])
    if category:
        items = [i for i in items if i.get("category", "").lower() == category.lower()]
    
    logger.info(f"✅ Returning {len(items)} menu items")
    return {"status": "success", "items": items}


# ============== Order Management ==============

@mcp.tool()
def get_customer_orders(customer_id: str, limit: int = 5) -> dict:
    """Get a customer's previous orders.
    
    Args:
        customer_id: ID of the customer.
        limit: Maximum number of orders to return.
    
    Returns:
        List of customer's previous orders.
    """
    logger.info(f"📦 Getting orders for customer {customer_id}")
    orders = _load_json("orders.json")
    
    customer_orders = [o for o in orders if o.get("customer_id") == customer_id]
    customer_orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    logger.info(f"✅ Found {len(customer_orders[:limit])} orders")
    return {"status": "success", "orders": customer_orders[:limit]}


@mcp.tool()
def create_order(customer_id: str, table_id: str, items: list[dict]) -> dict:
    """Create a new order for a customer.
    
    Args:
        customer_id: ID of the customer.
        table_id: ID of the table.
        items: List of items with name and quantity, e.g., [{"name": "Burger", "quantity": 2}]
    
    Returns:
        The created order record.
    """
    logger.info(f"🍽️ Creating order for customer {customer_id}: {items}")
    orders = _load_json("orders.json")
    menu = _load_json("menu.json")
    
    # Calculate total and validate items
    order_items = []
    total = 0.0
    
    for item in items:
        menu_item = next(
            (m for m in menu.get("items", []) if m.get("name", "").lower() == item.get("name", "").lower()),
            None
        )
        if menu_item:
            qty = item.get("quantity", 1)
            order_items.append({
                "name": menu_item["name"],
                "price": menu_item["price"],
                "quantity": qty
            })
            total += menu_item["price"] * qty
    
    new_order = {
        "id": str(uuid.uuid4())[:8],
        "customer_id": customer_id,
        "table_id": table_id,
        "items": order_items,
        "total": round(total, 2),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    orders.append(new_order)
    _save_json("orders.json", orders)
    logger.info(f"✅ Created order: {new_order}")
    return {"status": "created", "order": new_order}


@mcp.tool()
def get_order_status(order_id: str) -> dict:
    """Get the status of an order.
    
    Args:
        order_id: ID of the order.
    
    Returns:
        Order status and details.
    """
    logger.info(f"📦 Getting status for order {order_id}")
    orders = _load_json("orders.json")
    
    for order in orders:
        if order.get("id") == order_id:
            logger.info(f"✅ Order status: {order.get('status')}")
            return {"status": "success", "order": order}
    
    return {"status": "error", "message": "Order not found"}


@mcp.tool()
def update_order_status(order_id: str, status: str) -> dict:
    """Update the status of an order.
    
    Args:
        order_id: ID of the order.
        status: New status (pending, preparing, ready, served).
    
    Returns:
        Updated order record.
    """
    logger.info(f"📦 Updating order {order_id} status to {status}")
    orders = _load_json("orders.json")
    
    for order in orders:
        if order.get("id") == order_id:
            order["status"] = status
            order["updated_at"] = datetime.now().isoformat()
            _save_json("orders.json", orders)
            logger.info(f"✅ Order status updated to {status}")
            return {"status": "success", "order": order}
    
    return {"status": "error", "message": "Order not found"}


# ============== Payment Management ==============

@mcp.tool()
def generate_bill(customer_id: str) -> dict:
    """Generate a bill for a customer's current orders.
    
    Args:
        customer_id: ID of the customer.
    
    Returns:
        Generated bill with itemized details.
    """
    logger.info(f"🧾 Generating bill for customer {customer_id}")
    orders = _load_json("orders.json")
    bills = _load_json("bills.json")
    
    # Get unpaid orders for this customer
    unpaid_orders = [
        o for o in orders 
        if o.get("customer_id") == customer_id and o.get("status") in ["served", "ready"]
    ]
    
    if not unpaid_orders:
        return {"status": "error", "message": "No orders to bill"}
    
    total = sum(o.get("total", 0) for o in unpaid_orders)
    
    new_bill = {
        "id": str(uuid.uuid4())[:8],
        "customer_id": customer_id,
        "orders": [o["id"] for o in unpaid_orders],
        "subtotal": round(total, 2),
        "tax": round(total * 0.08, 2),
        "total": round(total * 1.08, 2),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    bills.append(new_bill)
    _save_json("bills.json", bills)
    logger.info(f"✅ Generated bill: {new_bill}")
    return {"status": "success", "bill": new_bill}


@mcp.tool()
def process_payment(bill_id: str, payment_method: str) -> dict:
    """Process payment for a bill.
    
    Args:
        bill_id: ID of the bill to pay.
        payment_method: Payment method (cash, card, tab).
    
    Returns:
        Payment confirmation.
    """
    logger.info(f"💳 Processing payment for bill {bill_id} via {payment_method}")
    bills = _load_json("bills.json")
    customers = _load_json("customers.json")
    
    for bill in bills:
        if bill.get("id") == bill_id:
            if bill.get("status") == "paid":
                return {"status": "error", "message": "Bill already paid"}
            
            bill["status"] = "paid"
            bill["payment_method"] = payment_method
            bill["paid_at"] = datetime.now().isoformat()
            
            # Update customer visit count
            for customer in customers:
                if customer.get("id") == bill.get("customer_id"):
                    customer["total_visits"] = customer.get("total_visits", 0) + 1
                    break
            
            _save_json("bills.json", bills)
            _save_json("customers.json", customers)
            logger.info(f"✅ Payment processed for bill {bill_id}")
            return {
                "status": "success",
                "message": "Payment processed successfully",
                "bill": bill
            }
    
    return {"status": "error", "message": "Bill not found"}


@mcp.tool()
def add_to_tab(customer_id: str, amount: float) -> dict:
    """Add an amount to customer's tab for later payment.
    
    Args:
        customer_id: ID of the customer.
        amount: Amount to add to tab.
    
    Returns:
        Updated tab balance.
    """
    logger.info(f"📝 Adding ${amount} to tab for customer {customer_id}")
    customers = _load_json("customers.json")
    
    for customer in customers:
        if customer.get("id") == customer_id:
            customer["tab_balance"] = customer.get("tab_balance", 0) + amount
            _save_json("customers.json", customers)
            logger.info(f"✅ Tab updated. New balance: ${customer['tab_balance']}")
            return {
                "status": "success",
                "tab_balance": customer["tab_balance"],
                "customer": customer
            }
    
    return {"status": "error", "message": "Customer not found"}


def create_app():
    """Create the ASGI app for deployment."""
    return mcp.http_app()


# For Cloud Run deployment with uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Restaurant backend server starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

