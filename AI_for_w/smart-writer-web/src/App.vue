<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

<style>
/* 1. 强力清除所有默认样式，防止白边 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 2. 核心：强制 HTML/BODY/APP 占满全屏且不留任何余地 */
html,
body,
#app {
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important; /* 禁止滚动条 */
  background-color: #000; /* 垫个黑色，防止彩虹加载前的白屏 */
}

/* 3. 关键点：Vue 初始化模板通常会限制 #app 的宽度，这里必须强制解除 */
#app {
  max-width: none !important;
  display: block !important;
}

/* 4. 如果还有边距，通常是 body 被设置了 display: grid 或 flex，这里强制恢复 */
body {
  display: block !important;
  place-items: initial !important;
}
</style>
