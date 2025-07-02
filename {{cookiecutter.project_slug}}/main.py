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

# FastMCP import
from mcp.server.fastmcp import FastMCP

# Import our modules
from core.config import config
from core.auth import auth
from core.client import client

# Data directory for storing API responses
DATA_DIR = "{{cookiecutter.project_slug}}_data"

# Get port from environment (Render sets this automatically)
PORT = int(os.environ.get("PORT", 8000))

# Initialize FastMCP server
mcp = FastMCP(
    name=config.mcp.server_name,
    host="0.0.0.0",
    port=PORT
)

def save_api_data(data_type: str, data: Dict[str, Any]) -> None:
    """Save API data to file for debugging and monitoring"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        # Add metadata
        data['saved_at'] = datetime.now().isoformat()
        data['server_name'] = config.mcp.server_name
        data['server_version'] = config.mcp.server_version
        
        with open(filepath, 'w') as f:
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
    """List resources from the API"""
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
    """Get a specific resource by ID"""
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
    """Create a new resource"""
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
    """Update an existing resource"""
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
            "action": "deleted",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete {resource_type}/{resource_id}: {str(e)}",
            "timestamp": datetime.now().isoformat()
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
    save_api_data(f"list_{resource_type}", result)
    return json.dumps(result, indent=2)

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
        return json.dumps(error_result, indent=2)
    
    result = run_async_tool(get_resource_by_id_async, resource_type, resource_id)
    save_api_data(f"get_{resource_type}_{resource_id}", result)
    return json.dumps(result, indent=2)

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
        return json.dumps(error_result, indent=2)
    
    try:
        # Parse JSON data
        parsed_data = json.loads(data)
    except json.JSONDecodeError as e:
        error_result = {
            "status": "error",
            "message": f"Invalid JSON data: {str(e)}"
        }
        return json.dumps(error_result, indent=2)
    
    result = run_async_tool(create_resource_async, resource_type, parsed_data)
    save_api_data(f"create_{resource_type}", result)
    return json.dumps(result, indent=2)

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
        return json.dumps(error_result, indent=2)
    
    try:
        # Parse JSON data
        parsed_data = json.loads(data)
    except json.JSONDecodeError as e:
        error_result = {
            "status": "error",
            "message": f"Invalid JSON data: {str(e)}"
        }
        return json.dumps(error_result, indent=2)
    
    result = run_async_tool(update_resource_async, resource_type, resource_id, parsed_data)
    save_api_data(f"update_{resource_type}_{resource_id}", result)
    return json.dumps(result, indent=2)

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
                "delete_resource"
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        content = f"# {{cookiecutter.project_name}} Server Status\n\n"
        content += f"**Status**: ✅ Running\n"
        content += f"**Version**: {status_info['server_version']}\n"
        content += f"**Environment**: {status_info['environment']}\n"
        content += f"**API**: {status_info['api_base_url']}\n"
        content += f"**Authentication**: {{cookiecutter.auth_type}}\n\n"
        
        content += f"## Available Tools ({len(status_info['available_tools'])})\n"
        for tool in status_info['available_tools']:
            content += f"- `{tool}`\n"
        
        content += f"\n## Configuration\n"
        content += f"- **Debug Mode**: {status_info['debug_mode']}\n"
        
        content += f"\n*Last Updated: {status_info['last_updated']}*\n"
        
        return content
        
    except Exception as e:
        return f"# Server Status Error\n\nError retrieving status: {str(e)}\n"

@mcp.resource("{{cookiecutter.project_slug}}://logs")
def get_recent_logs() -> str:
    """Get recent server logs and activity"""
    try:
        if not os.path.exists(DATA_DIR):
            return "# No Logs Available\n\nNo API data has been logged yet."
        
        log_files = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.json'):
                log_files.append(filename)
        
        log_files.sort(reverse=True)  # Most recent first
        
        content = f"# Recent {{cookiecutter.project_name}} Activity\n\n"
        
        if log_files:
            content += f"**Total Log Files**: {len(log_files)}\n\n"
            
            # Show recent files
            content += "## Recent Activity\n"
            for filename in log_files[:5]:  # Show last 5 files
                file_parts = filename.replace('.json', '').split('_')
                if len(file_parts) >= 3:
                    data_type = '_'.join(file_parts[:-2])
                    date_part = file_parts[-2]
                    time_part = file_parts[-1]
                    
                    content += f"- **{data_type}** - {date_part} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}\n"
            
            if len(log_files) > 5:
                content += f"\n*... and {len(log_files) - 5} more files*\n"
        else:
            content += "No activity logs found.\n"
        
        return content
        
    except Exception as e:
        return f"# Logs Error\n\nError retrieving logs: {str(e)}\n"

# Prompts
@mcp.prompt()
def api_integration_guide(resource_type: str = "users") -> str:
    """Generate a guide for integrating with the {{cookiecutter.api_service_type}} API"""
    return f"""You are an expert at {{cookiecutter.api_service_type}} API integration using {{cookiecutter.project_name}}.

Help the user interact with the API using the available MCP tools. Here's what you can do:

## Available Operations

1. **Check API Status**
   - Use `get_api_status()` to verify connectivity and authentication
   - This should be your first step for any integration

2. **List Resources** 
   - Use `list_resources(resource_type="{resource_type}")` to browse available data
   - Common resource types: users, orders, products, projects, tasks

3. **Get Specific Items**
   - Use `get_resource_by_id(resource_type, resource_id)` for detailed information
   - Useful for examining individual records

4. **Create New Resources**
   - Use `create_resource(resource_type, data)` to add new items
   - Data should be valid JSON for the resource type

5. **Update Existing Resources**
   - Use `update_resource(resource_type, resource_id, data)` to modify items
   - Use PATCH-style updates when possible

6. **Delete Resources**
   - Use `delete_resource(resource_type, resource_id)` to remove items
   - Be careful with this operation!

## Best Practices

- Always check API status first
- Start with listing resources to understand the data structure
- Use small limits when exploring (limit=5)
- Check error messages for API-specific requirements
- Respect rate limits and be patient with large operations

## Getting Started

1. Run `get_api_status()` to verify everything is working
2. Try `list_resources(resource_type="{resource_type}", limit=5)` to see sample data
3. Pick an ID from the results and try `get_resource_by_id("{resource_type}", "ID_HERE")`

What would you like to do with the {{cookiecutter.api_service_type}} API?"""

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
{% if cookiecutter.render_deployment == "yes" -%}
    print(f"🚀 Deployment: Render.com ready")
{% endif -%}
    print(f"🎯 Transport: SSE (Server-Sent Events)")
    
    print(f"🔧 6 tools registered: get_api_status, list_resources, get_resource_by_id, create_resource, update_resource, delete_resource")
    print(f"✅ {{cookiecutter.project_name}} is ready!")
    print(f"💡 Use with Claude Desktop or MCP-compatible clients")
    
    # Start the MCP server
    mcp.run(transport='sse')

if __name__ == "__main__":
    main()