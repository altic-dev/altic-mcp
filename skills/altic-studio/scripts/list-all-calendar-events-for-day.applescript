on run argv
	if (count of argv) < 1 then
		return "Usage: osascript list-all-calendar-events-for-day.applescript \"YYYY-MM-DD\""
	end if

	set dateStr to item 1 of argv

	try
		set AppleScript's text item delimiters to "-"
		set dateParts to text items of dateStr

		if (count of dateParts) is not 3 then
			return "Error: Date format must be 'YYYY-MM-DD'"
		end if

		set yearNum to item 1 of dateParts as integer
		set monthNum to item 2 of dateParts as integer
		set dayNum to item 3 of dateParts as integer

		set AppleScript's text item delimiters to ""

		set startDate to current date
		set year of startDate to yearNum
		set month of startDate to monthNum
		set day of startDate to dayNum
		set hours of startDate to 0
		set minutes of startDate to 0
		set seconds of startDate to 0

		set endDate to startDate + (24 * hours) - 1

		tell application "Calendar"
			set allEvents to {}

			repeat with cal in calendars
				set eventsInCal to (every event of cal whose start date ≥ startDate and start date ≤ endDate)
				set allEvents to allEvents & eventsInCal
			end repeat

			if (count of allEvents) is 0 then
				return "No events found for " & dateStr
			end if

			set output to "Events for " & dateStr & ":" & linefeed & linefeed

			set sortedEvents to allEvents
			repeat with i from 1 to (count of sortedEvents) - 1
				repeat with j from i + 1 to count of sortedEvents
					set event1 to item i of sortedEvents
					set event2 to item j of sortedEvents
					if (start date of event1) > (start date of event2) then
						set temp to item i of sortedEvents
						set item i of sortedEvents to item j of sortedEvents
						set item j of sortedEvents to temp
					end if
				end repeat
			end repeat

			repeat with i from 1 to count of sortedEvents
				set currentEvent to item i of sortedEvents

				set eventTitle to summary of currentEvent
				set eventStart to start date of currentEvent
				set eventEnd to end date of currentEvent
				set eventLocation to location of currentEvent

				set startHour to hours of eventStart as string
				if (length of startHour) is 1 then set startHour to "0" & startHour
				set startMin to minutes of eventStart as string
				if (length of startMin) is 1 then set startMin to "0" & startMin
				set startTime to startHour & ":" & startMin

				set endHour to hours of eventEnd as string
				if (length of endHour) is 1 then set endHour to "0" & endHour
				set endMin to minutes of eventEnd as string
				if (length of endMin) is 1 then set endMin to "0" & endMin
				set endTime to endHour & ":" & endMin

				set output to output & i & ". " & eventTitle & linefeed
				set output to output & "   Time: " & startTime & " - " & endTime & linefeed

				if eventLocation is not missing value and eventLocation is not "" then
					set output to output & "   Location: " & eventLocation & linefeed
				end if

				set output to output & linefeed
			end repeat

			return output
		end tell

	on error errMsg
		return "Error listing calendar events: " & errMsg
	end try
end run
