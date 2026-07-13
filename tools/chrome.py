import base64
import json
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import websocket

from . import security


@dataclass
class ChromeSession:
    session_id: str
    target_id: str
    page_ws_url: str
    debug_port: int


_SESSIONS: dict[str, ChromeSession] = {}


def _http_json(url: str, method: str = "GET", timeout: float = 3.0) -> dict | list:
    request = Request(url, method=method)
    with urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
        payload = payload.strip()
        return json.loads(payload) if payload else {}


def _chrome_debug_base(debug_port: int) -> str:
    return f"http://127.0.0.1:{debug_port}"


def _is_debugger_ready(debug_port: int) -> bool:
    try:
        _http_json(f"{_chrome_debug_base(debug_port)}/json/version")
        return True
    except Exception:
        return False


def _launch_chrome_with_debugger(debug_port: int, headless: bool) -> None:
    profile_dir = Path(tempfile.gettempdir()) / f"altic-mcp-chrome-{debug_port}"
    profile_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "open",
        "-a",
        "Google Chrome",
        "--args",
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--remote-allow-origins=*",
    ]
    if headless:
        command.extend(["--headless=new", "--disable-gpu"])

    subprocess.run(command, capture_output=True, text=True, timeout=20)


def _ensure_debugger(debug_port: int, headless: bool = False) -> None:
    if _is_debugger_ready(debug_port):
        return

    _launch_chrome_with_debugger(debug_port, headless)
    deadline = time.time() + 12
    while time.time() < deadline:
        if _is_debugger_ready(debug_port):
            return
        time.sleep(0.25)
    raise RuntimeError(
        "Chrome debugger is not available. Start Chrome with --remote-debugging-port."
    )


def _new_target(debug_port: int, url: str) -> dict:
    base = _chrome_debug_base(debug_port)
    encoded_url = quote(url, safe="")
    try:
        return _http_json(f"{base}/json/new?{encoded_url}", method="PUT", timeout=5)
    except Exception:
        return _http_json(f"{base}/json/new?{encoded_url}", method="GET", timeout=5)


def _close_target(debug_port: int, target_id: str) -> None:
    request = Request(
        f"{_chrome_debug_base(debug_port)}/json/close/{target_id}", method="GET"
    )
    with urlopen(request, timeout=3):
        return


def _cdp_call(
    page_ws_url: str,
    method: str,
    params: dict | None = None,
    timeout_seconds: int = 15,
) -> dict:
    request_id = int(time.time() * 1000)
    ws = websocket.create_connection(page_ws_url, timeout=timeout_seconds)
    try:
        ws.send(
            json.dumps(
                {
                    "id": request_id,
                    "method": method,
                    "params": params or {},
                }
            )
        )
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            message = ws.recv()
            payload = json.loads(message)
            if payload.get("id") != request_id:
                continue
            if payload.get("error"):
                error = payload["error"]
                raise RuntimeError(f"CDP {method} failed: {error}")
            return payload.get("result", {})
        raise RuntimeError(f"CDP {method} timed out")
    finally:
        ws.close()


def _require_session(session_id: str) -> ChromeSession:
    session = _SESSIONS.get(session_id)
    if not session:
        raise ValueError(f"Unknown session_id: {session_id}")
    return session


def _runtime_evaluate(session: ChromeSession, expression: str) -> object:
    result = _cdp_call(
        session.page_ws_url,
        "Runtime.evaluate",
        {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        },
    )
    details = result.get("exceptionDetails")
    if details:
        message = details.get("text", "Runtime exception")
        raise RuntimeError(message)
    return result.get("result", {}).get("value")


def chrome_open_session(
    start_url: str = "about:blank",
    debug_port: int = 9222,
    headless: bool = False,
) -> str:
    try:
        _ensure_debugger(debug_port=debug_port, headless=headless)
        target = _new_target(debug_port=debug_port, url=start_url)
        session_id = f"cdp-{uuid.uuid4().hex[:12]}"
        session = ChromeSession(
            session_id=session_id,
            target_id=target["id"],
            page_ws_url=target["webSocketDebuggerUrl"],
            debug_port=debug_port,
        )
        _SESSIONS[session_id] = session
        _cdp_call(session.page_ws_url, "Page.enable")
        _cdp_call(session.page_ws_url, "Runtime.enable")
        return (
            f"Opened CDP session: {session_id} (target={session.target_id}, "
            f"url={start_url}, port={debug_port})"
        )
    except (URLError, KeyError, RuntimeError, OSError) as exc:
        return f"Error: Failed to open chrome session: {exc}"


def chrome_list_sessions() -> str:
    if not _SESSIONS:
        return "No active Chrome sessions."
    summary = [
        f"{session.session_id} target={session.target_id or '-'}"
        for session in _SESSIONS.values()
    ]
    return "\n".join(summary)


def chrome_navigate(session_id: str, url: str) -> str:
    if not url.strip():
        return "Error: url cannot be empty"
    try:
        session = _require_session(session_id)
        _cdp_call(session.page_ws_url, "Page.navigate", {"url": url})
        return f"Navigated {session_id} to {url}"
    except Exception as exc:
        return f"Error: Failed to navigate: {exc}"


def chrome_wait_for(
    session_id: str,
    selector: str,
    timeout_ms: int = 10000,
    poll_ms: int = 200,
) -> str:
    if not selector.strip():
        return "Error: selector cannot be empty"
    try:
        session = _require_session(session_id)
        selector_json = json.dumps(selector)
        expression = (
            "(() => {"
            f"const el = document.querySelector({selector_json});"
            "if (!el) return false;"
            "const style = window.getComputedStyle(el);"
            "const visible = style && style.visibility !== 'hidden' && style.display !== 'none';"
            "return !!visible;"
            "})()"
        )
        deadline = time.time() + (timeout_ms / 1000)
        while time.time() < deadline:
            exists = _runtime_evaluate(session, expression)
            if exists:
                return f"Selector found and visible: {selector}"
            time.sleep(max(poll_ms, 50) / 1000)
        return f"Error: Timed out waiting for selector: {selector}"
    except Exception as exc:
        return f"Error: Failed while waiting for selector: {exc}"


def chrome_click(session_id: str, selector: str) -> str:
    if not selector.strip():
        return "Error: selector cannot be empty"
    try:
        session = _require_session(session_id)
        selector_json = json.dumps(selector)
        expression = (
            "(() => {"
            f"const el = document.querySelector({selector_json});"
            "if (!el) return 'not_found';"
            "el.scrollIntoView({block: 'center', inline: 'center'});"
            "el.click();"
            "return 'clicked';"
            "})()"
        )
        result = _runtime_evaluate(session, expression)
        if result != "clicked":
            return f"Error: Unable to click selector: {selector}"
        return f"Clicked selector: {selector}"
    except Exception as exc:
        return f"Error: Failed to click: {exc}"


def chrome_type(
    session_id: str, selector: str, text: str, clear_first: bool = True
) -> str:
    if not selector.strip():
        return "Error: selector cannot be empty"
    try:
        session = _require_session(session_id)
        selector_json = json.dumps(selector)
        text_json = json.dumps(text)
        clear_json = "true" if clear_first else "false"
        expression = (
            "(() => {"
            f"const el = document.querySelector({selector_json});"
            "if (!el) return 'not_found';"
            "el.focus();"
            f"if ({clear_json}) el.value = '';"
            f"el.value = {clear_json} ? {text_json} : (el.value || '') + {text_json};"
            "el.dispatchEvent(new Event('input', { bubbles: true }));"
            "el.dispatchEvent(new Event('change', { bubbles: true }));"
            "return 'typed';"
            "})()"
        )
        result = _runtime_evaluate(session, expression)
        if result != "typed":
            return f"Error: Unable to type into selector: {selector}"
        return f"Typed into selector: {selector}"
    except Exception as exc:
        return f"Error: Failed to type text: {exc}"


def chrome_extract(
    session_id: str,
    selector: str = "",
    attribute: str = "",
    javascript_expression: str = "",
) -> str:
    try:
        session = _require_session(session_id)
        if javascript_expression.strip():
            value = _runtime_evaluate(session, javascript_expression)
            return json.dumps({"value": value})

        if not selector.strip():
            return "Error: provide selector or javascript_expression"

        selector_json = json.dumps(selector)
        attribute_json = json.dumps(attribute)
        expression = (
            "(() => {"
            f"const el = document.querySelector({selector_json});"
            "if (!el) return null;"
            f"const attribute = {attribute_json};"
            "if (attribute) return el.getAttribute(attribute);"
            "return (el.innerText || el.textContent || '').trim();"
            "})()"
        )
        value = _runtime_evaluate(session, expression)
        return json.dumps({"value": value})
    except Exception as exc:
        return f"Error: Failed to extract data: {exc}"


def chrome_screenshot(session_id: str, output_path: str = "") -> str:
    try:
        session = _require_session(session_id)
        result = _cdp_call(
            session.page_ws_url, "Page.captureScreenshot", {"format": "png"}
        )
        encoded = result.get("data")
        if not encoded:
            return "Error: screenshot did not return image data"

        target_path = output_path.strip()
        if not target_path:
            timestamp = int(time.time())
            shots_dir = Path(tempfile.gettempdir()) / "altic-mcp-screenshots"
            shots_dir.mkdir(parents=True, exist_ok=True)
            target_path = str(shots_dir / f"{session_id}-{timestamp}.png")

        target = security.validate_path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(encoded))

        return f"Saved screenshot: {target}"
    except Exception as exc:
        return f"Error: Failed to capture screenshot: {exc}"


def chrome_close_session(session_id: str) -> str:
    session = _SESSIONS.get(session_id)
    if not session:
        return f"Error: Unknown session_id: {session_id}"

    try:
        _close_target(session.debug_port, session.target_id)
    except Exception:
        pass
    _SESSIONS.pop(session_id, None)
    return f"Closed session: {session_id}"
