on run argv
	if (count of argv) < 2 then
		return "Usage: osascript create-note.applescript \"note title\" \"note body\" [folder name]"
	end if

	set noteTitle to item 1 of argv
	set noteBody to item 2 of argv

	-- Optional: specify which folder (defaults to default Notes folder)
	if (count of argv) >= 3 then
		set folderName to item 3 of argv
	else
		set folderName to missing value
	end if

	try
		tell application "Notes"
			-- If folder is specified, use it; otherwise use default account
			if folderName is not missing value then
				-- Check if folder exists
				set folderExists to false
				repeat with acc in accounts
					repeat with fld in folders of acc
						if name of fld is folderName then
							set targetFolder to fld
							set folderExists to true
							exit repeat
						end if
					end repeat
					if folderExists then exit repeat
				end repeat

				if not folderExists then
					return "Error: Folder '" & folderName & "' not found"
				end if

				-- Create note in specified folder
				tell targetFolder
					set newNote to make new note with properties {name:noteTitle, body:noteBody}
				end tell
			else
				-- Create note in default location
				set newNote to make new note with properties {name:noteTitle, body:noteBody}
			end if

			set noteId to id of newNote
			set noteCreationDate to creation date of newNote

			set successMsg to "Note created successfully:" & linefeed
			set successMsg to successMsg & "  Title: " & noteTitle & linefeed
			set successMsg to successMsg & "  Created: " & (noteCreationDate as string) & linefeed
			if folderName is not missing value then
				set successMsg to successMsg & "  Folder: " & folderName & linefeed
			end if
			set successMsg to successMsg & "  ID: " & noteId

			return successMsg
		end tell

	on error errMsg
		return "Error creating note: " & errMsg
	end try
end run
