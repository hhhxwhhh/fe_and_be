<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useMainStore } from '../store'
import { useRoute, useRouter } from 'vue-router'
import MessageForm from '../components/MessageForm.vue'
import MessageItem from '../components/MessageItem.vue'
import { authAPI } from '../api' 

const store = useMainStore()
const route = useRoute()
const router = useRouter()

const messages = ref([])
const recipient = ref(null)
const loading = ref(true)

// 监听路由变化，确保组件正确更新
watch(() => route.params.userId, () => {
  initializeConversation()
}, { immediate: false })

onMounted(() => {
  initializeConversation()
})

const initializeConversation = async () => {
  const userId = parseInt(route.params.userId)
  if (isNaN(userId)) {
    router.push('/messages')
    return
  }

  await store.fetchConversation(userId)
  messages.value = Array.isArray(store.currentConversation?.messages) 
    ? store.currentConversation.messages 
    : []
  
  // 尝试从消息中获取recipient信息
  if (messages.value.length > 0) {
    const firstMessage = messages.value[0];
    if (firstMessage && firstMessage.sender && firstMessage.recipient) {
      recipient.value = firstMessage.sender.id === (store.user?.id || 0) 
        ? firstMessage.recipient 
        : firstMessage.sender
    }
  }
  
  // 如果还没有recipient信息，我们需要从API获取用户信息
  if (!recipient.value && userId) {
    try {
      // 使用正确的 API 方法获取用户信息
      const response = await authAPI.userProfile(userId)
      if (response && response.data) {
        recipient.value = {
          id: response.data.id,
          username: response.data.username,
          avatar: response.data.avatar
        }
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取失败，使用默认值
      recipient.value = {
        id: userId,
        username: `用户 ${userId}`,
        avatar: null
      }
    }
  }
  
  loading.value = false
  
  // 滚动到最新消息
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    const container = document.querySelector('.messages-container')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

const handleNewMessage = async (content) => {
  const userId = parseInt(route.params.userId)
  if (isNaN(userId)) return;
  
  try {
    // 发送消息并获取返回的结果
    const newMessage = await store.sendMessage(userId, content)
    
    // 更新本地消息列表（如果需要）
    if (newMessage && typeof newMessage === 'object') {
      // 检查消息是否已经存在于列表中
      const existingMessageIndex = messages.value.findIndex(msg => msg.id === newMessage.id)
      
      if (existingMessageIndex !== -1) {
        // 如果已存在，更新它
        messages.value[existingMessageIndex] = newMessage
      } else {
        // 如果不存在，添加到列表
        messages.value.push(newMessage)
      }
      
      scrollToBottom()
    }
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}



</script>
<template>
  <div class="conversation-page">
    <div class="conversation-header">
      <button @click="router.push('/messages')" class="back-button">←</button>
      <div class="recipient-info">
        <div class="recipient-avatar">
          <img 
            v-if="recipient && recipient.avatar" 
            :src="recipient.avatar" 
            :alt="recipient.username"
          >
          <div v-else class="avatar-placeholder">
            {{ recipient && recipient.username ? recipient.username.charAt(0).toUpperCase() : 'U' }}
          </div>
        </div>
        <div class="recipient-name">{{ recipient && recipient.username ? recipient.username : `用户 ${route.params.userId}` }}</div>
      </div>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else class="messages-container">
      <div 
        v-for="(message, index) in messages" 
        :key="message?.id || index"
        class="message-wrapper"
        :class="{ 'own-message': message?.sender?.id === (store.user?.id || 0) }"
      >
        <MessageItem :message="message" :current-user-id="store.user?.id || 0" />
      </div>
      
      <div v-if="messages.length === 0" class="no-messages">
        还没有消息，开始对话吧！
      </div>
    </div>
    
    <div class="message-form-container">
      <MessageForm @send="handleNewMessage" />
    </div>
  </div>
</template>
<style scoped>
.conversation-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
  border-radius: 15px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.conversation-header {
  display: flex;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  margin-bottom: 15px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 15px;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.back-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: white;
  margin-right: 15px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-button:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.recipient-info {
  display: flex;
  align-items: center;
}

.recipient-avatar img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
  border: 3px solid #fff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.avatar-placeholder {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #42b883, #3498db);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  margin-right: 15px;
  border: 3px solid #fff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  font-size: 1.2rem;
}

.recipient-name {
  font-weight: 600;
  font-size: 1.3rem;
  color: #2c3e50;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #7f8c8d;
  font-style: italic;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 10px;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  margin-bottom: 15px;
  backdrop-filter: blur(5px);
}

.message-wrapper {
  display: flex;
  margin-bottom: 15px;
}

.message-wrapper.own-message {
  justify-content: flex-end;
}

.no-messages {
  text-align: center;
  padding: 40px 20px;
  color: #95a5a6;
  font-style: italic;
  align-self: center;
}

.message-form-container {
  padding-top: 15px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 15px;
  backdrop-filter: blur(10px);
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style>