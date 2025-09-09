<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

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
  <div class="hello-world">
    <h2>前后端通信示例</h2>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else class="message">
      <p><strong>从后端接收到的消息:</strong></p>
      <p>{{ message }}</p>
    </div>
    
    <button @click="fetchHelloMessage" :disabled="loading">
      {{ loading ? '请求中...' : '重新获取消息' }}
    </button>
    
    <div class="explanation">
      <h3>前后端通信原理说明:</h3>
      <ul>
        <li>前端通过HTTP请求向后端发送请求</li>
        <li>后端接收请求，处理业务逻辑</li>
        <li>后端将处理结果以JSON格式返回给前端</li>
        <li>前端接收响应数据并更新界面</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.hello-world {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: Arial, sans-serif;
}

.loading, .error, .message {
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
}

.loading {
  background-color: #f0f8ff;
  text-align: center;
}

.error {
  background-color: #ffecec;
  color: #d8000c;
  border: 1px solid #ffd2d2;
}

.message {
  background-color: #f8fff8;
  border: 1px solid #d2ffd2;
}

button {
  padding: 0.5rem 1rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

button:hover:not(:disabled) {
  background-color: #359c6d;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
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