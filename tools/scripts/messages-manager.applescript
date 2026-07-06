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

on chatJson(chatItem)
	tell application "Messages"
		set chatId to id of chatItem
		try
			set chatName to name of chatItem
		on error
			set chatName to ""
		end try
		try
			set accountId to id of account of chatItem
		on error
			set accountId to ""
		end try
		try
			set accountDescription to description of account of chatItem
		on error
			set accountDescription to ""
		end try
	end tell
	return "{\"id\":\"" & jsonEscape(chatId) & "\",\"name\":\"" & jsonEscape(chatName) & "\",\"account_id\":\"" & jsonEscape(accountId) & "\",\"account\":\"" & jsonEscape(accountDescription) & "\"}"
end chatJson

on findChat(chatIdentifier)
	tell application "Messages"
		repeat with chatItem in chats
			if id of chatItem is chatIdentifier then return chatItem
		end repeat
	end tell
	error "chat not found: " & chatIdentifier
end findChat

on run argv
	if (count of argv) < 1 then error "action is required"
	set actionName to item 1 of argv
	try
		if actionName is "list_chats" then
			set limitCount to item 2 of argv as integer
			set outputItems to {}
			tell application "Messages"
				launch
				repeat with chatItem in chats
					set end of outputItems to my chatJson(chatItem)
					if (count of outputItems) is greater than or equal to limitCount then exit repeat
				end repeat
			end tell
			return "{\"chats\":[" & my joinJson(outputItems) & "],\"count\":" & (count of outputItems) & "}"
		else if actionName is "send_file" then
			set recipientIdentifier to item 2 of argv
			set filePath to item 3 of argv
			set messageText to item 4 of argv
			set recipientType to item 5 of argv
			set fileAlias to POSIX file filePath as alias
			tell application "Messages"
				launch
				if recipientType is "chat" then
					set targetChat to my findChat(recipientIdentifier)
					if messageText is not "" then send messageText to targetChat
					send fileAlias to targetChat
				else
					set targetService to 1st service whose service type = iMessage
					set targetBuddy to buddy recipientIdentifier of targetService
					if messageText is not "" then send messageText to targetBuddy
					send fileAlias to targetBuddy
				end if
			end tell
			return "{\"sent\":true,\"recipient\":\"" & my jsonEscape(recipientIdentifier) & "\",\"recipient_type\":\"" & my jsonEscape(recipientType) & "\",\"path\":\"" & my jsonEscape(filePath) & "\"}"
		else
			error "unknown action: " & actionName
		end if
	on error errMsg
		error errMsg
	end try
end run
