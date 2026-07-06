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

on joinJson(itemsToJoin)
	set AppleScript's text item delimiters to ","
	set joinedText to itemsToJoin as text
	set AppleScript's text item delimiters to ""
	return joinedText
end joinJson

on contactInfoJson(infoItem)
	tell application "Contacts"
		try
			set infoLabel to label of infoItem
		on error
			set infoLabel to ""
		end try
		try
			set infoValue to value of infoItem
		on error
			set infoValue to ""
		end try
		try
			set infoId to id of infoItem
		on error
			set infoId to ""
		end try
	end tell
	return "{\"id\":\"" & jsonEscape(infoId) & "\",\"label\":\"" & jsonEscape(infoLabel) & "\",\"value\":\"" & jsonEscape(infoValue) & "\"}"
end contactInfoJson

on contactJson(personItem)
	set phoneItems to {}
	set emailItems to {}
	tell application "Contacts"
		try
			set contactId to id of personItem
		on error
			set contactId to ""
		end try
		try
			set contactName to name of personItem
		on error
			set contactName to ""
		end try
		try
			set firstNameText to first name of personItem
		on error
			set firstNameText to ""
		end try
		try
			set lastNameText to last name of personItem
		on error
			set lastNameText to ""
		end try
		try
			set organizationText to organization of personItem
		on error
			set organizationText to ""
		end try
		try
			set noteText to note of personItem
		on error
			set noteText to ""
		end try
		repeat with phoneItem in phones of personItem
			set end of phoneItems to my contactInfoJson(phoneItem)
		end repeat
		repeat with emailItem in emails of personItem
			set end of emailItems to my contactInfoJson(emailItem)
		end repeat
	end tell
	return "{\"id\":\"" & jsonEscape(contactId) & "\",\"name\":\"" & jsonEscape(contactName) & "\",\"first_name\":\"" & jsonEscape(firstNameText) & "\",\"last_name\":\"" & jsonEscape(lastNameText) & "\",\"organization\":\"" & jsonEscape(organizationText) & "\",\"note\":\"" & jsonEscape(noteText) & "\",\"phones\":[" & my joinJson(phoneItems) & "],\"emails\":[" & my joinJson(emailItems) & "]}"
end contactJson

on findPeople(identifier)
	set matches to {}
	tell application "Contacts"
		repeat with personItem in people
			set shouldInclude to false
			try
				if id of personItem is identifier then set shouldInclude to true
			end try
			try
				ignoring case
					if name of personItem contains identifier then set shouldInclude to true
				end ignoring
			end try
			if shouldInclude then set end of matches to personItem
		end repeat
	end tell
	return matches
end findPeople

on addPhoneIfProvided(personItem, phoneValue)
	if phoneValue is "" then return
	tell application "Contacts"
		make new phone at end of phones of personItem with properties {label:"mobile", value:phoneValue}
	end tell
end addPhoneIfProvided

on addEmailIfProvided(personItem, emailValue)
	if emailValue is "" then return
	tell application "Contacts"
		make new email at end of emails of personItem with properties {label:"home", value:emailValue}
	end tell
end addEmailIfProvided

on run argv
	if (count of argv) < 1 then error "action is required"
	set actionName to item 1 of argv
	try
		if actionName is "get" then
			set identifier to item 2 of argv
			set matches to my findPeople(identifier)
			if (count of matches) is not 1 then return "{\"found\":false,\"match_count\":" & (count of matches) & "}"
			return "{\"found\":true,\"contact\":" & my contactJson(item 1 of matches) & "}"
		else if actionName is "create" then
			set firstNameText to item 2 of argv
			set lastNameText to item 3 of argv
			set organizationText to item 4 of argv
			set phoneValue to item 5 of argv
			set emailValue to item 6 of argv
			set noteText to item 7 of argv
			tell application "Contacts"
				launch
				set newPerson to make new person at end of people with properties {first name:firstNameText, last name:lastNameText}
				if organizationText is not "" then set organization of newPerson to organizationText
				if noteText is not "" then set note of newPerson to noteText
			end tell
			my addPhoneIfProvided(newPerson, phoneValue)
			my addEmailIfProvided(newPerson, emailValue)
			tell application "Contacts" to save
			return "{\"created\":true,\"contact\":" & my contactJson(newPerson) & "}"
		else if actionName is "update" then
			set identifier to item 2 of argv
			set firstNameText to item 3 of argv
			set lastNameText to item 4 of argv
			set organizationText to item 5 of argv
			set phoneValue to item 6 of argv
			set emailValue to item 7 of argv
			set noteText to item 8 of argv
			set matches to my findPeople(identifier)
			if (count of matches) is not 1 then return "{\"updated\":false,\"match_count\":" & (count of matches) & "}"
			set personItem to item 1 of matches
			tell application "Contacts"
				if firstNameText is not "" then set first name of personItem to firstNameText
				if lastNameText is not "" then set last name of personItem to lastNameText
				if organizationText is not "" then set organization of personItem to organizationText
				if noteText is not "" then set note of personItem to noteText
			end tell
			my addPhoneIfProvided(personItem, phoneValue)
			my addEmailIfProvided(personItem, emailValue)
			tell application "Contacts" to save
			return "{\"updated\":true,\"contact\":" & my contactJson(personItem) & "}"
		else
			error "unknown action: " & actionName
		end if
	on error errMsg
		error errMsg
	end try
end run
