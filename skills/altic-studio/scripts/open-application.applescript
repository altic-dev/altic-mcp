on run argv
    set appName to item 1 of argv

    try
        tell application appName
            activate
        end tell
        return "Successfully opened " & appName
    on error errMsg
        return "Error opening " & appName & ": " & errMsg
    end try
end run
