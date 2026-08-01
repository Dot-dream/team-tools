# 质量审核（Quality Gates）

> 知识库交付前必须过的检查。分三层：**自动轻量校验**（必跑）→ **可选全量渲染** → **人工内容审核**。

## 一、自动轻量校验（必跑，无依赖）

```bash
node ~/.claude/skills/project-knowledge-base/scripts/validate-kb.js <vault路径>
```

检查项与判定：

| 检查项 | 通过标准 | 失败处理 |
|---|---|---|
| frontmatter | 每篇 .md 以 `---` 开头 | 补 frontmatter |
| wikilink 解析 | 所有 `[[...]]` 能解析到真实文件（行内代码里的除外） | 建缺失笔记或改链接 |
| Canvas JSON | `架构关系.canvas` 可解析、边端点/节点文件有效 | 修复 JSON |
| Mermaid 结构 | `subgraph`==`end`、`sequenceDiagram` 有 participant、mindmap 无 `空格+(` 组合 | 按 mermaid-guide 修复 |

## 二、可选全量渲染（有 mermaid-cli 时）

```bash
node ~/.claude/skills/project-knowledge-base/scripts/render-mermaid.js <vault路径>
```

- 首次运行 `npx @mermaid-js/mermaid-cli` 会下载 chromium（几百 MB）
- **目标：所有图表 100% 渲染通过**。参考经验：33 个图全通过是达标线
- 失败必须修复后重跑，不能跳过（这是"图表化优化"质量的核心保证）
- 若本机无 chromium 且无法安装：明确告知用户"未做渲染验证"，并用 validate-kb.js 的结构检查兜底

## 三、人工内容审核（机器 + 人）

### 3.1 事实准确性抽查
- 关键数字/宏/地址与源码核对（抽查 3~5 处：如服务数量、内存地址、宏状态）
- 图表里的函数名与 `代码符号索引` 一致
- 不要有"编造的"构建命令/开发任务（除非来自 README/工程文件）

### 3.2 完整性检查（对照 checklist）
- [ ] 首页 MOC：mindmap 导航 + 知识地图 + 关键宏表
- [ ] 架构全景（mindmap + 分层图 + 调用关系图）
- [ ] 每个核心子系统一篇笔记（职责表/接口/配置/调用关系）
- [ ] 调用关系总览（初始化/诊断/收发/跳转等关键调用链）
- [ ] Canvas 分层可视化
- [ ] 术语表
- [ ] 端到端走读教程（时序图，主题自适应项目最有代表性的数据链路）
- [ ] 代码符号索引
- [ ] CLAUDE.md（构建命令 + 架构 + 关键宏 + 注意事项）

### 3.3 已知问题标注
- 分析 agent 发现的坑、`#if 0` 死代码、未接线逻辑、遗留函数缺失等
- **必须**写进对应笔记的「⚠️ 已知问题」或 CLAUDE.md 的「Development Notes」
- 这是知识库"值钱"的地方——接手人不用重新踩坑

## 四、交付汇报模板

向用户汇报时给出：
1. 笔记数 / Mermaid 图表数 / 渲染通过率
2. wikilink 解析率（目标 100%）
3. 质量门通过项清单
4. 已知问题清单（来自分析阶段）
