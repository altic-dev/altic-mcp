on run argv
	-- Default increment value
	set incrementValue to 0.0625
	
	-- If argument provided, use it as increment value
	if (count of argv) > 0 then
		set incrementValue to (item 1 of argv) as real
	end if
	
	try
		-- Use absolute path since `do shell script` uses a minimal PATH
		-- that does not include Homebrew's /opt/homebrew/bin
		set brightnessBin to "/opt/homebrew/bin/brightness"
		
		-- Get current brightness (0.0 to 1.0)
		set currentBrightness to do shell script brightnessBin & " -l | grep 'brightness' | head -n 1 | awk '{print $2}'"
		set currentBrightness to currentBrightness as real
		
		-- Calculate new brightness
		set newBrightness to currentBrightness + incrementValue
		if newBrightness > 1 then
			set newBrightness to 1
		end if
		
		-- Set new brightness
		do shell script brightnessBin & " " & newBrightness
		
		return "Brightness increased from " & (round (currentBrightness * 100)) & "% to " & (round (newBrightness * 100)) & "%"
	on error errMsg
		return "Error: Unable to increase brightness: " & errMsg
	end try
end run

