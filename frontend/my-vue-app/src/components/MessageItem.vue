<script setup>
import { ref, computed } from 'vue'
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

const emit = defineEmits(['edit-message', 'delete-message', 'revoke-message'])

// 控制错误提示模态框的显示
const showErrorModal = ref(false)
const errorMessage = ref('')

const isOwnMessage = computed(() => {
  // 确保消息和发送者存在
  if (!props.message || !props.message.sender) {
    return false
  }

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
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)) {
    return '🖼️'
  } else if (['pdf'].includes(ext)) {
    return '📄'
  } else if (['doc', 'docx'].includes(ext)) {
    return '📝'
  } else if (['xls', 'xlsx'].includes(ext)) {
    return '📊'
  } else if (['ppt', 'pptx'].includes(ext)) {
    return '📑'
  } else if (['zip', 'rar', '7z', 'tar'].includes(ext)) {
    return '📦'
  } else if (['mp3', 'wav', 'ogg'].includes(ext)) {
    return '🎵'
  } else if (['mp4', 'avi', 'mov', 'mkv'].includes(ext)) {
    return '🎬'
  } else {
    return '📎'
  }
}

const getFileName = (filePath) => {
  if (!filePath) return '未知文件'
  try {
    const fileName = filePath.split('/').pop()
    return decodeURIComponent(fileName)
  } catch (e) {
    return '未知文件'
  }
}

const handleEdit = () => {
  emit('edit-message', props.message)
}

const handleDelete = () => {
  emit('delete-message', props.message)
}

const handleRevoke = async () => {
  try {
    // 确保消息ID存在
    if (!props.message || !props.message.id) {
      console.error('Message ID is missing')
      errorMessage.value = '无法撤回消息：消息尚未完全发送或ID不存在'
      showErrorModal.value = true
      return
    }

    const response = await messageAPI.revokeMessage(props.message.id)
    emit('revoke-message', props.message.id, response.data)
  } catch (error) {
    console.error('撤回消息失败:', error)
    if (error.response && error.response.data && error.response.data.detail) {
      errorMessage.value = '撤回消息失败: ' + error.response.data.detail
    } else {
      errorMessage.value = '撤回消息失败: ' + (error.message || '未知错误')
    }
    showErrorModal.value = true
  }
}

const closeErrorModal = () => {
  showErrorModal.value = false
  errorMessage.value = ''
}
</script>
<template>
  <div :key="message.id" class="message-wrapper" :class="{ 'own-message': isOwnMessage }">
    <!-- 对方消息 -->
    <template v-if="!isOwnMessage">
      <div class="avatar-container">
        <el-avatar :src="message.sender.avatar" :size="35" class="message-avatar">
          <span v-if="!message.sender.avatar">
            {{ message.sender.username?.charAt(0).toUpperCase() }}
          </span>
        </el-avatar>
      </div>
      <div class="message-item">
        <div class="sender-name" v-if="!isOwnMessage">
          {{ message.sender.username }}
        </div>
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
                <span class="file-name">{{ getFileName(message.file) }}</span>
              </a>
            </div>
          </template>

          <div class="message-meta">
            <span class="timestamp">{{ formatDate(message.timestamp) }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- 自己的消息 -->
    <template v-else>
      <div class="avatar-container">
        <el-avatar :src="message.sender.avatar" :size="35" class="message-avatar">
          <span v-if="!message.sender.avatar">
            {{ message.sender.username?.charAt(0).toUpperCase() }}
          </span>
        </el-avatar>
      </div>
      <div class="message-item own-message-item">
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
                <span class="file-name">{{ getFileName(message.file) }}</span>
              </a>
            </div>
          </template>

          <div class="message-meta">
            <span class="timestamp">{{ formatDate(message.timestamp) }}</span>
            <div v-if="!message.is_revoked && (message.content || message.image || message.file)"
              class="message-actions">
              <button v-if="canRevoke" @click.stop="handleRevoke" class="action-btn revoke-btn">撤回</button>
              <button @click.stop="handleEdit" class="action-btn edit-btn">编辑</button>
              <button @click.stop="handleDelete" class="action-btn delete-btn">删除</button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 自定义错误提示模态框 -->
    <div v-if="showErrorModal" class="modal-overlay" @click="closeErrorModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>提示</h3>
          <button class="modal-close" @click="closeErrorModal">&times;</button>
        </div>
        <div class="modal-body">
          <p>{{ errorMessage }}</p>
        </div>
        <div class="modal-footer">
          <button class="modal-confirm-btn" @click="closeErrorModal">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
.message-wrapper {
  display: flex;
  margin-bottom: 20px;
  animation: messageAppear 0.3s ease-out;
  max-width: 100%;
  width: 100%;
}

.message-wrapper.own-message {
  flex-direction: row-reverse;
}

.avatar-container {
  display: flex;
  align-items: flex-start;
  margin: 0 10px;
  flex-shrink: 0;
}

.message-avatar {
  font-size: 14px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.message-item {
  display: flex;
  flex-direction: column;
  max-width: 75%;
}

.own-message-item {
  align-items: flex-end;
  margin-left: auto;
  display: flex;
  flex-direction: column;
}

.sender-name {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
  margin-left: 12px;
}

.message-content {
  background: white;
  padding: 12px 16px;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
  max-width: 100%;
  word-wrap: break-word;
}

.message-wrapper:not(.own-message) .message-content {
  border-top-left-radius: 6px;
  margin-left: 12px;
}

.message-wrapper.own-message .message-content {
  background: linear-gradient(135deg, #409eff, #337ecc);
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  border-top-right-radius: 6px;
  margin-right: 12px;
}

.message-content:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.message-wrapper.own-message .message-content:hover {
  box-shadow: 0 6px 15px rgba(64, 158, 255, 0.4);
}

.text-content {
  margin-bottom: 8px;
  word-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.5;
  font-size: 15px;
}

.image-content {
  margin-bottom: 8px;
  text-align: center;
}

.uploaded-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 12px;
  display: block;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  margin: 0 auto;
}

.uploaded-image:hover {
  transform: scale(1.02);
}

.file-content {
  margin-bottom: 8px;
}

.file-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 10px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
  min-width: 200px;
}

.message-wrapper.own-message .file-link {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.file-link:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.message-wrapper.own-message .file-link:hover {
  background: rgba(255, 255, 255, 0.3);
}

.file-icon {
  font-size: 20px;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.message-wrapper.own-message .message-meta {
  color: rgba(255, 255, 255, 0.9);
}

.message-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 500;
  transition: all 0.3s ease;
  opacity: 0.9;
  color: inherit;
  /* 确保文字颜色正确显示 */
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

.message-wrapper.own-message .edit-btn,
.message-wrapper.own-message .delete-btn,
.message-wrapper.own-message .revoke-btn {
  color: white;
  background: rgba(255, 255, 255, 0.25);
}

.revoked-message {
  font-style: italic;
  opacity: 0.7;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
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

/* 自定义模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  min-width: 300px;
  max-width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 10px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.modal-body p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.modal-footer {
  padding: 15px 20px 20px;
  text-align: right;
}

.modal-confirm-btn {
  background: linear-gradient(135deg, #409eff, #337ecc);
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.modal-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(64, 158, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-item {
    max-width: 85%;
  }

  .text-content {
    font-size: 14px;
  }

  .message-meta {
    font-size: 11px;
  }

  .action-btn {
    font-size: 11px;
    padding: 2px 6px;
  }
}
</style>