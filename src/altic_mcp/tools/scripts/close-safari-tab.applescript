on run argv
	-- Optional tab index argument (-1 or no argument means current tab)
	if (count of argv) > 0 then
		set tabIndex to item 1 of argv as integer
	else
		set tabIndex to -1
	end if
	
	try
		tell application "Safari"
			if (count of windows) = 0 then
				return "Error: No Safari windows are open"
			end if
			
			tell window 1
				if (count of tabs) = 0 then
					return "Error: No tabs are open in Safari"
				end if
				
				-- If tabIndex is -1, close current tab
				if tabIndex = -1 then
					close current tab
					return "Successfully closed current Safari tab"
				else
					-- Validate tab index
					if tabIndex < 1 or tabIndex > (count of tabs) then
						return "Error: Tab index " & tabIndex & " is out of range (1-" & (count of tabs) & ")"
					end if
					
					close tab tabIndex
					return "Successfully closed Safari tab " & tabIndex
				end if
			end tell
		end tell
	on error errMsg
		return "Error closing Safari tab: " & errMsg
	end try
end run

