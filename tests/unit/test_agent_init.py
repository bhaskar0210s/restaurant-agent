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

"""Simple unit tests for agent module initialization."""

import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Add restaurant_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))


class TestAgentModule(unittest.TestCase):
    """Test cases for agent module."""

    def test_backend_api_url_default(self):
        """Test that BACKEND_API_URL has a default value."""
        from restaurant_agent.agent import BACKEND_API_URL
        
        # Should have a default value
        self.assertIsNotNone(BACKEND_API_URL)
        self.assertIsInstance(BACKEND_API_URL, str)
        self.assertGreater(len(BACKEND_API_URL), 0)

    def test_backend_api_url_structure(self):
        """Test that BACKEND_API_URL has correct structure."""
        from restaurant_agent.agent import BACKEND_API_URL
        
        # Should be a valid URL format
        self.assertIsInstance(BACKEND_API_URL, str)
        # Should contain /mcp endpoint
        self.assertIn("/mcp", BACKEND_API_URL)

    def test_prompts_exist(self):
        """Test that all required prompts exist."""
        from restaurant_agent.prompts import (
            CAPTAIN_INSTRUCTION,
            WAITER_INSTRUCTION,
            CHEF_INSTRUCTION,
            SERVER_INSTRUCTION,
            CASHIER_INSTRUCTION,
        )
        
        self.assertIsNotNone(CAPTAIN_INSTRUCTION)
        self.assertIsNotNone(WAITER_INSTRUCTION)
        self.assertIsNotNone(CHEF_INSTRUCTION)
        self.assertIsNotNone(SERVER_INSTRUCTION)
        self.assertIsNotNone(CASHIER_INSTRUCTION)
        
        # Check that prompts are not empty
        self.assertGreater(len(CAPTAIN_INSTRUCTION), 0)
        self.assertGreater(len(WAITER_INSTRUCTION), 0)
        self.assertGreater(len(CHEF_INSTRUCTION), 0)
        self.assertGreater(len(SERVER_INSTRUCTION), 0)
        self.assertGreater(len(CASHIER_INSTRUCTION), 0)

    def test_callbacks_exist(self):
        """Test that callback functions exist."""
        from restaurant_agent.callbacks import (
            track_waiter_tools,
            enforce_waiter_prerequisites,
            track_captain_tools,
            enforce_captain_workflow,
            REQUIRED_WAITER_TOOLS,
            CAPTAIN_WORKFLOW_TOOLS,
        )
        
        self.assertIsNotNone(track_waiter_tools)
        self.assertIsNotNone(enforce_waiter_prerequisites)
        self.assertIsNotNone(track_captain_tools)
        self.assertIsNotNone(enforce_captain_workflow)
        self.assertIsNotNone(REQUIRED_WAITER_TOOLS)
        self.assertIsNotNone(CAPTAIN_WORKFLOW_TOOLS)
        
        # Check that constants are sets/lists
        self.assertIsInstance(REQUIRED_WAITER_TOOLS, set)
        self.assertIsInstance(CAPTAIN_WORKFLOW_TOOLS, list)
        self.assertGreater(len(REQUIRED_WAITER_TOOLS), 0)
        self.assertGreater(len(CAPTAIN_WORKFLOW_TOOLS), 0)

    def test_tools_exist(self):
        """Test that all tools are exported."""
        from restaurant_agent.tools import ALL_TOOLS
        
        self.assertIsNotNone(ALL_TOOLS)
        self.assertIsInstance(ALL_TOOLS, list)
        self.assertGreater(len(ALL_TOOLS), 0)
        
        # Check that common tools exist
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
        
        # All should be callable
        self.assertTrue(callable(get_customer))
        self.assertTrue(callable(get_reservations))
        self.assertTrue(callable(create_reservation))
        self.assertTrue(callable(check_table_availability))
        self.assertTrue(callable(assign_table))
        self.assertTrue(callable(release_table))
        self.assertTrue(callable(get_menu))
        self.assertTrue(callable(get_customer_orders))
        self.assertTrue(callable(create_order))
        self.assertTrue(callable(get_order_status))
        self.assertTrue(callable(update_order_status))
        self.assertTrue(callable(generate_bill))
        self.assertTrue(callable(process_payment))
        self.assertTrue(callable(add_to_tab))


if __name__ == "__main__":
    unittest.main()

