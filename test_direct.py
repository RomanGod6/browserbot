#!/usr/bin/env python3
"""Direct test of the MCP server"""
import subprocess
import json
import time

# Start the server
process = subprocess.Popen(
    ["python", "browser_testing_mcp.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=0
)

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

print("Sending initialize request...")
process.stdin.write(json.dumps(init_request) + "\n")
process.stdin.flush()

# Give it a moment
time.sleep(0.5)

# Check if process is still running
if process.poll() is not None:
    stdout, stderr = process.communicate()
    print(f"Process exited with code: {process.returncode}")
    print(f"STDOUT: {stdout}")
    print(f"STDERR: {stderr}")
else:
    print("Process is still running, attempting to read response...")
    # Try to read response
    try:
        response = process.stdout.readline()
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error reading response: {e}")
    
    # Terminate
    process.terminate()