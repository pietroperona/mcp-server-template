"""
Example MCP Tools for {{cookiecutter.project_name}}
Generic API integration tools that can be customized for any service
Auto-generated from mcp-server-template
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

# Import our core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import config
from core.client import client
from core.auth import auth


# ===================================
# 🔧 UTILITY FUNCTIONS
# ===================================

def run_async_tool(async_func, *args, **kwargs):
    """
    Synchronous wrapper for async tools - Required for FastMCP compatibility
    
    FastMCP tools must be synchronous, but our API calls are async.
    This wrapper handles the async/sync conversion properly.
    """
    try:
        import concurrent.futures
        from datetime import datetime
        
        try:
            # Try to get the existing event loop
            loop = asyncio.get_running_loop()
            
            # If we have a running loop, we need to run in a thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, async_func(*args, **kwargs))
                result = future.result(timeout=60)  # 60 second timeout
                return result
                
        except RuntimeError:
            # No running loop, safe to create new one
            result = asyncio.run(async_func(*args, **kwargs))
            return result
            
    except concurrent.futures.TimeoutError:
        return {
            "status": "error",
            "message": "Tool execution timed out after 60 seconds",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Tool execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def format_response(data: Dict[str, Any]) -> str:
    """
    Format tool response as JSON string for MCP
    
    Args:
        data: Response data dictionary
        
    Returns:
        str: Formatted JSON string
    """
    return json.dumps(data, indent=2, ensure_ascii=False)


# ===================================
# 🔍 ASYNC IMPLEMENTATION FUNCTIONS
# ===================================

async def get_api_status_async() -> Dict[str, Any]:
    """
    Get API status and connectivity information
    
    Returns:
        Dict containing API status, authentication info, and connectivity
    """
    try:
        print(f"🔍 Checking {{cookiecutter.api_service_type}} API status...")
        
        # Test authentication
        auth_info = auth.get_auth_info()
        is_auth_valid = await auth.validate_auth()
        
        # Test API connectivity
        is_api_healthy = await client.health_check()
        
        # Get client information
        client_info = await client.get_api_info()
        
        status = "healthy" if is_auth_valid and is_api_healthy else "degraded"
        
        return {
            "status": "success",
            "api_status": status,
            "timestamp": datetime.now().isoformat(),
            "authentication": {
                "type": auth_info["auth_type"],
                "valid": is_auth_valid,
                "details": auth_info
            },
            "connectivity": {
                "api_accessible": is_api_healthy,
                "base_url": client_info["base_url"],
                "timeout": client_info["timeout"]
            },
            "configuration": {
                "environment": config.mcp.environment,
                "debug_mode": config.mcp.debug,
                "server_version": config.mcp.server_version
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to check API status: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


async def list_resources_async(
    resource_type: str = "items",
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List resources from the API
    
    Args:
        resource_type: Type of resource to list (e.g., 'users', 'orders', 'products')
        limit: Maximum number of resources to return
        offset: Number of resources to skip
        
    Returns:
        Dict containing list of resources and pagination info
    """
    try:
        print(f"📋 Listing {resource_type} (limit: {limit}, offset: {offset})...")
        
        # Prepare query parameters
        params = {
            "limit": limit,
            "offset": offset
        }
        
        # Make API request - adjust endpoint based on your API
        endpoint = f"/{resource_type}"
        response = await client.get(endpoint, params=params)
        
        # Extract data (adjust based on your API response structure)
        items = response.get("data", response.get("items", response.get(resource_type, [])))
        total = response.get("total", len(items))
        
        return {
            "status": "success",
            "resource_type": resource_type,
            "items": items,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total,
                "has_more": offset + limit < total
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list {resource_type}: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


async def get_resource_by_id_async(
    resource_type: str,
    resource_id: str
) -> Dict[str, Any]:
    """
    Get a specific resource by ID
    
    Args:
        resource_type: Type of resource (e.g., 'users', 'orders', 'products')
        resource_id: Unique identifier for the resource
        
    Returns:
        Dict containing resource details
    """
    try:
        print(f"🔍 Getting {resource_type}/{resource_id}...")
        
        # Make API request
        endpoint = f"/{resource_type}/{resource_id}"
        response = await client.get(endpoint)
        
        return {
            "status": "success",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "data": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get {resource_type}/{resource_id}: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


async def create_resource_async(
    resource_type: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new resource
    
    Args:
        resource_type: Type of resource to create
        data: Resource data
        
    Returns:
        Dict containing created resource details
    """
    try:
        print(f"➕ Creating new {resource_type}...")
        
        # Make API request
        endpoint = f"/{resource_type}"
        response = await client.post(endpoint, json_data=data)
        
        return {
            "status": "success",
            "resource_type": resource_type,
            "action": "created",
            "data": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create {resource_type}: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


async def update_resource_async(
    resource_type: str,
    resource_id: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update an existing resource
    
    Args:
        resource_type: Type of resource to update
        resource_id: Unique identifier for the resource
        data: Updated resource data
        
    Returns:
        Dict containing updated resource details
    """
    try:
        print(f"✏️ Updating {resource_type}/{resource_id}...")
        
        # Make API request
        endpoint = f"/{resource_type}/{resource_id}"
        response = await client.put(endpoint, json_data=data)
        
        return {
            "status": "success",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": "updated",
            "data": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to update {resource_type}/{resource_id}: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


async def delete_resource_async(
    resource_type: str,
    resource_id: str
) -> Dict[str, Any]:
    """
    Delete a resource
    
    Args:
        resource_type: Type of resource to delete
        resource_id: Unique identifier for the resource
        
    Returns:
        Dict containing deletion confirmation
    """
    try:
        print(f"🗑️ Deleting {resource_type}/{resource_id}...")
        
        # Make API request
        endpoint = f"/{resource_type}/{resource_id}"
        response = await client.delete(endpoint)
        
        return {
            "status": "success",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": "deleted",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete {resource_type}/{resource_id}: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# ===================================
# 🔧 MCP TOOL REGISTRATION
# ===================================

def register_tools(mcp):
    """
    Register all tools with the MCP server
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    def get_api_status() -> str:
        """
        Get {{cookiecutter.api_service_type}} API status and connectivity information.
        
        Returns comprehensive status including:
        - Authentication validation
        - API connectivity check  
        - Configuration details
        - Server health status
        
        Returns:
            JSON string with complete API status information
        """
        result = run_async_tool(get_api_status_async)
        return format_response(result)
    
    @mcp.tool()
    def list_resources(resource_type: str = "items", limit: int = 10, offset: int = 0) -> str:
        """
        List resources from the {{cookiecutter.api_service_type}} API.
        
        Args:
            resource_type: Type of resource to list (default: "items")
            limit: Maximum number of resources to return (default: 10)
            offset: Number of resources to skip for pagination (default: 0)
        
        Common resource types might include:
        - users, customers, clients
        - orders, transactions, payments
        - products, items, inventory
        - projects, tasks, issues
        
        Returns:
            JSON string with list of resources and pagination information
        """
        result = run_async_tool(list_resources_async, resource_type, limit, offset)
        return format_response(result)
    
    @mcp.tool()
    def get_resource_by_id(resource_type: str, resource_id: str) -> str:
        """
        Get detailed information about a specific resource by ID.
        
        Args:
            resource_type: Type of resource (e.g., "users", "orders", "products")
            resource_id: Unique identifier for the resource
        
        Returns:
            JSON string with detailed resource information
        """
        if not resource_type or not resource_id:
            error_result = {
                "status": "error", 
                "message": "Both resource_type and resource_id are required"
            }
            return format_response(error_result)
        
        result = run_async_tool(get_resource_by_id_async, resource_type, resource_id)
        return format_response(result)
    
    @mcp.tool()
    def create_resource(resource_type: str, data: str) -> str:
        """
        Create a new resource in the {{cookiecutter.api_service_type}} API.
        
        Args:
            resource_type: Type of resource to create (e.g., "users", "orders")
            data: JSON string containing resource data
        
        Example data format:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "status": "active"
        }
        
        Returns:
            JSON string with created resource details
        """
        if not resource_type or not data:
            error_result = {
                "status": "error", 
                "message": "Both resource_type and data are required"
            }
            return format_response(error_result)
        
        try:
            # Parse JSON data
            parsed_data = json.loads(data)
        except json.JSONDecodeError as e:
            error_result = {
                "status": "error",
                "message": f"Invalid JSON data: {str(e)}"
            }
            return format_response(error_result)
        
        result = run_async_tool(create_resource_async, resource_type, parsed_data)
        return format_response(result)
    
    @mcp.tool()
    def update_resource(resource_type: str, resource_id: str, data: str) -> str:
        """
        Update an existing resource in the {{cookiecutter.api_service_type}} API.
        
        Args:
            resource_type: Type of resource to update
            resource_id: Unique identifier for the resource
            data: JSON string containing updated resource data
        
        Returns:
            JSON string with updated resource details
        """
        if not resource_type or not resource_id or not data:
            error_result = {
                "status": "error", 
                "message": "resource_type, resource_id, and data are all required"
            }
            return format_response(error_result)
        
        try:
            # Parse JSON data
            parsed_data = json.loads(data)
        except json.JSONDecodeError as e:
            error_result = {
                "status": "error",
                "message": f"Invalid JSON data: {str(e)}"
            }
            return format_response(error_result)
        
        result = run_async_tool(update_resource_async, resource_type, resource_id, parsed_data)
        return format_response(result)
    
    @mcp.tool()
    def delete_resource(resource_type: str, resource_id: str) -> str:
        """
        Delete a resource from the {{cookiecutter.api_service_type}} API.
        
        Args:
            resource_type: Type of resource to delete
            resource_id: Unique identifier for the resource
        
        Returns:
            JSON string with deletion confirmation
        """
        if not resource_type or not resource_id:
            error_result = {
                "status": "error", 
                "message": "Both resource_type and resource_id are required"
            }
            return format_response(error_result)
        
        result = run_async_tool(delete_resource_async, resource_type, resource_id)
        return format_response(result)
    
    print(f"🔧 Registered 6 {{cookiecutter.project_name}} tools")
