import subprocess
from .constants import SCRIPTS_PREFIX


def add_screen_glow() -> str:
    """
    Add a glowing border around the screen edges as visual feedback.
    Uses a Swift script to create 4 transparent windows at screen edges.
    
    Returns:
        Success or error message
    """
    script_path = SCRIPTS_PREFIX / "screen-glow.swift"
    
    try:
        # Start the glow process in the background
        result = subprocess.Popen(
            ["swift", str(script_path), "add"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        # Give it a moment to start up
        import time
        time.sleep(0.5)
        
        # Check if it's still running (it should be)
        if result.poll() is None:
            return "Screen glow activated - visual feedback enabled"
        else:
            stderr = result.stderr.read() if result.stderr else ""
            return f"Error: Screen glow process failed to start: {stderr}"
    except Exception as e:
        return f"Error: Failed to add screen glow: {str(e)}"


def remove_screen_glow() -> str:
    """
    Remove the screen glow effect by terminating the glow process.
    
    Returns:
        Success or error message
    """
    script_path = SCRIPTS_PREFIX / "screen-glow.swift"
    
    try:
        result = subprocess.run(
            ["swift", str(script_path), "remove"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if result.returncode != 0:
            return f"Error: Unable to remove screen glow: {result.stderr}"
        
        return result.stdout.strip() or "Screen glow removed - visual feedback disabled"
    except Exception as e:
        return f"Error: Failed to remove screen glow: {str(e)}"
