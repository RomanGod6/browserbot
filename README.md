# Browser Testing MCP Server - Cursor AI Instructions

## Setup Instructions

1. **Install Python dependencies:**
```bash
pip install mcp playwright python-dotenv
playwright install chromium
```

2. **Save the Python file** as `browser_testing_mcp.py`

3. **Make it executable:**
```bash
chmod +x browser_testing_mcp.py
```

4. **Configure MCP in Cursor:**
Add to your MCP configuration file:
```json
{
  "mcpServers": {
    "browser-testing": {
      "command": "python",
      "args": ["/full/path/to/browser_testing_mcp.py"]
    }
  }
}
```

---

## Instructions for Cursor AI

You have access to a Browser Testing MCP server that allows you to control a real browser to test web applications. This is particularly useful for verifying that web apps you create are functioning correctly.

### Available Tools

You can use these tools to interact with a browser:

#### Browser Management
- `launch_browser` - Start a browser instance (set headless=false to see it)
- `close_browser` - Close the browser when done
- `navigate_to` - Go to any URL

#### Interaction
- `click_element` - Click any element by CSS selector
- `type_text` - Type into input fields
- `fill_form` - Fill multiple form fields at once
- `evaluate_javascript` - Execute custom JavaScript

#### Monitoring & Debugging
- `get_console_logs` - See JavaScript errors and console output
- `get_network_requests` - Monitor API calls and responses
- `get_page_metrics` - Check performance metrics
- `take_screenshot` - Capture visual state

#### Verification
- `wait_for_selector` - Wait for elements to appear
- `check_element_state` - Verify element states (visible, enabled, etc.)
- `get_local_storage` - Check stored data
- `get_cookies` - Verify authentication cookies
- `get_page_content` - Get HTML content

### Testing Workflow Example

When testing a web application you've created, follow this pattern:

```python
# 1. Launch browser in visible mode to see what's happening
launch_browser(headless=False, viewport_width=1280, viewport_height=720)

# 2. Navigate to the app
navigate_to(url="http://localhost:3000", wait_until="networkidle")

# 3. Test user registration/login
fill_form(fields=[
    {"selector": "#email", "value": "test@example.com", "field_type": "text"},
    {"selector": "#password", "value": "SecurePass123", "field_type": "text"},
    {"selector": "#agree", "value": "true", "field_type": "checkbox"}
])
click_element(selector="#submit-button")

# 4. Wait for success
wait_for_selector(selector=".dashboard", state="visible", timeout=5000)

# 5. Check for errors
get_console_logs(log_type="error")  # Check for JavaScript errors

# 6. Verify API calls worked
get_network_requests(method="POST", url_pattern="/api/auth")

# 7. Check authentication state
get_local_storage(key="authToken")
get_cookies(name="session")

# 8. Test navigation
click_element(selector="a[href='/profile']")
wait_for_selector(selector=".profile-page")

# 9. Verify content loaded
check_element_state(selector=".user-data", checks=["visible", "enabled"])

# 10. Take screenshot for visual verification
take_screenshot(full_page=True)

# 11. Get performance metrics
get_page_metrics()

# 12. Close when done
close_browser()
```

### Common Testing Scenarios

#### Test Form Validation
```python
# Try submitting empty form
click_element(selector="#submit")
wait_for_selector(selector=".error-message")
get_page_content(selector=".error-message")
```

#### Test API Error Handling
```python
# Check how app handles API failures
navigate_to(url="http://localhost:3000/users")
get_network_requests(url_pattern="/api/users")
# Check if error state is displayed properly
check_element_state(selector=".error-banner", checks=["visible"])
```

#### Test Authentication Flow
```python
# Test login -> dashboard -> logout
fill_form(fields=[
    {"selector": "#username", "value": "testuser"},
    {"selector": "#password", "value": "password123"}
])
click_element(selector="#login-btn")
wait_for_selector(selector=".dashboard")
get_local_storage(key="auth_token")  # Verify token stored
click_element(selector="#logout")
wait_for_selector(selector=".login-page")
get_local_storage(key="auth_token")  # Verify token cleared
```

#### Test Responsive Design
```python
# Test mobile view
launch_browser(headless=False, viewport_width=375, viewport_height=667)
navigate_to(url="http://localhost:3000")
check_element_state(selector=".mobile-menu", checks=["visible"])
check_element_state(selector=".desktop-menu", checks=["hidden"])
```

### Debugging Tips

1. **Always check console logs** after interactions to catch JavaScript errors
2. **Monitor network requests** to ensure APIs are called correctly
3. **Use screenshots** to visually verify UI state
4. **Check localStorage/cookies** to verify data persistence
5. **Use wait_for_selector** before interacting with dynamically loaded content
6. **Run with headless=False** to see what's happening during debugging

### Error Handling

If you encounter errors:
- "Browser not launched" - Call `launch_browser` first
- "Element not found" - Check selector is correct, use `wait_for_selector` first
- "Timeout" - Increase timeout value or check if element actually appears
- Network issues - Check if the app is running on the expected port

### Best Practices

1. **Always close the browser** when done testing
2. **Use descriptive selectors** (IDs or data-testid attributes)
3. **Wait for elements** before interacting with them
4. **Check both success and error cases**
5. **Verify API calls** match expected patterns
6. **Take screenshots** at key points for visual verification
7. **Check performance metrics** to ensure app loads efficiently

This tool allows you to thoroughly test any web application you create, ensuring all features work correctly before considering the task complete.
