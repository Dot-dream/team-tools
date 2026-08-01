# team-tools

团队共享的 **Claude Code 技能包（Skills）、MCP 服务配置与项目知识库** 管理仓库。

## 目录结构

```
team-tools/
├── README.md                    # 本文
├── skills/                      # Claude Code 技能包
│   └── project-knowledge-base/  # 项目知识库构建技能包
├── mcp/                         # MCP 服务配置与脚本
│   ├── README.md
│   └── examples/                # 配置模板
└── knowledge-bases/             # 各项目知识库（归档/索引）
    └── README.md
```

## skills/project-knowledge-base

把一个代码项目一键打造成 **结构化的 Obsidian 项目知识库 + CLAUDE.md**。

流程：codegraph 扫描索引 → /init → 按子系统并行深度分析 → 搭建标准分层知识库（Mermaid 图表 / Canvas 可视化 / 术语表 / 走读教程）→ 质量审核。

### 安装

```bash
# 克隆到目标机器，然后把技能复制到 Claude Code 全局 skills 目录
git clone https://github.com/Dot-dream/team-tools.git
cp -r team-tools/skills/project-knowledge-base ~/.claude/skills/

# 验证
ls ~/.claude/skills/project-knowledge-base/
```

### 使用

在 Claude Code 中对任意项目说：

> "用 project-knowledge-base 给 <项目路径> 搭建知识库"

或手动触发：`/project-knowledge-base`

### 依赖（可选，开工时会询问安装 or 降级）

| 依赖 | 用途 | 缺失时 |
|---|---|---|
| codegraph | 代码索引/调用关系分析 | 询问后选安装或降级为纯文件解析 |
| mermaid-cli | Mermaid 图表全量渲染验证 | 询问后选安装或降级为结构校验 |
| Dataview 插件 | 知识库自动索引 | 无碍 |

### 维护约定

- 修改技能后 push 到本仓库即可同步到团队
- 技能内部结构：`SKILL.md`（主编排）+ `references/`（规范与坑）+ `templates/`（模板）+ `scripts/`（校验脚本）
- 具体说明见 `skills/project-knowledge-base/README.md`

## mcp/ 与 knowledge-bases/

- `mcp/` — MCP 服务配置/脚本，含可复用的配置模板，见其 README
- `knowledge-bases/` — 各项目知识库的归档或索引，见其 README
