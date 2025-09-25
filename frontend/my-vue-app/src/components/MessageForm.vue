<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  onSend: {
    type: Function,
    required: true
  },
  editingMessage: {
    type: Object,
    default: null
  },
  editContent: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['cancel-edit'])

const content = ref('')
const selectedFile = ref(null)
const fileInput = ref(null)
const isEditing = ref(false)

// 监听编辑消息的变化
watch(() => props.editingMessage, (newVal) => {
  if (newVal) {
    isEditing.value = true
    content.value = props.editContent || newVal.content || ''
  } else {
    isEditing.value = false
    content.value = ''
  }
})

// 监听编辑内容的变化
watch(() => props.editContent, (newVal) => {
  if (isEditing.value) {
    content.value = newVal || ''
  }
})

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 添加文件类型验证
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];

    if (!allowedTypes.includes(file.type)) {
      alert('不支持的文件类型。支持的类型: 图片(JPG, PNG, GIF, BMP, WebP), PDF, Word, 文本文件');
      return;
    }

    // 检查文件大小
    if (file.size > 10 * 1024 * 1024) {
      alert('文件大小不能超过10MB');
      return;
    }

    selectedFile.value = file;
  }
}

const removeFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleSubmit = async () => {
  if (!content.value.trim() && !selectedFile.value) {
    return
  }

  try {
    const formData = new FormData()
    // 总是添加content字段，即使为空
    formData.append('content', content.value)

    if (selectedFile.value) {
      // 根据文件类型决定添加到哪个字段
      if (selectedFile.value.type.startsWith('image/')) {
        formData.append('image', selectedFile.value)
      } else {
        formData.append('file', selectedFile.value)
      }
    }

    await props.onSend(formData)
    content.value = ''
    removeFile()
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}

const handleUpdate = async () => {
  if (!props.editingMessage || !props.editingMessage.id) {
    return
  }

  try {
    const formData = new FormData()
    formData.append('content', content.value)

    await props.onSend(formData, props.editingMessage.id)
    content.value = ''
    isEditing.value = false
  } catch (error) {
    console.error('更新消息失败:', error)
  }
}

const cancelEdit = () => {
  isEditing.value = false
  content.value = ''
  emit('cancel-edit')
}

const handleKeyPress = (event) => {
  if (event.ctrlKey && event.key === 'Enter') {
    if (isEditing.value) {
      handleUpdate()
    } else {
      handleSubmit()
    }
  }
}
</script>

<template>
  <div class="message-form">
    <div v-if="selectedFile" class="file-preview">
      <div class="file-info">
        <span>{{ selectedFile.name }}</span>
        <button @click="removeFile" class="remove-file">×</button>
      </div>
    </div>

    <div class="input-area">
      <textarea v-model="content" placeholder="输入消息内容..." @keydown="handleKeyPress" class="message-input"></textarea>

      <div class="actions">
        <input ref="fileInput" type="file" @change="handleFileChange" accept="image/*,.pdf,.doc,.docx,.txt"
          class="file-input" id="file-upload" :disabled="isEditing" />
        <label for="file-upload" class="file-upload-btn" :class="{ disabled: isEditing }">
          📎
        </label>

        <div class="buttons">
          <button v-if="isEditing" @click="cancelEdit" class="cancel-button">
            取消
          </button>

          <button v-if="isEditing" @click="handleUpdate" :disabled="!content.trim()" class="update-button">
            更新
          </button>

          <button v-else @click="handleSubmit" :disabled="!content.trim() && !selectedFile" class="send-button">
            发送
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-form {
  border-top: 1px solid #eee;
  padding: 15px;
  background: white;
  border-radius: 0 0 15px 15px;
}

.file-preview {
  margin-bottom: 10px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 5px;
}

.file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remove-file {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #999;
}

.remove-file:hover {
  color: #ff4444;
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message-input {
  width: 100%;
  min-height: 80px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  font-family: inherit;
  font-size: 14px;
}

.message-input:focus {
  outline: none;
  border-color: #409eff;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-input {
  display: none;
}

.file-input:disabled+.file-upload-btn {
  opacity: 0.5;
  cursor: not-allowed;
}

.file-upload-btn {
  padding: 8px 12px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.file-upload-btn:hover:not(.disabled) {
  background: #e0e0e0;
}

.buttons {
  display: flex;
  gap: 10px;
}

.send-button,
.update-button,
.cancel-button {
  padding: 8px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.send-button {
  background: #409eff;
  color: white;
}

.send-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.send-button:hover:not(:disabled) {
  background: #337ecc;
}

.update-button {
  background: #67c23a;
  color: white;
}

.update-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.update-button:hover:not(:disabled) {
  background: #529b2e;
}

.cancel-button {
  background: #909399;
  color: white;
}

.cancel-button:hover {
  background: #a6a9ad;
}
</style>