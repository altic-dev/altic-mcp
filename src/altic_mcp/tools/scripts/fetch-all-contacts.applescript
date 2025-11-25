on run argv
	tell application "Contacts"
		launch
		set allPeople to every person
		set contactList to {}

		repeat with aPerson in allPeople
			set personName to name of aPerson
			set phoneNumbers to phones of aPerson

			-- Only include contacts with phone numbers
			if (count of phoneNumbers) > 0 then
				set phoneList to {}

				repeat with aPhone in phoneNumbers
					set phoneLabel to label of aPhone
					set phoneValue to value of aPhone
					set end of phoneList to phoneLabel & ":" & phoneValue
				end repeat

				set AppleScript's text item delimiters to ";"
				set phoneString to phoneList as text
				set AppleScript's text item delimiters to ""

				-- Format: Name|Label1:Number1;Label2:Number2
				set end of contactList to personName & "|" & phoneString
			end if
		end repeat

		-- Return all contacts separated by newlines
		set AppleScript's text item delimiters to linefeed
		set resultString to contactList as text
		set AppleScript's text item delimiters to ""

		return resultString
	end tell
end run
