on run argv
	if (count of argv) < 1 then
		return "Usage: osascript switch-safari-tab.applescript <tab_index>"
	end if
	
	set tabIndex to item 1 of argv as integer
	
	try
		tell application "Safari"
			if (count of windows) = 0 then
				return "Error: No Safari windows are open"
			end if
			
			tell window 1
				if (count of tabs) = 0 then
					return "Error: No tabs are open in Safari"
				end if
				
				-- Validate tab index
				if tabIndex < 1 or tabIndex > (count of tabs) then
					return "Error: Tab index " & tabIndex & " is out of range (1-" & (count of tabs) & ")"
				end if
				
				set current tab to tab tabIndex
				set tabName to name of tab tabIndex
				set tabURL to URL of tab tabIndex
				
				return "Successfully switched to tab " & tabIndex & ": " & tabName
			end tell
		end tell
	on error errMsg
		return "Error switching Safari tab: " & errMsg
	end try
end run

