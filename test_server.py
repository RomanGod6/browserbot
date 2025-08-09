#!/usr/bin/env python3
"""Test the browser MCP server is working correctly"""
import json
import sys

# Send initialize request
init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }
}

print(json.dumps(init_request))
sys.stdout.flush()

# Read response
response = input()
print(f"Server response: {response}", file=sys.stderr)