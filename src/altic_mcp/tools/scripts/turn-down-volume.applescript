on run argv
	-- Default decrement value (0-100 scale)
	set decrementValue to 6.25
	
	-- If argument provided, use it as decrement value
	if (count of argv) > 0 then
		set decrementValue to (item 1 of argv) as real
	end if
	
	try
		-- Get current volume (0-100)
		set currentVolume to output volume of (get volume settings)
		
		-- Calculate new volume
		set newVolume to currentVolume - decrementValue
		if newVolume < 0 then
			set newVolume to 0
		end if
		
		-- Set new volume
		set volume output volume newVolume
		
		return "Volume decreased from " & (round currentVolume) & "% to " & (round newVolume) & "%"
	on error errMsg
		return "Error adjusting volume: " & errMsg
	end try
end run

