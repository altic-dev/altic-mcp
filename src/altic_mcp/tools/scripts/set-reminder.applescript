on run argv
	if (count of argv) < 2 then
		return "Usage: osascript set-reminder.applescript \"reminder text\" \"YYYY-MM-DD HH:MM\" [list name]"
	end if

	set reminderText to item 1 of argv
	set dueDateTimeStr to item 2 of argv

	-- Optional: specify which list (defaults to "Reminders")
	if (count of argv) >= 3 then
		set listName to item 3 of argv
	else
		set listName to "Reminders"
	end if

	try
		-- Parse the date/time string (format: YYYY-MM-DD HH:MM)
		set AppleScript's text item delimiters to " "
		set dateTimeParts to text items of dueDateTimeStr

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

		-- Create the date object
		set dueDate to current date
		set year of dueDate to yearNum
		set month of dueDate to monthNum
		set day of dueDate to dayNum
		set hours of dueDate to hourNum
		set minutes of dueDate to minuteNum
		set seconds of dueDate to 0

		-- Create the reminder using Reminders app
		tell application "Reminders"
			-- Find or create the list
			if not (exists list listName) then
				make new list with properties {name:listName}
			end if

			-- Create the reminder
			tell list listName
				set newReminder to make new reminder with properties {name:reminderText, due date:dueDate}
			end tell

			set successMsg to "Reminder created successfully:" & linefeed
			set successMsg to successMsg & "  Text: " & reminderText & linefeed
			set successMsg to successMsg & "  Due: " & (dueDate as string) & linefeed
			set successMsg to successMsg & "  List: " & listName
			return successMsg
		end tell

	on error errMsg
		return "Error creating reminder: " & errMsg
	end try
end run
