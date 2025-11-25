on run argv
	if (count of argv) < 1 then
		return "Usage: osascript search-for-note.applescript \"search query\" [max results]"
	end if

	set searchQuery to item 1 of argv

	-- Optional: limit number of results (defaults to 10)
	if (count of argv) >= 2 then
		set maxResults to item 2 of argv as integer
	else
		set maxResults to 10
	end if

	try
		tell application "Notes"
			set matchingNotes to {}
			set noteCount to 0

			-- Search through all accounts and notes
			repeat with acc in accounts
				repeat with nte in notes of acc
					-- Check if query matches note name or body
					set noteName to name of nte
					set noteBody to body of nte

					if noteName contains searchQuery or noteBody contains searchQuery then
						set noteCount to noteCount + 1
						set end of matchingNotes to {noteName:noteName, noteId:id of nte, creationDate:creation date of nte, modificationDate:modification date of nte}

						-- Stop if we've reached max results
						if noteCount >= maxResults then
							exit repeat
						end if
					end if
				end repeat

				if noteCount >= maxResults then
					exit repeat
				end if
			end repeat

			-- Build output
			if noteCount is 0 then
				return "No notes found matching query: " & searchQuery
			end if

			set output to "Found " & noteCount & " note(s) matching '" & searchQuery & "':" & linefeed & linefeed

			repeat with noteInfo in matchingNotes
				set output to output & "Title: " & noteName of noteInfo & linefeed
				set output to output & "  ID: " & noteId of noteInfo & linefeed
				set output to output & "  Created: " & (creationDate of noteInfo as string) & linefeed
				set output to output & "  Modified: " & (modificationDate of noteInfo as string) & linefeed
				set output to output & linefeed
			end repeat

			return output
		end tell

	on error errMsg
		return "Error searching notes: " & errMsg
	end try
end run
