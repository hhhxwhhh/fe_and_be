<script setup>
import { ref } from 'vue'

const props = defineProps({
  onSend: {
    type: Function,
    required: true
  }
})

const content = ref('')
const selectedFile = ref(null)
const fileInput = ref(null)

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

const handleKeyPress = (event) => {
  if (event.ctrlKey && event.key === 'Enter') {
    handleSubmit()
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
      <textarea
        v-model="content"
        placeholder="输入消息内容..."
        @keydown="handleKeyPress"
        class="message-input"
      ></textarea>
      
      <div class="actions">
        <input
          ref="fileInput"
          type="file"
          @change="handleFileChange"
          accept="image/*,.pdf,.doc,.docx,.txt"
          class="file-input"
          id="file-upload"
        />
        <label for="file-upload" class="file-upload-btn">
          📎
        </label>
        
        <button 
          @click="handleSubmit" 
          :disabled="!content.trim() && !selectedFile"
          class="send-button"
        >
          发送
        </button>
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

.file-upload-btn {
  padding: 8px 12px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.file-upload-btn:hover {
  background: #e0e0e0;
}

.send-button {
  padding: 8px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.send-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.send-button:hover:not(:disabled) {
  background: #337ecc;
}
</style>