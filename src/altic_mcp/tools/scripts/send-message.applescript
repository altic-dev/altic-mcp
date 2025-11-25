on run argv
	set recipientHandle to item 1 of argv
	set messageText to item 2 of argv

	tell application "Messages"
		launch
		set targetService to 1st service whose service type = iMessage
		set targetBuddy to buddy recipientHandle of targetService
		send messageText to targetBuddy
		return "Message sent successfully to " & recipientHandle
	end tell
end run
