// checkEnv.js
require('dotenv').config();

const requiredEnv = [
  'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'AES_KEY'
];

console.log('🔍 开始环境变量检查...');
let allValid = true;

requiredEnv.forEach(name => {
  if (!process.env[name]) {
    console.error(`❌ 缺失环境变量: ${name}`);
    allValid = false;
  } else {
    console.log(`✅ ${name.padEnd(12)}: ${process.env[name].slice(0, 3)}...`);
  }
});

if (!allValid) {
  console.error('\n🚨 环境变量验证未通过！');
  process.exit(1);
}

console.log('\n🎉 所有环境变量检查通过！');