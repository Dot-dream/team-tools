# Mcp-Service

团队共享的 Claude Code 技能包（Skills）与 MCP 相关资源仓库。

## 目录结构

```
Mcp-Service/
└── skills/
    └── project-knowledge-base/   # 项目知识库构建技能包
```

## skills/project-knowledge-base

把一个代码项目一键打造成 **结构化的 Obsidian 项目知识库 + CLAUDE.md**。

流程：codegraph 扫描索引 → /init → 按子系统并行深度分析 → 搭建标准分层知识库（Mermaid 图表 / Canvas 可视化 / 术语表 / 走读教程）→ 质量审核。

### 安装

```bash
# 克隆到目标机器，然后把技能复制到 Claude Code 全局 skills 目录
git clone https://github.com/Dot-dream/Mcp-Service.git
cp -r Mcp-Service/skills/project-knowledge-base ~/.claude/skills/

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
