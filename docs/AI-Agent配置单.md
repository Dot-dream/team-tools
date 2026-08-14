# AI Agent 环境配置单 · 新机器手动恢复

> 用途:换公司后在新 Windows 机器上重建工具链。**配置=拷文件,凭证=重新申请,不自动脚本。**
> 恢复顺序:装基础 → 装 Agent → 拷配置 → 填凭证 → 装 MCP → 验通。

## 1. 基础环境(winget 装)
| 软件 | 版本(旧机) | 安装命令 |
|---|---|---|
| PowerShell 7 | 7.6.4 | `winget install Microsoft.PowerShell` |
| Windows Terminal | 1.24 | `winget install Microsoft.WindowsTerminal` |
| Git | 2.43 | `winget install Git.Git` |
| GitHub CLI | 2.97 | `winget install GitHub.cli` |
| Node.js | 22.16 | `winget install OpenJS.NodeJS.LTS` |
| Python | 3.13.5 | `winget install Python.Python.3.13` |
| WSL2 | 2.7.10 / Ubuntu 26.04 | `wsl --install -d Ubuntu`,WSL 内用户名 **hermes** |

## 2. 要拷贝的配置文件(旧机 → U盘 → 新机)
| 文件 | 属于 | 说明 |
|---|---|---|
| `~/.claude/settings.json` + `settings.local.json` | Claude Code | DeepSeek 代理 + 默认 PS7 shell + 权限放行 |
| `~/.claude.json` | Claude Code | 全局状态 + 5 个 MCP 服务器定义 |
| `~/.claude/skills/aixprobe/`、`project-knowledge-base/` | Claude Code | 自建技能(其余 15 个是软链→cc-switch) |
| `~/.codex/config.toml` + `cc-switch-model-catalog.json` + `gpt-5.6-sol-unrestricted-v45.md` | Codex | provider、MCP、破甲提示词 |
| `~/.cc-switch/cc-switch.db` | cc-switch | **所有 provider 配置和 API key 都在里面** |
| `~/.cc-switch/skills/` | cc-switch | 15 个技能本体(office/PDF/obsidian/karpathy…) |
| `~/.config/opencode/opencode.json` | opencode | pwsh shell + MCP + DeepSeek/GLM provider |
| `~/.hermes/` | hermes | config.yaml + SOUL.md + memories |
| `~/team-tools/` | 团队仓库 | 直接 `git clone https://github.com/Dot-dream/team-tools.git` |
| `~/codex-switch.py`、`~/codex-aliases.sh`、`~/wsl-keepalive.bat`、`~/install_skillhub.sh`、`~/addrline.bat` | 脚本 | Codex 破甲切换/保活/装 skillhub |
| `~/moba-agent-bridge/` | MCP | MobaXterm agent 桥接 server |

**别拷**:`.cache/` `.npm/` `.nuget/` `AppData/Local` 下的缓存、日志、历史 sqlite;`~/.ssh/`(换公司重新生成)。

## 3. 凭证(全部手动重新获取)
| 凭证 | 用在哪 | 获取方式 |
|---|---|---|
| DeepSeek API key(公司账号) | Claude Code(`ANTHROPIC_AUTH_TOKEN`)/ Codex / opencode | platform.deepseek.com |
| 智谱 GLM key | opencode `glm` provider | open.bigmodel.cn |
| Xiaomi MiMo key | cc-switch 的 claude/codex provider | platform.xiaomimimo.com |
| PackyCode key | cc-switch 第三方 provider | packyapi.com |
| Claude / OpenAI 官方账号 | cc-switch `Claude Official` / `OpenAI Official` | 公司没有就跳过 |
| Google Gemini | 重新 `gemini` 登录(oauth_creds.json 别拷) | 浏览器授权 |
| GitHub | `gh auth login` | 个人 token |
| GitHub Copilot | VS Code 里登录 | 账号 |

## 4. MCP 服务(先装依赖,再填配置)
| 服务 | 安装 | 配置里怎么起 |
|---|---|---|
| codegraph | 独立 CLI 安装,每项目 `codegraph init` | `codegraph serve --mcp` |
| graphify-mcp | `pip install graphify-mcp` | `graphify-mcp --graph graphify-out/graph.json` |
| jlink-mcp | `pip install jlink-mcp` | `python -m jlink_mcp` |
| moba-agent-bridge | 拷目录即可 | `python server.py` |
| aixprobe | 公司内网硬件服务 | `http://192.168.137.217:8080/`(无硬件则跳过) |

各工具的 MCP 定义分别在:Claude Code `~/.claude.json` / Codex `config.toml` / opencode `opencode.json`,拷完文件就带上了,只补依赖。

## 5. Agent 工具逐个配
- **Claude Code**:`npm i -g @anthropic-ai/claude-code` → 拷 settings → 确认 env:`ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic`、模型映射 `deepseek-v4-flash/pro`、`defaultShell=powershell` + `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`(让 agent 跑在 PS7)。
- **cc-switch(核心)**:装好 → 导入 `cc-switch.db`(provider 全在里面,含 key)→ 语言 zh、`skillStorageLocation=cc_switch`、`skillSyncMethod=auto`。它统一管 claude/codex/gemini/opencode/hermes 的模型切换。
- **Codex**:`npm i -g @openai/codex` → 拷 config.toml 等 → 破甲切换 `source codex-aliases.sh; codex-jb / codex-vanilla`。⚠️ `node_repl` MCP 依赖 Codex 桌面端运行时路径,重装桌面端后路径要改。
- **opencode**:`npm i -g opencode-ai` → 拷 opencode.json(shell 已指到 pwsh.exe)。
- **其他**:openclaw(`npm i -g openclaw`)、skillhub(跑 `install_skillhub.sh`)、hermes(拷 `.hermes/`)、Gemini(`npm i -g @google/gemini-cli` 后重新登录)。
- **VS Code 扩展(82 个)**:核心——`anthropic.claude-code`、`openai.chatgpt`、`github.copilot(-chat)`;嵌入式——IAR/Keil、`cortex-debug`、JLink、C/C++(cpptools)、CMake、clangd。旧机 `code --list-extensions` 导清单。

## 6. 收尾
- WSL 里 `pip/python3/git` 已在;Node 用 Windows 的(`/mnt/c`)。
- `wsl-keepalive.bat` 放开机启动,保活 Ubuntu。
- 装完用一句话验通:**开 Claude Code 说"调用 codegraph 查这个项目"**,再在 opencode / Codex 各跑一次。

## 7. 坑
- `ANTHROPIC_AUTH_TOKEN` 是 **DeepSeek** 的 key,别和 Anthropic 官方混。
- cc-switch.db 是明文 key,拷的时候注意保密,别传公共仓库。
- aixprobe 是公司内网服务,新公司没这套硬件就跳过,别卡在这。
