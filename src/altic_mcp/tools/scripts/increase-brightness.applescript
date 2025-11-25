on run argv
	-- Default increment value
	set incrementValue to 0.0625
	
	-- If argument provided, use it as increment value
	if (count of argv) > 0 then
		set incrementValue to (item 1 of argv) as real
	end if
	
	try
		tell application "System Events"
			-- Get current brightness (0.0 to 1.0)
			set currentBrightness to do shell script "brightness -l | grep 'brightness' | head -n 1 | awk '{print $2}'"
			set currentBrightness to currentBrightness as real
			
			-- Calculate new brightness
			set newBrightness to currentBrightness + incrementValue
			if newBrightness > 1 then
				set newBrightness to 1
			end if
			
			-- Set new brightness
			do shell script "brightness " & newBrightness
			
			return "Brightness increased from " & (round (currentBrightness * 100)) & "% to " & (round (newBrightness * 100)) & "%"
		end tell
	on error errMsg
		-- Fallback: Use keyboard shortcut to increase brightness
		tell application "System Events"
			key code 113 -- F2 key (increase brightness)
		end tell
		return "Brightness increased (using keyboard shortcut)"
	end try
end run

