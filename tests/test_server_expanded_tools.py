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


def test_server_exposes_config_audit_and_search_tools():
    import server

    tool_names = set(server.mcp._tool_manager._tools)

    assert {
        "get_config",
        "set_config_value",
        "get_recent_tool_calls",
        "start_search",
        "get_more_search_results",
        "stop_search",
        "list_searches",
    }.issubset(tool_names)


def test_server_exposes_resources_and_prompts():
    import asyncio

    import server

    resources = asyncio.run(server.mcp.get_resources())
    resource_uris = set(resources.keys())
    assert "altic://apps/frontmost" in resource_uris
    assert "altic://finder/selection" in resource_uris
    assert "altic://clipboard/text" in resource_uris

    prompts = asyncio.run(server.mcp.get_prompts())
    prompt_names = set(prompts.keys())
    assert "summarize_today_calendar" in prompt_names
    assert "draft_imessage_reply" in prompt_names
    assert "find_and_summarize_notes" in prompt_names
