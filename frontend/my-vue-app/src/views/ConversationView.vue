<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useMainStore } from '../store'
import { useRoute, useRouter } from 'vue-router'
import MessageForm from '../components/MessageForm.vue'
import MessageItem from '../components/MessageItem.vue'
import { authAPI } from '../api' 
import { messageAPI } from '../api'

const store = useMainStore()
const route = useRoute()
const router = useRouter()

const messages = ref([])
const recipient = ref(null)
const loading = ref(true)

// 编辑消息相关的状态
const editingMessage = ref(null)
const editContent = ref('')

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

// 添加判断是否为自己发送的消息的方法
const isOwnMessage = (message) => {
  if (!message || !message.sender) return false
  const currentUserId = store.user?.id || 0
  return message.sender.id === currentUserId
}

const scrollToBottom = () => {
  nextTick(() => {
    const container = document.querySelector('.messages-container')
    if (container) {
      // 平滑滚动到底部
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}
const handleNewMessage = async (formData) => {
  const userId = parseInt(route.params.userId)
  if (isNaN(userId)) return;
  
  try {
    // 添加接收者ID到表单数据
    if (!formData.has('recipient')) {
      formData.append('recipient', userId)
    }
    
    // 发送消息并获取返回的结果
    const response = await messageAPI.sendMessage(formData)
    let newMessage = response.data
    
    
    if (!newMessage.sender || typeof newMessage.sender === 'number') {
      newMessage.sender = {
        id: store.user.id,
        username: store.user.username,
        avatar: store.user.avatar
      }
    }
    if (!newMessage.timestamp) {
      newMessage.timestamp = new Date().toISOString()
    }
    
    // 更新本地消息列表
    if (newMessage && typeof newMessage === 'object') {
      // 检查消息是否已经存在于列表中
      const existingMessageIndex = messages.value.findIndex(msg => msg.id === newMessage.id)
      
      if (existingMessageIndex !== -1) {
        // 如果已存在，更新它
        messages.value[existingMessageIndex] = newMessage
      } else {
        // 如果不存在，添加到列表末尾
        messages.value.push(newMessage)
      }
      
      // 强制 Vue 重新渲染以应用新样式
      messages.value = [...messages.value]
      
      // 确保在下次DOM更新后滚动到底部
      nextTick(() => {
        scrollToBottom()
      })
    }
  } catch (error) {
    // ... 错误处理保持不变 ...
  }
}
const handleEditMessage = (message) => {
  editingMessage.value = message
  editContent.value = message.content
}

const saveEditMessage = async () => {
  if (!editingMessage.value || !editingMessage.value.id) return
  
  try {
    const formData = new FormData()
    formData.append('content', editContent.value)
    
    const response = await messageAPI.updateMessage(editingMessage.value.id, formData)
    
    // 更新本地消息列表
    const index = messages.value.findIndex(msg => msg.id === editingMessage.value.id)
    if (index !== -1) {
      messages.value[index] = response.data
    }
    
    // 重置编辑状态
    editingMessage.value = null
    editContent.value = ''
  } catch (error) {
    console.error('编辑消息失败:', error)
    alert('编辑消息失败')
  }
}

const handleDeleteMessage = async (message) => {
  if (!message || !message.id) {
    alert('无效的消息')
    return
  }
  
  if (!confirm('确定要删除这条消息吗？')) {
    return
  }
  
  try {
    await messageAPI.deleteMessage(message.id)
    
    // 从本地消息列表中移除
    const index = messages.value.findIndex(msg => msg.id === message.id)
    if (index !== -1) {
      messages.value.splice(index, 1)
    }
  } catch (error) {
    console.error('删除消息失败:', error)
    alert('删除消息失败')
  }
}

const cancelEditMessage = () => {
  editingMessage.value = null
  editContent.value = ''
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
        :class="{ 'own-message': isOwnMessage(message) }"
      >
        <!-- 编辑消息表单 -->
        <div v-if="editingMessage && editingMessage.id === message.id" class="edit-form">
          <textarea v-model="editContent" class="edit-textarea"></textarea>
          <div class="edit-actions">
            <button @click="saveEditMessage" class="save-button">保存</button>
            <button @click="cancelEditMessage" class="cancel-button">取消</button>
          </div>
        </div>
        <!-- 消息显示 -->
        <MessageItem 
          v-else
          :message="message" 
          :current-user-id="store.user?.id || 0"
          @edit="handleEditMessage"
          @delete="handleDeleteMessage"
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
  padding: 15px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  margin-bottom: 15px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.conversation-header:hover {
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
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
  flex: 1;
}

.recipient-avatar img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
  border: 3px solid #fff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.recipient-avatar img:hover {
  transform: scale(1.05);
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
  transition: all 0.3s ease;
}

.avatar-placeholder:hover {
  transform: scale(1.05);
}

.recipient-name {
  font-weight: 600;
  font-size: 1.3rem;
  color: #2c3e50;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  padding: 20px;
  color: #7f8c8d;
  font-style: italic;
  font-size: 1.1rem;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 15px;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  margin-bottom: 15px;
  backdrop-filter: blur(5px);
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
  scrollbar-width: thin;
  scrollbar-color: #409eff #e0e0e0;
}

.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #409eff;
  border-radius: 10px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #337ecc;
}

.message-wrapper {
  display: flex;
  margin-bottom: 15px;
  animation: fadeIn 0.3s ease-out;
}

.message-wrapper.own-message {
  justify-content: flex-end;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.edit-form {
  width: 100%;
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.edit-textarea {
  width: 100%;
  min-height: 100px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  font-family: inherit;
  font-size: 1rem;
  margin-bottom: 15px;
  transition: border-color 0.3s ease;
}

.edit-textarea:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.save-button, .cancel-button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.save-button {
  background: linear-gradient(135deg, #42b883, #3498db);
  color: white;
}

.save-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(66, 184, 131, 0.3);
}

.cancel-button {
  background: #f5f5f5;
  color: #666;
}

.cancel-button:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
}

.no-messages {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-style: italic;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  margin: auto;
}
</style>