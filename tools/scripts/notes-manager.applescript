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

on noteJson(noteItem, folderName, includeBody)
	set noteName to name of noteItem
	set noteId to id of noteItem
	set createdText to creation date of noteItem as string
	set modifiedText to modification date of noteItem as string
	set payload to "{\"id\":\"" & jsonEscape(noteId) & "\",\"title\":\"" & jsonEscape(noteName) & "\",\"folder\":\"" & jsonEscape(folderName) & "\",\"created\":\"" & jsonEscape(createdText) & "\",\"modified\":\"" & jsonEscape(modifiedText) & "\""
	if includeBody then
		set htmlBody to body of noteItem
		set payload to payload & ",\"html_body\":\"" & jsonEscape(htmlBody) & "\",\"plain_text\":\"" & jsonEscape(htmlBody) & "\""
	end if
	return payload & "}"
end noteJson

on collectNotes(folderName, maxResults)
	set outputItems to {}
	tell application "Notes"
		repeat with accountItem in accounts
			repeat with folderItem in folders of accountItem
				set currentFolderName to name of folderItem
				if folderName is "" or currentFolderName is folderName then
					repeat with noteItem in notes of folderItem
						set end of outputItems to my noteJson(noteItem, currentFolderName, false)
						if (count of outputItems) ≥ maxResults then return outputItems
					end repeat
				end if
			end repeat
		end repeat
	end tell
	return outputItems
end collectNotes

on findNotes(identifier)
	set matches to {}
	tell application "Notes"
		repeat with accountItem in accounts
			repeat with folderItem in folders of accountItem
				set currentFolderName to name of folderItem
				repeat with noteItem in notes of folderItem
					if (id of noteItem is identifier) or (name of noteItem is identifier) then
						set end of matches to {noteItem, currentFolderName}
					end if
				end repeat
			end repeat
		end repeat
	end tell
	return matches
end findNotes

on findFolder(folderName)
	tell application "Notes"
		repeat with accountItem in accounts
			repeat with folderItem in folders of accountItem
				if name of folderItem is folderName then return folderItem
			end repeat
		end repeat
	end tell
	error "folder not found: " & folderName
end findFolder

on run argv
	if (count of argv) < 1 then error "action is required"
	set actionName to item 1 of argv
	try
		if actionName is "list_folders" then
			set folderItems to {}
			tell application "Notes"
				repeat with accountItem in accounts
					repeat with folderItem in folders of accountItem
						set end of folderItems to "\"" & my jsonEscape(name of folderItem) & "\""
					end repeat
				end repeat
			end tell
			return "{\"folders\":[" & my joinJson(folderItems) & "]}"
		else if actionName is "list" then
			set folderName to item 2 of argv
			set maxResults to item 3 of argv as integer
			set noteItems to my collectNotes(folderName, maxResults)
			return "{\"notes\":[" & my joinJson(noteItems) & "],\"count\":" & (count of noteItems) & "}"
		else if actionName is "get" then
			set identifier to item 2 of argv
			set matches to my findNotes(identifier)
			if (count of matches) is not 1 then return "{\"found\":false,\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			return "{\"found\":true,\"note\":" & my noteJson(item 1 of matchPair, item 2 of matchPair, true) & "}"
		else if actionName is "append" then
			set identifier to item 2 of argv
			set bodyText to item 3 of argv
			set matches to my findNotes(identifier)
			if (count of matches) is not 1 then return "{\"updated\":false,\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set noteItem to item 1 of matchPair
			tell application "Notes" to set body of noteItem to (body of noteItem) & "<br>" & bodyText
			return "{\"updated\":true,\"note\":" & my noteJson(noteItem, item 2 of matchPair, false) & "}"
		else if actionName is "update" then
			set identifier to item 2 of argv
			set bodyText to item 3 of argv
			set matches to my findNotes(identifier)
			if (count of matches) is not 1 then return "{\"updated\":false,\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set noteItem to item 1 of matchPair
			tell application "Notes" to set body of noteItem to bodyText
			return "{\"updated\":true,\"note\":" & my noteJson(noteItem, item 2 of matchPair, false) & "}"
		else if actionName is "delete" then
			set identifier to item 2 of argv
			set dryRun to ((item 3 of argv) is "true")
			set matches to my findNotes(identifier)
			if (count of matches) is not 1 then return "{\"deleted\":false,\"dry_run\":" & my boolText(dryRun) & ",\"match_count\":" & (count of matches) & "}"
			set matchPair to item 1 of matches
			set noteItem to item 1 of matchPair
			set noteData to my noteJson(noteItem, item 2 of matchPair, false)
			if dryRun is false then tell application "Notes" to delete noteItem
			return "{\"deleted\":" & my boolText(not dryRun) & ",\"dry_run\":" & my boolText(dryRun) & ",\"note\":" & noteData & "}"
		else if actionName is "move" then
			set identifier to item 2 of argv
			set folderName to item 3 of argv
			set matches to my findNotes(identifier)
			if (count of matches) is not 1 then return "{\"moved\":false,\"match_count\":" & (count of matches) & "}"
			set targetFolder to my findFolder(folderName)
			set matchPair to item 1 of matches
			set noteItem to item 1 of matchPair
			tell application "Notes" to move noteItem to targetFolder
			return "{\"moved\":true,\"note\":" & my noteJson(noteItem, folderName, false) & "}"
		else
			error "unknown action: " & actionName
		end if
	on error errMsg
		error errMsg
	end try
end run
