<script setup>
import { ref, onMounted, nextTick } from 'vue'
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

onMounted(async () => {
  const userId = parseInt(route.params.userId)
  if (isNaN(userId)) {
    router.push('/messages')
    return
  }

  await store.fetchConversation(userId)
  
  // 验证消息数据格式
  if (Array.isArray(store.currentConversation?.messages)) {
    messages.value = store.currentConversation.messages.filter(msg => 
      msg && typeof msg === 'object' && msg.sender && msg.recipient
    )
  } else {
    console.error('消息数据格式不正确:', store.currentConversation?.messages)
    messages.value = []
  }
  
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
      const response = await authAPI.userProfile(userId)
      recipient.value = {
        id: response.data.id,
        username: response.data.username,
        avatar: response.data.avatar
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      recipient.value = {
        id: userId,
        username: `用户 ${userId}`,
        avatar: null
      }
    }
  }
  
  loading.value = false
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
    
    // 验证新消息格式
    if (newMessage && typeof newMessage === 'object' && newMessage.sender && newMessage.recipient) {
      messages.value.push(newMessage)
      scrollToBottom()
    } else {
      console.error('收到的消息格式不正确:', newMessage)
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
        v-for="message in messages" 
        :key="message.id"
        class="message-wrapper"
        :class="{ 'own-message': message.sender && message.sender.id === (store.user?.id || 0) }"
      >
        <MessageItem 
          v-if="message && typeof message === 'object'" 
          :message="message" 
          :current-user-id="store.user?.id || 0" 
        />
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
/* 样式保持不变 */
</style>