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
const loadingMore = ref(false)

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
    ? [...store.currentConversation.messages].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
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

const loadMoreMessages = async () => {
  const userId = parseInt(route.params.userId)
  if (isNaN(userId) || loadingMore.value) return;
  loadingMore.value = true
  try {
    await store.fetchMoreMessages(userId)
    messages.value = Array.isArray(store.currentConversation?.messages)
      ? [...store.currentConversation.messages].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
      : []
  } catch (error) {
    console.error('加载更多消息失败:', error)
  } finally {
    loadingMore.value = false
  }
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

const handleSubmit = async (formData) => {
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

      // 按时间排序
      messages.value.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))

      // 强制 Vue 重新渲染以应用新样式
      messages.value = [...messages.value]

      // 确保在下次DOM更新后滚动到底部
      nextTick(() => {
        scrollToBottom()
      })
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    alert('发送消息失败')
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

const handleRevokeMessage = (messageId) => {
  const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
  if (messageIndex !== -1) {
    messages.value[messageIndex].is_revoked = true;
  }
}

const handleScroll = async (event) => {
  const { scrollTop } = event.target;

  // 当滚动到顶部时加载更多消息
  if (scrollTop <= 0 &&
    store.currentConversation?.pagination?.has_previous &&
    !loadingMore.value) {
    await loadMoreMessages();
  }
}

const goBack = () => {
  router.push('/messages');
}

const cancelEdit = () => {
  editingMessage.value = null;
  editContent.value = '';
}
</script>

<template>
  <div class="conversation-page">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <el-button icon="ArrowLeft" @click="goBack" circle class="back-button" />
      <div class="recipient-info" v-if="recipient">
        <el-avatar :src="recipient.avatar" :size="40" class="recipient-avatar">
          <span v-if="!recipient.avatar">
            {{ recipient.username?.charAt(0).toUpperCase() }}
          </span>
        </el-avatar>
        <div class="recipient-details">
          <div class="recipient-name">{{ recipient.username }}</div>
        </div>
      </div>
    </div>

    <!-- 消息容器 -->
    <div class="messages-container" @scroll="handleScroll">
      <div class="messages-content">
        <!-- 加载更多指示器 -->
        <div v-if="loadingMore" class="loading-more">
          <el-skeleton :rows="1" animated />
        </div>

        <!-- 消息列表 -->
        <MessageItem v-for="message in messages" :key="message.id" :message="message"
          :currentUserId="store.user?.id || 0" @edit-message="handleEditMessage" @delete-message="handleDeleteMessage"
          @revoke-message="handleRevokeMessage" />
      </div>
    </div>

    <!-- 消息输入表单 -->
    <MessageForm @send-message="handleSubmit" :on-send="handleSubmit" :editing-message="editingMessage"
      :edit-content="editContent" @cancel-edit="cancelEdit" />
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

.chat-header {
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

.chat-header:hover {
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

.recipient-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
  border: 3px solid #fff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  font-size: 1.2rem;
}

.recipient-avatar:hover {
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
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  margin-bottom: 15px;
  backdrop-filter: blur(5px);
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
  scrollbar-width: thin;
  scrollbar-color: #409eff #e0e0e0;
}

.messages-content {
  display: flex;
  flex-direction: column;
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

.loading-more {
  padding: 10px 0;
  display: flex;
  justify-content: center;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .conversation-page {
    padding: 10px;
    border-radius: 10px;
  }

  .chat-header {
    padding: 10px 15px;
  }

  .recipient-name {
    font-size: 1.1rem;
  }

  .back-button {
    width: 35px;
    height: 35px;
  }

  .messages-container {
    padding: 10px;
  }
}

@media (max-width: 480px) {
  .conversation-page {
    padding: 5px;
    height: calc(100vh - 60px);
  }

  .chat-header {
    padding: 8px 10px;
  }

  .recipient-name {
    font-size: 1rem;
  }

  .back-button {
    width: 30px;
    height: 30px;
    margin-right: 10px;
  }
}
</style>