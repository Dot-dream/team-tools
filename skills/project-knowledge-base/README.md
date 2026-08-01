# project-knowledge-base skill

把一个代码项目一站式打造成**结构化的 Obsidian 项目知识库 + CLAUDE.md**。

## 它能做什么

一次调用即可复现一条验证过的完整流程：

```
codegraph 索引 → /init 生成 CLAUDE.md → 按子系统并行深度分析
→ 搭建标准分层 Obsidian 知识库（Mermaid 图表 / Canvas 可视化 / 术语表 / 走读教程）
→ 图表化优化 → 质量审核（自动校验 + 可选全量渲染）
```

在不同项目上可复现约 95% 的效果。产出内容随项目而异，但流程、结构、质量门完全通用。

## 安装（团队分发）

skill 是**一个普通目录**，复制到目标机的 Claude Code skills 目录即可：

```bash
# 全局安装（本机所有项目可用）
cp -r project-knowledge-base/ ~/.claude/skills/

# 或在目标机确认
claude mcp list 2>/dev/null   # 可选：检查 codegraph
ls ~/.claude/skills/project-knowledge-base/
```

**团队分发建议**：把本目录放进团队 git 仓库（如 `team-skills/project-knowledge-base/`），成员各自 clone 后复制到 `~/.claude/skills/`。无脚本依赖、无编译、即拷即用。

## 使用

在 Claude Code 中，对任意项目说：

> "用 project-knowledge-base 给 <项目路径> 搭建知识库"

或手动触发：`/project-knowledge-base`。

## 依赖（开工时询问用户"安装 or 降级"）

| 依赖 | 用途 | 缺失时行为 |
|---|---|---|
| codegraph | 代码索引/符号/调用关系 | **P1 询问**：选"安装"→尝试安装+注册 MCP；选"降级"→纯文件解析。安装失败自动降级 |
| mermaid-cli | 图表全量渲染验证 | **P1 询问**：选"安装"→运行渲染时 npx 自动下载；选"降级"→validate-kb.js 结构检查兜底。失败自动降级 |
| Dataview 插件 | 知识库自动索引 | 自动索引页不渲染，无碍 |

> 决策原则：只问一次（P1 统一询问），记住选择贯穿会话；无论选哪条路，**安装失败都自动降级且不阻塞流程**。

## 目录结构

```
project-knowledge-base/
├── SKILL.md                  # 主编排指令（6 阶段）
├── README.md                 # 本文
├── references/
│   ├── kb-structure.md       # 目录规范与笔记规范
│   ├── mermaid-guide.md      # 4 类图表 + 已知坑（实测）
│   ├── quality-gates.md      # 验收清单
│   ├── canvas-layout.md      # 分层 Canvas 模板
│   └── claude-md-sections.md # CLAUDE.md 章节要点
├── templates/
│   ├── module-note.md        # 模块笔记模板
│   └── home-moc.md           # 首页 MOC 模板
└── scripts/
    ├── validate-kb.js        # 轻量校验（必跑，无依赖）
    └── render-mermaid.js     # 可选全量渲染验证
```

## 质量承诺

- `validate-kb.js` 无第三方依赖，Node.js 即跑即用
- Mermaid 已知坑（`DEFAULT` 保留字、mindmap 括号、引号规则等）已沉淀进 `references/mermaid-guide.md`
- 知识库验收清单见 `references/quality-gates.md`
