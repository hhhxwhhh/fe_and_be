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
    
    // 检查文件类型
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
    <h3>发布新帖子</h3>
    
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
    
    <div class="form-group">
      <input 
        type="file" 
        accept="image/*" 
        @change="handleImageUpload"
      />
    </div>
    
    <button 
      @click="submitPost" 
      :disabled="loading"
      class="submit-btn"
    >
      {{ loading ? '发布中...' : '发布' }}
    </button>
  </div>
</template>

<style scoped>
.post-form {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.form-group input[type="file"] {
  width: 100%;
}

.submit-btn {
  padding: 0.5rem 1rem;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:hover:not(:disabled) {
  background-color: #359c6d;
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  padding: 0.75rem;
  margin-bottom: 1rem;
  background-color: #ffecec;
  color: #d8000c;
  border: 1px solid #ffd2d2;
  border-radius: 4px;
}
</style>