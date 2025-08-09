#!/usr/bin/env python3
"""
Browser Testing MCP Server - Simplified Version
An MCP server that enables AI models to control a real browser for testing web applications.
"""

import asyncio
import json
import base64
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class BrowserTestingServer:
    def __init__(self):
        self.server = Server("browser-testing-mcp")
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.console_logs: List[Dict[str, Any]] = []
        self.network_requests: List[Dict[str, Any]] = []
        self.network_responses: List[Dict[str, Any]] = []
        
        # Register handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="launch_browser",
                    description="Launch a new browser instance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "headless": {"type": "boolean", "default": False},
                            "viewport_width": {"type": "number", "default": 1280},
                            "viewport_height": {"type": "number", "default": 720},
                            "user_agent": {"type": "string"}
                        }
                    }
                ),
                types.Tool(
                    name="navigate_to",
                    description="Navigate to a URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "wait_until": {"type": "string", "default": "networkidle"}
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
                            "selector": {"type": "string"},
                            "timeout": {"type": "number", "default": 30000}
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
                            "selector": {"type": "string"},
                            "text": {"type": "string"},
                            "delay": {"type": "number", "default": 0}
                        },
                        "required": ["selector", "text"]
                    }
                ),
                types.Tool(
                    name="get_page_content",
                    description="Get page HTML content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string"}
                        }
                    }
                ),
                types.Tool(
                    name="take_screenshot",
                    description="Take a screenshot",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "full_page": {"type": "boolean", "default": False},
                            "selector": {"type": "string"}
                        }
                    }
                ),
                types.Tool(
                    name="get_console_logs",
                    description="Get console logs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "log_type": {"type": "string", "default": "all"}
                        }
                    }
                ),
                types.Tool(
                    name="get_network_requests",
                    description="Get network requests",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "method": {"type": "string"},
                            "url_pattern": {"type": "string"}
                        }
                    }
                ),
                types.Tool(
                    name="wait_for_selector",
                    description="Wait for element to appear",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string"},
                            "state": {"type": "string", "default": "visible"},
                            "timeout": {"type": "number", "default": 30000}
                        },
                        "required": ["selector"]
                    }
                ),
                types.Tool(
                    name="evaluate_javascript",
                    description="Execute JavaScript code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"}
                        },
                        "required": ["code"]
                    }
                ),
                types.Tool(
                    name="get_local_storage",
                    description="Get localStorage data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"}
                        }
                    }
                ),
                types.Tool(
                    name="get_cookies",
                    description="Get cookies",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"}
                        }
                    }
                ),
                types.Tool(
                    name="fill_form",
                    description="Fill form fields",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "fields": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "selector": {"type": "string"},
                                        "value": {"type": "string"},
                                        "field_type": {"type": "string", "default": "text"}
                                    }
                                }
                            }
                        },
                        "required": ["fields"]
                    }
                ),
                types.Tool(
                    name="check_element_state",
                    description="Check element states",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string"},
                            "checks": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["selector"]
                    }
                ),
                types.Tool(
                    name="close_browser",
                    description="Close browser",
                    inputSchema={"type": "object", "properties": {}}
                ),
                types.Tool(
                    name="get_page_metrics",
                    description="Get performance metrics",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            try:
                result = await self.handle_tool_call(name, arguments)
                return [types.TextContent(type="text", text=result)]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def handle_tool_call(self, name: str, args: dict) -> str:
        if name == "launch_browser":
            return await self.launch_browser(
                args.get("headless", False),
                args.get("viewport_width", 1280),
                args.get("viewport_height", 720),
                args.get("user_agent")
            )
        elif name == "navigate_to":
            return await self.navigate_to(args["url"], args.get("wait_until", "networkidle"))
        elif name == "click_element":
            return await self.click_element(args["selector"], args.get("timeout", 30000))
        elif name == "type_text":
            return await self.type_text(args["selector"], args["text"], args.get("delay", 0))
        elif name == "get_page_content":
            return await self.get_page_content(args.get("selector"))
        elif name == "take_screenshot":
            return await self.take_screenshot(args.get("full_page", False), args.get("selector"))
        elif name == "get_console_logs":
            return await self.get_console_logs(args.get("log_type", "all"))
        elif name == "get_network_requests":
            return await self.get_network_requests(args.get("method"), args.get("url_pattern"))
        elif name == "wait_for_selector":
            return await self.wait_for_selector(
                args["selector"], 
                args.get("state", "visible"), 
                args.get("timeout", 30000)
            )
        elif name == "evaluate_javascript":
            return await self.evaluate_javascript(args["code"])
        elif name == "get_local_storage":
            return await self.get_local_storage(args.get("key"))
        elif name == "get_cookies":
            return await self.get_cookies(args.get("name"))
        elif name == "fill_form":
            return await self.fill_form(args["fields"])
        elif name == "check_element_state":
            return await self.check_element_state(args["selector"], args.get("checks"))
        elif name == "close_browser":
            return await self.close_browser()
        elif name == "get_page_metrics":
            return await self.get_page_metrics()
        else:
            return f"Unknown tool: {name}"
    
    async def launch_browser(self, headless: bool, width: int, height: int, user_agent: Optional[str]) -> str:
        try:
            # Clean up existing browser
            if self.browser:
                await self.browser.close()
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=headless)
            
            context_options = {"viewport": {"width": width, "height": height}}
            if user_agent:
                context_options["user_agent"] = user_agent
            
            self.context = await self.browser.new_context(**context_options)
            self.page = await self.context.new_page()
            
            # Reset logs
            self.console_logs = []
            self.network_requests = []
            self.network_responses = []
            
            # Set up listeners
            self.page.on("console", lambda msg: self.console_logs.append({
                "type": msg.type,
                "text": msg.text,
                "timestamp": datetime.now().isoformat()
            }))
            
            self.page.on("request", lambda req: self.network_requests.append({
                "url": req.url,
                "method": req.method,
                "headers": dict(req.headers),
                "resource_type": req.resource_type,
                "timestamp": datetime.now().isoformat()
            }))
            
            self.page.on("response", lambda res: self.network_responses.append({
                "url": res.url,
                "status": res.status,
                "headers": dict(res.headers),
                "timestamp": datetime.now().isoformat()
            }))
            
            return "Browser launched successfully"
        except Exception as e:
            return f"Failed to launch browser: {str(e)}"
    
    async def navigate_to(self, url: str, wait_until: str) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            await self.page.goto(url, wait_until=wait_until)
            return f"Navigated to {url}"
        except Exception as e:
            return f"Navigation failed: {str(e)}"
    
    async def click_element(self, selector: str, timeout: int) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            await self.page.click(selector, timeout=timeout)
            return f"Clicked element: {selector}"
        except Exception as e:
            return f"Click failed: {str(e)}"
    
    async def type_text(self, selector: str, text: str, delay: int) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            await self.page.type(selector, text, delay=delay)
            return f"Typed text into: {selector}"
        except Exception as e:
            return f"Type failed: {str(e)}"
    
    async def get_page_content(self, selector: Optional[str]) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            if selector:
                element = await self.page.query_selector(selector)
                if not element:
                    return f"Element not found: {selector}"
                return await element.inner_html()
            else:
                return await self.page.content()
        except Exception as e:
            return f"Failed to get content: {str(e)}"
    
    async def take_screenshot(self, full_page: bool, selector: Optional[str]) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            if selector:
                element = await self.page.query_selector(selector)
                if not element:
                    return f"Element not found: {selector}"
                screenshot = await element.screenshot()
            else:
                screenshot = await self.page.screenshot(full_page=full_page)
            
            return f"data:image/png;base64,{base64.b64encode(screenshot).decode('utf-8')}"
        except Exception as e:
            return f"Screenshot failed: {str(e)}"
    
    async def get_console_logs(self, log_type: str) -> str:
        logs = self.console_logs
        if log_type != "all":
            logs = [l for l in logs if l["type"] == log_type]
        return json.dumps(logs, indent=2)
    
    async def get_network_requests(self, method: Optional[str], url_pattern: Optional[str]) -> str:
        requests = self.network_requests.copy()
        
        if method:
            requests = [r for r in requests if r["method"] == method]
        if url_pattern:
            requests = [r for r in requests if url_pattern in r["url"]]
        
        # Match with responses
        results = []
        for req in requests:
            response = next((r for r in self.network_responses if r["url"] == req["url"]), None)
            results.append({"request": req, "response": response})
        
        return json.dumps(results, indent=2)
    
    async def wait_for_selector(self, selector: str, state: str, timeout: int) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            await self.page.wait_for_selector(selector, state=state, timeout=timeout)
            return f"Element found: {selector}"
        except Exception as e:
            return f"Wait failed: {str(e)}"
    
    async def evaluate_javascript(self, code: str) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            result = await self.page.evaluate(code)
            return json.dumps(result, indent=2) if result is not None else "undefined"
        except Exception as e:
            return f"JavaScript execution failed: {str(e)}"
    
    async def get_local_storage(self, key: Optional[str]) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            if key:
                result = await self.page.evaluate(f"window.localStorage.getItem('{key}')")
                return json.dumps({key: result}, indent=2)
            else:
                result = await self.page.evaluate("Object.fromEntries(Object.entries(window.localStorage))")
                return json.dumps(result, indent=2)
        except Exception as e:
            return f"Failed to get localStorage: {str(e)}"
    
    async def get_cookies(self, name: Optional[str]) -> str:
        if not self.context:
            return "Browser not launched. Call launch_browser first."
        try:
            cookies = await self.context.cookies()
            if name:
                cookies = [c for c in cookies if c["name"] == name]
            return json.dumps(cookies, indent=2)
        except Exception as e:
            return f"Failed to get cookies: {str(e)}"
    
    async def fill_form(self, fields: List[Dict]) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            for field in fields:
                selector = field["selector"]
                value = field["value"]
                field_type = field.get("field_type", "text")
                
                if field_type == "text":
                    await self.page.fill(selector, value)
                elif field_type in ["checkbox", "radio"]:
                    if value in ["true", True]:
                        await self.page.check(selector)
                    else:
                        await self.page.uncheck(selector)
                elif field_type == "select":
                    await self.page.select_option(selector, value)
            
            return f"Filled {len(fields)} form fields"
        except Exception as e:
            return f"Form fill failed: {str(e)}"
    
    async def check_element_state(self, selector: str, checks: Optional[List[str]]) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            element = await self.page.query_selector(selector)
            if not element:
                return f"Element not found: {selector}"
            
            if not checks:
                checks = ["visible", "enabled"]
            
            results = {}
            for check in checks:
                if check == "visible":
                    results["visible"] = await element.is_visible()
                elif check == "hidden":
                    results["hidden"] = await element.is_hidden()
                elif check == "enabled":
                    results["enabled"] = await element.is_enabled()
                elif check == "disabled":
                    results["disabled"] = await element.is_disabled()
                elif check == "editable":
                    results["editable"] = await element.is_editable()
                elif check == "checked":
                    results["checked"] = await element.is_checked()
            
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"State check failed: {str(e)}"
    
    async def close_browser(self) -> str:
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        return "Browser closed"
    
    async def get_page_metrics(self) -> str:
        if not self.page:
            return "Browser not launched. Call launch_browser first."
        try:
            metrics = await self.page.evaluate("""() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                return {
                    timing: {
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                        domInteractive: perfData.domInteractive,
                        responseTime: perfData.responseEnd - perfData.requestStart
                    },
                    resources: performance.getEntriesByType('resource').slice(0, 20).map(r => ({
                        name: r.name,
                        type: r.initiatorType,
                        duration: r.duration
                    }))
                };
            }""")
            return json.dumps(metrics, indent=2)
        except Exception as e:
            return f"Failed to get metrics: {str(e)}"
    
    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream,
                initialization_options={}
            )

async def main():
    server = BrowserTestingServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())