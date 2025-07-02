"""
MCP Tools for {{cookiecutter.project_name}}
Auto-generated from mcp-server-template

This module contains all MCP tool definitions for {{cookiecutter.api_service_type}} integration.
"""

from .example_tools import *

__all__ = [
    "register_all_tools",
    "get_available_tools"
]


def register_all_tools(mcp_server):
    """
    Register all available tools with the MCP server
    
    Args:
        mcp_server: FastMCP server instance
    """
    from .example_tools import register_tools
    
    # Register example tools
    register_tools(mcp_server)
    
    print(f"✅ All {{cookiecutter.project_name}} tools registered successfully")


def get_available_tools():
    """
    Get list of all available tools
    
    Returns:
        List[str]: Names of all available tools
    """
    return [
        "get_api_status",
        "list_resources", 
        "get_resource_by_id",
        "create_resource",
        "update_resource",
        "delete_resource"
    ]
