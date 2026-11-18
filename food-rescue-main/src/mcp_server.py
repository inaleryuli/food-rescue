"""Food Rescue MCP tool server: one JSON-RPC/stdio tool, no third-party deps.

Exposes ``search_food_rescue`` over the Model Context Protocol stdio
transport (newline-delimited JSON-RPC 2.0), wrapping the deterministic
ranking engine in :mod:`src.engine`.

    python src/mcp_server.py          # MCP stdio server (see mcp.json)
    python src/mcp_server.py --test   # local self-check, no client needed

Safety and validation order follows ``skills/food-rescue/SKILL.md``: scan for
non-food items first, then reject an empty or staples-only pantry, then rank.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Allow `python src/mcp_server.py` from any working directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine import rank_recipes
from src.normalizer import normalize_ingredient, normalize_pantry

SERVER_NAME = "food-rescue"
SERVER_VERSION = "1.0.0"
DEFAULT_PROTOCOL_VERSION = "2025-06-18"
TOOL_NAME = "search_food_rescue"
TOP_RESULT_LIMIT = 3

STAPLES_ONLY_MESSAGE = "[INPUT ERROR] Please provide at least one core ingredient."

from src.validation import DANGEROUS_NON_FOOD

# JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class ToolArgumentError(ValueError):
    """Raised when tools/call arguments do not match the tool input schema."""


def search_food_rescue(pantry, use_soon=None, max_time=None):
    from src.service import search_food_rescue as search
    for value, name in ((pantry, "pantry"), (use_soon, "use_soon")):
        if value is not None and not isinstance(value, (str, list, tuple)):
            raise ToolArgumentError(f"{name} must be a list of strings.")
        if isinstance(value, (list, tuple)) and any(not isinstance(item, str) for item in value):
            raise ToolArgumentError(f"{name} must contain only strings.")
    if pantry is None:
        raise ToolArgumentError("pantry is required.")
    if max_time is not None and (isinstance(max_time, bool) or not isinstance(max_time, int) or max_time < 1):
        raise ToolArgumentError("max_time must be a positive whole number of minutes.")
    return search(pantry, use_soon, max_time)


# ---------------------------------------------------------------------------
# MCP tool definition
# ---------------------------------------------------------------------------

TOOL_DEFINITION: Dict[str, Any] = {
    "name": TOOL_NAME,
    "title": "Search Food Rescue recipes",
    "description": (
        "Rank the best recipes from a pantry of ingredients, prioritising "
        "use-soon perishables and enforcing a maximum cooking time. Refuses "
        "non-food or hazardous items and staples-only pantries. Returns JSON "
        "with up to three candidates, each listing matched and missing "
        "ingredients."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "pantry": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 25,
                "description": (
                    "Core ingredients the cook has, e.g. "
                    "['chicken breast', 'rice', 'broccoli']."
                ),
            },
            "use_soon": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Perishables to prioritise; matching ingredients weigh "
                    "1.5x instead of 1.0x."
                ),
            },
            "max_time": {
                "type": "integer",
                "minimum": 1,
                "description": "Maximum total cooking time in minutes.",
            },
        },
        "required": ["pantry"],
        "additionalProperties": False,
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["ok", "no_matches", "refused", "error"],
            },
            "reason": {"type": "string"},
            "message": {"type": "string"},
            "query": {
                "type": "object",
                "properties": {
                    "pantry": {"type": "array", "items": {"type": "string"}},
                    "use_soon": {"type": "array", "items": {"type": "string"}},
                    "max_time": {"type": ["integer", "null"]},
                },
                "required": ["pantry", "use_soon", "max_time"],
            },
            "count": {"type": "integer"},
            "recipes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "score": {"type": "number"},
                        "time_minutes": {"type": ["integer", "null"]},
                        "matched_ingredients": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "missing_ingredients": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "instructions": {"type": "string"},
                    },
                    "required": [
                        "title",
                        "score",
                        "time_minutes",
                        "matched_ingredients",
                        "missing_ingredients",
                        "instructions",
                    ],
                },
            },
        },
        "required": ["status", "recipes"],
    },
    "annotations": {
        "readOnlyHint": True,
        "openWorldHint": False,
    },
}

ALLOWED_ARGUMENTS = ("pantry", "use_soon", "max_time")


# ---------------------------------------------------------------------------
# JSON-RPC plumbing
# ---------------------------------------------------------------------------

def _result(request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(
    request_id: Any, code: int, message: str, data: Any = None
) -> Dict[str, Any]:
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def _tool_result(payload: Dict[str, Any], is_error: bool = False) -> Dict[str, Any]:
    """Wrap a payload as MCP tool content (text plus structured JSON)."""
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, ensure_ascii=False, indent=2),
            }
        ],
        "structuredContent": payload,
        "isError": is_error,
    }


def _handle_tool_call(request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name")
    if name != TOOL_NAME:
        return _error(request_id, INVALID_PARAMS, f"Unknown tool: {name!r}")

    arguments = params.get("arguments")
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        return _error(request_id, INVALID_PARAMS, "arguments must be an object")

    unexpected = sorted(set(arguments) - set(ALLOWED_ARGUMENTS))
    if unexpected:
        return _error(
            request_id,
            INVALID_PARAMS,
            "Unexpected argument(s): " + ", ".join(unexpected),
        )

    try:
        payload = search_food_rescue(
            arguments.get("pantry"),
            arguments.get("use_soon"),
            arguments.get("max_time"),
        )
    except ToolArgumentError as error:
        return _error(request_id, INVALID_PARAMS, str(error))
    except (OSError, ValueError) as error:
        payload = {
            "status": "error",
            "reason": "engine_error",
            "message": f"[ENGINE ERROR] {error}",
            "recipes": [],
        }
        return _result(request_id, _tool_result(payload, is_error=True))

    failed = payload["status"] in ("refused", "error")
    return _result(request_id, _tool_result(payload, is_error=failed))


def handle_message(message: Any) -> Optional[Dict[str, Any]]:
    """Handle one decoded JSON-RPC message; return a response or None."""
    if not isinstance(message, dict):
        return _error(None, INVALID_REQUEST, "Invalid Request")

    request_id = message.get("id")
    method = message.get("method")
    if message.get("jsonrpc") != "2.0" or not isinstance(method, str):
        return _error(request_id, INVALID_REQUEST, "Invalid Request")

    if isinstance(request_id, bool) or not isinstance(request_id, (str, int, float, type(None))):
        return _error(None, INVALID_REQUEST, "Invalid request id")

    is_notification = "id" not in message
    if is_notification:
        return None
    params = message.get("params")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return _error(request_id, INVALID_PARAMS, "params must be an object")

    if method == "initialize":
        requested = params.get("protocolVersion")
        result = {
            "protocolVersion": (
                requested if requested == DEFAULT_PROTOCOL_VERSION else DEFAULT_PROTOCOL_VERSION
            ),
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": (
                "Use search_food_rescue with the cook's pantry ingredients, "
                "optional use-soon perishables, and an optional maximum time."
            ),
        }
    elif method in ("notifications/initialized", "notifications/cancelled"):
        return None
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [TOOL_DEFINITION]}
    elif method == "tools/call":
        return _handle_tool_call(request_id, params)
    else:
        if is_notification:
            return None
        return _error(request_id, METHOD_NOT_FOUND, f"Method not found: {method}")

    if is_notification:
        return None
    return _result(request_id, result)


def _write(sink: Any, response: Dict[str, Any]) -> None:
    sink.write(json.dumps(response, ensure_ascii=False) + "\n")
    sink.flush()


def serve(input_stream: Any = None, output_stream: Any = None) -> None:
    """Read newline-delimited JSON-RPC from stdin and answer on stdout."""
    source = sys.stdin if input_stream is None else input_stream
    sink = sys.stdout if output_stream is None else output_stream

    for line in source:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            _write(sink, _error(None, PARSE_ERROR, "Parse error"))
            continue

        response = handle_message(message)
        if response is not None:
            _write(sink, response)


def _configure_streams() -> None:
    """Force UTF-8 on stdio so JSON payloads survive non-UTF-8 consoles."""
    for stream in (sys.stdin, sys.stdout):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Local self-test (`python src/mcp_server.py --test`)
# ---------------------------------------------------------------------------

def run_self_test() -> bool:
    """Exercise the tool and the JSON-RPC surface without an external client."""
    total = 0
    failures = 0

    def check(label: str, condition: bool, detail: str = "") -> None:
        nonlocal total, failures
        total += 1
        if not condition:
            failures += 1
        print(f"[{'PASS' if condition else 'FAIL'}] {label}"
              + (f" - {detail}" if detail else ""))

    print("Food Rescue MCP self-test (no client required)")
    print("-" * 48)

    success = search_food_rescue(
        ["chicken breast", "mushrooms", "butter", "flour"],
        use_soon=["mushrooms"],
        max_time=30,
    )
    check("standard pantry returns ok", success["status"] == "ok",
          success.get("message", ""))
    check(
        "top three candidates",
        len(success["recipes"]) == TOP_RESULT_LIMIT,
        f"{len(success['recipes'])} recipes",
    )
    check(
        "candidates rank best first",
        [recipe["score"] for recipe in success["recipes"]]
        == sorted((recipe["score"] for recipe in success["recipes"]), reverse=True),
    )
    check(
        "matched and missing ingredients present",
        all(
            recipe["matched_ingredients"] and isinstance(
                recipe["missing_ingredients"], list
            )
            for recipe in success["recipes"]
        ),
    )
    check(
        "max_time is a hard filter",
        all(recipe["time_minutes"] <= 30 for recipe in success["recipes"]),
    )
    check(
        "use-soon ingredient is matched",
        any(
            any("mushroom" in item.lower()
                for item in recipe["matched_ingredients"])
            for recipe in success["recipes"]
        ),
    )

    try:
        json.dumps(success)
        serialisable = True
    except (TypeError, ValueError):
        serialisable = False
    check("payload is JSON-serialisable", serialisable)

    refusal = search_food_rescue(["chicken", "bleach"])
    check(
        "bleach returns the standard refusal",
        refusal["message"]
        == "[SAFETY REFUSAL] Dangerous non-food item detected: 'bleach'. "
        "Food Rescue only processes safe, edible ingredients.",
        refusal.get("message", ""),
    )
    check("refusal returns no recipes", refusal["recipes"] == [])

    staples = search_food_rescue(["salt", "black pepper", "water"])
    check(
        "staples-only returns the standard refusal",
        staples["message"] == STAPLES_ONLY_MESSAGE,
        staples.get("message", ""),
    )

    empty = search_food_rescue([])
    check("empty pantry returns the standard refusal",
          empty["message"] == STAPLES_ONLY_MESSAGE)

    no_match = search_food_rescue(["chicken"], max_time=1)
    check("impossible time limit reports no matches",
          no_match["status"] == "no_matches", no_match.get("message", ""))

    try:
        search_food_rescue(["rice"], max_time="30")
        rejected = False
    except ToolArgumentError:
        rejected = True
    check("non-integer max_time is rejected", rejected)

    init = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-06-18"},
        }
    )
    check(
        "initialize handshake",
        bool(init) and init["result"]["serverInfo"]["name"] == SERVER_NAME,
    )

    listing = handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    check(
        "tools/list exposes search_food_rescue",
        bool(listing)
        and listing["result"]["tools"][0]["name"] == TOOL_NAME,
    )

    call = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": TOOL_NAME,
                "arguments": {"pantry": ["egg", "rice"], "max_time": 60},
            },
        }
    )
    call_payload = {}
    if call and "result" in call:
        call_payload = json.loads(call["result"]["content"][0]["text"])
    check(
        "tools/call returns JSON text and structured content",
        call_payload.get("status") == "ok"
        and call["result"]["structuredContent"] == call_payload,
    )

    bad_call = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": TOOL_NAME, "arguments": {"use_soon": ["rice"]}},
        }
    )
    check(
        "missing pantry is an invalid-params error",
        bool(bad_call) and bad_call["error"]["code"] == INVALID_PARAMS,
    )

    print("-" * 48)
    print(f"{total - failures}/{total} checks passed")
    return failures == 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if "--test" in args:
        return 0 if run_self_test() else 1

    if args:
        print(f"Unknown option(s): {' '.join(args)}", file=sys.stderr)
        print("Usage: python src/mcp_server.py [--test]", file=sys.stderr)
        return 2

    _configure_streams()
    serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())
