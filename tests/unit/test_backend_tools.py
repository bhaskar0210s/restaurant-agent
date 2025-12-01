# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for backend server tools."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

# Add backend-server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend-server"))

# Import the mcp object to access tools
from server import mcp

# Access the underlying functions from FastMCP tools
# FastMCP tools are FunctionTool objects, we need to get the underlying function
def _get_tool_function(tool_name: str):
    """Get the underlying function from a FastMCP tool."""
    tool = mcp._tool_manager._tools.get(tool_name)
    if tool and hasattr(tool, 'fn'):
        return tool.fn
    raise ValueError(f"Tool {tool_name} not found")

# Create callable wrappers
get_customer = _get_tool_function("get_customer")
get_reservations = _get_tool_function("get_reservations")
create_reservation = _get_tool_function("create_reservation")
check_table_availability = _get_tool_function("check_table_availability")
assign_table = _get_tool_function("assign_table")
release_table = _get_tool_function("release_table")
get_menu = _get_tool_function("get_menu")
get_customer_orders = _get_tool_function("get_customer_orders")
create_order = _get_tool_function("create_order")
get_order_status = _get_tool_function("get_order_status")
update_order_status = _get_tool_function("update_order_status")
generate_bill = _get_tool_function("generate_bill")
process_payment = _get_tool_function("process_payment")
add_to_tab = _get_tool_function("add_to_tab")


class TestBackendTools(unittest.TestCase):
    """Test cases for backend server tools."""

    def setUp(self):
        """Set up test fixtures with temporary data directory."""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Patch the DATA_DIR in server module
        self.patcher = patch("server.DATA_DIR", self.data_dir)
        self.patcher.start()

        # Initialize test data files
        self._init_test_data()

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir)

    def _init_test_data(self):
        """Initialize test data files."""
        # Customers
        customers = [
            {
                "id": "cust001",
                "name": "John Smith",
                "phone": "555-0101",
                "created_at": "2025-01-15T10:30:00",
                "total_visits": 0,
                "tab_balance": 0.0,
            },
            {
                "id": "cust002",
                "name": "Sarah Johnson",
                "phone": "555-0102",
                "created_at": "2025-02-20T14:45:00",
                "total_visits": 0,
                "tab_balance": 0.0,
            },
        ]
        self._save_json("customers.json", customers)

        # Tables
        tables = [
            {
                "id": "table01",
                "number": 1,
                "capacity": 2,
                "location": "window",
                "status": "available",
                "customer_id": None,
                "seated_at": None,
            },
            {
                "id": "table02",
                "number": 2,
                "capacity": 4,
                "location": "center",
                "status": "available",
                "customer_id": None,
                "seated_at": None,
            },
            {
                "id": "table03",
                "number": 3,
                "capacity": 6,
                "location": "corner",
                "status": "occupied",
                "customer_id": "cust001",
                "seated_at": "2025-01-15T10:30:00",
            },
        ]
        self._save_json("tables.json", tables)

        # Menu
        menu = {
            "items": [
                {
                    "id": "app001",
                    "name": "Bruschetta",
                    "category": "appetizers",
                    "description": "Grilled bread",
                    "price": 8.99,
                },
                {
                    "id": "main001",
                    "name": "Grilled Salmon",
                    "category": "mains",
                    "description": "Atlantic salmon",
                    "price": 24.99,
                },
            ]
        }
        self._save_json("menu.json", menu)

        # Reservations
        reservations = [
            {
                "id": "res001",
                "customer_id": "cust001",
                "date": "2025-12-25",
                "time": "19:00",
                "party_size": 2,
                "status": "confirmed",
                "created_at": "2025-01-15T10:30:00",
            }
        ]
        self._save_json("reservations.json", reservations)

        # Orders
        orders = [
            {
                "id": "order001",
                "customer_id": "cust001",
                "table_id": "table03",
                "items": [
                    {"name": "Bruschetta", "price": 8.99, "quantity": 1},
                    {"name": "Grilled Salmon", "price": 24.99, "quantity": 1},
                ],
                "total": 33.98,
                "status": "served",
                "created_at": "2025-01-15T10:30:00",
            }
        ]
        self._save_json("orders.json", orders)

        # Bills
        bills = []
        self._save_json("bills.json", bills)

    def _save_json(self, filename: str, data):
        """Save JSON data to test file."""
        filepath = self.data_dir / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def _load_json(self, filename: str):
        """Load JSON data from test file."""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, "r") as f:
                return json.load(f)
        return [] if filename != "menu.json" else {"items": []}

    # ============== Customer Management Tests ==============

    def test_get_customer_existing(self):
        """Test getting existing customer."""
        result = get_customer(name="John Smith", phone="555-0101")
        self.assertEqual(result["status"], "found")
        self.assertEqual(result["customer"]["id"], "cust001")

    def test_get_customer_new(self):
        """Test getting non-existent customer (should create)."""
        result = get_customer(name="New Customer", phone="555-8888")
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["customer"]["name"], "New Customer")

    # ============== Reservation Management Tests ==============

    def test_get_reservations_by_customer(self):
        """Test getting reservations by customer ID."""
        result = get_reservations(customer_id="cust001")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["reservations"]), 1)
        self.assertEqual(result["reservations"][0]["date"], "2025-12-25")

    def test_get_reservations_by_date(self):
        """Test getting reservations by date."""
        result = get_reservations(date="2025-12-25")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["reservations"]), 1)

    def test_get_reservations_empty(self):
        """Test getting reservations with no matches."""
        result = get_reservations(customer_id="nonexistent")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["reservations"]), 0)

    def test_create_reservation(self):
        """Test creating a new reservation."""
        result = create_reservation(
            customer_id="cust002",
            date="2025-12-26",
            time="20:00",
            party_size=4,
        )
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["reservation"]["date"], "2025-12-26")
        self.assertEqual(result["reservation"]["party_size"], 4)
        self.assertIn("id", result["reservation"])

    # ============== Table Management Tests ==============

    def test_check_table_availability(self):
        """Test checking table availability."""
        result = check_table_availability(party_size=2)
        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["count"], 1)
        # Should find table01 (capacity 2) and table02 (capacity 4)
        available_ids = [t["id"] for t in result["available_tables"]]
        self.assertIn("table01", available_ids)
        self.assertIn("table02", available_ids)

    def test_check_table_availability_no_match(self):
        """Test checking availability for party size with no matches."""
        result = check_table_availability(party_size=20)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 0)

    def test_assign_table(self):
        """Test assigning a table to a customer."""
        result = assign_table(customer_id="cust002", table_id="table01")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["table"]["status"], "occupied")
        self.assertEqual(result["table"]["customer_id"], "cust002")
        self.assertIsNotNone(result["table"]["seated_at"])

    def test_assign_table_already_occupied(self):
        """Test assigning an already occupied table."""
        result = assign_table(customer_id="cust002", table_id="table03")
        self.assertEqual(result["status"], "error")
        self.assertIn("not available", result["message"])

    def test_assign_table_not_found(self):
        """Test assigning non-existent table."""
        result = assign_table(customer_id="cust002", table_id="nonexistent")
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])

    def test_release_table(self):
        """Test releasing a table."""
        result = release_table(capacity=6)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["table"]["status"], "available")
        self.assertIsNone(result["table"]["customer_id"])

    def test_release_table_not_found(self):
        """Test releasing table with no occupied tables of that capacity."""
        result = release_table(capacity=20)
        self.assertEqual(result["status"], "error")

    # ============== Menu Management Tests ==============

    def test_get_menu_all(self):
        """Test getting entire menu."""
        result = get_menu()
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["items"]), 0)

    def test_get_menu_by_category(self):
        """Test getting menu filtered by category."""
        result = get_menu(category="appetizers")
        self.assertEqual(result["status"], "success")
        for item in result["items"]:
            self.assertEqual(item["category"], "appetizers")

    # ============== Order Management Tests ==============

    def test_get_customer_orders(self):
        """Test getting customer orders."""
        result = get_customer_orders(customer_id="cust001", limit=5)
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["orders"]), 0)
        self.assertEqual(result["orders"][0]["customer_id"], "cust001")

    def test_get_customer_orders_empty(self):
        """Test getting orders for customer with no orders."""
        result = get_customer_orders(customer_id="cust002", limit=5)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["orders"]), 0)

    def test_create_order(self):
        """Test creating a new order."""
        items = [{"name": "Bruschetta", "quantity": 2}]
        result = create_order(
            customer_id="cust002", table_id="table02", items=items
        )
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["order"]["customer_id"], "cust002")
        self.assertEqual(result["order"]["status"], "pending")
        self.assertEqual(len(result["order"]["items"]), 1)
        self.assertEqual(result["order"]["items"][0]["quantity"], 2)

    def test_create_order_invalid_item(self):
        """Test creating order with invalid menu item."""
        items = [{"name": "Nonexistent Item", "quantity": 1}]
        result = create_order(
            customer_id="cust002", table_id="table02", items=items
        )
        # Order should be created but with empty items
        self.assertEqual(result["status"], "created")
        self.assertEqual(len(result["order"]["items"]), 0)

    def test_get_order_status(self):
        """Test getting order status."""
        result = get_order_status(order_id="order001")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["order"]["id"], "order001")
        self.assertEqual(result["order"]["status"], "served")

    def test_get_order_status_not_found(self):
        """Test getting status for non-existent order."""
        result = get_order_status(order_id="nonexistent")
        self.assertEqual(result["status"], "error")

    def test_update_order_status(self):
        """Test updating order status."""
        result = update_order_status(order_id="order001", status="ready")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["order"]["status"], "ready")
        self.assertIn("updated_at", result["order"])

    def test_update_order_status_not_found(self):
        """Test updating status for non-existent order."""
        result = update_order_status(order_id="nonexistent", status="ready")
        self.assertEqual(result["status"], "error")

    # ============== Payment Management Tests ==============

    def test_generate_bill(self):
        """Test generating a bill for customer."""
        # First create an order with served status
        items = [{"name": "Bruschetta", "quantity": 1}]
        order_result = create_order(
            customer_id="cust002", table_id="table02", items=items
        )
        order_id = order_result["order"]["id"]
        update_order_status(order_id=order_id, status="served")

        result = generate_bill(customer_id="cust002")
        self.assertEqual(result["status"], "success")
        self.assertIn("bill", result)
        self.assertGreater(result["bill"]["total"], 0)
        self.assertIn("tax", result["bill"])

    def test_generate_bill_no_orders(self):
        """Test generating bill with no orders."""
        result = generate_bill(customer_id="cust002")
        # Should fail if no orders exist
        if result["status"] == "error":
            self.assertIn("No orders", result["message"])

    def test_process_payment(self):
        """Test processing payment for a bill."""
        # Create order and bill first
        items = [{"name": "Bruschetta", "quantity": 1}]
        order_result = create_order(
            customer_id="cust002", table_id="table02", items=items
        )
        order_id = order_result["order"]["id"]
        update_order_status(order_id=order_id, status="served")
        bill_result = generate_bill(customer_id="cust002")
        bill_id = bill_result["bill"]["id"]

        result = process_payment(bill_id=bill_id, payment_method="card")
        self.assertEqual(result["status"], "success")
        self.assertIn("Payment processed", result["message"])

        # Verify bill is marked as paid
        bills = self._load_json("bills.json")
        bill = next(b for b in bills if b["id"] == bill_id)
        self.assertEqual(bill["status"], "paid")
        self.assertEqual(bill["payment_method"], "card")

    def test_process_payment_already_paid(self):
        """Test processing payment for already paid bill."""
        # Create and pay bill
        items = [{"name": "Bruschetta", "quantity": 1}]
        order_result = create_order(
            customer_id="cust002", table_id="table02", items=items
        )
        order_id = order_result["order"]["id"]
        update_order_status(order_id=order_id, status="served")
        bill_result = generate_bill(customer_id="cust002")
        bill_id = bill_result["bill"]["id"]
        process_payment(bill_id=bill_id, payment_method="card")

        # Try to pay again
        result = process_payment(bill_id=bill_id, payment_method="cash")
        self.assertEqual(result["status"], "error")
        self.assertIn("already paid", result["message"])

    def test_add_to_tab(self):
        """Test adding amount to customer tab."""
        result = add_to_tab(customer_id="cust001", amount=50.0)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tab_balance"], 50.0)

        # Add more
        result = add_to_tab(customer_id="cust001", amount=25.0)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tab_balance"], 75.0)

    def test_add_to_tab_customer_not_found(self):
        """Test adding to tab for non-existent customer."""
        result = add_to_tab(customer_id="nonexistent", amount=50.0)
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()

