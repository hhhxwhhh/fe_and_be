<script setup>
import { computed } from 'vue'
import { messageAPI } from '../api'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete', 'revoke'])

const isOwnMessage = computed(() => {
  // 确保消息和发送者存在
  if (!props.message || !props.message.sender) {
    return false
  }
  
  // 兼容不同的sender格式（可能是对象或者ID）
  const senderId = typeof props.message.sender === 'object' ? props.message.sender.id : props.message.sender
    
  return senderId === props.currentUserId
})

// 检查消息是否可以撤回（发送后2分钟内）
const canRevoke = computed(() => {
  // 检查基本条件
  if (!props.message || !props.message.id || props.message.is_revoked) {
    return false
  }
  
  // 检查是否是自己的消息
  if (!isOwnMessage.value) {
    return false
  }
  
  // 检查时间是否在2分钟内
  const sendTime = new Date(props.message.timestamp)
  const now = new Date()
  
  // 确保日期有效
  if (isNaN(sendTime.getTime())) {
    console.warn('Invalid message timestamp:', props.message.timestamp)
    return false
  }
  
  const diffMinutes = (now - sendTime) / (1000 * 60)
  
  // 2分钟内可以撤回 (允许少量误差)
  // 增加一个更宽松的时间窗口，确保刚发送的消息可以撤回
  return diffMinutes >= 0 && diffMinutes <= 3
})

const formatDate = (dateString) => {
  // 添加时间有效性验证
  if (!dateString) {
    return '未知时间'
  }
  
  // 解析日期字符串
  const date = new Date(dateString)
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    return '无效时间'
  }
  
  // 获取当前日期用于比较
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  
  // 如果是今天的消息，只显示时间
  if (today.getTime() === messageDate.getTime()) {
    // 使用本地时间格式化
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false
    })
  } else {
    // 如果不是今天，显示日期和时间
    return date.toLocaleString('zh-CN', { 
      year: '2-digit', 
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false
    })
  }
}

const getFileIcon = (filename) => {
  // 确保filename存在
  if (!filename) return '📎'
  
  // 确保filename是字符串
  if (typeof filename !== 'string') return '📎'
  
  const ext = filename.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) {
    return '🖼️'
  } else if (['pdf'].includes(ext)) {
    return '📄'
  } else if (['doc', 'docx'].includes(ext)) {
    return '📝'
  } else {
    return '📎'
  }
}

const handleEdit = () => {
  emit('edit', props.message)
}

const handleDelete = () => {
  emit('delete', props.message)
}

const handleRevoke = async () => {
  try {
    // 确保消息ID存在
    if (!props.message || !props.message.id) {
      console.error('Message ID is missing')
      alert('无法撤回消息：消息尚未完全发送或ID不存在')
      return
    }
    
    await messageAPI.revokeMessage(props.message.id)
    emit('revoke', props.message.id)
  } catch (error) {
    console.error('撤回消息失败:', error)
    alert('撤回消息失败: ' + (error.response?.data?.detail || '未知错误'))
  }
}
</script>

<template>
  <div class="message-item" :class="{ 'own-message': isOwnMessage }">
    <div class="message-content">
      <!-- 显示已撤回消息 -->
      <div v-if="message.is_revoked" class="revoked-message">
        {{ isOwnMessage ? '你撤回了一条消息' : '对方撤回了一条消息' }}
      </div>
      
      <!-- 正常消息内容 -->
      <template v-else>
        <div v-if="message.content" class="text-content">
          {{ message.content }}
        </div>
        
        <div v-if="message.image" class="image-content">
          <img :src="message.image" alt="上传的图片" class="uploaded-image" />
        </div>
        
        <div v-if="message.file" class="file-content">
          <a :href="message.file" target="_blank" class="file-link">
            <span class="file-icon">{{ getFileIcon(message.file) }}</span>
            <span class="file-name">{{ message.file.split('/').pop() }}</span>
          </a>
        </div>
      </template>
      
      <div class="message-meta">
        <span class="timestamp">{{ formatDate(message.timestamp) }}</span>
        <div v-if="isOwnMessage && !message.is_revoked && (message.content || message.image || message.file)" class="message-actions">
          <button v-if="canRevoke" @click="handleRevoke" class="action-btn revoke-btn">撤回</button>
          <button @click="handleEdit" class="action-btn edit-btn">编辑</button>
          <button @click="handleDelete" class="action-btn delete-btn">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
.message-item {
  display: flex;
  margin-bottom: 15px;
  max-width: 85%;
  animation: messageAppear 0.3s ease-out;
}

.message-item.own-message {
  align-self: flex-end;
  margin-left: auto;
}

@keyframes messageAppear {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-content {
  background: white;
  padding: 15px;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.message-item.own-message .message-content {
  background: linear-gradient(135deg, #409eff, #337ecc);
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.message-content:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.message-item.own-message .message-content:hover {
  box-shadow: 0 6px 15px rgba(64, 158, 255, 0.4);
}

.text-content {
  margin-bottom: 12px;
  word-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.5;
  font-size: 1rem;
}

.image-content {
  margin-bottom: 12px;
}

.uploaded-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 12px;
  display: block;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.uploaded-image:hover {
  transform: scale(1.02);
}

.file-content {
  margin-bottom: 12px;
}

.file-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.message-item.own-message .file-link {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.file-link:hover {
  background: rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.message-item.own-message .file-link:hover {
  background: rgba(255, 255, 255, 0.3);
}

.file-icon {
  font-size: 20px;
}

.file-name {
  font-size: 15px;
  font-weight: 500;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #999;
  margin-top: 5px;
}

.message-item.own-message .message-meta {
  color: rgba(255, 255, 255, 0.85);
}

.message-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  padding: 4px 10px;
  border-radius: 5px;
  font-weight: 500;
  transition: all 0.3s ease;
  opacity: 0.8;
}

.action-btn:hover {
  opacity: 1;
  transform: translateY(-1px);
}

.edit-btn {
  color: #409eff;
  background: rgba(64, 158, 255, 0.15);
}

.delete-btn {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.15);
}

.revoke-btn {
  color: #e6a23c;
  background: rgba(230, 162, 60, 0.15);
}

.message-item.own-message .edit-btn,
.message-item.own-message .delete-btn,
.message-item.own-message .revoke-btn {
  color: white;
  background: rgba(255, 255, 255, 0.25);
}

.revoked-message {
  font-style: italic;
  opacity: 0.7;
  text-align: center;
  padding: 10px 0;
}
</style>