#!/usr/bin/env python3
"""
{{cookiecutter.project_name}} - MCP Server
{{cookiecutter.project_description}}

Generated from mcp-server-template
Author: {{cookiecutter.author_name}} <{{cookiecutter.author_email}}>
Version: {{cookiecutter.project_version}}
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import json
from datetime import datetime
from typing import Any, Dict

from core.auth import auth
from core.client import client

# Import our modules
from core.config import config

# FastMCP import
from mcp.server.fastmcp import FastMCP

# Data directory for storing API responses
DATA_DIR = "{{cookiecutter.project_slug}}_data"

# Get port from environment (Render sets this automatically)
PORT = int(os.environ.get("PORT", 8000))

# Initialize FastMCP server
mcp = FastMCP(name=config.mcp.server_name, host="0.0.0.0", port=PORT)


def save_api_data(data_type: str, data: Dict[str, Any]) -> None:
    """Save API data to file for debugging and monitoring"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)

        # Add metadata
        data["saved_at"] = datetime.now().isoformat()
        data["server_name"] = config.mcp.server_name
        data["server_version"] = config.mcp.server_version

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if config.mcp.debug:
            print(f"💾 Data saved to: {filepath}")

    except Exception as e:
        print(f"❌ Error saving data: {str(e)}")


def run_async_tool(async_func, *args, **kwargs):
    """
    Synchronous wrapper for async tools - Required for FastMCP compatibility

    FastMCP tools must be synchronous, but our API calls are async.
    This wrapper handles the async/sync conversion properly.
    """
    try:
        import asyncio
        import concurrent.futures

        try:
            # Try to get the existing event loop
            loop = asyncio.get_running_loop()

            # If we have a running loop, we need to run in a thread
            # to avoid "Event loop is closed" errors
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Use a custom runner function to ensure event loop is properly closed
                def run_and_close_loop():
                    # Create a new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        # Run the async function
                        return loop.run_until_complete(async_func(*args, **kwargs))
                    finally:
                        # Ensure the loop is closed properly
                        loop.close()
                
                future = executor.submit(run_and_close_loop)
                result = future.result(timeout=60)  # 60 second timeout
                return result

        except RuntimeError:
            # No running loop, safe to create new one
            # asyncio.run handles loop creation and cleanup automatically
            result = asyncio.run(async_func(*args, **kwargs))
            return result

    except concurrent.futures.TimeoutError:
        return {
            "status": "error",
            "message": "Tool execution timed out after 60 seconds",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Tool execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


# API Implementation Functions
async def get_api_status_async() -> Dict[str, Any]:
    """Get API status and connectivity information"""
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
                "details": auth_info,
            },
            "connectivity": {
                "api_accessible": is_api_healthy,
                "base_url": client_info["base_url"],
                "timeout": client_info["timeout"],
            },
            "configuration": {
                "environment": config.mcp.environment,
                "debug_mode": config.mcp.debug,
                "server_version": config.mcp.server_version,
            },
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to check API status: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


async def list_resources_async(
    resource_type: str = "items", limit: int = 10, offset: int = 0
) -> Dict[str, Any]:
    """List resources from the API"""
    try:
        print(f"📋 Listing {resource_type} (limit: {limit}, offset: {offset})...")

        # Prepare query parameters
        params = {"limit": limit, "offset": offset}

        # Make API request - adjust endpoint based on your API
        endpoint = f"/{resource_type}"
        response = await client.get(endpoint, params=params)

        # Extract data (adjust based on your API response structure)
        items = response.get(
            "data", response.get("items", response.get(resource_type, []))
        )
        total = response.get("total", len(items))

        return {
            "status": "success",
            "resource_type": resource_type,
            "items": items,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total,
                "has_more": offset + limit < total,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list {resource_type}: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


async def get_resource_by_id_async(
    resource_type: str, resource_id: str
) -> Dict[str, Any]:
    """Get a specific resource by ID"""
    try:
        print(f"🔍 Getting {resource_type}/{resource_id}...")

        # Make API request
        endpoint = f"/{resource_type}/{resource_id}"
        response = await client.get(endpoint)

        # Extract data (adjust based on your API response structure)
        item = response.get("data", response.get("item", response))

        return {
            "status": "success",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "item": item,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get {resource_type}/{resource_id}: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


async def create_resource_async(
    resource_type: str, data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new resource"""
    try:
        print(f"➕ Creating new {resource_type}...")

        # Make API request
        endpoint = f"/{resource_type}"
        response = await client.post(endpoint, json_data=data)

        # Extract data (adjust based on your API response structure)
        created_item = response.get("data", response.get("item", response))
        resource_id = created_item.get("id", created_item.get("_id", "unknown"))

        return {
            "status": "success",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "item": created_item,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create {resource_type}: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


async def update_resource_async(
    resource_type: str, resource_id: str, data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update an existing resource"""
    try:
        print(f"✏️ Updating {resource_type}/{resource_id}...")

        # Make API request
        endpoint = f"/{resource_type}/{resource_id}"
        response = await client.put(endpoint, json_data=data)

        # Extract data (adjust based on your API response structure)
        updated_item = response.get("data", response.get("item", response))

        return {
            "status": "success",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "item": updated_item,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to update {resource_type}/{resource_id}: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


async def delete_resource_async(resource_type: str, resource_id: str) -> Dict[str, Any]:
    """Delete a resource"""
    try:
        print(f"🗑️ Deleting {resource_type}/{resource_id}...")

        # Make API request
        endpoint = f"/{resource_type}/{resource_id}"
        response = await client.delete(endpoint)

        return {
            "status": "success",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "deleted": True,
            "message": "Resource deleted successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete {resource_type}/{resource_id}: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


# MCP Tool Registration
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
    save_api_data("api_status", result)
    return json.dumps(result, indent=2)


@mcp.tool()
def list_resources(
    resource_type: str = "items", limit: int = 10, offset: int = 0
) -> str:
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
    save_api_data(f"list_{resource_type}", result)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_resource_by_id(resource_type: str, resource_id: str) -> str:
    """
    Get detailed information about a specific resource by ID.

    Args:
        resource_type: Type of resource to retrieve (e.g., "users", "products")
        resource_id: Unique identifier for the resource

    Returns:
        JSON string with complete resource details
    """
    if not resource_type or not resource_id:
        error_result = {
            "status": "error",
            "message": "Both resource_type and resource_id are required",
        }
        return json.dumps(error_result, indent=2)

    result = run_async_tool(get_resource_by_id_async, resource_type, resource_id)
    save_api_data(f"get_{resource_type}_{resource_id}", result)
    return json.dumps(result, indent=2)


@mcp.tool()
def create_resource(resource_type: str, data: str) -> str:
    """
    Create a new resource in the {{cookiecutter.api_service_type}} API.

    Args:
        resource_type: Type of resource to create (e.g., "users", "products")
        data: JSON string with resource data

    Returns:
        JSON string with created resource details
    """
    if not resource_type:
        error_result = {"status": "error", "message": "resource_type is required"}
        return json.dumps(error_result, indent=2)

    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError:
        error_result = {"status": "error", "message": "Invalid JSON data"}
        return json.dumps(error_result, indent=2)

    result = run_async_tool(create_resource_async, resource_type, data_dict)
    save_api_data(f"create_{resource_type}", result)
    return json.dumps(result, indent=2)


@mcp.tool()
def update_resource(resource_type: str, resource_id: str, data: str) -> str:
    """
    Update an existing resource in the {{cookiecutter.api_service_type}} API.

    Args:
        resource_type: Type of resource to update (e.g., "users", "products")
        resource_id: Unique identifier for the resource
        data: JSON string with updated resource data

    Returns:
        JSON string with updated resource details
    """
    if not resource_type or not resource_id:
        error_result = {
            "status": "error",
            "message": "Both resource_type and resource_id are required",
        }
        return json.dumps(error_result, indent=2)

    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError:
        error_result = {"status": "error", "message": "Invalid JSON data"}
        return json.dumps(error_result, indent=2)

    result = run_async_tool(
        update_resource_async, resource_type, resource_id, data_dict
    )
    save_api_data(f"update_{resource_type}_{resource_id}", result)
    return json.dumps(result, indent=2)


@mcp.tool()
def delete_resource(resource_type: str, resource_id: str) -> str:
    """
    Delete a resource from the {{cookiecutter.api_service_type}} API.

    Args:
        resource_type: Type of resource to delete (e.g., "users", "products")
        resource_id: Unique identifier for the resource

    Returns:
        JSON string with deletion confirmation
    """
    if not resource_type or not resource_id:
        error_result = {
            "status": "error",
            "message": "Both resource_type and resource_id are required",
        }
        return json.dumps(error_result, indent=2)

    result = run_async_tool(delete_resource_async, resource_type, resource_id)
    save_api_data(f"delete_{resource_type}_{resource_id}", result)
    return json.dumps(result, indent=2)


# Resources
@mcp.resource("{{cookiecutter.project_slug}}://status")
def get_server_status() -> str:
    """Get current server status and configuration"""
    try:
        status_info = {
            "server_name": config.mcp.server_name,
            "server_version": config.mcp.server_version,
            "environment": config.mcp.environment,
            "debug_mode": config.mcp.debug,
            "api_base_url": config.api.base_url,
            "auth_type": "{{cookiecutter.auth_type}}",
            "available_tools": [
                "get_api_status",
                "list_resources",
                "get_resource_by_id",
                "create_resource",
                "update_resource",
                "delete_resource",
            ],
            "last_updated": datetime.now().isoformat(),
        }

        content = f"# {{cookiecutter.project_name}} Server Status\n\n"
        content += f"**Status**: ✅ Running\n"
        content += f"**Version**: {status_info['server_version']}\n"
        content += f"**Environment**: {status_info['environment']}\n"
        content += f"**API**: {status_info['api_base_url']}\n"
        content += f"**Authentication**: {{cookiecutter.auth_type}}\n\n"

        content += f"## Available Tools ({len(status_info['available_tools'])})\n"
        for tool in status_info["available_tools"]:
            content += f"- `{tool}`\n"

        content += f"\n## Configuration\n"
        content += f"- Debug Mode: {'✅' if status_info['debug_mode'] else '❌'}\n"
        content += f"- Server Name: {status_info['server_name']}\n"

        content += f"\n## API Integration\n"
        content += f"- Base URL: {status_info['api_base_url']}\n"
        content += f"- Auth Type: {status_info['auth_type']}\n"

        content += f"\n---\n"
        content += f"Last updated: {status_info['last_updated']}\n"

        return content

    except Exception as e:
        return f"# Server Status Error\n\nError retrieving server status: {str(e)}"


@mcp.resource("{{cookiecutter.project_slug}}://docs/examples")
def get_examples() -> str:
    """Get examples of how to use this API"""
    content = f"""# {{cookiecutter.project_name}} - Usage Examples

Below are examples of how to use the available tools with this MCP Server.

## 1. Check API Status

```python
status = get_api_status()
```

This will return the current status of the {{cookiecutter.api_service_type}} API, including authentication status and connectivity.

## 2. List Resources

```python
# List users (first 10)
users = list_resources("users", 10, 0)

# List products with pagination
products = list_resources("products", 20, 40)  # Get products 41-60
```

## 3. Get Resource by ID

```python
# Get user by ID
user = get_resource_by_id("users", "123456")

# Get product by ID
product = get_resource_by_id("products", "ABC-123")
```

## 4. Create Resource

```python
# Create a new user
user_data = \"\"\"
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user"
}
\"\"\"
new_user = create_resource("users", user_data)
```

## 5. Update Resource

```python
# Update an existing user
update_data = \"\"\"
{
  "name": "John Smith",
  "email": "john.smith@example.com"
}
\"\"\"
updated_user = update_resource("users", "123456", update_data)
```

## 6. Delete Resource

```python
# Delete a user
result = delete_resource("users", "123456")
```

## API Response Format

All API responses follow this general format:

```json
{
  "status": "success",
  "resource_type": "users",
  "items": [...],
  "timestamp": "2023-06-15T12:34:56.789Z"
}
```

For more information, check the server status page at {{cookiecutter.project_slug}}://status
"""
    return content
    return content


@mcp.resource("{{cookiecutter.project_slug}}://docs/auth")
def get_auth_docs() -> str:
    """Get documentation about authentication setup"""
    content = "# {{cookiecutter.project_name}} - Authentication Guide\n\n"
    content += "This MCP server uses {{cookiecutter.auth_type}} authentication to connect to the {{cookiecutter.api_service_type}} API.\n\n"
    content += "## Authentication Configuration\n\n"
    content += (
        "To configure authentication, set the following environment variables:\n\n"
    )
    content += "```\n"
    content += "# Required Environment Variables\n"
    content += "API_BASE_URL=https://api.example.com\n"

    # Authentication-specific variables based on the type set in cookiecutter
    auth_type = "{{cookiecutter.auth_type}}"

    if auth_type == "API Key":
        content += "# API Key Authentication\n"
        content += "API_KEY=your_api_key\n"
        content += "API_KEY_HEADER=X-API-Key  # Optional, defaults to X-API-Key\n"
    elif auth_type == "Bearer Token":
        content += "# Bearer Token Authentication\n"
        content += "BEARER_TOKEN=your_bearer_token\n"
    elif auth_type == "OAuth2":
        content += "# OAuth2 Authentication\n"
        content += "CLIENT_ID=your_client_id\n"
        content += "CLIENT_SECRET=your_client_secret\n"
        content += "OAUTH_SCOPE=read,write  # Optional\n"
        content += "OAUTH_REDIRECT_URI=http://localhost:8080/callback  # Optional\n"
    elif auth_type == "Basic Auth":
        content += "# Basic Authentication\n"
        content += "USERNAME=your_username\n"
        content += "PASSWORD=your_password\n"
    else:
        content += "# Custom Authentication\n"
        content += "# Add your authentication variables here\n"

    content += "```\n\n"

    # Add setup instructions
    content += "## Setting Up Environment Variables\n\n"
    content += "1. Create a `.env` file in the root directory\n"
    content += "2. Add the required environment variables with your actual values\n"
    content += "3. Restart the server\n\n"

    content += "## Testing Authentication\n\n"
    content += "You can test if authentication is working correctly by using the `get_api_status()` tool:\n\n"
    content += "```python\n"
    content += "auth_status = get_api_status()\n"
    content += "```\n\n"
    content += "This will return a detailed report of the authentication status and API connectivity.\n\n"

    content += "## Troubleshooting\n\n"
    content += "If you encounter authentication issues:\n\n"
    content += "1. Check that all required environment variables are set correctly\n"
    content += "2. Verify that your credentials are valid\n"
    content += "3. Check that the API base URL is correct\n"
    content += "4. Ensure your credentials have the necessary permissions\n\n"
    content += "For more help, contact the API provider or check their documentation.\n"

    return content


def main():
    """Main server entry point"""

    # Configuration validation
    print("🔧 Validating configuration...")
    try:
        config.validate()
        debug_info = config.get_debug_info()
        print(f"✅ Configuration valid")

        if config.mcp.debug:
            print(f"🔍 Debug info: {debug_info}")

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        print("💡 Check your .env file and environment variables")
        sys.exit(1)

    # Data directory setup
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"📁 Data directory: {DATA_DIR}")

    # Server startup
    print(f"\n🚀 Starting {{cookiecutter.project_name}} MCP Server")
    print(f"📊 Server: {config.mcp.server_name}")
    print(f"🌍 Host: 0.0.0.0:{PORT}")
    print(f"🔗 API: {config.api.base_url}")

    # Check if render deployment is enabled
    render_deployment = "{{cookiecutter.render_deployment}}"
    if render_deployment == "yes":
        print(f"🚀 Deployment: Render.com ready")

    print(f"🎯 Transport: SSE (Server-Sent Events)")

    print(
        f"🔧 6 tools registered: get_api_status, list_resources, get_resource_by_id, create_resource, update_resource, delete_resource"
    )
    print(f"✅ {{cookiecutter.project_name}} is ready!")
    print(f"💡 Use with Claude Desktop or MCP-compatible clients")

    # Start the MCP server
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
