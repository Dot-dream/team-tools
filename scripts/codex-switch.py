#!/usr/bin/env python3
"""Codex 破甲/默认 一键切换器

用法:
    python3 codex-switch.py unrestricted    # 启用破甲 (model_instructions_file -> v45)
    python3 codex-switch.py default         # 恢复默认 (移除 model_instructions_file)
    python3 codex-switch.py status          # 查看当前状态

可选: --codex-dir <路径> 指定 Codex 配置目录 (默认 C:/Users/Administrator/.codex)
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROMPT_FILENAME = "gpt-5.6-sol-unrestricted-v45.md"
PROMPT_FILENAME_HAGENT = "hagent-armor-nova.md"
KEY = "model_instructions_file"
# 匹配顶层 model_instructions_file 赋值行（不含缩进，即不在 TOML 表内）
LINE_PATTERN = re.compile(r"^model_instructions_file\s*=.*$", re.MULTILINE)
BACKUP_SUFFIX = ".switch-bak"


def find_config(codex_dir: Path) -> Path:
    return codex_dir / "config.toml"


def current_value(config_path: Path):
    if not config_path.exists():
        return None
    text = config_path.read_text(encoding="utf-8")
    m = LINE_PATTERN.search(text)
    if not m:
        return None
    return m.group(0).strip()


def write_with_backup(config_path: Path, new_text: str) -> None:
    # 覆盖式最近备份，只保留切换前一份
    shutil.copy2(config_path, config_path.with_name(config_path.name + BACKUP_SUFFIX))
    config_path.write_text(new_text, encoding="utf-8")


def cmd_unrestricted(config_path: Path) -> int:
    if not config_path.exists():
        print(f"[错误] 未找到 {config_path}", file=sys.stderr)
        return 1
    prompt_path = config_path.parent / PROMPT_FILENAME
    if not prompt_path.exists():
        print(f"[错误] 提示词文件不存在: {prompt_path}，请先部署 v45", file=sys.stderr)
        return 1
    text = config_path.read_text(encoding="utf-8")
    new_line = f'{KEY} = "./{PROMPT_FILENAME}"'
    if LINE_PATTERN.search(text):
        new_text = LINE_PATTERN.sub(new_line, text, count=1)
        changed = new_text != text
    else:
        new_text = new_line + "\n" + text
        changed = True
    if not changed:
        print("[状态] 已是破甲模式，未做修改")
        return 0
    write_with_backup(config_path, new_text)
    print(f"[OK] 已切换为破甲模式: {new_line}")
    return 0


def cmd_hagent(config_path: Path) -> int:
    if not config_path.exists():
        print(f"[错误] 未找到 {config_path}", file=sys.stderr)
        return 1
    prompt_path = config_path.parent / PROMPT_FILENAME_HAGENT
    if not prompt_path.exists():
        print(f"[错误] 提示词文件不存在: {prompt_path}", file=sys.stderr)
        return 1
    text = config_path.read_text(encoding="utf-8")
    new_line = f'{KEY} = \"./{PROMPT_FILENAME_HAGENT}\"'
    if LINE_PATTERN.search(text):
        new_text = LINE_PATTERN.sub(new_line, text, count=1)
        changed = new_text != text
    else:
        new_text = new_line + "\n" + text
        changed = True
    if not changed:
        print("[状态] 已是 H-agent ARMOR-NOVA 模式，未做修改")
        return 0
    write_with_backup(config_path, new_text)
    print(f"[OK] 已切换为 H-agent ARMOR-NOVA 模式: {new_line}")
    return 0


def cmd_default(config_path: Path) -> int:
    if not config_path.exists():
        print(f"[错误] 未找到 {config_path}", file=sys.stderr)
        return 1
    text = config_path.read_text(encoding="utf-8")
    if not LINE_PATTERN.search(text):
        print("[状态] 已是默认模式，未做修改")
        return 0
    new_text = LINE_PATTERN.sub("", text, count=1)
    # 清理可能产生的多余空行（顶部/连续空行）
    while "\n\n\n" in new_text:
        new_text = new_text.replace("\n\n\n", "\n\n")
    new_text = new_text.lstrip("\n")
    write_with_backup(config_path, new_text)
    print("[OK] 已恢复默认模式（model_instructions_file 已移除）")
    return 0


def cmd_status(config_path: Path) -> int:
    val = current_value(config_path)
    if val is None:
        print("当前模式: 默认 (无 model_instructions_file)")
    elif PROMPT_FILENAME in val:
        print(f"当前模式: 破甲 v45  ->  {val}")
    else:
        print(f"当前模式: 自定义  ->  {val}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex 破甲/默认一键切换")
    parser.add_argument("mode", choices=["unrestricted", "default", "status", "hagent"])
    parser.add_argument("--codex-dir", default=None, help="Codex 配置目录")
    args = parser.parse_args()

    if args.codex_dir:
        codex_dir = Path(args.codex_dir)
    else:
        # 候选目录: 本机 home / WSL 挂载 / 容器挂载
        candidates = [
            Path.home() / ".codex",
            Path("/mnt/c/Users/Administrator/.codex"),
            Path("/workspace/.codex"),
        ]
        codex_dir = next((c for c in candidates if c.exists()), candidates[0])

    config_path = find_config(codex_dir)
    if args.mode == "unrestricted":
        return cmd_unrestricted(config_path)
    if args.mode == "hagent":
        return cmd_hagent(config_path)
    if args.mode == "default":
        return cmd_default(config_path)
    return cmd_status(config_path)


if __name__ == "__main__":
    sys.exit(main())
