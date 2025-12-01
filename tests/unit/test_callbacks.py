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

"""Unit tests for callback functions."""

import unittest
from unittest.mock import MagicMock, Mock

import sys
import os

# Add restaurant_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from restaurant_agent.callbacks import (
    track_waiter_tools,
    enforce_waiter_prerequisites,
    track_captain_tools,
    enforce_captain_workflow,
    REQUIRED_WAITER_TOOLS,
    CAPTAIN_WORKFLOW_TOOLS,
)


class TestCallbacks(unittest.TestCase):
    """Test cases for callback functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool_context = MagicMock()
        self.tool_context.state = {}

    def test_track_waiter_tools(self):
        """Test tracking waiter tool calls."""
        tool = MagicMock()
        tool.name = "get_customer_orders"

        result = track_waiter_tools(
            tool=tool,
            args={},
            tool_context=self.tool_context,
            tool_response={},
        )

        self.assertIsNone(result)
        self.assertTrue(self.tool_context.state.get("waiter_get_customer_orders_called"))

    def test_track_waiter_tools_non_required(self):
        """Test tracking non-required waiter tools."""
        tool = MagicMock()
        tool.name = "some_other_tool"

        result = track_waiter_tools(
            tool=tool,
            args={},
            tool_context=self.tool_context,
            tool_response={},
        )

        self.assertIsNone(result)
        self.assertNotIn("waiter_some_other_tool_called", self.tool_context.state)

    def test_track_captain_tools(self):
        """Test tracking captain tool calls."""
        tool = MagicMock()
        tool.name = "get_customer"

        result = track_captain_tools(
            tool=tool,
            args={},
            tool_context=self.tool_context,
            tool_response={},
        )

        self.assertIsNone(result)
        self.assertTrue(self.tool_context.state.get("captain_get_customer_called"))

    def test_enforce_waiter_prerequisites_all_called(self):
        """Test waiter prerequisites when all tools are called."""
        callback_context = MagicMock()
        callback_context._invocation_context.agent.name = "waiter_agent"
        callback_context.state = {
            "waiter_get_customer_orders_called": True,
            "waiter_get_menu_called": True,
        }
        callback_context._invocation_context.session = MagicMock()
        callback_context._invocation_context.session.events = []

        llm_request = MagicMock()
        llm_request.contents = []

        result = enforce_waiter_prerequisites(callback_context, llm_request)
        self.assertIsNone(result)

    def test_enforce_waiter_prerequisites_missing_tools(self):
        """Test waiter prerequisites when tools are missing."""
        callback_context = MagicMock()
        callback_context._invocation_context.agent.name = "waiter_agent"
        callback_context.state = {}
        callback_context._invocation_context.session = MagicMock()
        callback_context._invocation_context.session.events = []

        llm_request = MagicMock()
        content = MagicMock()
        content.parts = []
        llm_request.contents = [content]

        result = enforce_waiter_prerequisites(callback_context, llm_request)
        self.assertIsNone(result)
        # Should inject instruction
        self.assertGreater(len(llm_request.contents), 1)

    def test_enforce_waiter_prerequisites_other_agent(self):
        """Test waiter prerequisites for non-waiter agent."""
        callback_context = MagicMock()
        callback_context._invocation_context.agent.name = "captain_agent"
        callback_context.state = {}
        callback_context._invocation_context.session = MagicMock()

        llm_request = MagicMock()

        result = enforce_waiter_prerequisites(callback_context, llm_request)
        self.assertIsNone(result)
        # Should not modify request for other agents
        self.assertEqual(len(llm_request.contents), 0)

    def test_enforce_waiter_prerequisites_already_calling_tools(self):
        """Test waiter prerequisites when agent is already calling tools."""
        callback_context = MagicMock()
        callback_context._invocation_context.agent.name = "waiter_agent"
        callback_context.state = {}
        callback_context._invocation_context.session = MagicMock()
        callback_context._invocation_context.session.events = []

        llm_request = MagicMock()
        part = MagicMock()
        part.function_call = MagicMock()  # Simulating tool call
        content = MagicMock()
        content.parts = [part]
        llm_request.contents = [content]

        result = enforce_waiter_prerequisites(callback_context, llm_request)
        self.assertIsNone(result)
        # Should not inject instruction if already calling tools

    def test_enforce_captain_workflow_complete(self):
        """Test captain workflow when complete."""
        callback_context = MagicMock()
        callback_context._invocation_context.agent.name = "captain_agent"
        callback_context.state = {}
        callback_context._invocation_context.session = MagicMock()

        # Create mock events showing all tools called
        events = []
        for tool_name in CAPTAIN_WORKFLOW_TOOLS:
            event = MagicMock()
            event.function_call = MagicMock()
            event.function_call.name = tool_name
            events.append(event)

        callback_context._invocation_context.session.events = events

        llm_request = MagicMock()
        llm_request.contents = []

        result = enforce_captain_workflow(callback_context, llm_request)
        self.assertIsNone(result)

    def test_enforce_captain_workflow_next_step(self):
        """Test captain workflow enforcing next step."""
        callback_context = MagicMock()
        callback_context._invocation_context.agent.name = "captain_agent"
        callback_context.state = {}

        # Create mock events showing get_customer called
        event = MagicMock()
        event.function_call = MagicMock()
        event.function_call.name = "get_customer"
        event.function_response = {"id": "cust001"}
        callback_context._invocation_context.session = MagicMock()
        callback_context._invocation_context.session.events = [event]

        llm_request = MagicMock()
        content = MagicMock()
        content.parts = []
        llm_request.contents = [content]

        result = enforce_captain_workflow(callback_context, llm_request)
        self.assertIsNone(result)
        # Should inject instruction for next step (get_reservations)
        self.assertGreater(len(llm_request.contents), 1)

    def test_enforce_captain_workflow_other_agent(self):
        """Test captain workflow for non-captain agent."""
        callback_context = MagicMock()
        callback_context._invocation_context.agent.name = "waiter_agent"
        callback_context.state = {}
        callback_context._invocation_context.session = MagicMock()

        llm_request = MagicMock()

        result = enforce_captain_workflow(callback_context, llm_request)
        self.assertIsNone(result)
        # Should not modify request for other agents

    def test_enforce_captain_workflow_already_calling_tools(self):
        """Test captain workflow when agent is already calling tools."""
        callback_context = MagicMock()
        callback_context._invocation_context.agent.name = "captain_agent"
        callback_context.state = {}
        callback_context._invocation_context.session = MagicMock()
        callback_context._invocation_context.session.events = []

        llm_request = MagicMock()
        part = MagicMock()
        part.function_call = MagicMock()  # Simulating tool call
        content = MagicMock()
        content.parts = [part]
        llm_request.contents = [content]

        result = enforce_captain_workflow(callback_context, llm_request)
        self.assertIsNone(result)
        # Should not inject instruction if already calling tools


if __name__ == "__main__":
    unittest.main()

