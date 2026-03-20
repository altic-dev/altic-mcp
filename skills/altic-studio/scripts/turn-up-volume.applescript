on run argv
	set incrementValue to 6.25

	if (count of argv) > 0 then
		set incrementValue to (item 1 of argv) as real
	end if

	try
		set currentVolume to output volume of (get volume settings)

		set newVolume to currentVolume + incrementValue
		if newVolume > 100 then
			set newVolume to 100
		end if

		set volume output volume newVolume

		return "Volume increased from " & (round currentVolume) & "% to " & (round newVolume) & "%"
	on error errMsg
		return "Error adjusting volume: " & errMsg
	end try
end run
