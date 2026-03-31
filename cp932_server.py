# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp"]
# ///
"""MCP server providing ReadCP932 and EditCP932 tools for CP932/Shift_JIS encoded files."""

import fnmatch
import os
import re
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cp932-tools")


def detect_and_decode(raw: bytes) -> tuple[str, str]:
    """Detect encoding (UTF-8 or CP932) and decode bytes to text.

    Tries UTF-8 strict first because CP932 can silently accept many UTF-8
    byte sequences, but UTF-8 strict will reject genuine CP932 bytes.
    """
    for encoding in ("utf-8", "cp932"):
        try:
            return raw.decode(encoding), encoding
        except (UnicodeDecodeError, ValueError):
            continue
    raise ValueError("File could not be decoded as UTF-8 or CP932 (possibly binary)")


def _expand_glob(pattern: str) -> list[str]:
    """Expand simple brace expressions like '*.{pas,dfm}' into multiple fnmatch patterns."""
    m = re.match(r'^(.*)\{([^}]+)\}(.*)$', pattern)
    if m:
        prefix, alternatives, suffix = m.groups()
        return [prefix + alt.strip() + suffix for alt in alternatives.split(',')]
    return [pattern]


@mcp.tool()
def ReadCP932(
    file_path: str,
    offset: int = 0,
    limit: int = 0,
) -> str:
    """Read a file that may be encoded in CP932 (Shift_JIS) or UTF-8.

    Automatically detects encoding and returns the content as UTF-8 text
    with line numbers. Use this instead of the built-in Read tool for
    files in the UniKyuyo project (.pas, .ini, .dfm, .dpr).

    Args:
        file_path: Absolute path to the file to read.
        offset: 1-based start line (default 0 means start from line 1).
        limit: Maximum number of lines to return (default 0 means all lines).
    """
    if not os.path.isabs(file_path):
        return f"Error: file_path must be absolute, got: {file_path}"
    if not os.path.exists(file_path):
        return f"Error: file not found: {file_path}"
    if not os.path.isfile(file_path):
        return f"Error: not a file: {file_path}"

    try:
        raw = open(file_path, "rb").read()
    except OSError as e:
        return f"Error reading file: {e}"

    try:
        text, encoding = detect_and_decode(raw)
    except ValueError as e:
        return f"Error: {e}"

    lines = text.splitlines()
    total = len(lines)

    # Apply offset (1-based) and limit
    start = max(0, offset - 1) if offset > 0 else 0
    if limit > 0:
        end = start + limit
    else:
        end = total
    selected = lines[start:end]

    # Format with line numbers (cat -n style)
    numbered = []
    for i, line in enumerate(selected, start=start + 1):
        numbered.append(f"{i:>6}\t{line}")

    header = f"[Encoding: {encoding}, Lines: {total}]"
    return header + "\n" + "\n".join(numbered)


@mcp.tool()
def EditCP932(
    file_path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> str:
    """Edit a file that may be encoded in CP932 (Shift_JIS) or UTF-8.

    Finds old_string in the decoded text and replaces it with new_string,
    then writes the file back in its original encoding. Use this instead of
    the built-in Edit tool for files in the UniKyuyo project (.pas, .ini, .dfm, .dpr).

    Args:
        file_path: Absolute path to the file to edit.
        old_string: The text to find (provide as UTF-8).
        new_string: The replacement text (provide as UTF-8).
        replace_all: If true, replace all occurrences. If false (default), exactly one occurrence must exist.
    """
    if not os.path.isabs(file_path):
        return f"Error: file_path must be absolute, got: {file_path}"
    if not os.path.exists(file_path):
        return f"Error: file not found: {file_path}"
    if not os.path.isfile(file_path):
        return f"Error: not a file: {file_path}"
    if old_string == new_string:
        return "Error: old_string and new_string are identical"
    if not old_string:
        return "Error: old_string must not be empty"

    try:
        raw = open(file_path, "rb").read()
    except OSError as e:
        return f"Error reading file: {e}"

    try:
        text, encoding = detect_and_decode(raw)
    except ValueError as e:
        return f"Error: {e}"

    # Detect original line ending style and normalize everything to \n for matching.
    # This prevents mismatches when the caller sends \n but the file has \r\n.
    if "\r\n" in text:
        original_eol = "\r\n"
    elif "\r" in text:
        original_eol = "\r"
    else:
        original_eol = "\n"
    text_norm = text.replace("\r\n", "\n").replace("\r", "\n")
    old_norm = old_string.replace("\r\n", "\n").replace("\r", "\n")
    new_norm = new_string.replace("\r\n", "\n").replace("\r", "\n")

    count = text_norm.count(old_norm)
    if count == 0:
        return "Error: old_string not found in file"
    if count > 1 and not replace_all:
        return (
            f"Error: old_string found {count} times. "
            f"Provide more context to make the match unique, or set replace_all=true."
        )

    new_text = text_norm.replace(old_norm, new_norm)

    # Restore original line ending style
    if original_eol != "\n":
        new_text = new_text.replace("\n", original_eol)

    # Replace common Unicode characters that have no CP932 equivalent
    if encoding == "cp932":
        _CP932_SUBSTITUTIONS = {
            "\u2014": "--",   # em-dash
            "\u2013": "-",    # en-dash
            "\u2018": "'",    # left single quote
            "\u2019": "'",    # right single quote
            "\u201c": '"',    # left double quote
            "\u201d": '"',    # right double quote
            "\u2026": "...",  # ellipsis
        }
        for char, replacement in _CP932_SUBSTITUTIONS.items():
            new_text = new_text.replace(char, replacement)

    try:
        new_raw = new_text.encode(encoding)
    except UnicodeEncodeError as e:
        return (
            f"Error: new_string contains characters not representable in {encoding}: {e}"
        )

    try:
        with open(file_path, "wb") as f:
            f.write(new_raw)
    except OSError as e:
        return f"Error writing file: {e}"

    replaced = count if replace_all else 1
    return (
        f"Successfully replaced {replaced} occurrence(s) in {file_path} "
        f"[Encoding preserved: {encoding}]"
    )


@mcp.tool()
def WriteCP932(
    file_path: str,
    content: str,
    encoding: str = "cp932",
) -> str:
    """Write a file encoded in CP932 (Shift_JIS) or UTF-8.

    Creates or overwrites a file, encoding the provided UTF-8 text content
    into the specified encoding. Use this instead of the built-in Write tool
    when creating new files for the UniKyuyo project (.pas, .ini, .dfm, .dpr).

    Args:
        file_path: Absolute path to the file to write.
        content: The text content to write (provide as UTF-8).
        encoding: Target encoding, either "cp932" (default) or "utf-8".
    """
    if not os.path.isabs(file_path):
        return f"Error: file_path must be absolute, got: {file_path}"
    if encoding not in ("cp932", "utf-8"):
        return f"Error: encoding must be 'cp932' or 'utf-8', got: {encoding}"

    parent = os.path.dirname(file_path)
    if not os.path.isdir(parent):
        return f"Error: parent directory does not exist: {parent}"

    # Replace common Unicode characters that have no CP932 equivalent
    if encoding == "cp932":
        _CP932_SUBSTITUTIONS = {
            "\u2014": "--",   # em-dash
            "\u2013": "-",    # en-dash
            "\u2018": "'",    # left single quote
            "\u2019": "'",    # right single quote
            "\u201c": '"',    # left double quote
            "\u201d": '"',    # right double quote
            "\u2026": "...",  # ellipsis
        }
        for char, replacement in _CP932_SUBSTITUTIONS.items():
            content = content.replace(char, replacement)

    try:
        encoded = content.encode(encoding)
    except UnicodeEncodeError as e:
        return f"Error: content contains characters not representable in {encoding}: {e}"

    try:
        with open(file_path, "wb") as f:
            f.write(encoded)
    except OSError as e:
        return f"Error writing file: {e}"

    lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
    return f"Successfully wrote {file_path} [{encoding}, {lines} lines, {len(encoded)} bytes]"


@mcp.tool()
def GrepCP932(
    pattern: str,
    path: str = "",
    glob_pattern: str = "",
    case_insensitive: bool = False,
    output_mode: str = "files_with_matches",
    context_lines: int = 0,
    head_limit: int = 0,
) -> str:
    """Search for a regex pattern across CP932/UTF-8 encoded files.

    Recursively walks directories, decodes each file from CP932/UTF-8,
    and searches the decoded text. Use this instead of the built-in Grep
    tool when searching for Japanese text in UniKyuyo source files.

    Args:
        pattern: Regex pattern to search for (matched against decoded UTF-8 text).
        path: Absolute path to a file or directory (default: current working directory).
        glob_pattern: Filter filenames (e.g., "*.pas", "*.{pas,dfm,dpr}").
        case_insensitive: If true, search case-insensitively.
        output_mode: "files_with_matches" (default), "content", or "count".
        context_lines: Lines of context around matches (content mode only).
        head_limit: Maximum number of results to return (0 = unlimited).
    """
    if not path:
        path = os.getcwd()
    if not os.path.isabs(path):
        return f"Error: path must be absolute, got: {path}"
    if not os.path.exists(path):
        return f"Error: path not found: {path}"

    valid_modes = ("files_with_matches", "content", "count")
    if output_mode not in valid_modes:
        return f"Error: output_mode must be one of {valid_modes}, got: {output_mode}"

    flags = re.IGNORECASE if case_insensitive else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return f"Error: invalid regex pattern: {e}"

    # Collect files
    if os.path.isfile(path):
        files = [path]
    else:
        patterns = _expand_glob(glob_pattern) if glob_pattern else []
        files = []
        for dirpath, _dirnames, filenames in os.walk(path):
            for fname in filenames:
                if patterns and not any(fnmatch.fnmatch(fname, p) for p in patterns):
                    continue
                files.append(os.path.join(dirpath, fname))
        files.sort()

    # Search
    results = []  # list of (filepath, matches, all_lines_or_none)
    files_searched = 0
    files_matched = 0
    total_matches = 0
    store_lines = output_mode == "content" and context_lines > 0

    for filepath in files:
        try:
            raw = open(filepath, "rb").read()
        except OSError:
            continue
        try:
            text, _enc = detect_and_decode(raw)
        except ValueError:
            continue

        files_searched += 1
        lines = text.splitlines()
        file_matches = []
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                file_matches.append((i, line))

        if file_matches:
            files_matched += 1
            total_matches += len(file_matches)
            results.append((filepath, file_matches, lines if store_lines else None))
            if output_mode in ("files_with_matches", "count") and head_limit > 0 and files_matched >= head_limit:
                break

    # Format output
    if output_mode == "files_with_matches":
        out_lines = [fp for fp, _m, _l in results]
        if head_limit > 0:
            out_lines = out_lines[:head_limit]
        header = f"[{len(out_lines)} files matched, {files_searched} files searched]"
        if not out_lines:
            return header
        return header + "\n" + "\n".join(out_lines)

    elif output_mode == "count":
        out_lines = []
        for fp, matches, _l in results:
            out_lines.append(f"{fp}:{len(matches)}")
        if head_limit > 0:
            out_lines = out_lines[:head_limit]
        header = f"[{total_matches} matches in {files_matched} files, {files_searched} files searched]"
        if not out_lines:
            return header
        return header + "\n" + "\n".join(out_lines)

    else:  # content
        parts = []
        result_count = 0
        for fp, matches, all_lines in results:
            if head_limit > 0 and result_count >= head_limit:
                break
            file_out = []
            if context_lines > 0 and all_lines is not None:
                match_linenos = {m[0] for m in matches}
                lines_to_show = set()
                for lineno in match_linenos:
                    for ctx in range(lineno - context_lines, lineno + context_lines + 1):
                        if 1 <= ctx <= len(all_lines):
                            lines_to_show.add(ctx)
                prev = 0
                for lineno in sorted(lines_to_show):
                    if prev and lineno > prev + 1:
                        file_out.append("--")
                    marker = ":" if lineno in match_linenos else "-"
                    file_out.append(f"{fp}{marker}{lineno}{marker}{all_lines[lineno - 1]}")
                    prev = lineno
            else:
                for lineno, line_text in matches:
                    file_out.append(f"{fp}:{lineno}:{line_text}")
            parts.append("\n".join(file_out))
            result_count += 1

        header = f"[{total_matches} matches in {files_matched} files, {files_searched} files searched]"
        if not parts:
            return header
        return header + "\n" + "\n\n".join(parts)


if __name__ == "__main__":
    mcp.run(transport="stdio")
