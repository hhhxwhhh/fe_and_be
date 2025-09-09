<script setup>
import { RouterView } from 'vue-router'
import { ElContainer, ElHeader, ElMain, ElMenu, ElMenuItem, ElIcon } from 'element-plus'
import { HomeFilled, UserFilled } from '@element-plus/icons-vue'
</script>

<template>
  <el-container id="app">
    <el-header>
      <el-menu
        :default-active="$route.path"
        mode="horizontal"
        router
        background-color="#42b883"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <div class="nav-brand">
          <h2>Social Network</h2>
        </div>
        <el-menu-item index="/"> 
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><UserFilled /></el-icon>
          <span>个人资料</span>
        </el-menu-item>
      </el-menu>
    </el-header>
    
    <el-main>
      <RouterView />
    </el-main>
  </el-container>
</template>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
}

.el-header {
  padding: 0;
}

.nav-brand {
  float: left;
  color: white;
  margin-right: 2rem;
  padding: 0 1rem;
  display: flex;
  align-items: center;
}

.nav-brand h2 {
  margin: 0;
}
</style>