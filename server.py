from decimal import DefaultContext

from fastmcp import FastMCP
from pydantic import Field

from tools import (
    app,
    calendar,
    chrome,
    contacts,
    display,
    messages,
    notes,
    reminders,
    safari,
    screenshot,
    system,
)

mcp = FastMCP("Altic-MCP")


@mcp.tool()
def open_app(name: str) -> str:
    """
    Open any mac application by specifying its name. Use this tool
    if you encounter any error or issue mentioning that the app is not
    open

    Args:
        name: Name of the mac app. e.g. "Mail", "Contacts", "Messages" etc.

    Returns:
        A success or failure message
    """
    return app.open_app(name)


@mcp.tool()
def send_imessage(phone_number: str, message: str) -> str:
    """
    Send an imessage to someone in your contacts

    Args:
        phone_number: The phone number of the recipient
        message: The message text to send

    Returns:
        Success or error message
    """
    return messages.send_message(phone_number=phone_number, message=message)


@mcp.tool()
async def search_contacts(name: str) -> str:
    """
    Search for a phone number from contacts by name. Returns multiple
    options if more than one contact is found or more than one number is found.
    Ask clarifying questions on which number if any following actions are required

    Args:
        name: The name of contact to search for
        ctx: FastMCP context for logging

    Returns:
        A list of matching contacts
    """
    return contacts.search_contacts(name)


@mcp.tool()
async def read_recent_messages(
    phone_number: str, recent_message_count: int = Field(default=25, ge=1, le=200)
) -> str:
    """
    Read the recent X messages from the iMessage app between the user and the
    person with the phone number. X is defined based on the value of recent_message_count

    Args:
        phone_number: The phone number of the person you want to retrieve the chat from
        recent_message_count: The recent messages to retrieve, can be a maximum of 200

    Returns:
        A list of recent messages in the chat
    """
    return messages.read_recent_messages(phone_number, recent_message_count)


@mcp.tool()
async def set_reminder(name: str, datetime: str, list_name: str = "Reminders") -> str:
    """
    Set a reminder

    Args:
        name: The reminder text
        datetime: The time to set the reminder for, must in the following format "YYYY-MM-DD HH:MM"
        list_name: Reminder list, e.g. Work, Personal etc. Defaults to "Reminders"

    Returns:
        A success or error message
    """
    return reminders.set_reminder(name, datetime, list_name)


@mcp.tool()
async def create_note(name: str, body: str, folder: str = Field(default="")) -> str:
    """
    Create a note

    Args:
        name: Title of the note
        body: Content of the note
        folder: Use this if the note has to be created in a specific folder. Uses
        default folder if none is specified

    Returns:
        A success or error message
    """
    return notes.create_note(name, body, folder)


@mcp.tool()
async def search_notes(
    query: str, max_results: int = Field(default=10, ge=1, le=20)
) -> str:
    """
    Search Apple notes based on a query

    Args:
        query: The query string
        max_results: The maximum number of results returned from the tool, defaults to 10

    Returns:
        A list of notes based on search
    """
    return notes.search_notes(query, max_results)


@mcp.tool()
async def decrease_brightness(
    amount: float = Field(default=0.0625, ge=0.0, le=1.0),
) -> str:
    """
    Decrease screen brightness

    Args:
        amount: Amount to decrease brightness by (0.0 to 1.0 scale). Default is 0.0625 (6.25%)

    Returns:
        Success or error message
    """
    return system.decrease_brightness(amount)


@mcp.tool()
async def increase_brightness(
    amount: float = Field(default=0.0625, ge=0.0, le=1.0),
) -> str:
    """
    Increase screen brightness

    Args:
        amount: Amount to increase brightness by (0.0 to 1.0 scale). Default is 0.0625 (6.25%)

    Returns:
        Success or error message
    """
    return system.increase_brightness(amount)


@mcp.tool()
async def turn_up_volume(amount: float = Field(default=6.25, ge=0.0, le=100.0)) -> str:
    """
    Turn up system volume

    Args:
        amount: Amount to increase volume by (0-100 scale). Default is 6.25 (6.25%)

    Returns:
        Success or error message
    """
    return system.turn_up_volume(amount)


@mcp.tool()
async def turn_down_volume(
    amount: float = Field(default=6.25, ge=0.0, le=100.0),
) -> str:
    """
    Turn down system volume

    Args:
        amount: Amount to decrease volume by (0-100 scale). Default is 6.25 (6.25%)

    Returns:
        Success or error message
    """
    return system.turn_down_volume(amount)


@mcp.tool()
async def create_calendar_event(
    title: str,
    start_datetime: str,
    duration_minutes: int,
    calendar_name: str = Field(default=""),
) -> str:
    """
    Create a calendar event in the macOS Calendar app

    Args:
        title: The event title
        start_datetime: Start date and time in format 'YYYY-MM-DD HH:MM' (e.g., '2025-10-30 14:30')
        duration_minutes: Duration of the event in minutes
        calendar_name: Optional calendar name (uses default calendar if not specified)

    Returns:
        Success or error message
    """
    return calendar.create_calendar_event(
        title, start_datetime, duration_minutes, calendar_name
    )


@mcp.tool()
async def list_calendar_events_for_day(date: str) -> str:
    """
    List all calendar events for a specific day

    Args:
        date: Date in format 'YYYY-MM-DD' (e.g., '2025-10-30')

    Returns:
        List of events for the specified day or error message
    """
    return calendar.list_calendar_events_for_day(date)


@mcp.tool()
async def open_safari_tab(url: str = Field(default="")) -> str:
    """
    Open a new tab in Safari with optional URL

    Args:
        url: Optional URL to open in the new tab

    Returns:
        Success or error message
    """
    return safari.open_safari_tab(url)


@mcp.tool()
async def close_safari_tab(tab_index: int = Field(default=-1)) -> str:
    """
    Close a Safari tab. Use -1 for current tab or specify tab index (1-based)

    Args:
        tab_index: Tab index to close (-1 for current tab, or 1-based index)

    Returns:
        Success or error message
    """
    return safari.close_safari_tab(tab_index)


@mcp.tool()
async def get_safari_tabs() -> str:
    """
    Get a list of all open Safari tabs with their URLs and titles

    Returns:
        List of tabs with URLs and titles or error message
    """
    return safari.get_safari_tabs()


@mcp.tool()
async def switch_safari_tab(tab_index: int) -> str:
    """
    Switch to a specific Safari tab by index (1-based)

    Args:
        tab_index: Tab index to switch to (must be greater than 0)

    Returns:
        Success or error message
    """
    return safari.switch_safari_tab(tab_index)


@mcp.tool()
async def run_safari_javascript(javascript_code: str) -> str:
    """
    Execute JavaScript code in the current Safari tab and return the result

    Args:
        javascript_code: JavaScript code to execute

    Returns:
        JavaScript execution result or error message
    """
    return safari.run_safari_javascript(javascript_code)


@mcp.tool()
async def navigate_safari(url: str) -> str:
    """
    Navigate to a URL in the current Safari tab

    Args:
        url: URL to navigate to

    Returns:
        Success or error message
    """
    return safari.navigate_safari(url)


@mcp.tool()
async def reload_safari_page() -> str:
    """
    Reload the current Safari page

    Returns:
        Success or error message
    """
    return safari.reload_safari_page()


@mcp.tool()
async def safari_go_back() -> str:
    """
    Navigate back in Safari history

    Returns:
        Success or error message
    """
    return safari.safari_go_back()


@mcp.tool()
async def safari_go_forward() -> str:
    """
    Navigate forward in Safari history

    Returns:
        Success or error message
    """
    return safari.safari_go_forward()


@mcp.tool()
async def open_safari_window(url: str = Field(default="")) -> str:
    """
    Open a new Safari window with optional URL

    Args:
        url: Optional URL to open in the new window

    Returns:
        Success or error message
    """
    return safari.open_safari_window(url)


@mcp.tool()
async def close_safari_window() -> str:
    """
    Close the current Safari window

    Returns:
        Success or error message
    """
    return safari.close_safari_window()


@mcp.tool()
async def get_safari_page_info() -> str:
    """
    Get information about the current Safari page including URL, title, text content, and HTML source

    Returns:
        Page information including URL, title, text, and source or error message
    """
    return safari.get_safari_page_info()


@mcp.tool()
async def chrome_open_session(
    start_url: str = Field(default="about:blank"),
    debug_port: int = Field(default=9222, ge=1024, le=65535),
    headless: bool = Field(default=False),
) -> str:
    """
    Open a Chrome automation session for browser control.

    Args:
        start_url: Initial page URL to open
        debug_port: Chrome remote debugging port for CDP sessions
        headless: Launch Chrome headless if debugger needs to be started

    Returns:
        Session identifier and connection details or error message
    """
    return chrome.chrome_open_session(start_url, debug_port, headless)


@mcp.tool()
async def chrome_list_sessions() -> str:
    """
    List active Chrome automation sessions.

    Returns:
        A list of active session IDs
    """
    return chrome.chrome_list_sessions()


@mcp.tool()
async def chrome_navigate(session_id: str, url: str) -> str:
    """
    Navigate an active Chrome CDP session to a URL.

    Args:
        session_id: Session returned by chrome_open_session
        url: URL to load

    Returns:
        Success or error message
    """
    return chrome.chrome_navigate(session_id, url)


@mcp.tool()
async def chrome_wait_for(
    session_id: str,
    selector: str,
    timeout_ms: int = Field(default=10000, ge=100, le=120000),
    poll_ms: int = Field(default=200, ge=50, le=5000),
) -> str:
    """
    Wait for a CSS selector to exist and be visible in the page.

    Args:
        session_id: Session returned by chrome_open_session
        selector: CSS selector to wait for
        timeout_ms: Max wait time in milliseconds
        poll_ms: Poll interval in milliseconds

    Returns:
        Success or timeout/error message
    """
    return chrome.chrome_wait_for(session_id, selector, timeout_ms, poll_ms)


@mcp.tool()
async def chrome_click(session_id: str, selector: str) -> str:
    """
    Click an element in an active Chrome CDP session using a CSS selector.

    Args:
        session_id: Session returned by chrome_open_session
        selector: CSS selector for target element

    Returns:
        Success or error message
    """
    return chrome.chrome_click(session_id, selector)


@mcp.tool()
async def chrome_type(
    session_id: str,
    selector: str,
    text: str,
    clear_first: bool = Field(default=True),
) -> str:
    """
    Type text into an input element in an active Chrome CDP session.

    Args:
        session_id: Session returned by chrome_open_session
        selector: CSS selector for input element
        text: Text to type
        clear_first: Clear existing value before typing

    Returns:
        Success or error message
    """
    return chrome.chrome_type(session_id, selector, text, clear_first)


@mcp.tool()
async def chrome_extract(
    session_id: str,
    selector: str = Field(default=""),
    attribute: str = Field(default=""),
    javascript_expression: str = Field(default=""),
) -> str:
    """
    Extract data from a page by selector or by JavaScript expression.

    Args:
        session_id: Session returned by chrome_open_session
        selector: CSS selector to query
        attribute: Attribute name to read from selected element
        javascript_expression: JavaScript expression to evaluate directly

    Returns:
        Extracted value as JSON or error message
    """
    return chrome.chrome_extract(session_id, selector, attribute, javascript_expression)


@mcp.tool()
async def chrome_screenshot(
    session_id: str,
    output_path: str = Field(default=""),
) -> str:
    """
    Capture a screenshot of the active page in a Chrome CDP session.

    Args:
        session_id: Session returned by chrome_open_session
        output_path: Optional file path for output PNG

    Returns:
        Saved path or error message
    """
    return chrome.chrome_screenshot(session_id, output_path)


@mcp.tool()
async def chrome_close_session(session_id: str) -> str:
    """
    Close a Chrome automation session.

    Args:
        session_id: Session returned by chrome_open_session

    Returns:
        Success or error message
    """
    return chrome.chrome_close_session(session_id)


@mcp.tool()
async def capture_active_screen(
    output_path: str = Field(default=""),
) -> str | list[object]:
    """
    Capture a full screenshot of the display containing the frontmost app and share
    the image directly with the model.

    Args:
        output_path: Optional file path for output PNG

    Returns:
        A text status plus image content, or an error message
    """
    return screenshot.capture_active_screen(output_path)


@mcp.tool()
async def add_screen_glow() -> str:
    """
    Add a visual feedback indicator (orange glow around screen edges) to show that automated actions are in progress.

    IMPORTANT: Call this FIRST before performing any automated actions to provide visual feedback
    to the user that the tool is actively working. This serves as a clear indicator that
    operations are being executed.

    Returns:
        Success or error message
    """
    return display.add_screen_glow()


@mcp.tool()
async def remove_screen_glow() -> str:
    """
    Remove the visual feedback indicator (screen glow) when automated actions are complete.

    IMPORTANT: Call this when all automated actions are complete to stop the visual feedback
    indicator and signal to the user that operations have finished.

    Returns:
        Success or error message
    """
    return display.remove_screen_glow()


if __name__ == "__main__":
    mcp.run()
