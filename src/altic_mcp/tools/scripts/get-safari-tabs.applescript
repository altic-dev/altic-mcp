on run argv
	try
		tell application "Safari"
			if (count of windows) = 0 then
				return "No Safari windows are open"
			end if
			
			set output to "Safari Tabs:" & linefeed & linefeed
			
			repeat with w from 1 to count of windows
				tell window w
					set output to output & "Window " & w & " (" & (count of tabs) & " tabs):" & linefeed
					
					repeat with t from 1 to count of tabs
						tell tab t
							set tabURL to URL
							set tabName to name
							set isCurrent to false
							
							-- Check if this is the current tab
							if t = (index of current tab) and w = 1 then
								set isCurrent to true
							end if
							
							set output to output & "  [" & t & "] "
							if isCurrent then
								set output to output & "* "
							end if
							set output to output & tabName & linefeed
							set output to output & "      " & tabURL & linefeed
						end tell
					end repeat
					set output to output & linefeed
				end tell
			end repeat
			
			return output
		end tell
	on error errMsg
		return "Error getting Safari tabs: " & errMsg
	end try
end run

