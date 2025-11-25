on run argv
	-- Optional URL argument
	if (count of argv) > 0 then
		set targetURL to item 1 of argv
	else
		set targetURL to ""
	end if
	
	try
		tell application "Safari"
			activate
			
			-- Create new window
			if targetURL is not "" then
				make new document with properties {URL:targetURL}
				return "Successfully opened new Safari window with URL: " & targetURL
			else
				make new document
				return "Successfully opened new Safari window"
			end if
		end tell
	on error errMsg
		return "Error opening Safari window: " & errMsg
	end try
end run

