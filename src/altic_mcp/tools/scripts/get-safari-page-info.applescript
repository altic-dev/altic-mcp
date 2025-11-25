on run argv
	try
		tell application "Safari"
			if (count of windows) = 0 then
				return "Error: No Safari windows are open"
			end if
			
			tell window 1
				if (count of tabs) = 0 then
					return "Error: No tabs are open in Safari"
				end if
				
				tell current tab
					set pageURL to URL
					set pageTitle to name
					
					-- Get page text content
					set pageText to do JavaScript "document.body.innerText || document.body.textContent || '';"
					
					-- Get page source (first 5000 characters to avoid overwhelming output)
					set pageSource to do JavaScript "(function() { var src = document.documentElement.outerHTML; return src.length > 5000 ? src.substring(0, 5000) + '... [truncated]' : src; })();"
					
					set output to "Safari Page Information:" & linefeed & linefeed
					set output to output & "URL: " & pageURL & linefeed
					set output to output & "Title: " & pageTitle & linefeed & linefeed
					set output to output & "Text Content (first 2000 chars):" & linefeed
					
					-- Truncate text if too long
					if length of pageText > 2000 then
						set output to output & text 1 thru 2000 of pageText & "... [truncated]" & linefeed & linefeed
					else
						set output to output & pageText & linefeed & linefeed
					end if
					
					set output to output & "HTML Source:" & linefeed & pageSource
					
					return output
				end tell
			end tell
		end tell
	on error errMsg
		return "Error getting Safari page info: " & errMsg
	end try
end run

