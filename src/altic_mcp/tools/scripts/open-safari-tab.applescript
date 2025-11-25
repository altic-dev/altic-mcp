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
			
			-- Check if Safari has any windows
			if (count of windows) = 0 then
				make new document
				if targetURL is not "" then
					set URL of document 1 to targetURL
				end if
				return "Successfully opened new Safari tab" & (if targetURL is not "" then " with URL: " & targetURL else "")
			else
				-- Open new tab in frontmost window
				tell window 1
					set currentTab to make new tab
					if targetURL is not "" then
						set URL of currentTab to targetURL
					end if
				end tell
				return "Successfully opened new Safari tab" & (if targetURL is not "" then " with URL: " & targetURL else "")
			end if
		end tell
	on error errMsg
		return "Error opening Safari tab: " & errMsg
	end try
end run

