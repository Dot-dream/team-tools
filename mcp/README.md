# mcp/ — MCP 服务配置与脚本

存放团队的 **MCP（Model Context Protocol）服务**配置、脚本和说明，统一版本管理，成员 clone 即用。

## 目录约定

```
mcp/
├── README.md                # 本文
├── examples/                # 配置示例（可直接参考/复用）
│   └── mcp-config-template.json
└── <service-name>/          # 每个 MCP 服务一个子目录（按需添加）
    ├── README.md            # 该服务说明：用途、命令、如何接入
    └── ...（配置/脚本）
```

## 如何添加一个新 MCP 服务

1. 在 `mcp/` 下建子目录 `<service-name>/`，写 `README.md` 说明用途和接入命令
2. 把配置片段整理成 JSON（见 `examples/mcp-config-template.json`）
3. 团队内接入：在各自 `~/.claude.json` 的 `mcpServers` 中加入对应条目，或运行 `claude mcp add`

## MCP 配置要点（实测踩坑）

- Claude Code 的 `mcpServers` 里**每个顶级键 = 一个服务器**，必须扁平结构；不要把多个服务器包进 `mcp_servers` 之类嵌套键，否则解析器会跳过（报 `command: expected string`）
- 本地命令型服务器：`{"command": "...", "args": [...]}`
- HTTP 型服务器：`{"type": "http", "url": "..."}`

### 已知可用配置示例（codegraph + graphify + aixprobe）

见 `examples/mcp-config-template.json` —— 其中 codegraph（代码索引）与 graphify 已验证可用。

## 本机在用的 MCP 服务(新机器恢复顺序)

| 服务 | 安装 | 配置里怎么起 |
|---|---|---|
| codegraph | 独立 CLI,每项目 `codegraph init` | `codegraph serve --mcp` |
| graphify-mcp | `pip install graphify-mcp` | `graphify-mcp --graph graphify-out/graph.json` |
| jlink-mcp | `pip install jlink-mcp` | `python -m jlink_mcp` |
| moba-agent-bridge | 用本目录源码(见下) | `python moba-agent-bridge/server.py` |
| aixprobe | 公司内网硬件服务 | `http://192.168.137.217:8080/`(无硬件则跳过) |

各工具的 MCP 定义分别落在 Claude Code `~/.claude.json`、Codex `config.toml`、opencode `opencode.json`,模板见 `configs/`。

## moba-agent-bridge(自建)

MobaXterm 终端与 AI Agent 之间的桥接 server,把 MobaXterm 的会话/输出接给 Agent 用。

```bash
cd moba-agent-bridge
pip install -r requirements.txt
python server.py          # 或 python -m moba_agent_bridge
```

在 opencode / Claude Code 的 MCP 里注册为本地 stdio:`python <仓库路径>/moba-agent-bridge/server.py`。

## 常用检查命令

```bash
claude mcp list          # 查看已配置的 MCP 服务器及连接状态
claude mcp add <name>    # 交互式添加
```
