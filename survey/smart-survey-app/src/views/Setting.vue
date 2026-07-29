<template>
  <div class="setting-page">
    <van-nav-bar title="系统设置" />
    
    <van-cell-group inset class="mt-4">
      <van-field
        v-model="apiKey"
        label="API Key"
        placeholder="请输入大模型 API 密钥"
        type="password"
        clearable
        size="large"
      />
    </van-cell-group>

    <div class="p-4 mt-4">
      <van-button type="primary" block round @click="handleSave">
        保存配置
      </van-button>
    </div>

    <div class="p-4 mt-8">
      <van-button type="danger" plain block round @click="handleClear">
        清空所有问卷与答题数据
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { showToast, showDialog } from 'vant';
import { saveApiKey, getApiKey, clearAllData } from '../store/localDb';

const apiKey = ref('');

onMounted(() => {
  // 进页面时回显已保存的 Key
  apiKey.value = getApiKey();
});

const handleSave = () => {
  if (!apiKey.value.trim()) {
    showToast('密钥不能为空');
    return;
  }
  saveApiKey(apiKey.value.trim());
  showToast({ type: 'success', message: '保存成功' });
};

const handleClear = () => {
  showDialog({
    title: '警告',
    message: '确认清空所有历史数据吗？此操作不可逆。',
    showCancelButton: true,
  }).then(() => {
    clearAllData();
    showToast('数据已清空');
  }).catch(() => {});
};
</script>

<style scoped>
.mt-4 { margin-top: 16px; }
.mt-8 { margin-top: 32px; }
.p-4 { padding: 16px; }
</style>