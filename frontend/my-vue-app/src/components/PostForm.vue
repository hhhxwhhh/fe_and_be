<script setup>
import { ref } from 'vue'
import { postAPI } from '../api'

const emit = defineEmits(['postCreated'])

const content = ref('')
const image = ref(null)
const loading = ref(false)
const error = ref('')

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 检查文件大小（例如限制为5MB）
    if (file.size > 5 * 1024 * 1024) {
      error.value = '图片大小不能超过5MB'
      image.value = null
      event.target.value = '' // 清空输入
      return
    }
    
    // 棎查文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif','image/jpg']
    if (!allowedTypes.includes(file.type)) {
      error.value = '只支持JPEG、PNG、GIF以及JPG格式的图片'
      image.value = null
      event.target.value = '' // 清空输入
      return
    }
    
    image.value = file
    error.value = ''
  }
}

const removeImage = () => {
  image.value = null
  const fileInput = document.querySelector('input[type="file"]')
  if (fileInput) fileInput.value = ''
}

const submitPost = async () => {
  if (!content.value.trim()) {
    error.value = '内容不能为空'
    return
  }
  
  try {
    loading.value = true
    error.value = ''
    
    const formData = new FormData()
    formData.append('content', content.value)
    if (image.value) {
      formData.append('image', image.value)
    }
    
    await postAPI.createPost(formData)
    content.value = ''
    image.value = null
    
    // 重置文件输入
    const fileInput = document.querySelector('input[type="file"]')
    if (fileInput) fileInput.value = ''
    
    emit('postCreated')
  } catch (error) {
    console.error('发布帖子失败:', error)
    if (error.response && error.response.data) {
      // 显示后端返回的具体错误信息
      if (typeof error.response.data === 'object') {
        const errorMessages = []
        for (const [field, messages] of Object.entries(error.response.data)) {
          if (Array.isArray(messages)) {
            errorMessages.push(`${field}: ${messages.join(', ')}`)
          } else {
            errorMessages.push(`${field}: ${messages}`)
          }
        }
        error.value = errorMessages.join('; ')
      } else {
        error.value = error.response.data
      }
    } else {
      error.value = '发布帖子失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="post-form">
    <div class="form-header">
      <h3>发布新帖子</h3>
      <div class="char-count" :class="{ 'limit-exceeded': content.length > 280 }">
        {{ content.length }}/280
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div class="form-group">
      <textarea 
        v-model="content"
        placeholder="分享你的想法..."
        rows="4"
      ></textarea>
    </div>
    
    <div class="form-group file-upload">
      <label class="file-label">
        <input 
          type="file" 
          accept="image/*" 
          @change="handleImageUpload"
          class="file-input"
        />
        <div class="file-button">
          <span>📁 上传图片</span>
        </div>
      </label>
      <div v-if="image" class="image-preview">
        <div class="preview-container">
          <span class="image-name">{{ image.name }}</span>
          <button @click="removeImage" class="remove-image">×</button>
        </div>
      </div>
    </div>
    
    <button 
      @click="submitPost" 
      :disabled="loading || (!content.trim() && !image)"
      class="submit-btn"
    >
      <span v-if="loading" class="loading-spinner"></span>
      {{ loading ? '发布中...' : '发布帖子' }}
    </button>
  </div>
</template>

<style scoped>
.post-form {
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.post-form:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.form-header h3 {
  margin: 0;
  color: #2c3e50;
  font-weight: 600;
}

.char-count {
  font-size: 0.85rem;
  color: #718096;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  background-color: #edf2f7;
}

.char-count.limit-exceeded {
  color: #e53e3e;
  background-color: #fed7d7;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
  font-size: 1rem;
  line-height: 1.5;
  transition: all 0.2s ease;
  background-color: #fff;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  min-height: 120px;
}

.form-group textarea:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1), inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.form-group textarea::placeholder {
  color: #a0aec0;
}

.file-upload {
  margin-bottom: 1.5rem;
}

.file-label {
  display: block;
  cursor: pointer;
}

.file-input {
  display: none;
}

.file-button {
  display: inline-block;
  padding: 0.75rem 1.25rem;
  background: #edf2f7;
  color: #4a5568;
  border-radius: 8px;
  transition: all 0.2s ease;
  border: 1px dashed #cbd5e0;
}

.file-button:hover {
  background: #e2e8f0;
  border-color: #a0aec0;
}

.image-preview {
  margin-top: 0.75rem;
}

.preview-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.image-name {
  font-size: 0.9rem;
  color: #4a5568;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-image {
  background: #fed7d7;
  color: #c53030;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.remove-image:hover {
  background: #feb2b2;
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.8rem 1.5rem;
  background: linear-gradient(45deg, #42b883, #3498db);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(66, 184, 131, 0.3);
  width: 100%;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #3aa876, #2980b9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 184, 131, 0.4);
}

.submit-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #fff5f5;
  color: #c53030;
  border: 1px solid #fed7d7;
  border-radius: 8px;
  font-size: 0.9rem;
}
</style>