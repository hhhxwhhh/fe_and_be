<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useMainStore } from '../store'
import { useRoute, useRouter } from 'vue-router'
import MessageForm from '../components/MessageForm.vue'
import MessageItem from '../components/MessageItem.vue'

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
  recipient.value = messages.value.length > 0 
    ? (messages.value[0].sender.id === store.user.id 
        ? messages.value[0].recipient 
        : messages.value[0].sender)
    : null
  
  // 如果还没有recipient信息，我们需要从路由参数中获取
  if (!recipient.value) {
    // 这里可以调用API获取用户信息
    // 为简化起见，我们暂时使用userId作为标识
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
      <div v-if="recipient" class="recipient-info">
        <div class="recipient-avatar">
          <img 
            v-if="recipient.avatar" 
            :src="recipient.avatar" 
            :alt="recipient.username"
          >
          <div v-else class="avatar-placeholder">
            {{ recipient.username.charAt(0).toUpperCase() }}
          </div>
        </div>
        <div class="recipient-name">{{ recipient.username }}</div>
      </div>
      <div v-else class="recipient-info">
        <div class="recipient-avatar">
          <div class="avatar-placeholder">
            U
          </div>
        </div>
        <div class="recipient-name">用户 {{ route.params.userId }}</div>
      </div>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else class="messages-container">
      <div 
        v-for="message in messages" 
        :key="message.id"
        class="message-wrapper"
        :class="{ 'own-message': message.sender.id === store.user.id }"
      >
        <MessageItem :message="message" :current-user-id="store.user.id" />
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