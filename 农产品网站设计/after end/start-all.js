const { spawn } = require('child_process');
const path = require('path');

const services = [
  { name: '主服务(注册)',     file: 'server.js',       port: 3000 },
  { name: '密码重置',         file: 'forget.js',       port: 3001 },
  { name: '登录服务',         file: 'mian.js',         port: 3002 },
  { name: '管理员认证',       file: 'rootfirst.js',    port: 3005 },
  { name: '商品管理',         file: 'endback.js',      port: 3006 },
  { name: '商品查询',         file: 'yutaoyangmei.js', port: 3008 },
  { name: '商品详情',         file: 'detail.js',       port: 3010 },
  { name: '订单服务',         file: 'Myproduct.js',    port: 3011 },
];

const children = [];

console.log('╔══════════════════════════════╗');
console.log('║   农产品供需平台 - 后端启动   ║');
console.log('╚══════════════════════════════╝');
console.log('');

services.forEach(({ name, file, port }) => {
  const child = spawn('node', [file], {
    cwd: __dirname,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  let started = false;

  child.stdout.on('data', (data) => {
    const msg = data.toString().trim();
    if (msg) {
      if (!started) {
        console.log(`✅ ${name} 已启动 → http://localhost:${port}`);
        started = true;
      }
    }
  });

  child.stderr.on('data', (data) => {
    console.error(`[${name}] ${data.toString().trim()}`);
  });

  child.on('error', () => {
    console.error(`❌ ${name} 启动失败`);
  });

  child.on('exit', (code) => {
    if (code !== 0 && !started) {
      console.error(`❌ ${name} 异常退出 (code: ${code})`);
    }
  });

  children.push({ name, child });
});

// 优雅关闭
process.on('SIGINT', () => {
  console.log('\n🛑 正在关闭所有服务...');
  children.forEach(({ name, child }) => {
    child.kill('SIGINT');
  });
  setTimeout(() => process.exit(0), 1000);
});

process.on('SIGTERM', () => {
  children.forEach(({ name, child }) => child.kill());
  process.exit(0);
});
