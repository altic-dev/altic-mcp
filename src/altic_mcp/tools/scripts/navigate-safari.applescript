on run argv
	if (count of argv) < 1 then
		return "Usage: osascript navigate-safari.applescript \"url\""
	end if
	
	set targetURL to item 1 of argv
	
	try
		tell application "Safari"
			activate
			
			if (count of windows) = 0 then
				-- No windows open, create new one
				make new document with properties {URL:targetURL}
				return "Successfully navigated to: " & targetURL
			else
				-- Navigate in current tab of frontmost window
				tell window 1
					if (count of tabs) = 0 then
						set newTab to make new tab
						set URL of newTab to targetURL
					else
						set URL of current tab to targetURL
					end if
				end tell
				return "Successfully navigated to: " & targetURL
			end if
		end tell
	on error errMsg
		return "Error navigating Safari: " & errMsg
	end try
end run

