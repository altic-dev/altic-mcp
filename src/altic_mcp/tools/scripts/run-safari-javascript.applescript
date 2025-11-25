on run argv
	if (count of argv) < 1 then
		return "Usage: osascript run-safari-javascript.applescript \"javascript code\""
	end if
	
	set jsCode to item 1 of argv
	
	try
		tell application "Safari"
			if (count of windows) = 0 then
				return "Error: No Safari windows are open"
			end if
			
			tell window 1
				if (count of tabs) = 0 then
					return "Error: No tabs are open in Safari"
				end if
				
				-- Execute JavaScript in current tab
				set jsResult to do JavaScript jsCode in current tab
				
				-- Return the result
				if jsResult is missing value or jsResult is "" then
					return "JavaScript executed successfully (no return value)"
				else
					return "JavaScript result: " & linefeed & jsResult
				end if
			end tell
		end tell
	on error errMsg
		return "Error executing JavaScript in Safari: " & errMsg
	end try
end run

