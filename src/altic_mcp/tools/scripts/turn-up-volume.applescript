on run argv
	-- Default increment value (0-100 scale)
	set incrementValue to 6.25
	
	-- If argument provided, use it as increment value
	if (count of argv) > 0 then
		set incrementValue to (item 1 of argv) as real
	end if
	
	try
		-- Get current volume (0-100)
		set currentVolume to output volume of (get volume settings)
		
		-- Calculate new volume
		set newVolume to currentVolume + incrementValue
		if newVolume > 100 then
			set newVolume to 100
		end if
		
		-- Set new volume
		set volume output volume newVolume
		
		return "Volume increased from " & (round currentVolume) & "% to " & (round newVolume) & "%"
	on error errMsg
		return "Error adjusting volume: " & errMsg
	end try
end run

