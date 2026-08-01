#!/usr/bin/env node
/**
 * render-mermaid.js — 全量 Mermaid 渲染验证（可选质量门）
 *
 * 用法:
 *   node render-mermaid.js <vault路径>
 *
 * 依赖: mermaid-cli（mmdc）。未安装时提示并退出(0)，由 validate-kb.js 的结构检查兜底。
 *   安装: npm install -g @mermaid-js/mermaid-cli   （首次会下载 chromium）
 *
 * 输出: 每块图表渲染为临时 .svg 验证语法；全部成功 = 通过。
 */
'use strict';
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');

const root = path.resolve(process.argv[2] || '.');
if (!fs.existsSync(root)) { console.error('❌ 路径不存在:', root); process.exit(1); }

// 探测 mmdc
function hasMmdc() {
  try {
    execSync('npx --yes @mermaid-js/mermaid-cli --version', { stdio: 'ignore', timeout: 90000 });
    return true;
  } catch { return false; }
}
if (!hasMmdc()) {
  console.log('ℹ️ mermaid-cli 未安装，跳过渲染验证（结构检查由 validate-kb.js 兜底）。');
  console.log('   安装: npm install -g @mermaid-js/mermaid-cli');
  process.exit(0);
}

// 提取 mermaid 块
const mdFiles = [];
(function walk(dir) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    if (fs.statSync(p).isDirectory()) { if (!f.startsWith('.') && f !== 'Templates') walk(p); }
    else if (f.endsWith('.md')) mdFiles.push(p);
  }
})(root);

const blocks = [];
for (const f of mdFiles) {
  const s = fs.readFileSync(f, 'utf8');
  const re = /```mermaid\n([\s\S]*?)```/g;
  let m;
  while ((m = re.exec(s)) !== null) blocks.push({ file: f, body: m[1] });
}
if (blocks.length === 0) { console.log('ℹ️ 未发现 Mermaid 图表'); process.exit(0); }

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'mmd-'));
let ok = 0; const fails = [];
for (let i = 0; i < blocks.length; i++) {
  const inFile = path.join(tmp, `m${i}.mmd`);
  fs.writeFileSync(inFile, blocks[i].body);
  try {
    execSync(`npx --yes @mermaid-js/mermaid-cli -i ${inFile} -o ${path.join(tmp, `m${i}.svg`)} --quiet`, {
      timeout: 60000, stdio: ['ignore', 'ignore', 'pipe']
    });
    ok++;
  } catch (e) {
    const err = (e.stderr || e.message || '').toString();
    const line = err.split('\n').filter(l => /error|Error|Parse/i.test(l)).slice(-2).join(' | ') || err.slice(0, 150);
    fails.push(`  ${path.relative(root, blocks[i].file)} :: ${blocks[i].body.trim().split(/[\s\n]/)[0]} :: ${line}`);
  }
}
fs.rmSync(tmp, { recursive: true, force: true });

console.log(`🔷 Mermaid: ${ok}/${blocks.length} 渲染成功`);
if (fails.length) {
  console.log('❌ 渲染失败（参考 mermaid-guide.md 修复，改后重跑）:');
  fails.forEach(f => console.log(f));
  process.exit(1);
}
console.log('✅ 全部图表可渲染');
