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

"""Unit tests for agent tools (HTTP wrappers)."""

import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Add restaurant_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from restaurant_agent.tools import (
    get_customer,
    get_reservations,
    create_reservation,
    check_table_availability,
    assign_table,
    release_table,
    get_menu,
    get_customer_orders,
    create_order,
    get_order_status,
    update_order_status,
    generate_bill,
    process_payment,
    add_to_tab,
)


class TestAgentTools(unittest.TestCase):
    """Test cases for agent tools (HTTP wrappers)."""


    @patch("restaurant_agent.tools.httpx.Client")
    def test_get_customer(self, mock_client_class):
        """Test get_customer tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {"status": "found", "customer": {"id": "cust001", "name": "John"}}
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = get_customer(name="John", phone="555-0101")
        self.assertEqual(result["status"], "found")

    @patch("restaurant_agent.tools.httpx.Client")
    def test_get_reservations(self, mock_client_class):
        """Test get_reservations tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "reservations": [
                    {"id": "res001", "date": "2025-12-25", "time": "19:00"}
                ],
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = get_reservations(customer_id="cust001")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["reservations"]), 1)

    @patch("restaurant_agent.tools.httpx.Client")
    def test_create_reservation(self, mock_client_class):
        """Test create_reservation tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "created",
                "reservation": {
                    "id": "res002",
                    "date": "2025-12-26",
                    "time": "20:00",
                    "party_size": 4,
                },
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = create_reservation(
            customer_id="cust001", date="2025-12-26", time="20:00", party_size=4
        )
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["reservation"]["party_size"], 4)

    @patch("restaurant_agent.tools.httpx.Client")
    def test_check_table_availability(self, mock_client_class):
        """Test check_table_availability tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "available_tables": [
                    {"id": "table01", "capacity": 2},
                    {"id": "table02", "capacity": 4},
                ],
                "count": 2,
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = check_table_availability(party_size=2)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 2)

    @patch("restaurant_agent.tools.httpx.Client")
    def test_assign_table(self, mock_client_class):
        """Test assign_table tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "table": {"id": "table01", "status": "occupied", "customer_id": "cust001"},
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = assign_table(customer_id="cust001", table_id="table01")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["table"]["status"], "occupied")

    @patch("restaurant_agent.tools.httpx.Client")
    def test_release_table(self, mock_client_class):
        """Test release_table tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {"status": "success", "table": {"id": "table01", "status": "available"}}
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = release_table(table_id="table01")
        self.assertEqual(result["status"], "success")

    @patch("restaurant_agent.tools.httpx.Client")
    def test_get_menu(self, mock_client_class):
        """Test get_menu tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "items": [
                    {"id": "app001", "name": "Bruschetta", "category": "appetizers", "price": 8.99}
                ],
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = get_menu()
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["items"]), 0)

    @patch("restaurant_agent.tools.httpx.Client")
    def test_get_customer_orders(self, mock_client_class):
        """Test get_customer_orders tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "orders": [
                    {"id": "order001", "customer_id": "cust001", "total": 33.98}
                ],
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = get_customer_orders(customer_id="cust001", limit=5)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["orders"]), 1)

    @patch("restaurant_agent.tools.httpx.Client")
    def test_create_order(self, mock_client_class):
        """Test create_order tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "created",
                "order": {
                    "id": "order002",
                    "customer_id": "cust001",
                    "table_id": "table01",
                    "items": [{"name": "Bruschetta", "quantity": 2}],
                    "total": 17.98,
                    "status": "pending",
                },
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        items = [{"name": "Bruschetta", "quantity": 2}]
        result = create_order(customer_id="cust001", table_id="table01", items=items)
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["order"]["status"], "pending")

    @patch("restaurant_agent.tools.httpx.Client")
    def test_get_order_status(self, mock_client_class):
        """Test get_order_status tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "order": {"id": "order001", "status": "ready"},
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = get_order_status(order_id="order001")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["order"]["status"], "ready")

    @patch("restaurant_agent.tools.httpx.Client")
    def test_update_order_status(self, mock_client_class):
        """Test update_order_status tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "order": {"id": "order001", "status": "ready"},
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = update_order_status(order_id="order001", status="ready")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["order"]["status"], "ready")

    @patch("restaurant_agent.tools.httpx.Client")
    def test_generate_bill(self, mock_client_class):
        """Test generate_bill tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "bill": {
                    "id": "bill001",
                    "customer_id": "cust001",
                    "subtotal": 33.98,
                    "tax": 2.72,
                    "total": 36.70,
                    "status": "pending",
                },
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = generate_bill(customer_id="cust001")
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["bill"]["total"], 0)

    @patch("restaurant_agent.tools.httpx.Client")
    def test_process_payment(self, mock_client_class):
        """Test process_payment tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "message": "Payment processed successfully",
                "bill": {"id": "bill001", "status": "paid", "payment_method": "card"},
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = process_payment(bill_id="bill001", payment_method="card")
        self.assertEqual(result["status"], "success")
        self.assertIn("Payment processed", result["message"])

    @patch("restaurant_agent.tools.httpx.Client")
    def test_add_to_tab(self, mock_client_class):
        """Test add_to_tab tool."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": "success",
                "tab_balance": 50.0,
                "customer": {"id": "cust001", "tab_balance": 50.0},
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = add_to_tab(customer_id="cust001", amount=50.0)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tab_balance"], 50.0)

    @patch("restaurant_agent.tools.httpx.Client")
    def test_tool_error_handling(self, mock_client_class):
        """Test error handling in tools."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": {"message": "Backend error"}}
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        with self.assertRaises(RuntimeError) as context:
            get_customer(name="Test", phone="555-0000")
        self.assertIn("Backend API error", str(context.exception))

    @patch("restaurant_agent.tools.httpx.Client")
    def test_tool_http_error(self, mock_client_class):
        """Test HTTP error handling."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client.post.side_effect = Exception("Connection error")
        mock_client_class.return_value = mock_client

        with self.assertRaises(Exception):
            get_customer(name="Test", phone="555-0000")


if __name__ == "__main__":
    unittest.main()

