# team-tools

AI Agent 环境**配置备份 + 新机器恢复**仓库。
换公司换电脑后,`git clone` 下来按配置单手动重建整套工具链(Claude Code / Codex / opencode / cc-switch / MCP 服务)。

> ⚠️ 本仓库公开,**不含任何 API key / 明文凭证**。带 key 的配置一律以 `.tpl` 模板 + `<占位符>` 提交,恢复时手动填。

## 新机器恢复入口

1. 先看 **[docs/AI-Agent配置单.md](docs/AI-Agent配置单.md)** —— 一步步的恢复指南
2. 装基础环境:PowerShell 7、Windows Terminal、Git、Node、Python、WSL2
3. 装 Agent 工具:`@anthropic-ai/claude-code`、`@openai/codex`、`opencode-ai`、cc-switch
4. 按 **configs/** 里的模板填 key,放回各工具配置位置
5. 装 MCP 依赖(见 mcp/README.md)
6. 辅助脚本拷到用户目录(见 scripts/)

## 目录结构

```
team-tools/
├── docs/
│   └── AI-Agent配置单.md         # 新机器手动恢复配置单(核心)
├── configs/                      # 各 Agent 工具的脱敏配置模板
│   ├── claude/                   # settings.json.tpl + mcp-servers.json
│   ├── codex/                    # config.toml.tpl
│   ├── opencode/                 # opencode.json.tpl
│   ├── hermes/                   # config.yaml.tpl
│   └── cc-switch/                # provider 清单参考(无 key)
├── scripts/                      # 辅助脚本
│   ├── codex-switch.py           # Codex 破甲/默认 一键切换
│   ├── codex-aliases.sh          # codex-jb / codex-vanilla 命令
│   ├── wsl-keepalive.bat         # WSL 保活
│   ├── install_skillhub.sh       # 装 skillhub 技能包
│   └── addrline.bat
├── skills/
│   ├── project-knowledge-base/   # 项目知识库构建技能包(自建)
│   └── aixprobe/                 # 芯片探测/寄存器调试技能(自建)
├── mcp/                          # MCP 服务说明 + 自建 server
│   ├── moba-agent-bridge/        # MobaXterm agent 桥接 server 源码
│   └── examples/
├── knowledge-bases/              # 各项目知识库归档/索引
```

## 迁移什么 / 不迁什么

- **迁**:`~/.claude`、`~/.codex`、`~/.cc-switch`、`~/.config/opencode`、`~/.hermes`、`~/team-tools`、本机小脚本 —— 见配置单"要拷贝的配置"一节
- **不迁(重新申请)**:API key、`~/.ssh/`、Gemini OAuth、GitHub 凭证
- **绝不提交**:`cc-switch.db`、`auth.json`、`secrets.json`、`.env`、任何含 `sk-` 的文件(见 .gitignore)

## 维护约定

- 配置有变更就更新 `configs/` 模板和配置单
- 自建技能改动后 push 同步
- 详见各目录 README
