on run argv
	set contactIdentifier to item 1 of argv
	set messageCount to item 2 of argv as integer

	-- Build SQL query to get recent messages from specific contact
	-- Query for more messages than requested to account for filtering empty ones
	set queryLimit to messageCount * 5
	set sqlQuery to "SELECT
    datetime(message.date / 1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime') AS message_date,
    message.text,
    message.is_from_me,
    chat.chat_identifier
FROM chat
JOIN chat_message_join ON chat.ROWID = chat_message_join.chat_id
JOIN message ON chat_message_join.message_id = message.ROWID
WHERE chat.chat_identifier LIKE '%" & contactIdentifier & "%'
ORDER BY message.date DESC
LIMIT " & queryLimit & ";"

	try
		-- Query the Messages database
		set dbPath to (POSIX path of (path to home folder)) & "Library/Messages/chat.db"
		set queryResult to do shell script "sqlite3 -separator '|' " & quoted form of dbPath & " " & quoted form of sqlQuery

		if queryResult is "" then
			return "No messages found for contact: " & contactIdentifier
		end if

		-- Parse results and build output
		set output to "Last " & messageCount & " message(s) from chat with " & contactIdentifier & ":" & linefeed & linefeed

		set messageLines to paragraphs of queryResult

		-- Collect non-empty messages
		set nonEmptyMessages to {}
		repeat with i from 1 to (count of messageLines)
			set msgLine to item i of messageLines

			if msgLine is not "" then
				set AppleScript's text item delimiters to "|"
				set msgParts to text items of msgLine

				if (count of msgParts) ≥ 3 then
					set msgText to item 2 of msgParts

					-- Only include non-empty messages
					if msgText is not "" then
						set end of nonEmptyMessages to msgLine

						-- Stop once we have enough messages
						if (count of nonEmptyMessages) ≥ messageCount then
							exit repeat
						end if
					end if
				end if

				set AppleScript's text item delimiters to ""
			end if
		end repeat

		-- Reverse to show oldest to newest and build output
		repeat with i from (count of nonEmptyMessages) to 1 by -1
			set msgLine to item i of nonEmptyMessages

			set AppleScript's text item delimiters to "|"
			set msgParts to text items of msgLine

			set msgDate to item 1 of msgParts
			set msgText to item 2 of msgParts
			set isFromMe to item 3 of msgParts

			-- Determine sender label
			if isFromMe is "1" then
				set senderLabel to "Me"
			else
				set senderLabel to contactIdentifier
			end if

			set output to output & "[" & msgDate & "] " & senderLabel & ": " & msgText & linefeed
			set AppleScript's text item delimiters to ""
		end repeat

		return output

	on error errMsg
		return "Error: " & errMsg & linefeed & "Make sure you have Full Disk Access enabled for Terminal or the app running this script."
	end try
end run
