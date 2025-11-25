import subprocess
from .constants import SCRIPTS_PREFIX


def open_safari_tab(url: str = "") -> str:
    script_path = SCRIPTS_PREFIX / "open-safari-tab.applescript"

    try:
        args = ["osascript", script_path]
        if url:
            args.append(url)

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to open Safari tab: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to open Safari tab: {str(e)}"


def close_safari_tab(tab_index: int = -1) -> str:
    script_path = SCRIPTS_PREFIX / "close-safari-tab.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path, str(tab_index)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to close Safari tab: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to close Safari tab: {str(e)}"


def get_safari_tabs() -> str:
    script_path = SCRIPTS_PREFIX / "get-safari-tabs.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to get Safari tabs: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to get Safari tabs: {str(e)}"


def switch_safari_tab(tab_index: int) -> str:
    script_path = SCRIPTS_PREFIX / "switch-safari-tab.applescript"

    if tab_index < 1:
        return "Error: Tab index must be greater than 0"

    try:
        result = subprocess.run(
            ["osascript", script_path, str(tab_index)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to switch Safari tab: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to switch Safari tab: {str(e)}"


def run_safari_javascript(javascript_code: str) -> str:
    script_path = SCRIPTS_PREFIX / "run-safari-javascript.applescript"

    if not javascript_code or not javascript_code.strip():
        return "Error: JavaScript code cannot be empty"

    try:
        result = subprocess.run(
            ["osascript", script_path, javascript_code],
            capture_output=True,
            text=True,
            timeout=60,  # Longer timeout for JavaScript execution
        )

        if result.returncode != 0:
            return f"Error: Unable to execute JavaScript in Safari: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to execute JavaScript in Safari: {str(e)}"


def navigate_safari(url: str) -> str:
    script_path = SCRIPTS_PREFIX / "navigate-safari.applescript"

    if not url or not url.strip():
        return "Error: URL cannot be empty"

    try:
        result = subprocess.run(
            ["osascript", script_path, url],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to navigate Safari: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to navigate Safari: {str(e)}"


def reload_safari_page() -> str:
    script_path = SCRIPTS_PREFIX / "reload-safari-page.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to reload Safari page: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to reload Safari page: {str(e)}"


def safari_go_back() -> str:
    script_path = SCRIPTS_PREFIX / "safari-go-back.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to navigate back in Safari: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to navigate back in Safari: {str(e)}"


def safari_go_forward() -> str:
    script_path = SCRIPTS_PREFIX / "safari-go-forward.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to navigate forward in Safari: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to navigate forward in Safari: {str(e)}"


def open_safari_window(url: str = "") -> str:
    script_path = SCRIPTS_PREFIX / "open-safari-window.applescript"

    try:
        args = ["osascript", script_path]
        if url:
            args.append(url)

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to open Safari window: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to open Safari window: {str(e)}"


def close_safari_window() -> str:
    script_path = SCRIPTS_PREFIX / "close-safari-window.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to close Safari window: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to close Safari window: {str(e)}"


def get_safari_page_info() -> str:
    script_path = SCRIPTS_PREFIX / "get-safari-page-info.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to get Safari page info: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to get Safari page info: {str(e)}"
