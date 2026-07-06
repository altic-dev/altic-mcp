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

on parseDateTime(dateTimeText)
	set AppleScript's text item delimiters to " "
	set dateTimeParts to text items of dateTimeText
	if (count of dateTimeParts) is not 2 then error "Date/time format must be 'YYYY-MM-DD HH:MM'"
	set datePart to item 1 of dateTimeParts
	set timePart to item 2 of dateTimeParts
	set AppleScript's text item delimiters to "-"
	set dateParts to text items of datePart
	if (count of dateParts) is not 3 then error "Date format must be 'YYYY-MM-DD'"
	set AppleScript's text item delimiters to ":"
	set timeParts to text items of timePart
	if (count of timeParts) is not 2 then error "Time format must be 'HH:MM'"
	set AppleScript's text item delimiters to ""
	set parsedDate to current date
	set year of parsedDate to (item 1 of dateParts as integer)
	set month of parsedDate to (item 2 of dateParts as integer)
	set day of parsedDate to (item 3 of dateParts as integer)
	set hours of parsedDate to (item 1 of timeParts as integer)
	set minutes of parsedDate to (item 2 of timeParts as integer)
	set seconds of parsedDate to 0
	return parsedDate
end parseDateTime

on reminderJson(reminderItem, listName)
	tell application "Reminders"
		set reminderName to name of reminderItem
		set reminderId to id of reminderItem
		set isCompleted to completed of reminderItem
		try
			set bodyText to body of reminderItem
		on error
			set bodyText to ""
		end try
		try
			set priorityValue to priority of reminderItem
		on error
			set priorityValue to 0
		end try
		try
			set flaggedValue to flagged of reminderItem
		on error
			set flaggedValue to false
		end try
		try
			set dueText to due date of reminderItem as string
		on error
			set dueText to ""
		end try
	end tell
	return "{\"id\":\"" & jsonEscape(reminderId) & "\",\"name\":\"" & jsonEscape(reminderName) & "\",\"list\":\"" & jsonEscape(listName) & "\",\"completed\":" & boolText(isCompleted) & ",\"due\":\"" & jsonEscape(dueText) & "\",\"body\":\"" & jsonEscape(bodyText) & "\",\"priority\":" & priorityValue & ",\"flagged\":" & boolText(flaggedValue) & "}"
end reminderJson

on joinJson(itemsToJoin)
	set AppleScript's text item delimiters to ","
	set joinedText to itemsToJoin as text
	set AppleScript's text item delimiters to ""
	return joinedText
end joinJson

on collectReminders(listName, includeCompleted, queryText)
	set outputItems to {}
	tell application "Reminders"
		if listName is "" then
			set targetLists to lists
		else
			set targetLists to {list listName}
		end if
		repeat with targetList in targetLists
			set currentListName to name of targetList
			if queryText is "" then
				if includeCompleted then
					set matchingReminders to reminders of targetList
				else
					set matchingReminders to reminders of targetList whose completed is false
				end if
			else
				if includeCompleted then
					set matchingReminders to reminders of targetList whose name contains queryText
				else
					set matchingReminders to reminders of targetList whose completed is false and name contains queryText
				end if
			end if
			repeat with reminderItem in matchingReminders
				set end of outputItems to my reminderJson(reminderItem, currentListName)
			end repeat
		end repeat
	end tell
	return outputItems
end collectReminders

on findReminder(identifier, listName)
	set matches to {}
	tell application "Reminders"
		if listName is "" then
			set targetLists to lists
		else
			set targetLists to {list listName}
		end if
		repeat with targetList in targetLists
			set currentListName to name of targetList
			set idMatches to reminders of targetList whose id is identifier
			if (count of idMatches) is greater than 0 then
				repeat with reminderItem in idMatches
					set end of matches to {reminderItem, currentListName}
				end repeat
			else
				set nameMatches to reminders of targetList whose name is identifier
				repeat with reminderItem in nameMatches
					set end of matches to {reminderItem, currentListName}
				end repeat
			end if
		end repeat
	end tell
	return matches
end findReminder

on run argv
	if (count of argv) < 1 then error "action is required"
	set actionName to item 1 of argv
	try
		if actionName is "list_lists" then
			set listItems to {}
			tell application "Reminders"
				repeat with reminderList in lists
					set end of listItems to "\"" & my jsonEscape(name of reminderList) & "\""
				end repeat
			end tell
			return "{\"lists\":[" & my joinJson(listItems) & "]}"
		else if actionName is "list" then
			set listName to item 2 of argv
			set includeCompleted to ((item 3 of argv) is "true")
			set reminderItems to my collectReminders(listName, includeCompleted, "")
			return "{\"reminders\":[" & my joinJson(reminderItems) & "],\"count\":" & (count of reminderItems) & "}"
		else if actionName is "search" then
			set queryText to item 2 of argv
			set listName to item 3 of argv
			set includeCompleted to ((item 4 of argv) is "true")
			set reminderItems to my collectReminders(listName, includeCompleted, queryText)
			return "{\"query\":\"" & my jsonEscape(queryText) & "\",\"reminders\":[" & my joinJson(reminderItems) & "],\"count\":" & (count of reminderItems) & "}"
		else if actionName is "complete" then
			set identifier to item 2 of argv
			set listName to item 3 of argv
			set matches to my findReminder(identifier, listName)
			if (count of matches) is not 1 then return "{\"completed\":false,\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set reminderItem to item 1 of matchPair
			set matchedListName to item 2 of matchPair
			tell application "Reminders" to set completed of reminderItem to true
			return "{\"completed\":true,\"reminder\":" & my reminderJson(reminderItem, matchedListName) & "}"
		else if actionName is "delete" then
			set identifier to item 2 of argv
			set listName to item 3 of argv
			set dryRun to ((item 4 of argv) is "true")
			set matches to my findReminder(identifier, listName)
			if (count of matches) is not 1 then return "{\"deleted\":false,\"dry_run\":" & my boolText(dryRun) & ",\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set reminderItem to item 1 of matchPair
			set matchedListName to item 2 of matchPair
			set reminderData to my reminderJson(reminderItem, matchedListName)
			if dryRun is false then tell application "Reminders" to delete reminderItem
			return "{\"deleted\":" & my boolText(not dryRun) & ",\"dry_run\":" & my boolText(dryRun) & ",\"reminder\":" & reminderData & "}"
		else if actionName is "reschedule" then
			set identifier to item 2 of argv
			set dueDate to my parseDateTime(item 3 of argv)
			set listName to item 4 of argv
			set matches to my findReminder(identifier, listName)
			if (count of matches) is not 1 then return "{\"rescheduled\":false,\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set reminderItem to item 1 of matchPair
			set matchedListName to item 2 of matchPair
			tell application "Reminders" to set due date of reminderItem to dueDate
			return "{\"rescheduled\":true,\"reminder\":" & my reminderJson(reminderItem, matchedListName) & "}"
		else if actionName is "update" then
			set identifier to item 2 of argv
			set listName to item 3 of argv
			set newName to item 4 of argv
			set newBody to item 5 of argv
			set dueDateText to item 6 of argv
			set completedText to item 7 of argv
			set priorityText to item 8 of argv
			set flaggedText to item 9 of argv
			set matches to my findReminder(identifier, listName)
			if (count of matches) is not 1 then return "{\"updated\":false,\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set reminderItem to item 1 of matchPair
			set matchedListName to item 2 of matchPair
			tell application "Reminders"
				if newName is not "" then set name of reminderItem to newName
				if newBody is not "" then set body of reminderItem to newBody
				if dueDateText is not "" then set due date of reminderItem to my parseDateTime(dueDateText)
				if completedText is "true" then set completed of reminderItem to true
				if completedText is "false" then set completed of reminderItem to false
				if priorityText is not "" then set priority of reminderItem to priorityText as integer
				if flaggedText is "true" then set flagged of reminderItem to true
				if flaggedText is "false" then set flagged of reminderItem to false
			end tell
			return "{\"updated\":true,\"reminder\":" & my reminderJson(reminderItem, matchedListName) & "}"
		else if actionName is "show" then
			set identifier to item 2 of argv
			set listName to item 3 of argv
			set matches to my findReminder(identifier, listName)
			if (count of matches) is not 1 then return "{\"shown\":false,\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set reminderItem to item 1 of matchPair
			set matchedListName to item 2 of matchPair
			tell application "Reminders"
				activate
				ignoring application responses
					show reminderItem
				end ignoring
			end tell
			return "{\"shown\":true,\"reminder\":" & my reminderJson(reminderItem, matchedListName) & "}"
		else
			error "unknown action: " & actionName
		end if
	on error errMsg
		error errMsg
	end try
end run
