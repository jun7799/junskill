// Boss Job Hunter 前置依赖检查
// 检测 CDP Proxy 和 Chrome 连接状态

const CDP_PROXY = 'http://localhost:3456';

async function check() {
  console.log('[CHECK] Boss Job Hunter 前置检查\n');

  // 1. 检查 CDP Proxy
  console.log('[1/2] 检查 CDP Proxy...');
  try {
    const res = await fetch(`${CDP_PROXY}/health`, { signal: AbortSignal.timeout(5000) });
    const data = await res.json();
    if (data.connected) {
      console.log(`  [OK] CDP Proxy 已连接, Chrome 端口: ${data.chromePort}`);
    } else {
      console.log('  [FAIL] CDP Proxy 运行中但 Chrome 未连接');
      console.log('  -> 请确认 Chrome 已启动并开启远程调试端口');
      process.exit(1);
    }
  } catch {
    console.log('  [FAIL] CDP Proxy 未运行 (localhost:3456 无法连接)');
    console.log('  -> 请先启动 web-access skill 的 CDP Proxy');
    process.exit(1);
  }

  // 2. 检查 web-access skill
  console.log('[2/2] 检查 web-access skill...');
  try {
    const fs = await import('fs');
    const skillPath = new URL('../../web-access/SKILL.md', import.meta.url);
    fs.accessSync(skillPath);
    console.log('  [OK] web-access skill 已安装');
  } catch {
    console.log('  [FAIL] web-access skill 未找到');
    console.log('  -> 请先安装 web-access skill');
    process.exit(1);
  }

  console.log('\n[OK] 所有依赖检查通过，可以开始搜索职位');
}

check();
