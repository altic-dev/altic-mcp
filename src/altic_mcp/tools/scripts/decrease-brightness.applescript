on run argv
	-- Default decrement value
	set decrementValue to 0.0625
	
	-- If argument provided, use it as decrement value
	if (count of argv) > 0 then
		set decrementValue to (item 1 of argv) as real
	end if
	
	try
		tell application "System Events"
			-- Get current brightness (0.0 to 1.0)
			set currentBrightness to do shell script "brightness -l | grep 'brightness' | head -n 1 | awk '{print $2}'"
			set currentBrightness to currentBrightness as real
			
			-- Calculate new brightness
			set newBrightness to currentBrightness - decrementValue
			if newBrightness < 0 then
				set newBrightness to 0
			end if
			
			-- Set new brightness
			do shell script "brightness " & newBrightness
			
			return "Brightness decreased from " & (round (currentBrightness * 100)) & "% to " & (round (newBrightness * 100)) & "%"
		end tell
	on error errMsg
		-- Fallback: Use keyboard shortcut to decrease brightness
		tell application "System Events"
			key code 107 -- F1 key (decrease brightness)
		end tell
		return "Brightness decreased (using keyboard shortcut)"
	end try
end run

