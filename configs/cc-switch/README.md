# cc-switch 模型供应商参考

cc-switch 是一个统一的模型切换器,管理 claude / codex / gemini / opencode / hermes 的 provider。
**真实配置(含 API key)在旧机 `~/.cc-switch/cc-switch.db`,不提交到本仓库。** 下表是各应用的 provider 清单,供新机重建时对照。

## 各应用已配置的 provider

| 应用 | provider(加粗=当前启用) | 端点 |
|---|---|---|
| **claude** | Claude Official(官方)、**DeepSeek(公司专属账号)**、Xiaomi MiMo、PackyCode | https://api.deepseek.com/anthropic |
| **codex** | OpenAI Official(官方)、**DeepSeek(公司账号)**、Xiaomi MiMo、PackyCode | https://api.deepseek.com |
| **claude-desktop** | Claude Desktop Official、**DeepSeek(proxy 模式)**、PackyCode | https://api.deepseek.com/anthropic |
| **opencode** | DeepSeek、DeepSeek(公司专属)、Zhipu GLM | https://api.deepseek.com/v1 、https://open.bigmodel.cn/api/coding/paas/v4 |
| **hermes** | DeepSeek(work 公司专属)、Xiaomi MiMo、my-provider | https://api.deepseek.com 、https://api.xiaomimimo.com/v1 |
| **gemini** | Google Official | — |

## cc-switch 关键设置(settings.json)

- `language: "zh"`
- `skillStorageLocation: "cc_switch"`、`skillSyncMethod: "auto"` → 15 个技能本体存在 `~/.cc-switch/skills/`,自动同步到 `~/.claude/skills/`(软链)
- `preferredTerminal: "powershell"`
- `hermesConfigDir: "C:\Users\<user>\.hermes"`

## 迁移注意

- 新机装好 cc-switch 后,直接在旧机导出/导入 provider 配置(或手填下表 key)。
- `cc-switch.db` 含明文 API key,只在本地/U盘之间传递,绝不进 git。
- 技能清单:claude-office-pack、coding-standard-c、debugging-agent、doc-coauthoring、docx、find-skills、internal-comms、karpathy-guidelines、obsidian、pdf、pptx、recursive-self-improvement、self-improvement、skill-creator、xlsx
