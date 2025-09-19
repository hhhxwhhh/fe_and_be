<template>
  <div class="websocket-test">
    <h3>WebSocket测试</h3>
    <div class="status">
      状态: {{ websocket.isConnected ? '已连接' : '未连接' }}
    </div>
    <div class="controls">
      <button @click="connect" :disabled="websocket.isConnected">连接</button>
      <button @click="disconnect" :disabled="!websocket.isConnected">断开</button>
      <button @click="sendMessage">发送测试消息</button>
    </div>
    <div class="messages">
      <div v-for="(msg, index) in messages" :key="index" class="message">
        {{ msg }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMainStore } from '../store'
import websocket from '../services/websocket'

const store = useMainStore()
const messages = ref([])

const connect = () => {
  store.initWebSocket()
}

const disconnect = () => {
  websocket.disconnect()
}

const sendMessage = () => {
  if (websocket.isConnected) {
    websocket.sendMessage(1, '测试消息') // 发送给用户ID为1的用户
  }
}

// 监听WebSocket事件
websocket.on('connected', () => {
  messages.value.push('WebSocket已连接')
})

websocket.on('disconnected', () => {
  messages.value.push('WebSocket已断开')
})

websocket.on('message', (data) => {
  messages.value.push(`收到消息: ${JSON.stringify(data)}`)
})

websocket.on('error', (error) => {
  messages.value.push(`WebSocket错误: ${error.message}`)
})
</script>

<style scoped>
.websocket-test {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 20px 0;
}

.status {
  margin: 10px 0;
  font-weight: bold;
}

.controls {
  margin: 10px 0;
}

.controls button {
  margin-right: 10px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #42b883;
  color: white;
  cursor: pointer;
}

.controls button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.messages {
  margin-top: 20px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  padding: 10px;
}

.message {
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}
</style>