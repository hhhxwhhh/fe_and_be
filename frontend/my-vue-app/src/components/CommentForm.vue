<script setup>
import { ref } from 'vue'
import { commentAPI } from '../api'

// --- 核心修改 1: 接收新的 props ---
const props = defineProps({
  postId: {
    type: Number,
    required: true
  },
  // parentId 是可选的，用于指定回复的是哪条评论
  parentId: {
    type: Number,
    default: null
  },
  // isReply 是一个布尔值，用于调整 UI 显示
  isReply: {
    type: Boolean,
    default: false
  }
})
// --- 修改结束 ---

const emit = defineEmits(['commentAdded'])

const content = ref('')
const image = ref(null)
const loading = ref(false)
const error = ref('')

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      error.value = '图片大小不能超过5MB'
      image.value = null
      event.target.value = ''
      return
    }
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']
    if (!allowedTypes.includes(file.type)) {
      error.value = '只支持JPEG、PNG、GIF以及JPG格式的图片'
      image.value = null
      event.target.value = ''
      return
    }
    image.value = file
    error.value = ''
  }
}

const removeImage = () => {
  image.value = null
  const fileInput = document.querySelector('.comment-file-input')
  if (fileInput) fileInput.value = ''
}

const submitComment = async () => {
  if (!content.value.trim() && !image.value) {
    error.value = '评论内容或图片不能为空'
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

    // --- 核心修改 2: 如果是回复，添加 parent 字段 ---
    if (props.parentId) {
      formData.append('parent', props.parentId)
    }
    // --- 修改结束 ---
    
    const response = await commentAPI.createComment(props.postId, formData)
    
    emit('commentAdded', response.data)
    content.value = ''
    image.value = null
    
    const fileInput = document.querySelector('.comment-file-input')
    if (fileInput) fileInput.value = ''
  } catch (err) { // 使用 err 避免与外层 error 变量冲突
    console.error('添加评论/回复失败:', err)
    if (err.response && err.response.data) {
      if (typeof err.response.data === 'object') {
        const errorMessages = []
        for (const [field, messages] of Object.entries(err.response.data)) {
          if (Array.isArray(messages)) {
            errorMessages.push(`${field}: ${messages.join(', ')}`)
          } else {
            errorMessages.push(`${field}: ${messages}`)
          }
        }
        error.value = errorMessages.join('; ')
      } else {
        error.value = err.response.data
      }
    } else {
      error.value = '操作失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="comment-form">
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- --- 核心修改 3: 根据 isReply 调整 UI --- -->
    <textarea 
      v-model="content"
      :placeholder="isReply ? '发表你的回复...' : '添加评论...'"
      rows="3"
    ></textarea>
    
    <div class="form-actions">
      <div class="file-upload">
        <label class="file-label">
          <input 
            type="file" 
            accept="image/*" 
            @change="handleImageUpload"
            class="comment-file-input"
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
      
      <div class="form-footer">
        <span v-if="content.length > 0" class="char-count">{{ content.length }}/500</span>
        <button 
          @click="submitComment"
          :disabled="loading || (!content.trim() && !image)"
          class="submit-button"
        >
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? '提交中...' : (isReply ? '回复' : '发布评论') }}
        </button>
      </div>
    </div>
    <!-- --- 修改结束 --- -->
  </div>
</template>

<style scoped>
.comment-form {
  margin-top: 1.5rem;
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.comment-form textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-sizing: border-box;
  resize: vertical;
  margin-bottom: 1rem;
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.5;
  transition: all 0.2s ease;
  background-color: #fff;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.comment-form textarea:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1), inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.comment-form textarea::placeholder {
  color: #a0aec0;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.file-upload {
  margin-bottom: 0.5rem;
}

.file-label {
  display: block;
  cursor: pointer;
}

.comment-file-input {
  display: none;
}

.file-button {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #edf2f7;
  color: #4a5568;
  border-radius: 8px;
  transition: all 0.2s ease;
  border: 1px dashed #cbd5e0;
  font-size: 0.9rem;
}

.file-button:hover {
  background: #e2e8f0;
  border-color: #a0aec0;
}

.image-preview {
  margin-top: 0.5rem;
}

.preview-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.image-name {
  font-size: 0.8rem;
  color: #4a5568;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 80%;
}

.remove-image {
  background: #fed7d7;
  color: #c53030;
  border: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 0.8rem;
}

.remove-image:hover {
  background: #feb2b2;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  font-size: 0.8rem;
  color: #718096;
}

.submit-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.5rem;
  background: linear-gradient(45deg, #42b883, #3498db);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(66, 184, 131, 0.3);
}

.submit-button:hover:not(:disabled) {
  background: linear-gradient(45deg, #3aa876, #2980b9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 184, 131, 0.4);
}

.submit-button:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
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
  padding: 0.75rem;
  margin-bottom: 1rem;
  background-color: #fff5f5;
  color: #c53030;
  border: 1px solid #fed7d7;
  border-radius: 8px;
  font-size: 0.85rem;
}
</style>