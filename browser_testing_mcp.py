#!/usr/bin/env python3
"""
Browser Testing MCP Server
"""

import asyncio
import json
import base64
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Global browser state
browser_state = {
    "browser": None,
    "context": None,
    "page": None,
    "playwright": None,
    "console_logs": []
}

# Create the MCP server
server = Server("browser-testing", version="1.0.0")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available browser testing tools."""
    return [
        types.Tool(
            name="launch_browser",
            description="Launch a new browser instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "headless": {
                        "type": "boolean",
                        "description": "Run in headless mode",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="navigate_to",
            description="Navigate to a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="click_element",
            description="Click on an element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector"
                    }
                },
                "required": ["selector"]
            }
        ),
        types.Tool(
            name="type_text",
            description="Type text into an input field",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    }
                },
                "required": ["selector", "text"]
            }
        ),
        types.Tool(
            name="get_console_logs",
            description="Get browser console logs",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="take_screenshot",
            description="Take a screenshot of the current page",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_page_content",
            description="Get the HTML content of the page",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="close_browser",
            description="Close the browser",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute browser testing tools."""
    try:
        if name == "launch_browser":
            headless = arguments.get("headless", False)
            
            # Close existing browser if any
            if browser_state["browser"]:
                await browser_state["browser"].close()
            
            try:
                # Launch new browser
                browser_state["playwright"] = await async_playwright().start()
                browser_state["browser"] = await browser_state["playwright"].chromium.launch(headless=headless)
                browser_state["context"] = await browser_state["browser"].new_context()
                browser_state["page"] = await browser_state["context"].new_page()
                
                # Set up console logging
                browser_state["console_logs"] = []
                browser_state["page"].on("console", lambda msg: browser_state["console_logs"].append({
                    "type": msg.type,
                    "text": msg.text,
                    "timestamp": datetime.now().isoformat()
                }))
                
                return [types.TextContent(type="text", text="Browser launched successfully")]
            except Exception as e:
                error_msg = str(e)
                if "Executable doesn't exist" in error_msg:
                    return [types.TextContent(type="text", text="Error: Playwright browsers not installed. Please run: playwright install chromium")]
                elif "Host system is missing dependencies" in error_msg or "missing dependencies" in error_msg:
                    return [types.TextContent(type="text", text="Error: System dependencies missing. Please run: sudo playwright install-deps")]
                else:
                    return [types.TextContent(type="text", text=f"Error launching browser: {error_msg}")]
        
        elif name == "navigate_to":
            if not browser_state["page"]:
                return [types.TextContent(type="text", text="Error: Browser not launched. Call launch_browser first.")]
            
            url = arguments["url"]
            await browser_state["page"].goto(url)
            return [types.TextContent(type="text", text=f"Navigated to {url}")]
        
        elif name == "click_element":
            if not browser_state["page"]:
                return [types.TextContent(type="text", text="Error: Browser not launched. Call launch_browser first.")]
            
            selector = arguments["selector"]
            await browser_state["page"].click(selector)
            return [types.TextContent(type="text", text=f"Clicked element: {selector}")]
        
        elif name == "type_text":
            if not browser_state["page"]:
                return [types.TextContent(type="text", text="Error: Browser not launched. Call launch_browser first.")]
            
            selector = arguments["selector"]
            text = arguments["text"]
            await browser_state["page"].type(selector, text)
            return [types.TextContent(type="text", text=f"Typed text into: {selector}")]
        
        elif name == "get_console_logs":
            logs = json.dumps(browser_state["console_logs"], indent=2)
            return [types.TextContent(type="text", text=logs)]
        
        elif name == "take_screenshot":
            if not browser_state["page"]:
                return [types.TextContent(type="text", text="Error: Browser not launched. Call launch_browser first.")]
            
            screenshot = await browser_state["page"].screenshot()
            base64_img = base64.b64encode(screenshot).decode('utf-8')
            # Return truncated version for display
            return [types.TextContent(type="text", text=f"Screenshot taken. Base64 data: {base64_img[:100]}...")]
        
        elif name == "get_page_content":
            if not browser_state["page"]:
                return [types.TextContent(type="text", text="Error: Browser not launched. Call launch_browser first.")]
            
            content = await browser_state["page"].content()
            return [types.TextContent(type="text", text=content)]
        
        elif name == "close_browser":
            if browser_state["browser"]:
                await browser_state["browser"].close()
                browser_state["browser"] = None
            if browser_state["playwright"]:
                await browser_state["playwright"].stop()
                browser_state["playwright"] = None
            return [types.TextContent(type="text", text="Browser closed")]
        
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        try:
            await server.run(read_stream, write_stream, server.create_initialization_options())
        finally:
            # Clean up browser if still open
            if browser_state["browser"]:
                await browser_state["browser"].close()
            if browser_state["playwright"]:
                await browser_state["playwright"].stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)