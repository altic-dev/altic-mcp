on run argv
	try
		tell application "Safari"
			if (count of windows) = 0 then
				return "Error: No Safari windows are open"
			end if
			
			-- Close the frontmost window
			close window 1
			
			return "Successfully closed Safari window"
		end tell
	on error errMsg
		return "Error closing Safari window: " & errMsg
	end try
end run

