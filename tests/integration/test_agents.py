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

"""Integration tests for restaurant agents."""

import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Add restaurant_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))


class TestAgentInitialization(unittest.TestCase):
    """Test cases for agent initialization."""

    @patch("restaurant_agent.agent.load_dotenv")
    @patch("restaurant_agent.agent.os.getenv")
    def test_root_agent_initialization(self, mock_getenv, mock_load_dotenv):
        """Test that root agent is initialized correctly."""
        mock_getenv.return_value = "http://localhost:8080/mcp"
        
        # Import after mocking
        from restaurant_agent.agent import root_agent
        
        self.assertIsNotNone(root_agent)
        self.assertEqual(root_agent.name, "captain_agent")
        self.assertIn("Captain", root_agent.description)
        self.assertIsNotNone(root_agent.instruction)
        self.assertIsNotNone(root_agent.tools)
        self.assertIsNotNone(root_agent.sub_agents)
        self.assertEqual(len(root_agent.sub_agents), 1)  # Should have waiter_agent

    @patch("restaurant_agent.sub_agents.waiter.load_dotenv")
    @patch("restaurant_agent.sub_agents.waiter.os.getenv")
    def test_waiter_agent_initialization(self, mock_getenv, mock_load_dotenv):
        """Test that waiter agent is initialized correctly."""
        mock_getenv.return_value = "http://localhost:8080/mcp"
        
        from restaurant_agent.sub_agents.waiter import waiter_agent
        
        self.assertIsNotNone(waiter_agent)
        self.assertEqual(waiter_agent.name, "waiter_agent")
        self.assertIn("Waiter", waiter_agent.description)
        self.assertIsNotNone(waiter_agent.instruction)
        self.assertIsNotNone(waiter_agent.tools)
        self.assertIsNotNone(waiter_agent.sub_agents)
        self.assertGreaterEqual(len(waiter_agent.sub_agents), 1)

    @patch("restaurant_agent.sub_agents.chef.load_dotenv")
    @patch("restaurant_agent.sub_agents.chef.os.getenv")
    def test_chef_agent_initialization(self, mock_getenv, mock_load_dotenv):
        """Test that chef agent is initialized correctly."""
        mock_getenv.return_value = "http://localhost:8080/mcp"
        
        from restaurant_agent.sub_agents.chef import chef_agent
        
        self.assertIsNotNone(chef_agent)
        self.assertEqual(chef_agent.name, "chef_agent")
        self.assertIn("Chef", chef_agent.description)
        self.assertIsNotNone(chef_agent.instruction)
        self.assertIsNotNone(chef_agent.tools)
        self.assertIsNotNone(chef_agent.sub_agents)

    @patch("restaurant_agent.sub_agents.cashier.load_dotenv")
    @patch("restaurant_agent.sub_agents.cashier.os.getenv")
    def test_cashier_agent_initialization(self, mock_getenv, mock_load_dotenv):
        """Test that cashier agent is initialized correctly."""
        mock_getenv.return_value = "http://localhost:8080/mcp"
        
        from restaurant_agent.sub_agents.cashier import cashier_agent
        
        self.assertIsNotNone(cashier_agent)
        self.assertEqual(cashier_agent.name, "cashier_agent")
        self.assertIn("Cashier", cashier_agent.description)
        self.assertIsNotNone(cashier_agent.instruction)
        self.assertIsNotNone(cashier_agent.tools)

    @patch("restaurant_agent.sub_agents.server.load_dotenv")
    @patch("restaurant_agent.sub_agents.server.os.getenv")
    def test_server_agent_initialization(self, mock_getenv, mock_load_dotenv):
        """Test that server agent is initialized correctly."""
        mock_getenv.return_value = "http://localhost:8080/mcp"
        
        from restaurant_agent.sub_agents.server import server_agent
        
        self.assertIsNotNone(server_agent)
        self.assertEqual(server_agent.name, "server_agent")
        self.assertIn("Server", server_agent.description)
        self.assertIsNotNone(server_agent.instruction)
        self.assertIsNotNone(server_agent.tools)

    def test_agent_hierarchy(self):
        """Test that agent hierarchy is correct."""
        from restaurant_agent.agent import root_agent
        
        # Root agent should have waiter as sub-agent
        self.assertEqual(len(root_agent.sub_agents), 1)
        waiter = root_agent.sub_agents[0]
        self.assertEqual(waiter.name, "waiter_agent")
        
        # Waiter should have chef and cashier as sub-agents
        self.assertGreaterEqual(len(waiter.sub_agents), 1)
        sub_agent_names = [agent.name for agent in waiter.sub_agents]
        self.assertIn("chef_agent", sub_agent_names)
        self.assertIn("cashier_agent", sub_agent_names)


if __name__ == "__main__":
    unittest.main()
