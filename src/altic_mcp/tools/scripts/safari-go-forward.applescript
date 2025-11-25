on run argv
	try
		tell application "Safari"
			if (count of windows) = 0 then
				return "Error: No Safari windows are open"
			end if
			
			tell window 1
				if (count of tabs) = 0 then
					return "Error: No tabs are open in Safari"
				end if
				
				tell current tab
					-- Go forward in history using JavaScript
					do JavaScript "window.history.forward();"
				end tell
				
				return "Successfully navigated forward in Safari"
			end tell
		end tell
	on error errMsg
		return "Error navigating forward in Safari: " & errMsg
	end try
end run

