"""Callback functions for restaurant agents."""

import logging
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

logger = logging.getLogger(__name__)

# Required tools that must be called before the waiter can interact with customers
REQUIRED_WAITER_TOOLS = {"get_customer_orders", "get_menu"}

# Required tools for captain workflow (in order)
CAPTAIN_WORKFLOW_TOOLS = ["get_customer", "get_reservations", "check_table_availability", "assign_table", "transfer_to_agent"]


def track_waiter_tools(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
) -> Optional[dict]:
    """Track when required waiter tools have been called."""
    if tool.name in REQUIRED_WAITER_TOOLS:
        tool_context.state[f"waiter_{tool.name}_called"] = True
        logger.info(f"✅ Tracked waiter tool call: {tool.name}")
    return None


def enforce_waiter_prerequisites(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Enforce that required tools are called before waiter interacts with customer.
    
    This callback checks if the waiter agent has called get_customer_orders and get_menu
    before generating user-facing messages. If not, it injects instructions to call them first.
    """
    # Only apply to waiter_agent
    agent_name = callback_context._invocation_context.agent.name
    if agent_name != "waiter_agent":
        return None
    
    # Check session events to see if required tools have been called
    session = callback_context._invocation_context.session
    state = callback_context.state
    
    # Check if tools have been called in this session
    tools_called = {
        tool_name: state.get(f"waiter_{tool_name}_called", False)
        for tool_name in REQUIRED_WAITER_TOOLS
    }
    
    # Also check session events as a fallback - look for function_call events
    for event in session.events:
        if hasattr(event, "function_call") and event.function_call:
            tool_name = event.function_call.name
            if tool_name in REQUIRED_WAITER_TOOLS:
                tools_called[tool_name] = True
                state[f"waiter_{tool_name}_called"] = True
    
    # If all required tools have been called, allow the request to proceed
    if all(tools_called.values()):
        return None
    
    # Check if this request already contains tool calls - if so, allow it
    # (the agent might be calling the required tools)
    has_tool_calls = False
    for content in llm_request.contents:
        for part in content.parts:
            if hasattr(part, "function_call") and part.function_call:
                has_tool_calls = True
                break
    
    # If the agent is already calling tools, allow it to proceed
    if has_tool_calls:
        return None
    
    # If tools haven't been called and agent isn't calling tools now,
    # inject instruction to call them first
    missing_tools = [tool for tool, called in tools_called.items() if not called]
    logger.warning(
        f"⚠️ Waiter agent needs to call required tools first: {missing_tools}"
    )
    
    # Inject instruction into the request
    instruction_text = (
        "CRITICAL: Before greeting or asking the customer anything, you MUST first call these tools:\n"
    )
    for tool in missing_tools:
        instruction_text += f"- {tool}\n"
    instruction_text += (
        "\nDo NOT greet the customer or ask any questions until you have called ALL of these tools. "
        "Call them now automatically without asking the customer."
    )
    
    # Prepend instruction to the request contents
    instruction_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=instruction_text)]
    )
    llm_request.contents.insert(0, instruction_content)
    logger.info(f"📝 Injected instruction to call tools: {missing_tools}")
    
    return None


def track_captain_tools(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict,
) -> Optional[dict]:
    """Track when captain workflow tools have been called."""
    if tool.name in CAPTAIN_WORKFLOW_TOOLS:
        tool_context.state[f"captain_{tool.name}_called"] = True
        logger.info(f"✅ Tracked captain tool call: {tool.name}")
    return None


def enforce_captain_workflow(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Enforce that captain completes the full workflow automatically.
    
    After get_customer succeeds, captain MUST call get_reservations, check_table_availability,
    assign_table, and transfer_to_agent without asking the customer.
    """
    # Only apply to captain_agent
    agent_name = callback_context._invocation_context.agent.name
    if agent_name != "captain_agent":
        return None
    
    session = callback_context._invocation_context.session
    state = callback_context.state
    
    # Check which tools have been called
    tools_called = {}
    for tool_name in CAPTAIN_WORKFLOW_TOOLS:
        # Check state first
        called = state.get(f"captain_{tool_name}_called", False)
        # Also check session events
        for event in session.events:
            if hasattr(event, "function_call") and event.function_call:
                if event.function_call.name == tool_name:
                    called = True
                    state[f"captain_{tool_name}_called"] = True
                    break
        tools_called[tool_name] = called
    
    # Find the last completed step
    last_completed_index = -1
    for i, tool_name in enumerate(CAPTAIN_WORKFLOW_TOOLS):
        if tools_called[tool_name]:
            last_completed_index = i
        else:
            break
    
    # If workflow is complete (transfer_to_agent called), allow normal flow
    if last_completed_index == len(CAPTAIN_WORKFLOW_TOOLS) - 1:
        return None
    
    # Check if this request already contains tool calls - if so, allow it
    has_tool_calls = False
    for content in llm_request.contents:
        for part in content.parts:
            if hasattr(part, "function_call") and part.function_call:
                has_tool_calls = True
                break
    
    # If the agent is already calling tools, allow it to proceed
    if has_tool_calls:
        return None
    
    # Determine next required tool
    next_tool_index = last_completed_index + 1
    if next_tool_index >= len(CAPTAIN_WORKFLOW_TOOLS):
        return None
    
    next_tool = CAPTAIN_WORKFLOW_TOOLS[next_tool_index]
    
    # Special handling for each step
    if next_tool == "get_reservations":
        # Need customer_id from get_customer result
        customer_id = None
        # Try to extract from previous tool response
        for event in reversed(session.events):
            if hasattr(event, "function_call") and event.function_call:
                if event.function_call.name == "get_customer":
                    # Look for customer_id in the response
                    if hasattr(event, "function_response"):
                        response = event.function_response
                        if isinstance(response, dict) and "id" in response:
                            customer_id = response["id"]
                    break
        
        if customer_id:
            instruction_text = (
                f"CRITICAL: You MUST immediately call `get_reservations` with customer_id='{customer_id}'. "
                "Do NOT ask the customer if they have a reservation - check automatically. "
                "Call the tool now."
            )
        else:
            instruction_text = (
                "CRITICAL: You MUST immediately call `get_reservations` with the customer_id from the previous get_customer call. "
                "Do NOT ask the customer if they have a reservation - check automatically. "
                "Call the tool now."
            )
    
    elif next_tool == "check_table_availability":
        instruction_text = (
            "CRITICAL: You MUST immediately call `check_table_availability` to find available tables. "
            "Do NOT ask the customer - check automatically. Call the tool now."
        )
    
    elif next_tool == "assign_table":
        instruction_text = (
            "CRITICAL: You MUST immediately call `assign_table` to seat the customer. "
            "Use one of the available tables from the previous check_table_availability result. "
            "Call the tool now."
        )
    
    elif next_tool == "transfer_to_agent":
        instruction_text = (
            "CRITICAL: You MUST immediately call `transfer_to_agent` with agent_name='waiter_agent'. "
            "Include the customer_id and table_id in your message. Call the function now."
        )
    
    else:
        return None
    
    logger.warning(f"⚠️ Captain agent needs to call: {next_tool}")
    
    # Inject instruction into the request
    instruction_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=instruction_text)]
    )
    llm_request.contents.insert(0, instruction_content)
    logger.info(f"📝 Injected instruction to call: {next_tool}")
    
    return None

