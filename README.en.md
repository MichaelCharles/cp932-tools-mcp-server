# Shift_JIS / CP932 Tools MCP Server

[日本語](README.md)

An MCP server that provides tools for reading, writing, editing, and searching files encoded in CP932 (Shift_JIS) or UTF-8. Designed for working with Japanese-language source code while using Claude Code.

## Setup

### 1. Install uv

If you don't have `uv` installed, follow the instructions at https://docs.astral.sh/uv/getting-started/installation/

### 2. Download the server script

**Bash:**

```bash
mkdir -p ~/.claude/mcp-servers
curl -o ~/.claude/mcp-servers/cp932_server.py https://raw.githubusercontent.com/MichaelCharles/cp932-tools-mcp-server/main/cp932_server.py
```

**PowerShell:**

```powershell
New-Item -ItemType Directory -Force -Path ~/.claude/mcp-servers
Invoke-WebRequest -Uri https://raw.githubusercontent.com/MichaelCharles/cp932-tools-mcp-server/main/cp932_server.py -OutFile ~/.claude/mcp-servers/cp932_server.py
```

### 3. Register the server with Claude Code

```
claude mcp add cp932-tools -- uv run ~/.claude/mcp-servers/cp932_server.py
```

### 4. Verify

```
claude mcp list
```

You should see `cp932-tools` in the output. The next time you start Claude Code, the tools `ReadCP932`, `EditCP932`, `WriteCP932`, and `GrepCP932` will be available.

## Uninstall

```
claude mcp remove cp932-tools
```

## Tools

Provides the following tools for interacting with Japanese language files:

- **ReadCP932** — Read a file with automatic encoding detection (CP932 or UTF-8). Supports line offset and limit parameters.
- **EditCP932** — Find-and-replace text in a file, preserving the original encoding and line endings. Handles Unicode character substitution (curly quotes, em-dash, ellipsis, etc.) for characters with no CP932 equivalent.
- **WriteCP932** — Create or overwrite a file in CP932 or UTF-8 encoding.
- **GrepCP932** — Search for a regex pattern across files with directory recursion, glob filtering, and context lines.

Each tool can read, write, edit, or search files in either CP932 or UTF-8 encoding, with automatic detection and while preserving the original encoding when writing back to the files. The primary use case is for working with Japanese source code files on Windows in Shift_JIS (CP932) encoding, but it can also handle UTF-8 files for the case where the user has files with mixed encodings.
