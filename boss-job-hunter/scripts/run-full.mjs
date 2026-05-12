// Boss Job Hunter - 一键编排脚本
// 串联：process-and-save → 筛选高分 → batch-extract-jd → 输出结果
// 用法: node run-full.mjs <raw-jobs.json>
// 输出: jd-details.json（4-5分职位的完整JD）+ 终端打印TOP 5

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCRIPTS_DIR = __dirname;
const CDP = 'http://localhost:3456';
const JD_EXTRACT_JS = `(() => { const desc = document.querySelector('.job-sec-text'); const info = document.querySelector('.job-banner'); const name = info?.querySelector('h1')?.innerText?.trim() || ''; const salary = info?.querySelector('.salary')?.innerText?.trim() || ''; const detail = desc?.innerText?.trim() || ''; return JSON.stringify({name,salary,detail: detail.substring(0,2000)}); })()`;

async function main() {
  const inputFile = process.argv[2];
  if (!inputFile) {
    console.log('[ERROR] 用法: node run-full.mjs <raw-jobs.json>');
    process.exit(1);
  }

  const absInput = path.resolve(inputFile);
  if (!fs.existsSync(absInput)) {
    console.log(`[ERROR] 文件不存在: ${absInput}`);
    process.exit(1);
  }

  console.log('========================================');
  console.log('  Boss Job Hunter - 全自动流水线');
  console.log('========================================\n');

  // ========== Stage 1: 处理原始数据 ==========
  console.log('[Stage 1/3] 处理原始数据（去重+打分+存储）...');
  try {
    execSync(`node "${path.join(SCRIPTS_DIR, 'process-and-save.mjs')}" "${absInput}"`, {
      stdio: 'inherit',
      cwd: SCRIPTS_DIR
    });
  } catch (e) {
    console.log('[ERROR] Stage 1 失败，流水线终止');
    process.exit(1);
  }

  // ========== Stage 2: 筛选高分职位 ==========
  console.log('\n[Stage 2/3] 筛选4-5分职位，准备批量提取JD...');
  const jobsFile = path.resolve('D:/求职/boss-jobs/jobs.md');
  if (!fs.existsSync(jobsFile)) {
    console.log('[ERROR] jobs.md 不存在');
    process.exit(1);
  }

  // 从 Markdown 解析职位数据
  const md = fs.readFileSync(jobsFile, 'utf-8');
  const jobs = [];
  const lines = md.split('\n');
  for (const line of lines) {
    if (line.startsWith('| ') && !line.includes('---') && !line.includes('职位名称')) {
      const cols = line.split('|').map(c => c.trim()).filter(Boolean);
      if (cols.length >= 7) {
        const title = cols[0] || '';
        const company = cols[1] || '';
        const salary = cols[2] || '';
        const city = cols[3] || '';
        const score = parseInt(cols[4]) || 0;
        const url = cols[5] || '';
        const status = cols[6] || '新发现';

        // 跳过分隔行和表头
        if (title === '职位名称' || title.match(/^-+$/)) continue;

        if (score >= 4 && url.startsWith('http')) {
          jobs.push({ name: `${company}-${title}`, url, score, title, company, salary, city });
        }
      }
    }
  }

  if (jobs.length === 0) {
    console.log('[WARN] 没有找到4分以上的职位，跳过JD提取');
    console.log('\n[DONE] 流水线完成（仅数据存储）');
    return;
  }

  console.log(`[INFO] 找到 ${jobs.length} 个高分职位需要提取JD`);

  // ========== Stage 3: 批量提取JD ==========
  console.log(`\n[Stage 3/3] 批量提取 ${jobs.length} 个职位详情页JD...`);
  const results = [];

  for (let i = 0; i < jobs.length; i++) {
    const job = jobs[i];
    try {
      // 打开tab
      const newRes = await (await fetch(`${CDP}/new?url=${encodeURIComponent(job.url)}`)).json();
      const targetId = newRes.targetId;

      // 等待页面加载
      await new Promise(r => setTimeout(r, 3000));

      // 提取JD
      const evalRes = await fetch(`${CDP}/eval?target=${targetId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: JD_EXTRACT_JS
      });
      const evalData = await evalRes.json();
      const jd = JSON.parse(evalData.value);

      results.push({
        key: job.name,
        ...jd,
        score: job.score,
        city: job.city,
        searchSalary: job.salary,
        url: job.url
      });
      console.log(`  [${i + 1}/${jobs.length}] ${jd.name} | ${jd.salary} (搜索页: ${job.salary})`);

      // 关闭tab
      await fetch(`${CDP}/close?target=${targetId}`);
    } catch (e) {
      console.log(`  [${i + 1}/${jobs.length}] [ERROR] ${job.name}: ${e.message}`);
    }
  }

  // ========== 输出结果 ==========
  const outputFile = path.resolve('D:/求职/jd-details.json');
  fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));

  // TOP 5 摘要
  console.log('\n========================================');
  console.log(`  JD提取完成！共 ${results.length} 个职位`);
  console.log('========================================');
  console.log('\n[TOP 5 推荐]');
  results
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .forEach((j, i) => {
      console.log(`  ${i + 1}. [${j.score}分] ${j.name} - ${j.company || ''} - 详情页薪资:${j.salary} - ${j.city}`);
    });

  console.log(`\n[OUTPUT] JD详情: ${outputFile}`);
  console.log('[OUTPUT] 职位表: D:/求职/boss-jobs/jobs.md');
  console.log('\n[NEXT] 请 Claude 读取 jd-details.json + 简历，生成推荐报告');
}

main().catch(err => {
  console.error('[ERROR]', err.message);
  process.exit(1);
});
