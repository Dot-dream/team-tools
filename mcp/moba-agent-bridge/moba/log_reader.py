import os
import re
import time
import glob as glob_mod
import logging
from typing import Optional
from dataclasses import dataclass, field
from collections import deque

from ansiparse import strip_ansi
from detector.prompt import get_detector
from detector.event import EventDetector

logger = logging.getLogger(__name__)

MOBA_LOG_DIRS = [
    os.path.expandvars(r"%USERPROFILE%\Documents\MobaXterm"),
    os.path.expandvars(r"%APPDATA%\MobaXterm"),
    os.path.expandvars(r"%LOCALAPPDATA%\MobaXterm"),
]

LOG_PATTERNS = ["*.log", "*.txt", "*.term"]
SKIP_FILENAMES = {"MobaXterm.log", "MobaXterm.ini"}

MAX_BUFFER_LINES = 10_000
MAX_LINE_SCAN = 100_000


@dataclass
class LogFileInfo:
    path: str
    name: str
    size: int
    modified: float
    encoding: str = "utf-8"
    description: str = ""


@dataclass
class MonitorState:
    file_path: str
    position: int
    last_check: float = 0.0
    file_inode: int = 0
    buffer: list[str] = field(default_factory=list)


_encoding_cache: dict[str, str] = {}


def _detect_encoding(file_path: str) -> str:
    if file_path in _encoding_cache:
        return _encoding_cache[file_path]

    encodings = ["utf-8", "gbk", "gb2312", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                f.read(1024)
            _encoding_cache[file_path] = enc
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue

    _encoding_cache[file_path] = "latin-1"
    return "latin-1"


def _count_lines(file_path: str, encoding: str) -> int:
    count = 0
    try:
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            for _ in f:
                count += 1
                if count >= MAX_LINE_SCAN:
                    return MAX_LINE_SCAN
    except Exception:
        pass
    return count


# ── discovery ────────────────────────────────────────────


def discover_logs(log_dir: Optional[str] = None, pattern: Optional[str] = None) -> list[LogFileInfo]:
    results: list[LogFileInfo] = []
    seen: set[str] = set()

    dirs = [log_dir] if log_dir else MOBA_LOG_DIRS
    patterns = [pattern] if pattern else LOG_PATTERNS

    for d in dirs:
        if not d or not os.path.isdir(d):
            continue
        try:
            for pat in patterns:
                full_pat = os.path.join(d, "**", pat)
                for fpath in glob_mod.glob(full_pat, recursive=True):
                    fpath = os.path.abspath(fpath)
                    if fpath in seen:
                        continue
                    name = os.path.basename(fpath)
                    if name in SKIP_FILENAMES:
                        continue
                    seen.add(fpath)
                    try:
                        st = os.stat(fpath)
                        enc = _detect_encoding(fpath)
                        results.append(LogFileInfo(
                            path=fpath,
                            name=name,
                            size=st.st_size,
                            modified=st.st_mtime,
                            encoding=enc,
                        ))
                    except OSError:
                        continue
        except Exception as e:
            logger.debug("Error scanning %s: %s", d, e)

    results.sort(key=lambda x: x.modified, reverse=True)
    return results


# ── read / tail / search ─────────────────────────────────


def read_log(
    file_path: str,
    offset: int = 0,
    limit: int = 500,
    strip_ansi_flag: bool = True,
    encoding: Optional[str] = None,
) -> dict:
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    enc = encoding or _detect_encoding(file_path)
    st = os.stat(file_path)

    try:
        with open(file_path, "r", encoding=enc, errors="replace") as f:
            lines = _read_lines_from_offset(f, offset, limit)
    except Exception as e:
        return {"error": str(e)}

    text = "\n".join(lines)
    if strip_ansi_flag:
        text = strip_ansi(text)

    pd = get_detector()
    prompt = pd.find_last_prompt(text)
    ed = EventDetector()
    events = ed.detect_names(text)

    return {
        "file": file_path,
        "size": st.st_size,
        "modified": st.st_mtime,
        "offset": offset,
        "lines_returned": len(lines),
        "has_more": len(lines) == limit,
        "text": text,
        "encoding": enc,
        "prompt_detected": prompt,
        "events_detected": events,
    }


def tail_log(
    file_path: str,
    lines: int = 50,
    strip_ansi_flag: bool = True,
    encoding: Optional[str] = None,
) -> dict:
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    enc = encoding or _detect_encoding(file_path)
    st = os.stat(file_path)

    try:
        with open(file_path, "r", encoding=enc, errors="replace") as f:
            all_lines = f.readlines()
    except Exception as e:
        return {"error": str(e)}

    tail_lines = [l.rstrip("\n\r") for l in all_lines[-lines:]]
    text = "\n".join(tail_lines)
    if strip_ansi_flag:
        text = strip_ansi(text)

    pd = get_detector()
    prompt = pd.find_last_prompt(text)
    ed = EventDetector()
    events = ed.detect_names(text)

    return {
        "file": file_path,
        "size": st.st_size,
        "modified": st.st_mtime,
        "total_lines": len(all_lines),
        "lines_returned": len(tail_lines),
        "text": text,
        "encoding": enc,
        "prompt_detected": prompt,
        "events_detected": events,
    }


def search_log(
    file_path: str,
    pattern: str,
    context_lines: int = 3,
    max_matches: int = 50,
    strip_ansi_flag: bool = True,
    encoding: Optional[str] = None,
    case_sensitive: bool = False,
) -> dict:
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    enc = encoding or _detect_encoding(file_path)
    flags = 0 if case_sensitive else re.IGNORECASE

    try:
        pat = re.compile(pattern, flags)
    except re.error as e:
        return {"error": f"Invalid regex pattern: {e}"}

    matches: list[dict] = []
    ring = deque(maxlen=context_lines * 2 + 1)  # sliding context window
    line_num = 0

    try:
        with open(file_path, "r", encoding=enc, errors="replace") as f:
            for raw_line in f:
                line_num += 1
                clean = raw_line.rstrip("\n\r")
                if strip_ansi_flag:
                    clean = strip_ansi(clean)
                ring.append({"line_number": line_num, "text": clean})

                if pat.search(raw_line):
                    ctx = list(ring)
                    for item in ctx:
                        item["is_match"] = item["line_number"] == line_num
                    matches.append({
                        "match_line": line_num,
                        "match_text": raw_line.rstrip("\n\r"),
                        "context": ctx,
                    })
                    if len(matches) >= max_matches:
                        break
    except Exception as e:
        return {"error": str(e)}

    return {
        "file": file_path,
        "pattern": pattern,
        "total_lines_scanned": line_num,
        "matches_found": len(matches),
        "truncated": len(matches) >= max_matches,
        "results": matches,
    }


# ── info ─────────────────────────────────────────────────


def get_file_info(file_path: str, encoding: Optional[str] = None) -> dict:
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    enc = encoding or _detect_encoding(file_path)
    st = os.stat(file_path)
    lc = _count_lines(file_path, enc)

    return {
        "file": file_path,
        "name": os.path.basename(file_path),
        "size": st.st_size,
        "size_human": _human_size(st.st_size),
        "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
        "line_count": lc,
        "encoding": enc,
        "directory": os.path.dirname(file_path),
    }


def _human_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _read_lines_from_offset(f, offset: int, limit: int) -> list[str]:
    lines: list[str] = []
    skipped = 0
    for raw in f:
        if skipped < offset:
            skipped += 1
            continue
        lines.append(raw.rstrip("\n\r"))
        if len(lines) >= limit:
            break
    return lines


# ── monitor ──────────────────────────────────────────────


_monitors: dict[str, MonitorState] = {}
MONITOR_POLL_INTERVAL = 0.3  # seconds between polls in follow mode


def monitor_start(file_path: str, monitor_id: Optional[str] = None) -> dict:
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}

    mid = monitor_id or os.path.basename(file_path)
    st = os.stat(file_path)
    _monitors[mid] = MonitorState(
        file_path=file_path,
        position=st.st_size,
        last_check=time.time(),
        file_inode=st.st_ino if hasattr(st, "st_ino") else st.st_size,
    )
    return {
        "monitor_id": mid,
        "file": file_path,
        "position": st.st_size,
        "status": "started",
    }


def monitor_check(monitor_id: str, strip_ansi_flag: bool = True) -> dict:
    if monitor_id not in _monitors:
        return {"error": f"Monitor not found: {monitor_id}"}

    state = _monitors[monitor_id]
    if not os.path.isfile(state.file_path):
        state.buffer.append("[WARN] Log file has been deleted or moved")
        return {
            "monitor_id": monitor_id,
            "file": state.file_path,
            "new_content": "\n".join(state.buffer),
            "new_lines": len(state.buffer),
            "position": state.position,
            "status": "file_missing",
        }

    st = os.stat(state.file_path)
    current_inode = st.st_ino if hasattr(st, "st_ino") else st.st_size

    if current_inode != state.file_inode:
        logger.info("File %s rotated, resetting position", state.file_path)
        state.position = 0
        state.file_inode = current_inode

    if st.st_size < state.position:
        state.position = 0

    if st.st_size <= state.position:
        return {
            "monitor_id": monitor_id,
            "file": state.file_path,
            "new_content": "",
            "new_lines": 0,
            "position": state.position,
            "status": "no_new_data",
        }

    enc = _detect_encoding(state.file_path)
    try:
        with open(state.file_path, "r", encoding=enc, errors="replace") as f:
            f.seek(state.position)
            raw = f.read()
            state.position = f.tell()
    except Exception as e:
        return {"error": str(e)}

    text = strip_ansi(raw) if strip_ansi_flag else raw
    lines = [l for l in text.split("\n")]

    _append_to_buffer(state, lines)
    state.last_check = time.time()

    pd = get_detector()
    prompt = pd.find_last_prompt(text)
    ed = EventDetector()
    events = ed.detect_names(text)

    return {
        "monitor_id": monitor_id,
        "file": state.file_path,
        "new_content": text,
        "new_lines": len(lines),
        "position": state.position,
        "file_size": st.st_size,
        "status": "data_read",
        "prompt_detected": prompt,
        "events_detected": events,
        "buffer_size": len(state.buffer),
    }


def monitor_follow(monitor_id: str, timeout: float = 30.0, strip_ansi_flag: bool = True) -> dict:
    if monitor_id not in _monitors:
        return {"error": f"Monitor not found: {monitor_id}"}

    deadline = time.time() + timeout
    accumulated: list[str] = []

    while time.time() < deadline:
        result = monitor_check(monitor_id, strip_ansi_flag=strip_ansi_flag)
        if "error" in result:
            return result

        if result.get("status") == "data_read":
            content = result.get("new_content", "")
            if content:
                accumulated.append(content)
        elif result.get("status") == "file_missing":
            result["follow_accumulated"] = "\n".join(accumulated)
            return result

        time.sleep(MONITOR_POLL_INTERVAL)

    return {
        "monitor_id": monitor_id,
        "status": "timeout" if not accumulated else "data_read",
        "new_content": "\n".join(accumulated),
        "timeout_reached": not bool(accumulated),
        "elapsed": timeout,
    }


def monitor_status(monitor_id: Optional[str] = None) -> dict:
    if monitor_id:
        if monitor_id not in _monitors:
            return {"error": f"Monitor not found: {monitor_id}"}
        s = _monitors[monitor_id]
        return {
            "monitor_id": monitor_id,
            "file": s.file_path,
            "position": s.position,
            "buffer_size": len(s.buffer),
            "last_check": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s.last_check)),
        }
    else:
        all_status = {}
        for mid, s in _monitors.items():
            all_status[mid] = {
                "file": s.file_path,
                "position": s.position,
                "buffer_size": len(s.buffer),
            }
        return {"monitors": all_status, "count": len(_monitors)}


def monitor_stop(monitor_id: str) -> dict:
    if monitor_id not in _monitors:
        return {"error": f"Monitor not found: {monitor_id}"}
    del _monitors[monitor_id]
    return {"monitor_id": monitor_id, "status": "stopped"}


def monitor_get_buffer(monitor_id: str, clear: bool = False) -> dict:
    if monitor_id not in _monitors:
        return {"error": f"Monitor not found: {monitor_id}"}

    s = _monitors[monitor_id]
    content = "\n".join(s.buffer)
    count = len(s.buffer)
    if clear:
        s.buffer.clear()
    return {
        "monitor_id": monitor_id,
        "content": content,
        "line_count": count,
        "cleared": clear,
    }


def _append_to_buffer(state: MonitorState, lines: list[str]) -> None:
    state.buffer.extend(lines)
    if len(state.buffer) > MAX_BUFFER_LINES:
        state.buffer = state.buffer[-MAX_BUFFER_LINES // 2:]
