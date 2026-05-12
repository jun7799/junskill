// Boss Job Hunter - 批量提取职位详情页JD
// 用法: node batch-extract-jd.mjs <urls.json> [output.json]
// urls.json 格式: [{ name: "标识", url: "https://www.zhipin.com/job_detail/xxx.html" }]
// 输出: [{ key, name, salary, detail }]

import fs from 'fs';

const CDP = 'http://localhost:3456';
const EXTRACT_JS = `(() => { const desc = document.querySelector('.job-sec-text'); const info = document.querySelector('.job-banner'); const name = info?.querySelector('h1')?.innerText?.trim() || ''; const salary = info?.querySelector('.salary')?.innerText?.trim() || ''; const detail = desc?.innerText?.trim() || ''; return JSON.stringify({name,salary,detail: detail.substring(0,2000)}); })()`;

async function main() {
  const inputFile = process.argv[2];
  const outputFile = process.argv[3] || 'jd-details.json';

  if (!inputFile) {
    console.log('[ERROR] 用法: node batch-extract-jd.mjs <urls.json> [output.json]');
    console.log('  urls.json 格式: [{ name: "标识", url: "https://..." }]');
    process.exit(1);
  }

  const jobs = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));
  console.log(`[INFO] 共 ${jobs.length} 个职位需要提取JD`);

  const results = [];

  for (const job of jobs) {
    try {
      const newRes = await (await fetch(`${CDP}/new?url=${encodeURIComponent(job.url)}`)).json();
      const targetId = newRes.targetId;

      await new Promise(r => setTimeout(r, 3000));

      const evalRes = await fetch(`${CDP}/eval?target=${targetId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: EXTRACT_JS
      });
      const evalData = await evalRes.json();
      const jd = JSON.parse(evalData.value);

      results.push({ key: job.name, ...jd });
      console.log(`[OK] ${job.name} | ${jd.salary}`);

      await fetch(`${CDP}/close?target=${targetId}`);
    } catch (e) {
      console.log(`[ERROR] ${job.name}: ${e.message}`);
    }
  }

  fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
  console.log(`\n[DONE] 已保存 ${results.length} 个JD到 ${outputFile}`);
}

main().catch(err => {
  console.error('[ERROR]', err.message);
  process.exit(1);
});
