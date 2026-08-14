import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from moba import (
    discover_logs,
    read_log,
    tail_log,
    search_log,
    get_file_info,
    monitor_start,
    monitor_check,
    monitor_follow,
    monitor_status,
    monitor_stop,
    monitor_get_buffer,
)

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

mcp = FastMCP(
    name="moba-agent-bridge",
    instructions="""
MobaXterm Agent Bridge - read-only MCP server that connects AI agents to MobaXterm
serial/SSH/shell session logs.

Workflow:
1. Open a session in MobaXterm (serial, SSH, telnet, etc.)
2. Enable terminal logging in MobaXterm (right-click -> Log to file)
3. Use log_list to discover log files
4. Use log_read or log_tail to inspect content
5. Use log_monitor_start + log_monitor_check to watch for new output
6. Use log_search to find specific patterns

The bridge handles ANSI escape codes, prompt detection, and event detection automatically.
All serial protocol complexity is handled by MobaXterm.
""",
)

DEFAULT_LINES = 200
DEFAULT_TAIL_LINES = 80


@mcp.tool()
def log_list(log_dir: str = "", pattern: str = "") -> str:
    """List available log files from MobaXterm or custom directory.

    Args:
        log_dir: Optional custom log directory path. If empty, scans default MobaXterm locations.
        pattern: Optional file pattern (e.g. '*.log', '*.txt'). Defaults to common log patterns.
    """
    ld = log_dir if log_dir else None
    pt = pattern if pattern else None
    logs = discover_logs(log_dir=ld, pattern=pt)

    if not logs:
        return ("No log files found. "
                "Make sure MobaXterm logging is enabled (right-click in terminal -> Log to file), "
                "or specify a custom log_dir.")

    import time
    lines = [f"Found {len(logs)} log file(s):", "-" * 80]
    for i, log in enumerate(logs):
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(log.modified))
        lines.append(f"  [{i}] {log.name}")
        lines.append(f"      Path:     {log.path}")
        lines.append(f"      Size:     {log.size:,} bytes")
        lines.append(f"      Modified: {mtime}")
        lines.append(f"      Encoding: {log.encoding}")
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
def log_read(
    file_path: str,
    offset: int = 0,
    limit: int = DEFAULT_LINES,
    strip_ansi: bool = True,
    encoding: str = "",
) -> str:
    """Read content from a log file with pagination support.

    Args:
        file_path: Full path to the log file.
        offset: Line number to start reading from (0-based).
        limit: Maximum number of lines to return.
        strip_ansi: Whether to strip ANSI escape codes. Default True.
        encoding: File encoding. Auto-detected if empty.
    """
    enc = encoding if encoding else None
    result = read_log(file_path=file_path, offset=offset, limit=limit,
                      strip_ansi_flag=strip_ansi, encoding=enc)

    if "error" in result:
        return f"Error: {result['error']}"

    lines = [
        f"File: {result['file']}",
        f"Lines {result['offset']}-{result['offset'] + result['lines_returned']}",
        f"Has more: {result['has_more']}",
        f"Encoding: {result['encoding']}",
    ]
    if result.get("prompt_detected"):
        lines.append(f"Prompt: {result['prompt_detected']!r}")
    if result.get("events_detected"):
        lines.append(f"Events: {result['events_detected']}")
    lines.append("-" * 60)
    lines.append(result["text"])
    return "\n".join(lines)


@mcp.tool()
def log_tail(
    file_path: str,
    lines: int = DEFAULT_TAIL_LINES,
    strip_ansi: bool = True,
    encoding: str = "",
) -> str:
    """Read the last N lines from a log file (like Unix tail command).

    Args:
        file_path: Full path to the log file.
        lines: Number of lines to read from the end.
        strip_ansi: Whether to strip ANSI escape codes.
        encoding: File encoding. Auto-detected if empty.
    """
    enc = encoding if encoding else None
    result = tail_log(file_path=file_path, lines=lines,
                      strip_ansi_flag=strip_ansi, encoding=enc)

    if "error" in result:
        return f"Error: {result['error']}"

    out = [
        f"File: {result['file']}",
        f"Total lines: {result['total_lines']:,}, showing last {result['lines_returned']}",
        f"Size: {result['size']:,} bytes",
        f"Encoding: {result['encoding']}",
    ]
    if result.get("prompt_detected"):
        out.append(f"Prompt: {result['prompt_detected']!r}")
    if result.get("events_detected"):
        out.append(f"Events: {result['events_detected']}")
    out.append("-" * 60)
    out.append(result["text"])
    return "\n".join(out)


@mcp.tool()
def log_search(
    file_path: str,
    pattern: str,
    context_lines: int = 3,
    max_matches: int = 50,
    strip_ansi: bool = True,
    encoding: str = "",
    case_sensitive: bool = False,
) -> str:
    """Search for a regex pattern in a log file with context lines.

    Args:
        file_path: Full path to the log file.
        pattern: Regular expression pattern to search for.
        context_lines: Number of context lines before/after each match.
        max_matches: Maximum number of matches to return.
        strip_ansi: Whether to strip ANSI escape codes.
        encoding: File encoding. Auto-detected if empty.
        case_sensitive: Whether matching is case-sensitive.
    """
    enc = encoding if encoding else None
    result = search_log(
        file_path=file_path, pattern=pattern, context_lines=context_lines,
        max_matches=max_matches, strip_ansi_flag=strip_ansi, encoding=enc,
        case_sensitive=case_sensitive,
    )

    if "error" in result:
        return f"Error: {result['error']}"

    out = [
        f"File: {result['file']}",
        f"Pattern: {result['pattern']}",
        f"Lines scanned: {result['total_lines_scanned']:,}",
        f"Matches found: {result['matches_found']}{' (truncated)' if result.get('truncated') else ''}",
        "-" * 60,
    ]

    for m in result["results"]:
        out.append(f"\n--- Match at line {m['match_line']} ---")
        for ctx in m["context"]:
            prefix = ">>>" if ctx["is_match"] else "   "
            out.append(f"  {prefix} L{ctx['line_number']}: {ctx['text']}")

    return "\n".join(out)


@mcp.tool()
def log_info(file_path: str, encoding: str = "") -> str:
    """Get metadata and statistics for a log file.

    Args:
        file_path: Full path to the log file.
        encoding: File encoding. Auto-detected if empty.
    """
    enc = encoding if encoding else None
    result = get_file_info(file_path=file_path, encoding=enc)

    if "error" in result:
        return f"Error: {result['error']}"

    out = [
        f"Name:     {result['name']}",
        f"Path:     {result['file']}",
        f"Size:     {result['size_human']} ({result['size']:,} bytes)",
        f"Lines:    {result['line_count']:,}",
        f"Modified: {result['modified']}",
        f"Encoding: {result['encoding']}",
        f"Dir:      {result['directory']}",
    ]
    return "\n".join(out)


@mcp.tool()
def log_monitor_start(file_path: str, monitor_id: str = "") -> str:
    """Start monitoring a log file for new content.

    Use log_monitor_check periodically, or log_follow to block until data arrives.

    Args:
        file_path: Full path to the log file to monitor.
        monitor_id: Optional ID for this monitor. Defaults to filename.
    """
    mid = monitor_id if monitor_id else None
    result = monitor_start(file_path=file_path, monitor_id=mid)

    if "error" in result:
        return f"Error: {result['error']}"

    out = [
        f"Monitor started: {result['monitor_id']}",
        f"File: {result['file']}",
        f"Starting at byte offset: {result['position']}",
        "",
        "Use log_monitor_check to read new content as it arrives.",
        "Use log_follow to block and wait for new content.",
        "Use log_monitor_stop to stop monitoring.",
        "Use log_monitor_buffer to get accumulated content.",
    ]
    return "\n".join(out)


@mcp.tool()
def log_monitor_check(monitor_id: str, strip_ansi: bool = True) -> str:
    """Check a monitored log file for new content since last check.

    Args:
        monitor_id: The monitor ID returned by log_monitor_start.
        strip_ansi: Whether to strip ANSI escape codes from new content.
    """
    result = monitor_check(monitor_id=monitor_id, strip_ansi_flag=strip_ansi)

    if "error" in result:
        return f"Error: {result['error']}"

    status = result.get("status", "unknown")
    if status == "no_new_data":
        return f"Monitor '{monitor_id}': No new content. File position: {result['position']}"

    out = [
        f"Monitor: {result['monitor_id']}",
        f"Status: {result['status']}",
        f"New lines: {result.get('new_lines', 0)}",
        f"Position: {result.get('position', 0)} / {result.get('file_size', '?')}",
        f"Buffer size: {result.get('buffer_size', 0)} lines",
    ]
    if result.get("prompt_detected"):
        out.append(f"Prompt: {result['prompt_detected']!r}")
    if result.get("events_detected"):
        out.append(f"Events: {result['events_detected']}")
    out.append("-" * 60)
    out.append(result.get("new_content", ""))
    return "\n".join(out)


@mcp.tool()
def log_follow(monitor_id: str, timeout: float = 30.0, strip_ansi: bool = True) -> str:
    """Block and wait for new content from a monitored log file.

    Returns as soon as new data is detected, or after timeout expires.

    Args:
        monitor_id: The monitor ID returned by log_monitor_start.
        timeout: Maximum seconds to wait. Default 30.
        strip_ansi: Whether to strip ANSI escape codes.
    """
    result = monitor_follow(monitor_id=monitor_id, timeout=timeout, strip_ansi_flag=strip_ansi)

    if "error" in result:
        return f"Error: {result['error']}"

    status = result.get("status", "unknown")
    content = result.get("new_content", "")

    if status == "timeout":
        return f"Monitor '{monitor_id}': Timeout after {result['elapsed']}s, no new content."

    if not content:
        return f"Monitor '{monitor_id}': No new content received."

    out = [
        f"Monitor: {monitor_id}",
        f"Status: {status}",
        "-" * 60,
        content,
    ]
    return "\n".join(out)


@mcp.tool()
def log_monitor_status(monitor_id: str = "") -> str:
    """Get status of all monitors or a specific monitor.

    Args:
        monitor_id: Optional monitor ID. If empty, returns status for all monitors.
    """
    mid = monitor_id if monitor_id else None
    result = monitor_status(monitor_id=mid)

    if "error" in result:
        return f"Error: {result['error']}"

    if "monitors" in result:
        monitors = result["monitors"]
        if not monitors:
            return "No active monitors."
        out = [f"Active monitors: {result['count']}", "-" * 50]
        for mid, info in monitors.items():
            out.append(f"  [{mid}]")
            out.append(f"    File:     {info['file']}")
            out.append(f"    Position: {info['position']}")
            out.append(f"    Buffer:   {info['buffer_size']} lines")
        return "\n".join(out)
    else:
        return "\n".join(f"{k}: {v}" for k, v in result.items())


@mcp.tool()
def log_monitor_stop(monitor_id: str) -> str:
    """Stop monitoring a log file.

    Args:
        monitor_id: The monitor ID to stop.
    """
    result = monitor_stop(monitor_id=monitor_id)
    if "error" in result:
        return f"Error: {result['error']}"
    return f"Monitor '{result['monitor_id']}' stopped."


@mcp.tool()
def log_monitor_buffer(monitor_id: str, clear: bool = False) -> str:
    """Get accumulated buffered content from a monitor without checking for new file content.

    Args:
        monitor_id: The monitor ID.
        clear: Whether to clear the buffer after reading.
    """
    result = monitor_get_buffer(monitor_id=monitor_id, clear=clear)

    if "error" in result:
        return f"Error: {result['error']}"

    out = [
        f"Monitor: {result['monitor_id']}",
        f"Buffer lines: {result['line_count']}",
        f"Cleared: {result['cleared']}",
        "-" * 60,
        result["content"],
    ]
    return "\n".join(out)


if __name__ == "__main__":
    mcp.run(transport="stdio")
