<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useMainStore } from '../store'
import { useRoute, useRouter } from 'vue-router'
import MessageForm from '../components/MessageForm.vue'
import MessageItem from '../components/MessageItem.vue'
import { authAPI } from '../api' // 导入正确的 API 方法

const store = useMainStore()
const route = useRoute()
const router = useRouter()

const messages = ref([])
const recipient = ref(null)
const loading = ref(true)

onMounted(async () => {
  const userId = parseInt(route.params.userId)
  if (isNaN(userId)) {
    router.push('/messages')
    return
  }

  await store.fetchConversation(userId)
  messages.value = store.currentConversation?.messages || []
  
  // 尝试从消息中获取recipient信息
  if (messages.value.length > 0) {
    const firstMessage = messages.value[0];
    if (firstMessage.sender && firstMessage.recipient) {
      recipient.value = firstMessage.sender.id === (store.user?.id || 0) 
        ? firstMessage.recipient 
        : firstMessage.sender
    }
  }
  
  // 如果还没有recipient信息，我们需要从API获取用户信息
  if (!recipient.value) {
    try {
      // 使用正确的 API 方法获取用户信息
      const response = await authAPI.userProfile(userId)
      recipient.value = {
        id: response.data.id,
        username: response.data.username,
        avatar: response.data.avatar
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
})

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
  try {
    const newMessage = await store.sendMessage(userId, content)
    messages.value.push(newMessage)
    scrollToBottom()
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
        v-for="message in messages" 
        :key="message.id"
        class="message-wrapper"
        :class="{ 'own-message': message.sender && message.sender.id === (store.user?.id || 0) }"
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

<!-- ... styles remain the same ... -->

<style scoped>
.conversation-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.conversation-header {
  display: flex;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
  margin-bottom: 15px;
}

.back-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #333;
  margin-right: 10px;
}

.recipient-info {
  display: flex;
  align-items: center;
}

.recipient-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
}

.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(45deg, #42b883, #3498db);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  margin-right: 10px;
}

.recipient-name {
  font-weight: bold;
  font-size: 1.1rem;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #999;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
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
  color: #999;
}

.message-form-container {
  padding-top: 15px;
  border-top: 1px solid #eee;
}
</style>