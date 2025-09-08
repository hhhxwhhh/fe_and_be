<script setup>
import { ref } from 'vue'
import { postAPI } from '../api'

const emit = defineEmits(['postCreated'])

const content = ref('')
const image = ref(null)
const loading = ref(false)

const handleImageUpload = (event) => {
  image.value = event.target.files[0]
}

const submitPost = async () => {
  if (!content.value.trim()) return
  
  try {
    loading.value = true
    
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
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="post-form">
    <h3>发布新帖子</h3>
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
      :disabled="loading || !content.trim()"
      class="btn btn-primary"
    >
      {{ loading ? '发布中...' : '发布' }}
    </button>
  </div>
</template>

<style scoped>
.post-form {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  resize: vertical;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary {
  background-color: #42b883;
  color: white;
}

.btn:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}
</style>