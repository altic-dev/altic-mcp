def test_server_exposes_expanded_calendar_reminders_and_notes_tools():
    import server

    tool_names = set(server.mcp._tool_manager._tools)

    assert {
        "list_reminder_lists",
        "list_reminders",
        "search_reminders",
        "complete_reminder",
        "delete_reminder",
        "reschedule_reminder",
        "list_calendars",
        "list_calendar_events",
        "search_calendar_events",
        "update_calendar_event",
        "delete_calendar_event",
        "check_calendar_availability",
        "create_recurring_event",
        "list_note_folders",
        "list_notes",
        "get_note",
        "append_to_note",
        "update_note",
        "delete_note",
        "move_note",
        "list_chats",
        "send_file_message",
        "get_contact",
        "create_contact",
        "update_contact",
        "update_reminder",
        "show_reminder",
    }.issubset(tool_names)
