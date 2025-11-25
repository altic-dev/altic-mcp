on run argv
	if (count of argv) < 3 then
		return "Usage: osascript create-calendar-event.applescript \"event title\" \"YYYY-MM-DD HH:MM\" \"duration_minutes\" [calendar name]"
	end if
	
	set eventTitle to item 1 of argv
	set startDateTimeStr to item 2 of argv
	set durationMinutes to (item 3 of argv) as integer
	
	-- Optional: specify which calendar (defaults to first calendar)
	if (count of argv) >= 4 then
		set calendarName to item 4 of argv
	else
		set calendarName to ""
	end if
	
	try
		-- Parse the date/time string (format: YYYY-MM-DD HH:MM)
		set AppleScript's text item delimiters to " "
		set dateTimeParts to text items of startDateTimeStr
		
		if (count of dateTimeParts) is not 2 then
			return "Error: Date/time format must be 'YYYY-MM-DD HH:MM'"
		end if
		
		set datePart to item 1 of dateTimeParts
		set timePart to item 2 of dateTimeParts
		
		-- Parse date (YYYY-MM-DD)
		set AppleScript's text item delimiters to "-"
		set dateParts to text items of datePart
		
		if (count of dateParts) is not 3 then
			return "Error: Date format must be 'YYYY-MM-DD'"
		end if
		
		set yearNum to item 1 of dateParts as integer
		set monthNum to item 2 of dateParts as integer
		set dayNum to item 3 of dateParts as integer
		
		-- Parse time (HH:MM)
		set AppleScript's text item delimiters to ":"
		set timeParts to text items of timePart
		
		if (count of timeParts) is not 2 then
			return "Error: Time format must be 'HH:MM'"
		end if
		
		set hourNum to item 1 of timeParts as integer
		set minuteNum to item 2 of timeParts as integer
		
		-- Reset delimiters
		set AppleScript's text item delimiters to ""
		
		-- Create the start date object
		set startDate to current date
		set year of startDate to yearNum
		set month of startDate to monthNum
		set day of startDate to dayNum
		set hours of startDate to hourNum
		set minutes of startDate to minuteNum
		set seconds of startDate to 0
		
		-- Calculate end date (start date + duration in minutes)
		set endDate to startDate + (durationMinutes * minutes)
		
		-- Create the calendar event
		tell application "Calendar"
			if calendarName is "" then
				-- Use the first calendar
				set targetCalendar to first calendar
			else
				-- Find the specified calendar
				set targetCalendar to first calendar whose name is calendarName
			end if
			
			tell targetCalendar
				set newEvent to make new event with properties {summary:eventTitle, start date:startDate, end date:endDate}
			end tell
			
			set successMsg to "Calendar event created successfully:" & linefeed
			set successMsg to successMsg & "  Title: " & eventTitle & linefeed
			set successMsg to successMsg & "  Start: " & (startDate as string) & linefeed
			set successMsg to successMsg & "  End: " & (endDate as string) & linefeed
			set successMsg to successMsg & "  Calendar: " & (name of targetCalendar)
			return successMsg
		end tell
		
	on error errMsg
		return "Error creating calendar event: " & errMsg
	end try
end run

