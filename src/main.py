#!/usr/bin/env python3

"""Splunk MCP Server - Main entry point."""

import asyncio
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import all tool functions
from tools.search import search_splunk_impl
from tools.indexes import get_splunk_indexes_impl
from tools.apps import get_splunk_apps_impl
from tools.alerts import create_splunk_alert_impl
from tools.events import send_to_splunk_impl
from tools.analysis import analyze_splunk_logs_impl

# Initialize MCP server
server = Server("splunk-mcp-server")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available Splunk tools."""
    return [
        Tool(
            name="search_splunk",
            description="Execute a Splunk search query and return results",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The Splunk search query (SPL)"},
                    "earliest_time": {"type": "string", "description": "Earliest time for search", "default": "-1h"},
                    "latest_time": {"type": "string", "description": "Latest time for search", "default": "now"},
                    "max_results": {"type": "integer", "description": "Maximum number of results", "default": 100},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_splunk_indexes",
            description="Get list of available Splunk indexes",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_splunk_apps",
            description="Get list of installed Splunk apps",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="create_splunk_alert",
            description="Create a Splunk alert",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Alert name"},
                    "search": {"type": "string", "description": "Search query"},
                    "cron_schedule": {"type": "string", "description": "Cron schedule"},
                    "actions": {"type": "array", "items": {"type": "string"}, "default": []},
                },
                "required": ["name", "search", "cron_schedule"],
            },
        ),
        Tool(
            name="send_to_splunk",
            description="Send event to Splunk via HEC",
            inputSchema={
                "type": "object",
                "properties": {
                    "event": {"type": "object", "description": "Event data"},
                    "source": {"type": "string", "description": "Event source"},
                    "sourcetype": {"type": "string", "description": "Event sourcetype"},
                    "index": {"type": "string", "description": "Target index"},
                },
                "required": ["event"],
            },
        ),
        Tool(
            name="analyze_splunk_logs",
            description="Perform automated log analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["error_analysis", "performance_analysis", "security_analysis", "usage_analysis"],
                        "description": "Type of analysis to perform",
                    },
                    "index": {"type": "string", "description": "Index to analyze", "default": "main"},
                    "time_range": {"type": "string", "description": "Time range", "default": "-24h"},
                },
                "required": ["analysis_type"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls by routing to appropriate implementation."""
    try:
        if name == "search_splunk":
            result = await search_splunk_impl(
                query=arguments["query"],
                earliest_time=arguments.get("earliest_time", "-1h"),
                latest_time=arguments.get("latest_time", "now"),
                max_results=arguments.get("max_results", 100),
            )
        elif name == "get_splunk_indexes":
            result = await get_splunk_indexes_impl()
        elif name == "get_splunk_apps":
            result = await get_splunk_apps_impl()
        elif name == "create_splunk_alert":
            result = await create_splunk_alert_impl(
                name=arguments["name"],
                search=arguments["search"],
                cron_schedule=arguments["cron_schedule"],
                actions=arguments.get("actions", []),
            )
        elif name == "send_to_splunk":
            result = await send_to_splunk_impl(
                event=arguments["event"],
                source=arguments.get("source"),
                sourcetype=arguments.get("sourcetype"),
                index=arguments.get("index"),
            )
        elif name == "analyze_splunk_logs":
            result = await analyze_splunk_logs_impl(
                analysis_type=arguments["analysis_type"],
                index=arguments.get("index", "main"),
                time_range=arguments.get("time_range", "-24h"),
            )
        else:
            result = f"Unknown tool: {name}"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())