on run argv
	set decrementValue to 6.25

	if (count of argv) > 0 then
		set decrementValue to (item 1 of argv) as real
	end if

	try
		set currentVolume to output volume of (get volume settings)

		set newVolume to currentVolume - decrementValue
		if newVolume < 0 then
			set newVolume to 0
		end if

		set volume output volume newVolume

		return "Volume decreased from " & (round currentVolume) & "% to " & (round newVolume) & "%"
	on error errMsg
		return "Error adjusting volume: " & errMsg
	end try
end run
