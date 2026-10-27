#!/usr/bin/env python3
"""setup.py -- Check MCP memory server prerequisites for persistent agent memory.

Usage:
    python integrations/mcp-memory/setup.py

The memory integration requires an MCP server that provides:
  - remember: store decisions, deliverables, context
  - recall: search memories by keyword or semantic similarity
  - rollback: revert to a previous state
  - search: find specific memories across sessions
"""
from __future__ import annotations

import json
from pathlib import Path

HOME_MCP_CONFIG_PATHS = [
    Path.home() / ".config/claude/mcp.json",
    Path.home() / ".cursor/mcp.json",
]


def find_mcp_config() -> Path | None:
    for path in HOME_MCP_CONFIG_PATHS:
        if path.is_file():
            return path
    local = Path(".mcp.json")
    if local.is_file():
        return local
    return None


def main() -> None:
    print("MCP Memory Integration Setup")
    print("==============================")
    print()
    print("This integration requires an MCP-compatible memory server.")
    print()
    print("Your MCP memory server must provide these tools:")
    print("  - remember: store decisions, deliverables, and context")
    print("  - recall: search memories by keyword or semantic similarity")
    print("  - rollback: revert to a previous state")
    print("  - search: find specific memories across sessions")
    print()

    found = find_mcp_config()
    if found is not None:
        print(f"Found MCP config at {found}")
    else:
        print("No MCP client config found.")
        print()
        print("Add your memory server to your MCP client config:")
        print()
        print(
            json.dumps(
                {
                    "mcpServers": {
                        "memory": {"command": "your-mcp-memory-server", "args": []}
                    }
                },
                indent=2,
            )
        )

    print()
    print("Next steps:")
    print("  1. Install an MCP memory server (pip install or npm install)")
    print("  2. Add it to your MCP client config")
    print("  3. Add a Memory Integration section to any agent prompt")
    print("     (see integrations/mcp-memory/README.md for the pattern)")


if __name__ == "__main__":
    main()
