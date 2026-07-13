import asyncio

from fastmcp.tools.tool import ToolResult
from mcp.types import ImageContent

from tools.mcp_result import normalize_payload, structured_only


def test_structured_only_has_no_text_content():
    result = structured_only('{"query":"passport","results":[],"truncated":true}')

    assert result.content == []
    assert result.structured_content == {
        "ok": True,
        "data": {"items": [], "count": 0, "has_more": True},
        "meta": {"query": "passport"},
    }


def test_file_collection_is_compact():
    payload = normalize_payload(
        {
            "source": "spotlight",
            "results": [
                {
                    "path": "/tmp/passport.pdf",
                    "name": "passport.pdf",
                    "parent": "/tmp",
                    "extension": ".pdf",
                    "exists": True,
                    "is_file": True,
                    "is_dir": False,
                    "is_symlink": False,
                    "size_bytes": 42,
                    "modified_at": 123.0,
                }
            ],
        }
    )

    assert payload == {
        "ok": True,
        "data": {
            "items": [
                {
                    "path": "/tmp/passport.pdf",
                    "type": "file",
                    "size_bytes": 42,
                    "modified_at": 123.0,
                }
            ],
            "count": 1,
            "has_more": False,
        },
        "meta": {"backend": "spotlight"},
    }


def test_mcp_failure_sets_is_error_and_has_no_content():
    import server

    result = asyncio.run(server.mcp._call_tool_mcp("find_files", {"query": ""}))

    assert result.content == []
    assert result.isError is True
    assert result.structuredContent == {
        "ok": False,
        "error": {"code": "tool_error", "message": "query cannot be empty"},
    }


def test_middleware_preserves_rich_content():
    import server

    rich_result = ToolResult(
        content=[ImageContent(type="image", data="aGVsbG8=", mimeType="image/png")]
    )

    async def call_next(_context):
        return rich_result

    normalized = asyncio.run(
        server.StructuredResultMiddleware().on_call_tool(None, call_next)
    )

    assert normalized is rich_result
