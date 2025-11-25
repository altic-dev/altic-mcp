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
					set currentURL to URL
					-- Reload by executing JavaScript
					do JavaScript "window.location.reload();"
				end tell
				
				return "Successfully reloaded Safari page"
			end tell
		end tell
	on error errMsg
		return "Error reloading Safari page: " & errMsg
	end try
end run

