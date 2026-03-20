on run argv
	if (count of argv) > 0 then
		set outputPath to item 1 of argv
	else
		set ts to do shell script "date +%Y%m%d-%H%M%S"
		set outputPath to (POSIX path of (path to desktop folder)) & "screenshot-" & ts & ".png"
	end if

	if (count of argv) > 1 then
		set captureMode to item 2 of argv
	else
		set captureMode to "full"
	end if

	try
		if captureMode is "interactive" then
			do shell script "screencapture -i -x " & quoted form of outputPath
		else if captureMode is "window" then
			do shell script "screencapture -w -x " & quoted form of outputPath
		else
			do shell script "screencapture -x " & quoted form of outputPath
		end if

		return "Screenshot saved: " & outputPath
	on error errMsg
		return "Error capturing screenshot: " & errMsg
	end try
end run
