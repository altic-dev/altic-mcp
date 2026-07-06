on jsonEscape(rawValue)
	set textValue to rawValue as text
	set AppleScript's text item delimiters to "\\"
	set textValue to text items of textValue
	set AppleScript's text item delimiters to "\\\\"
	set textValue to textValue as text
	set AppleScript's text item delimiters to "\""
	set textValue to text items of textValue
	set AppleScript's text item delimiters to "\\\""
	set textValue to textValue as text
	set AppleScript's text item delimiters to linefeed
	set textValue to text items of textValue
	set AppleScript's text item delimiters to "\\n"
	set textValue to textValue as text
	set AppleScript's text item delimiters to ""
	return textValue
end jsonEscape

on boolText(valueToFormat)
	if valueToFormat then return "true"
	return "false"
end boolText

on joinJson(itemsToJoin)
	set AppleScript's text item delimiters to ","
	set joinedText to itemsToJoin as text
	set AppleScript's text item delimiters to ""
	return joinedText
end joinJson

on parseDate(dateText)
	set AppleScript's text item delimiters to "-"
	set dateParts to text items of dateText
	if (count of dateParts) is not 3 then error "Date format must be 'YYYY-MM-DD'"
	set AppleScript's text item delimiters to ""
	set parsedDate to current date
	set year of parsedDate to (item 1 of dateParts as integer)
	set month of parsedDate to (item 2 of dateParts as integer)
	set day of parsedDate to (item 3 of dateParts as integer)
	set hours of parsedDate to 0
	set minutes of parsedDate to 0
	set seconds of parsedDate to 0
	return parsedDate
end parseDate

on parseDateTime(dateTimeText)
	set AppleScript's text item delimiters to " "
	set dateTimeParts to text items of dateTimeText
	if (count of dateTimeParts) is not 2 then error "Date/time format must be 'YYYY-MM-DD HH:MM'"
	set datePart to item 1 of dateTimeParts
	set timePart to item 2 of dateTimeParts
	set AppleScript's text item delimiters to ":"
	set timeParts to text items of timePart
	if (count of timeParts) is not 2 then error "Time format must be 'HH:MM'"
	set parsedDate to my parseDate(datePart)
	set hours of parsedDate to (item 1 of timeParts as integer)
	set minutes of parsedDate to (item 2 of timeParts as integer)
	set seconds of parsedDate to 0
	set AppleScript's text item delimiters to ""
	return parsedDate
end parseDateTime

on recurrenceUntilText(untilDateText)
	set AppleScript's text item delimiters to "-"
	set dateParts to text items of untilDateText
	if (count of dateParts) is not 3 then error "Date format must be 'YYYY-MM-DD'"
	set AppleScript's text item delimiters to ""
	return (item 1 of dateParts) & (item 2 of dateParts) & (item 3 of dateParts) & "T235959"
end recurrenceUntilText

on upperText(valueText)
	set lowerValues to "abcdefghijklmnopqrstuvwxyz"
	set upperValues to "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	set outputText to ""
	repeat with i from 1 to count characters of valueText
		set currentChar to character i of valueText
		set charIndex to offset of currentChar in lowerValues
		if charIndex is 0 then
			set outputText to outputText & currentChar
		else
			set outputText to outputText & character charIndex of upperValues
		end if
	end repeat
	return outputText
end upperText

on recurrenceRule(frequencyText, intervalText, countText, untilDateText)
	set ruleText to "FREQ=" & my upperText(frequencyText) & ";INTERVAL=" & intervalText
	if countText is not "" then set ruleText to ruleText & ";COUNT=" & countText
	if untilDateText is not "" then set ruleText to ruleText & ";UNTIL=" & my recurrenceUntilText(untilDateText)
	return ruleText
end recurrenceRule

on eventJson(eventItem, calendarName)
	tell application "Calendar"
		set eventTitle to summary of eventItem
		set eventId to uid of eventItem
		set startText to start date of eventItem as string
		set endText to end date of eventItem as string
		try
			set locationText to location of eventItem
		on error
			set locationText to ""
		end try
		try
			set notesText to description of eventItem
		on error
			set notesText to ""
		end try
	end tell
	return "{\"id\":\"" & jsonEscape(eventId) & "\",\"title\":\"" & jsonEscape(eventTitle) & "\",\"calendar\":\"" & jsonEscape(calendarName) & "\",\"start\":\"" & jsonEscape(startText) & "\",\"end\":\"" & jsonEscape(endText) & "\",\"location\":\"" & jsonEscape(locationText) & "\",\"notes\":\"" & jsonEscape(notesText) & "\"}"
end eventJson

on targetCalendars(calendarName)
	tell application "Calendar"
		if calendarName is "" then
			return calendars
		else
			return {calendar calendarName}
		end if
	end tell
end targetCalendars

on collectEvents(startDate, endDate, calendarName, queryText)
	set outputItems to {}
	tell application "Calendar"
		if calendarName is "" then
			set calendarsToSearch to calendars
		else
			set calendarsToSearch to {calendar calendarName}
		end if
		repeat with targetCalendar in calendarsToSearch
			set currentCalendarName to name of targetCalendar
			set matchingEvents to every event of targetCalendar whose start date ≥ startDate and start date ≤ endDate
			repeat with eventItem in matchingEvents
				set shouldInclude to true
				if queryText is not "" then
					set eventText to (summary of eventItem) & " " & (location of eventItem as text) & " " & (description of eventItem as text)
					ignoring case
						if eventText does not contain queryText then set shouldInclude to false
					end ignoring
				end if
				if shouldInclude then set end of outputItems to my eventJson(eventItem, currentCalendarName)
			end repeat
		end repeat
	end tell
	return outputItems
end collectEvents

on findEvents(identifier, startDateText, endDateText, calendarName)
	if startDateText is "" then
		set startDate to (current date) - (365 * days)
	else
		set startDate to my parseDate(startDateText)
	end if
	if endDateText is "" then
		set endDate to (current date) + (365 * days)
	else
		set endDate to (my parseDate(endDateText)) + (24 * hours) - 1
	end if
	set matches to {}
	tell application "Calendar"
		if calendarName is "" then
			set calendarsToSearch to calendars
		else
			set calendarsToSearch to {calendar calendarName}
		end if
		repeat with targetCalendar in calendarsToSearch
			set currentCalendarName to name of targetCalendar
			set matchingEvents to every event of targetCalendar whose start date ≥ startDate and start date ≤ endDate
			repeat with eventItem in matchingEvents
				if (uid of eventItem is identifier) or (summary of eventItem is identifier) then
					set end of matches to {eventItem, currentCalendarName}
				end if
			end repeat
		end repeat
	end tell
	return matches
end findEvents

on run argv
	if (count of argv) < 1 then error "action is required"
	set actionName to item 1 of argv
	try
		if actionName is "list_calendars" then
			set calendarItems to {}
			tell application "Calendar"
				repeat with calendarItem in calendars
					set end of calendarItems to "\"" & my jsonEscape(name of calendarItem) & "\""
				end repeat
			end tell
			return "{\"calendars\":[" & my joinJson(calendarItems) & "]}"
		else if actionName is "list" then
			set startDate to my parseDate(item 2 of argv)
			set endDate to (my parseDate(item 3 of argv)) + (24 * hours) - 1
			set calendarName to item 4 of argv
			set eventItems to my collectEvents(startDate, endDate, calendarName, "")
			return "{\"events\":[" & my joinJson(eventItems) & "],\"count\":" & (count of eventItems) & "}"
		else if actionName is "search" then
			set queryText to item 2 of argv
			if item 3 of argv is "" then
				set startDate to (current date) - (365 * days)
			else
				set startDate to my parseDate(item 3 of argv)
			end if
			if item 4 of argv is "" then
				set endDate to (current date) + (365 * days)
			else
				set endDate to (my parseDate(item 4 of argv)) + (24 * hours) - 1
			end if
			set calendarName to item 5 of argv
			set eventItems to my collectEvents(startDate, endDate, calendarName, queryText)
			return "{\"query\":\"" & my jsonEscape(queryText) & "\",\"events\":[" & my joinJson(eventItems) & "],\"count\":" & (count of eventItems) & "}"
		else if actionName is "update" then
			set identifier to item 2 of argv
			set newTitle to item 3 of argv
			set startDateTimeText to item 4 of argv
			set durationText to item 5 of argv
			set calendarName to item 6 of argv
			set newLocation to item 7 of argv
			set newNotes to item 8 of argv
			set matches to my findEvents(identifier, "", "", calendarName)
			if (count of matches) is not 1 then return "{\"updated\":false,\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set eventItem to item 1 of matchPair
			set matchedCalendarName to item 2 of matchPair
			tell application "Calendar"
				if newTitle is not "" then set summary of eventItem to newTitle
				if startDateTimeText is not "" then
					set newStart to my parseDateTime(startDateTimeText)
					set start date of eventItem to newStart
					if durationText is not "" then set end date of eventItem to newStart + ((durationText as integer) * minutes)
				else if durationText is not "" then
					set end date of eventItem to (start date of eventItem) + ((durationText as integer) * minutes)
				end if
				if newLocation is not "" then set location of eventItem to newLocation
				if newNotes is not "" then set description of eventItem to newNotes
			end tell
			return "{\"updated\":true,\"event\":" & my eventJson(eventItem, matchedCalendarName) & "}"
		else if actionName is "delete" then
			set identifier to item 2 of argv
			set startDateText to item 3 of argv
			set endDateText to item 4 of argv
			set calendarName to item 5 of argv
			set dryRun to ((item 6 of argv) is "true")
			set matches to my findEvents(identifier, startDateText, endDateText, calendarName)
			if (count of matches) is not 1 then return "{\"deleted\":false,\"dry_run\":" & my boolText(dryRun) & ",\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set eventItem to item 1 of matchPair
			set matchedCalendarName to item 2 of matchPair
			set eventData to my eventJson(eventItem, matchedCalendarName)
			if dryRun is false then tell application "Calendar" to delete eventItem
			return "{\"deleted\":" & my boolText(not dryRun) & ",\"dry_run\":" & my boolText(dryRun) & ",\"event\":" & eventData & "}"
		else if actionName is "availability" then
			set startDate to my parseDateTime(item 2 of argv)
			set durationMinutes to item 3 of argv as integer
			set endDate to startDate + (durationMinutes * minutes)
			set calendarName to item 4 of argv
			set eventItems to {}
			tell application "Calendar"
				if calendarName is "" then
					set calendarsToSearch to calendars
				else
					set calendarsToSearch to {calendar calendarName}
				end if
				repeat with targetCalendar in calendarsToSearch
					set currentCalendarName to name of targetCalendar
					set matchingEvents to every event of targetCalendar whose start date < endDate and end date > startDate
					repeat with eventItem in matchingEvents
						set end of eventItems to my eventJson(eventItem, currentCalendarName)
					end repeat
				end repeat
			end tell
			return "{\"available\":" & my boolText((count of eventItems) is 0) & ",\"conflicts\":[" & my joinJson(eventItems) & "],\"count\":" & (count of eventItems) & "}"
		else if actionName is "create_recurring" then
			set eventTitle to item 2 of argv
			set startDate to my parseDateTime(item 3 of argv)
			set durationMinutes to item 4 of argv as integer
			set frequencyText to item 5 of argv
			set intervalText to item 6 of argv
			set countText to item 7 of argv
			set untilDateText to item 8 of argv
			set calendarName to item 9 of argv
			set eventLocation to item 10 of argv
			set eventNotes to item 11 of argv
			set recurrenceText to my recurrenceRule(frequencyText, intervalText, countText, untilDateText)
			tell application "Calendar"
				if calendarName is "" then
					set targetCalendar to first calendar
				else
					set targetCalendar to calendar calendarName
				end if
				set newEvent to make new event at end of events of targetCalendar with properties {summary:eventTitle, start date:startDate, end date:(startDate + (durationMinutes * minutes)), recurrence:recurrenceText}
				if eventLocation is not "" then set location of newEvent to eventLocation
				if eventNotes is not "" then set description of newEvent to eventNotes
				set targetCalendarName to name of targetCalendar
			end tell
			return "{\"created\":true,\"recurrence\":\"" & my jsonEscape(recurrenceText) & "\",\"event\":" & my eventJson(newEvent, targetCalendarName) & "}"
		else
			error "unknown action: " & actionName
		end if
	on error errMsg
		error errMsg
	end try
end run
