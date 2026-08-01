#!/usr/bin/env node
/**
 * validate-kb.js — 知识库轻量校验（无第三方依赖，Node.js 即可运行）
 *
 * 用法:
 *   node validate-kb.js <vault路径> [--strict]
 *
 * 检查项:
 *   1. frontmatter: 每篇 .md 以 `---` 开头
 *   2. wikilink:  所有 [[...]] 能解析到真实笔记（行内代码/含扩展名的除外）
 *   3. Canvas:    *.canvas JSON 可解析、边端点有效、file 节点路径存在
 *   4. Mermaid:   结构基本平衡（subgraph/end、sequence participant、mindmap 特殊字符）
 *
 * 退出码: 0 = 全部通过; 1 = 有问题
 */
'use strict';
const fs = require('fs');
const path = require('path');

function walk(dir, ext, out = []) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    let st;
    try { st = fs.statSync(p); } catch { continue; }
    if (st.isDirectory()) {
      if (!f.startsWith('.') && f !== 'Templates') walk(p, ext, out); // 跳过隐藏目录与模板
    } else if (f.endsWith(ext)) out.push(p);
  }
  return out;
}

const root = path.resolve(process.argv[2] || '.');
const strict = process.argv.includes('--strict');
if (!fs.existsSync(root)) { console.error('❌ 路径不存在:', root); process.exit(1); }

const mdFiles = walk(root, '.md');
const canvasFiles = walk(root, '.canvas');
const names = new Set(mdFiles.map(f => path.basename(f, '.md')));
const problems = [];
const warns = [];

/* ---------- 1. frontmatter ---------- */
const noFm = mdFiles.filter(f => !fs.readFileSync(f, 'utf8').trimStart().startsWith('---'));
if (noFm.length) warns.push(`frontmatter: ${noFm.length} 篇缺（${noFm.slice(0, 3).map(f => path.relative(root, f)).join(', ')}...）`);

/* ---------- 2. wikilink ---------- */
for (const f of mdFiles) {
  const s = fs.readFileSync(f, 'utf8');
  const re = /\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g;
  let m;
  while ((m = re.exec(s)) !== null) {
    const link = m[1].trim();
    if (link.includes('.')) continue;                 // 跳过含扩展名/路径
    const before = s.slice(Math.max(0, m.index - 1), m.index);
    if (before === '`') continue;                     // 行内代码示例
    const base = link.split('/').pop();
    if (!names.has(base)) problems.push(`未解析 wikilink: ${path.relative(root, f)} → [[${m[1]}]]`);
  }
}

/* ---------- 3. Canvas ---------- */
for (const cf of canvasFiles) {
  try {
    const c = JSON.parse(fs.readFileSync(cf, 'utf8'));
    const ids = new Set(c.nodes.map(n => n.id));
    const badEdge = c.edges.filter(e => !ids.has(e.fromNode) || !ids.has(e.toNode));
    if (badEdge.length) problems.push(`${path.basename(cf)}: ${badEdge.length} 条边端点无效`);
    for (const n of c.nodes) {
      if (n.type === 'file' && !fs.existsSync(path.join(path.dirname(cf), n.file)))
        problems.push(`${path.basename(cf)}: 节点文件不存在 ${n.file}`);
      if (strict && n.type === 'file' && !n.color)
        warns.push(`${path.basename(cf)}: 节点 ${n.id} 未着色（建议分层颜色）`);
    }
  } catch (e) { problems.push(`${path.basename(cf)}: Canvas JSON 无效 (${e.message})`); }
}

/* ---------- 4. Mermaid 结构 ---------- */
const mdre = /```mermaid\n([\s\S]*?)```/g;
for (const f of mdFiles) {
  const s = fs.readFileSync(f, 'utf8');
  let m, bi = 0;
  while ((m = mdre.exec(s)) !== null) {
    const body = m[1].trim();
    const kind = body.split(/[\s\n]/)[0];
    const where = `${path.relative(root, f)}#${bi++}`;
    if (/^(flowchart|graph)/.test(kind)) {
      const subs = (body.match(/subgraph/g) || []).length;
      const ends = (body.match(/^\s*end\s*$/gm) || []).length;
      if (subs !== ends) problems.push(`Mermaid[${where}]: subgraph(${subs}) != end(${ends})`);
    }
    if (/^stateDiagram/.test(kind)) {
      // DEFAULT/Default 是保留字
      if (/-->\s*(DEFAULT|Default)\b/.test(body)) problems.push(`Mermaid[${where}]: 状态名用保留字 DEFAULT/Default`);
    }
    if (/^sequenceDiagram/.test(kind)) {
      if (!/^\s*participant\s/m.test(body)) problems.push(`Mermaid[${where}]: sequenceDiagram 缺 participant`);
    }
    if (/^mindmap/.test(kind)) {
      if (/[^"]\(\S*\/\S*\)/.test(body) || /\s\(\S+\/\S+\)/.test(body))
        warns.push(`Mermaid[${where}]: mindmap 可能含 空格+括号 陷阱`);
    }
  }
}

/* ---------- 汇总 ---------- */
console.log(`📚 笔记: ${mdFiles.length} | Canvas: ${canvasFiles.length} | 可解析 wikilink 目标: ${names.size}`);
if (warns.length) { console.log('⚠️ 警告:'); warns.forEach(w => console.log('   ', w)); }
if (problems.length) {
  console.log(`❌ 发现 ${problems.length} 个问题:`);
  [...new Set(problems)].forEach(p => console.log('   ', p));
  process.exit(1);
}
console.log('✅ 校验通过');
