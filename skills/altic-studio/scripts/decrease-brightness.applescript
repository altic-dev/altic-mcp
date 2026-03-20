on run argv
	set decrementValue to 0.0625

	if (count of argv) > 0 then
		set decrementValue to (item 1 of argv) as real
	end if

	try
		tell application "System Events"
			set currentBrightness to do shell script "brightness -l | grep 'brightness' | head -n 1 | awk '{print $2}'"
			set currentBrightness to currentBrightness as real

			set newBrightness to currentBrightness - decrementValue
			if newBrightness < 0 then
				set newBrightness to 0
			end if

			do shell script "brightness " & newBrightness

			return "Brightness decreased from " & (round (currentBrightness * 100)) & "% to " & (round (newBrightness * 100)) & "%"
		end tell
	on error errMsg
		tell application "System Events"
			key code 107
		end tell
		return "Brightness decreased (using keyboard shortcut)"
	end try
end run
