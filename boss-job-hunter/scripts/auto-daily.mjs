// Boss Job Hunter - 每日自动采集脚本
// 用于 Windows 计划任务，每天早上自动采集+处理+提取JD
// 用法: node auto-daily.mjs [关键词]
// 默认关键词: AI产品经理
// 前提: Chrome已打开且登录Boss, CDP Proxy正在运行

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CDP = 'http://localhost:3456';
const KEYWORD = process.argv[2] || 'AI产品经理';
const CITIES = ['广州', '深圳'];
const OUTPUT_DIR = 'D:/求职';

const EXTRACT_JOBS_JS = `(() => {
  const cards = document.querySelectorAll('.job-card-box');
  const results = [];
  for(const card of cards) {
    const title = card.querySelector('.job-name')?.innerText?.trim() || '';
    const salary = card.querySelector('.job-salary')?.innerText?.trim() || '';
    const tags = Array.from(card.querySelectorAll('.tag-list li')).map(li => li.innerText.trim()).join('|');
    const company = card.querySelector('.company-name a, [class*=company-name] a')?.innerText?.trim()
                 || card.querySelector('.boss-name')?.innerText?.trim() || '';
    const url = card.querySelector('.job-name')?.href || '';
    let area = '';
    const areaEls = card.querySelectorAll('[class*=area], [class*=location]');
    for(const el of areaEls) { if(el.innerText.match(/[一-\\u9fff]+/)) { area = el.innerText.trim(); break; } }
    results.push({title, salary, tags, company, url, area});
  }
  return JSON.stringify(results);
})()`;

const EXTRACT_JD_JS = `(() => {
  const desc = document.querySelector('.job-sec-text');
  const info = document.querySelector('.job-banner');
  const name = info?.querySelector('h1')?.innerText?.trim() || '';
  const salary = info?.querySelector('.salary')?.innerText?.trim() || '';
  const detail = desc?.innerText?.trim() || '';
  return JSON.stringify({name, salary, detail: detail.substring(0, 2000)});
})()`;

async function cdpFetch(url, opts = {}) {
  const res = await fetch(url, { ...opts, signal: AbortSignal.timeout(opts.timeout || 15000) });
  return res.json();
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function log(tag, msg) {
  const ts = new Date().toLocaleTimeString('zh-CN');
  console.log(`[${ts}] [${tag}] ${msg}`);
}

async function main() {
  console.log('========================================');
  console.log(`  Boss Job Hunter 每日自动采集`);
  console.log(`  关键词: ${KEYWORD} | 城市: ${CITIES.join('+')}`);
  console.log(`  时间: ${new Date().toLocaleString('zh-CN')}`);
  console.log('========================================\n');

  // ===== 1. 检查CDP连接 =====
  log('CHECK', '检查CDP Proxy...');
  try {
    await cdpFetch(`${CDP}/version`);
    log('CHECK', 'CDP Proxy 已连接');
  } catch {
    log('ERROR', 'CDP Proxy 未运行，退出');
    process.exit(1);
  }

  // ===== 2. 打开搜索页 =====
  const encodedKW = encodeURIComponent(KEYWORD);
  log('BROWSE', `打开搜索页: ${KEYWORD}`);
  const { targetId } = await cdpFetch(`${CDP}/new?url=https://www.zhipin.com/web/geek/job?query=${encodedKW}&ka=header-jobs`);
  await sleep(3000);

  // ===== 3. 逐个城市采集 =====
  const allJobs = [];

  for (const city of CITIES) {
    log('BROWSE', `切换到 ${city} 标签...`);
    try {
      const clickResult = await cdpFetch(`${CDP}/eval?target=${targetId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: `(() => { const spans = document.querySelectorAll('span.text-content'); for(const s of spans) { if(s.innerText.includes('${city}')) { s.click(); return 'clicked: ' + s.innerText; } } return 'not found'; })()`
      });
      if (clickResult.value?.includes('not found')) {
        log('WARN', `${city} 标签未找到，跳过`);
        continue;
      }
      log('BROWSE', `已切换到 ${city}`);
    } catch (e) {
      log('ERROR', `切换 ${city} 失败: ${e.message}`);
      continue;
    }

    await sleep(3000);

    // 滚动加载
    log('BROWSE', `${city} 滚动加载中...`);
    for (let i = 0; i < 5; i++) {
      await cdpFetch(`${CDP}/scroll?target=${targetId}&y=800&direction=down`, { timeout: 5000 }).catch(() => {});
      await sleep(1000);
    }

    // 提取数据
    log('EXTRACT', `提取 ${city} 职位数据...`);
    try {
      const extractResult = await cdpFetch(`${CDP}/eval?target=${targetId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: EXTRACT_JOBS_JS
      });
      const cityJobs = JSON.parse(extractResult.value);
      allJobs.push(...cityJobs);
      log('EXTRACT', `${city} 提取到 ${cityJobs.length} 条`);
    } catch (e) {
      log('ERROR', `${city} 提取失败: ${e.message}`);
    }
  }

  // 关闭搜索页
  await cdpFetch(`${CDP}/close?target=${targetId}`);
  log('BROWSE', `搜索页已关闭，共采集 ${allJobs.length} 条`);

  if (allJobs.length === 0) {
    log('ERROR', '未采集到任何职位，退出');
    process.exit(1);
  }

  // ===== 4. 保存原始数据 =====
  const rawFile = path.join(OUTPUT_DIR, 'raw-jobs.json');
  fs.writeFileSync(rawFile, JSON.stringify(allJobs, null, 2));
  log('SAVE', `原始数据已保存: ${rawFile}`);

  // ===== 5. 去重+打分+存储 =====
  log('PROCESS', '运行 process-and-save...');
  try {
    execSync(`node "${path.join(__dirname, 'process-and-save.mjs')}" "${rawFile}"`, {
      stdio: 'inherit',
      cwd: __dirname
    });
  } catch {
    log('ERROR', 'process-and-save 失败');
    process.exit(1);
  }

  // 清理原始数据
  fs.unlinkSync(rawFile);

  // ===== 6. 筛选高分职位 + 批量提取JD =====
  log('PROCESS', '从 jobs.md 筛选4-5分职位...');
  const jobsMd = path.resolve('D:/求职/boss-jobs/jobs.md');
  if (!fs.existsSync(jobsMd)) {
    log('ERROR', 'jobs.md 不存在');
    process.exit(1);
  }

  const md = fs.readFileSync(jobsMd, 'utf-8');
  const highScoreJobs = [];
  for (const line of md.split('\n')) {
    if (line.startsWith('| ') && !line.includes('---') && !line.includes('职位名称')) {
      const cols = line.split('|').map(c => c.trim()).filter(Boolean);
      if (cols.length >= 6) {
        const score = parseInt(cols[4]) || 0;
        const url = cols[5] || '';
        if (score >= 4 && url.startsWith('http')) {
          highScoreJobs.push({
            name: `${cols[1] || ''}-${cols[0] || ''}`,
            url,
            score,
            title: cols[0],
            company: cols[1],
            salary: cols[2],
            city: cols[3]
          });
        }
      }
    }
  }

  if (highScoreJobs.length === 0) {
    log('WARN', '没有4分以上职位，跳过JD提取');
    log('DONE', '采集完成（仅数据存储）');
    return;
  }

  log('EXTRACT', `开始提取 ${highScoreJobs.length} 个高分职位JD...`);
  const jdResults = [];

  for (let i = 0; i < highScoreJobs.length; i++) {
    const job = highScoreJobs[i];
    try {
      const { targetId: tid } = await cdpFetch(`${CDP}/new?url=${encodeURIComponent(job.url)}`);
      await sleep(3000);

      const jdRes = await cdpFetch(`${CDP}/eval?target=${tid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: EXTRACT_JD_JS
      });
      const jd = JSON.parse(jdRes.value);

      jdResults.push({
        key: job.name,
        ...jd,
        score: job.score,
        city: job.city,
        searchSalary: job.salary,
        url: job.url
      });
      log('EXTRACT', `  [${i + 1}/${highScoreJobs.length}] ${jd.name} | 详情薪资:${jd.salary}`);

      await cdpFetch(`${CDP}/close?target=${tid}`);
    } catch (e) {
      log('ERROR', `  [${i + 1}/${highScoreJobs.length}] ${job.name}: ${e.message}`);
    }
  }

  // ===== 7. 保存JD详情 =====
  const jdFile = path.join(OUTPUT_DIR, 'jd-details.json');
  fs.writeFileSync(jdFile, JSON.stringify(jdResults, null, 2));

  // ===== 8. 输出摘要 =====
  console.log('\n========================================');
  console.log(`  采集完成! ${new Date().toLocaleString('zh-CN')}`);
  console.log('========================================');
  console.log(`  原始职位: ${allJobs.length} 条`);
  console.log(`  高分JD: ${jdResults.length} 条`);
  console.log(`  数据文件: ${jdFile}`);
  console.log('  待办: 打开Claude Code运行推荐报告');
  console.log('========================================\n');

  // TOP 5 快览
  jdResults.sort((a, b) => b.score - a.score).slice(0, 5).forEach((j, i) => {
    console.log(`  ${i + 1}. [${j.score}分] ${j.name} | 详情薪资:${j.salary} | ${j.city}`);
  });
}

main().catch(err => {
  console.error('\n[FATAL]', err.message);
  process.exit(1);
});
