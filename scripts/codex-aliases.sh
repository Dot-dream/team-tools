# ---- Codex 破甲/默认一键切换 (by Hermes) ----
# 用法: source 本文件后, 在终端使用:
#   codex-jb       启用破甲 (挂载 v45 提示词)
#   codex-vanilla  恢复默认 (移除提示词挂载)
#   codex-mode     查看当前模式
# 注意: 切换后需重启 Codex 桌面端/新会话生效

export CODEX_SWITCH_PY="${CODEX_SWITCH_PY:-/mnt/c/Users/Administrator/codex-switch.py}"

codex-jb() {
    python3 "$CODEX_SWITCH_PY" unrestricted
}

codex-hagent() {
    python3 "$CODEX_SWITCH_PY" hagent
}

codex-vanilla() {
    python3 "$CODEX_SWITCH_PY" default
}

codex-mode() {
    python3 "$CODEX_SWITCH_PY" status
}
