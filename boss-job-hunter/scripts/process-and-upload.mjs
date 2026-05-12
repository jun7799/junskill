// Boss Job Hunter - 统一处理脚本
// 功能：去重 → 按地区分配城市 → 智能打分 → 写入飞书
// 用法：node process-and-upload.mjs <raw-jobs.json>

import fs from 'fs';

// ============ 配置区 ============

const FEISHU_APP_ID = 'cli_a9b8224c26381cbd';
const FEISHU_APP_SECRET = 'zbfzNvkUOV3okboAu6gXJbW6A3mncldQ';
const FEISHU_APP_TOKEN = 'N5Exbiea2awDlzsRch6cItMLnuh';
const FEISHU_TABLE_ID = 'tbltahvZwzYQIxbm';
const FEISHU_TABLE_URL = 'https://e5zve6mvyq.feishu.cn/base/N5Exbiea2awDlzsRch6cItMLnuh';

// 目标城市（只保留这些城市的职位）
const TARGET_CITIES = ['广州', '深圳'];

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

  // 方向匹配加分
  if (title.includes('agent') || title.includes('智能体')) score += 1;
  if (title.includes('ai') && title.includes('产品')) score += 0.5;
  if (tags.includes('agent') || tags.includes('大模型') || tags.includes('llm')) score += 0.5;
  if (tags.includes('b端') || tags.includes('b端产品')) score += 0.3;
  if (tags.includes('ai原生') || tags.includes('ai native')) score += 0.5;
  if (title.includes('效能') || title.includes('办公') || title.includes('提效')) score += 0.3;
  if (title.includes('coze') || title.includes('prompt') || title.includes('提示词')) score += 0.5;
  if (tags.includes('ai产品') || tags.includes('ai产品')) score += 0.3;

  // 经验匹配加分（用户10年经验，偏好5-10年）
  if (tags.includes('5-10年') || tags.includes('10年以上')) score += 0.5;

  // 薪资加分
  const num = parseInt(salary);
  if (num >= 40) score += 0.5;
  if (num >= 50) score += 0.3;

  // 不相关方向扣分
  if (title.includes('硬件') || title.includes('iot')) score -= 2;
  if (title.includes('童装') || title.includes('商品企划')) score -= 2;
  if (title.includes('实习')) score -= 2;
  if (title.includes('项目经理') && !title.includes('产品')) score -= 1;
  if (tags.includes('1-3年') && !tags.includes('5-10年') && !tags.includes('10年以上')) score -= 0.3;

  // 大厂加分
  const bigCompanies = ['腾讯', '美的', 'vivo', '顺丰', '网易', '传音', '金蝶', '平安', '富士康', '沃尔玛'];
  if (bigCompanies.some(c => (job.company || '').includes(c))) score += 0.3;

  return Math.max(1, Math.min(5, Math.round(score)));
}

// ============ 解析 tags ============

function parseTags(tags) {
  const parts = (tags || '').split('|');
  return { exp: parts[0] || '', edu: parts[1] || '', extra: parts.slice(2).join('|') };
}

// ============ 飞书操作 ============

async function getFeishuToken() {
  const res = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: FEISHU_APP_ID, app_secret: FEISHU_APP_SECRET })
  });
  const data = await res.json();
  if (data.code !== 0) throw new Error('飞书 token 获取失败: ' + data.msg);
  return data.tenant_access_token;
}

async function writeToFeishu(token, records) {
  const base = `https://open.feishu.cn/open-apis/bitable/v1/apps/${FEISHU_APP_TOKEN}/tables/${FEISHU_TABLE_ID}`;
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  for (let i = 0; i < records.length; i += 500) {
    const batch = records.slice(i, i + 500);
    const res = await fetch(`${base}/records/batch_create`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ records: batch })
    });
    const data = await res.json();
    if (data.code !== 0) {
      console.log('[ERROR] 写入失败:', data.msg);
    } else {
      console.log(`[OK] 已写入 ${batch.length} 条`);
    }
  }
}

// ============ 主流程 ============

async function main() {
  const inputFile = process.argv[2];
  if (!inputFile) {
    console.log('[ERROR] 用法: node process-and-upload.mjs <raw-jobs.json>');
    process.exit(1);
  }

  const raw = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));
  console.log(`[INFO] 读取到 ${raw.length} 条原始职位数据`);

  // 1. 去重
  const seen = new Set();
  const unique = [];
  for (const job of raw) {
    if (!seen.has(job.url)) {
      seen.add(job.url);
      unique.push(job);
    }
  }
  console.log(`[INFO] 去重后 ${unique.length} 条`);

  // 2. 分配城市 + 过滤
  const processed = [];
  for (const job of unique) {
    const city = getCity(job.area);
    if (!city || !TARGET_CITIES.includes(city)) continue;
    const score = scoreJob(job);
    const { exp, edu } = parseTags(job.tags);
    processed.push({
      title: job.title, city, salary: job.salary,
      exp, edu, company: job.company, area: job.area,
      url: job.url, score
    });
  }

  // 3. 按分数降序
  processed.sort((a, b) => b.score - a.score);

  const counts = {};
  processed.forEach(j => { counts[j.city] = (counts[j.city] || 0) + 1; });
  console.log(`[INFO] 过滤后 ${processed.length} 条: ${Object.entries(counts).map(([c, n]) => `${c} ${n}`).join(', ')}`);

  // 4. TOP 3
  console.log('\n[TOP 3 推荐]');
  processed.slice(0, 3).forEach((j, i) => {
    console.log(`  ${i + 1}. [${j.score}分] ${j.title} - ${j.company} - ${j.salary} - ${j.city}`);
  });

  // 5. 写入飞书
  console.log('\n[INFO] 正在写入飞书...');
  const token = await getFeishuToken();
  const records = processed.map(job => ({
    fields: {
      '职位名称': job.title,
      '城市': job.city,
      '薪资': job.salary,
      '经验要求': job.exp,
      '学历要求': job.edu,
      '公司': job.company,
      '地区': job.area,
      '职位链接': { link: job.url, text: '查看职位' },
      '推荐指数': job.score
    }
  }));
  await writeToFeishu(token, records);

  console.log(`\n[DONE] 完成! 共写入 ${processed.length} 条`);
  console.log(`[LINK] ${FEISHU_TABLE_URL}`);
}

main().catch(err => {
  console.error('[ERROR]', err.message);
  process.exit(1);
});
