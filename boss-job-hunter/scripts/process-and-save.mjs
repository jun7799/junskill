// Boss Job Hunter - Markdown 本地化处理脚本 v3
// 功能：去重 → 按地区分配城市 → 智能打分 → Markdown 存储 → 生成报告
// 用法：
//   node process-and-save.mjs <raw-jobs.json>   处理新抓取数据
//   node process-and-save.mjs --summary          查看总职位表摘要
//   node process-and-save.mjs --set-status <url片段> <状态>  更新状态

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const DATA_DIR = 'D:/求职/boss-jobs';
const JOBS_FILE = path.join(DATA_DIR, 'jobs.md');
const REPORTS_DIR = path.join(DATA_DIR, 'reports');

const TARGET_CITIES = ['广州', '深圳'];
const VALID_STATUSES = ['新发现', '已打招呼', '已投递', '面试中', '已拒绝', '不合适'];

// Boss直聘薪资字体修正：私用区字符 E030-E039 → 正常数字 0-9
function fixSalary(s) {
  if (!s) return s;
  return Array.from(s).map(c => {
    const code = c.charCodeAt(0);
    if (code >= 0xE030 && code <= 0xE039) return String(code - 0xE030);
    return c;
  }).join('');
}

// ============ 工具函数 ============

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  if (!fs.existsSync(REPORTS_DIR)) fs.mkdirSync(REPORTS_DIR, { recursive: true });
}

function jobIdFromUrl(url) {
  const match = url.match(/job_detail\/([^.]+)/);
  return match ? match[1] : url.replace(/[^a-zA-Z0-9]/g, '').substring(0, 32);
}

function parseSalaryNum(s) {
  if (!s) return 0;
  const m = s.match(/(\d+)/);
  return m ? Number(m[1]) : 0;
}

function esc(s) {
  return (s || '').replace(/\|/g, '\\|').replace(/\n/g, ' ');
}

function unesc(s) {
  return (s || '').replace(/\\\|/g, '|').trim();
}

// ============ MD 读写 ============

// 从 jobs.md 解析职位数组
function loadJobsMD() {
  if (!fs.existsSync(JOBS_FILE)) return [];

  const content = fs.readFileSync(JOBS_FILE, 'utf-8');
  const lines = content.split('\n');
  const jobs = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed.startsWith('|') || trimmed.includes('---')) continue;

    const cells = trimmed.split('|').map(c => c.trim());
    // 去掉首尾空元素（因为 | 开头和结尾会产生空串）
    if (cells[0] === '') cells.shift();
    if (cells[cells.length - 1] === '') cells.pop();

    // 表头行跳过
    if (cells[1] === '分数') continue;
    if (cells.length < 8) continue;

    const score = parseInt(cells[1]) || 3;

    // 从 Markdown 链接 [title](url) 中提取标题和URL
    const titleCell = unesc(cells[2]);
    const linkMatch = titleCell.match(/\[([^\]]+)\]\(([^)]+)\)/);
    const title = linkMatch ? linkMatch[1] : titleCell;
    const url = linkMatch ? linkMatch[2] : '';

    if (!url && !title) continue;

    jobs.push({
      id: jobIdFromUrl(url),
      url,
      title,
      salary: unesc(cells[3]),
      company: unesc(cells[4]),
      city: unesc(cells[5]),
      exp: unesc(cells[6]),
      status: unesc(cells[7]),
      notes: cells.length > 8 ? unesc(cells[8]) : '',
      score,
    });
  }

  return jobs;
}

// 将职位数组写入 jobs.md
function saveJobsMD(jobs) {
  ensureDataDir();

  const counts = {};
  const statusCounts = {};
  jobs.forEach(j => {
    counts[j.city] = (counts[j.city] || 0) + 1;
    statusCounts[j.status] = (statusCounts[j.status] || 0) + 1;
  });

  const today = new Date().toISOString().split('T')[0];

  let md = `# Boss直聘职位总表\n\n`;
  md += `> 更新于 ${today} | 共 ${jobs.length} 个`;
  md += Object.entries(counts).map(([c, n]) => ` | ${c} ${n}`).join('');
  if (Object.keys(statusCounts).length > 0) {
    md += `\n> 状态: ${Object.entries(statusCounts).map(([s, n]) => `${s}${n}`).join(' ')}`;
  }
  md += `\n\n`;
  md += `| # | 分数 | 职位 | 薪资 | 公司 | 城市 | 经验 | 状态 | 备注 |\n`;
  md += `|---|------|------|------|------|------|------|------|------|\n`;

  jobs.forEach((j, i) => {
    const titleLink = j.url ? `[${esc(j.title)}](${j.url})` : esc(j.title);
    md += `| ${i + 1} | ${j.score} | ${titleLink} | ${esc(j.salary)} | ${esc(j.company)} | ${j.city} | ${j.exp} | ${j.status} | ${esc(j.notes)} |\n`;
  });

  fs.writeFileSync(JOBS_FILE, md, 'utf-8');
  return JOBS_FILE;
}

// ============ 城市分配 ============

function getCity(area) {
  if (!area) return null;
  if (area.includes('深圳')) return '深圳';
  if (area.includes('广州')) return '广州';
  if (area.includes('佛山') || area.includes('东莞') || area.includes('惠州')) return '广州';
  return null;
}

// ============ 智能打分 ============

function scoreJob(job) {
  const title = job.title.toLowerCase();
  const tags = (job.tags || '').toLowerCase();
  const salary = job.salary || '';
  let score = 3;

  if (title.includes('agent') || title.includes('智能体')) score += 1;
  if (title.includes('ai') && title.includes('产品')) score += 0.5;
  if (tags.includes('agent') || tags.includes('大模型') || tags.includes('llm')) score += 0.5;
  if (tags.includes('b端') || tags.includes('b端产品')) score += 0.3;
  if (tags.includes('ai原生') || tags.includes('ai native')) score += 0.5;
  if (title.includes('效能') || title.includes('办公') || title.includes('提效')) score += 0.3;
  if (title.includes('coze') || title.includes('prompt') || title.includes('提示词')) score += 0.5;
  if (tags.includes('ai产品') || tags.includes('ai产品')) score += 0.3;

  if (tags.includes('5-10年') || tags.includes('10年以上')) score += 0.5;

  const num = parseInt(fixSalary(salary));
  if (num >= 40) score += 0.5;
  if (num >= 50) score += 0.3;

  if (title.includes('硬件') || title.includes('iot')) score -= 2;
  if (title.includes('童装') || title.includes('商品企划')) score -= 2;
  if (title.includes('实习')) score -= 2;
  if (title.includes('项目经理') && !title.includes('产品')) score -= 1;
  if (tags.includes('1-3年') && !tags.includes('5-10年') && !tags.includes('10年以上')) score -= 0.3;

  const bigCompanies = ['腾讯', '美的', 'vivo', '顺丰', '网易', '传音', '金蝶', '平安', '富士康', '沃尔玛', 'anker', 'shein'];
  if (bigCompanies.some(c => (job.company || '').toLowerCase().includes(c.toLowerCase()))) score += 0.3;

  return Math.max(1, Math.min(5, Math.round(score)));
}

// ============ 解析 tags ============

function parseTags(tags) {
  const parts = (tags || '').split('|');
  return { exp: parts[0] || '', edu: parts[1] || '', extra: parts.slice(2).join('|') };
}

// ============ 增量合并 ============

function mergeJobs(rawJobs, existingJobs) {
  const existingMap = new Map();
  existingJobs.forEach(j => existingMap.set(j.url, j));

  const newJobs = [];
  const updatedJobs = [];

  for (const raw of rawJobs) {
    const city = getCity(raw.area);
    if (!city || !TARGET_CITIES.includes(city)) continue;

    const score = scoreJob(raw);
    const { exp } = parseTags(raw.tags);
    const fixedSalary = fixSalary(raw.salary);

    if (existingMap.has(raw.url)) {
      const existing = existingMap.get(raw.url);
      const changed = existing.salary !== fixedSalary || existing.title !== raw.title;

      // 更新职位信息，保留用户手动修改的状态和备注
      existing.title = raw.title;
      existing.salary = fixedSalary;
      existing.company = raw.company;
      existing.city = city;
      existing.exp = exp;
      existing.score = score;

      if (changed) updatedJobs.push(existing);
    } else {
      const newJob = {
        id: jobIdFromUrl(raw.url),
        url: raw.url,
        title: raw.title,
        salary: fixedSalary,
        company: raw.company,
        city,
        exp,
        score,
        status: '新发现',
        notes: '',
      };
      existingJobs.push(newJob);
      newJobs.push(newJob);
    }
  }

  // 按分数降序，同分按薪资降序
  existingJobs.sort((a, b) => b.score - a.score || parseSalaryNum(b.salary) - parseSalaryNum(a.salary));

  return { newJobs, updatedJobs, allJobs: existingJobs };
}

// ============ 报告生成 ============

function generateReport(newJobs, updatedJobs, allJobs) {
  const today = new Date().toISOString().split('T')[0];
  const reportPath = path.join(REPORTS_DIR, `${today}.md`);

  const counts = {};
  allJobs.forEach(j => { counts[j.city] = (counts[j.city] || 0) + 1; });

  let md = `# 职位搜索报告 - ${today}\n\n`;
  md += `## 本次新增 ${newJobs.length} 个，更新 ${updatedJobs.length} 个\n\n`;

  if (newJobs.length > 0) {
    md += `## 新增职位\n\n`;
    md += `| # | 分数 | 职位 | 公司 | 薪资 | 城市 | 经验 |\n`;
    md += `|---|------|------|------|------|------|------|\n`;
    newJobs.forEach((j, i) => {
      md += `| ${i + 1} | ${j.score} | ${j.title} | ${j.company} | ${j.salary} | ${j.city} | ${j.exp} |\n`;
    });
    md += '\n';
  }

  if (updatedJobs.length > 0) {
    md += `## 更新职位（信息有变化）\n\n`;
    md += `| # | 分数 | 职位 | 公司 | 薪资 | 城市 |\n`;
    md += `|---|------|------|------|------|------|\n`;
    updatedJobs.forEach((j, i) => {
      md += `| ${i + 1} | ${j.score} | ${j.title} | ${j.company} | ${j.salary} | ${j.city} |\n`;
    });
    md += '\n';
  }

  const topNew = newJobs.filter(j => j.score >= 4).slice(0, 5);
  if (topNew.length > 0) {
    md += `## TOP 推荐\n\n`;
    topNew.forEach((j, i) => {
      md += `${i + 1}. **[${j.score}分] ${j.title}** - ${j.company} - ${j.salary} - ${j.city}\n`;
      md += `   - ${j.url}\n`;
    });
    md += '\n';
  }

  md += `## 统计\n\n`;
  md += `- 总职位数：${allJobs.length}\n`;
  md += `- ${Object.entries(counts).map(([c, n]) => `${c} ${n}`).join(' | ')}\n`;

  ensureDataDir();
  fs.writeFileSync(reportPath, md, 'utf-8');
  return reportPath;
}

// ============ 子命令 ============

function cmdSummary() {
  const jobs = loadJobsMD();
  if (jobs.length === 0) {
    console.log('[INFO] 职位表为空，先运行: node process-and-save.mjs <raw-jobs.json>');
    return;
  }

  const counts = {};
  const scoreCounts = {};
  const statusCounts = {};
  jobs.forEach(j => {
    counts[j.city] = (counts[j.city] || 0) + 1;
    scoreCounts[j.score] = (scoreCounts[j.score] || 0) + 1;
    statusCounts[j.status] = (statusCounts[j.status] || 0) + 1;
  });

  console.log(`\n[职位总览] ${JOBS_FILE}`);
  console.log(`  总数: ${jobs.length}`);
  console.log(`  城市: ${Object.entries(counts).map(([c, n]) => `${c} ${n}`).join(', ')}`);
  console.log(`  分数: ${Object.entries(scoreCounts).sort((a, b) => b[0] - a[0]).map(([s, n]) => `${s}分 ${n}`).join(', ')}`);
  console.log(`  状态: ${Object.entries(statusCounts).map(([s, n]) => `${s} ${n}`).join(', ')}`);

  console.log(`\n[TOP 5 推荐]`);
  jobs.slice(0, 5).forEach((j, i) => {
    console.log(`  ${i + 1}. [${j.score}分] ${j.title} - ${j.company} - ${j.salary} - ${j.city} [${j.status}]`);
  });
}

function cmdSetStatus(fragment, status) {
  if (!VALID_STATUSES.includes(status)) {
    console.log(`[ERROR] 无效状态: ${status}`);
    console.log(`  有效值: ${VALID_STATUSES.join(', ')}`);
    process.exit(1);
  }

  const jobs = loadJobsMD();
  const matches = jobs.filter(j =>
    j.url.includes(fragment) || j.id.includes(fragment) || j.title.includes(fragment) || j.company.includes(fragment)
  );

  if (matches.length === 0) {
    console.log(`[ERROR] 未找到匹配 "${fragment}" 的职位`);
    process.exit(1);
  }

  matches.forEach(j => { j.status = status; });
  saveJobsMD(jobs);

  console.log(`[OK] 已更新 ${matches.length} 个职位状态为 "${status}"`);
  matches.forEach(j => console.log(`  - ${j.title} @ ${j.company} (${j.salary})`));
  console.log(`\n  文件: ${JOBS_FILE}`);
}

// ============ 主流程 ============

function main() {
  ensureDataDir();
  const args = process.argv.slice(2);

  // 子命令路由
  if (args[0] === '--summary') { cmdSummary(); return; }
  if (args[0] === '--set-status') {
    if (args.length < 3) { console.log('[ERROR] 用法: --set-status <url片段或职位名> <状态>'); process.exit(1); }
    cmdSetStatus(args[1], args[2]);
    return;
  }

  // 主流程：处理新抓取数据
  const inputFile = args[0];
  if (!inputFile) {
    console.log('[ERROR] 用法: node process-and-save.mjs <raw-jobs.json>');
    console.log('       或: node process-and-save.mjs --summary / --set-status');
    process.exit(1);
  }

  const raw = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));
  console.log(`[INFO] 读取到 ${raw.length} 条原始职位数据`);

  const existingJobs = loadJobsMD();
  console.log(`[INFO] 当前总职位表: ${existingJobs.length} 条`);

  const { newJobs, updatedJobs, allJobs } = mergeJobs(raw, existingJobs);

  const counts = {};
  newJobs.forEach(j => { counts[j.city] = (counts[j.city] || 0) + 1; });
  console.log(`[INFO] 本次新增 ${newJobs.length} 条，更新 ${updatedJobs.length} 条`);
  if (newJobs.length > 0) console.log(`  新增分布: ${Object.entries(counts).map(([c, n]) => `${c} ${n}`).join(', ')}`);

  // TOP 3
  console.log('\n[TOP 3 新增推荐]');
  newJobs.slice(0, 3).forEach((j, i) => {
    console.log(`  ${i + 1}. [${j.score}分] ${j.title} - ${j.company} - ${j.salary} - ${j.city}`);
  });

  // 保存 MD
  const savedPath = saveJobsMD(allJobs);
  console.log(`\n[MD] 已保存到 ${savedPath}`);

  // 生成报告
  const reportPath = generateReport(newJobs, updatedJobs, allJobs);
  console.log(`[REPORT] 报告已保存: ${reportPath}`);

  // 总览
  const allCounts = {};
  allJobs.forEach(j => { allCounts[j.city] = (allCounts[j.city] || 0) + 1; });
  console.log(`\n[DONE] 总职位数: ${allJobs.length} (${Object.entries(allCounts).map(([c, n]) => `${c} ${n}`).join(', ')})`);
}

main();
