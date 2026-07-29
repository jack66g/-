<template>
  <div class="app-container">
    <router-view /> <van-tabbar route fixed placeholder>
      <van-tabbar-item replace to="/teacher" icon="home-o">控制台</van-tabbar-item>
      <van-tabbar-item replace to="/student" icon="edit">学生填答</van-tabbar-item>
      <van-tabbar-item replace to="/report" icon="chart-trending-o">分析报告</van-tabbar-item>
      <van-tabbar-item replace to="/setting" icon="setting-o">设置</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style>
body { background-color: #f7f8fa; margin: 0; }
</style>