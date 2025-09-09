<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElCard, ElButton, ElAlert, ElLoading, ElRow, ElCol } from 'element-plus'

const message = ref('')
const loading = ref(false)
const error = ref('')

// 创建API实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 5000,
})

const fetchHelloMessage = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await api.get('/auth/hello/')
    message.value = response.data.message
  } catch (err) {
    error.value = '获取消息失败: ' + (err.message || '未知错误')
    console.error('Error fetching hello message:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHelloMessage()
})
</script>

<template>
  <el-row justify="center">
    <el-col :span="16">
      <el-card class="hello-world-card">
        <template #header>
          <div class="card-header">
            <span>前后端通信示例</span>
          </div>
        </template>
        
        <div v-if="loading" class="loading-container">
          <el-alert
            title="加载中..."
            type="info"
            show-icon
            :closable="false"
          />
        </div>
        
        <div v-else-if="error">
          <el-alert
            :title="error"
            type="error"
            show-icon
          />
        </div>
        
        <div v-else class="message-container">
          <el-alert
            title="从后端接收到的消息:"
            type="success"
            :description="message"
            show-icon
          />
        </div>
        
        <div style="margin-top: 20px; text-align: center;">
          <el-button 
            type="primary" 
            @click="fetchHelloMessage" 
            :loading="loading"
          >
            {{ loading ? '请求中...' : '重新获取消息' }}
          </el-button>
        </div>
        
        <div class="explanation">
          <h3>前后端通信原理说明:</h3>
          <ul>
            <li>前端通过HTTP请求向后端发送请求</li>
            <li>后端接收请求，处理业务逻辑</li>
            <li>后端将处理结果以JSON格式返回给前端</li>
            <li>前端接收响应数据并更新界面</li>
          </ul>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.hello-world-card {
  margin: 2rem auto;
}

.card-header {
  font-size: 1.2rem;
  font-weight: bold;
}

.loading-container,
.message-container {
  margin: 1rem 0;
}

.explanation {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.explanation ul {
  text-align: left;
  padding-left: 1.5rem;
}

.explanation li {
  margin-bottom: 0.5rem;
}
</style>