"""Sub-agents for the restaurant agent system."""

# Import order matters to avoid circular dependencies:
# server (no deps) -> chef (imports server) -> cashier (no deps) -> waiter (imports chef, cashier)
from .server import server_agent
from .chef import chef_agent
from .cashier import cashier_agent
from .waiter import waiter_agent

__all__ = ["waiter_agent", "chef_agent", "server_agent", "cashier_agent"]

