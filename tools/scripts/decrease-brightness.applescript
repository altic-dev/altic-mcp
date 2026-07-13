on run argv
	-- Default decrement value
	set decrementValue to 0.0625
	
	-- If argument provided, use it as decrement value
	if (count of argv) > 0 then
		set decrementValue to (item 1 of argv) as real
	end if
	
	try
		-- Use absolute path since `do shell script` uses a minimal PATH
		-- that does not include Homebrew's /opt/homebrew/bin
		set brightnessBin to "/opt/homebrew/bin/brightness"
		
		-- Get current brightness (0.0 to 1.0)
		set currentBrightness to do shell script brightnessBin & " -l | grep 'brightness' | head -n 1 | awk '{print $2}'"
		set currentBrightness to currentBrightness as real
		
		-- Calculate new brightness
		set newBrightness to currentBrightness - decrementValue
		if newBrightness < 0 then
			set newBrightness to 0
		end if
		
		-- Set new brightness
		do shell script brightnessBin & " " & newBrightness
		
		return "Brightness decreased from " & (round (currentBrightness * 100)) & "% to " & (round (newBrightness * 100)) & "%"
	on error errMsg
		return "Error: Unable to decrease brightness: " & errMsg
	end try
end run

