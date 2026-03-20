on run argv
	set incrementValue to 0.0625

	if (count of argv) > 0 then
		set incrementValue to (item 1 of argv) as real
	end if

	try
		tell application "System Events"
			set currentBrightness to do shell script "brightness -l | grep 'brightness' | head -n 1 | awk '{print $2}'"
			set currentBrightness to currentBrightness as real

			set newBrightness to currentBrightness + incrementValue
			if newBrightness > 1 then
				set newBrightness to 1
			end if

			do shell script "brightness " & newBrightness

			return "Brightness increased from " & (round (currentBrightness * 100)) & "% to " & (round (newBrightness * 100)) & "%"
		end tell
	on error errMsg
		tell application "System Events"
			key code 113
		end tell
		return "Brightness increased (using keyboard shortcut)"
	end try
end run
