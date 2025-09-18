<script setup>
import { ref } from 'vue'
import { commentAPI } from '../api'

const props = defineProps({
  postId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['commentAdded'])

const content = ref('')
const loading = ref(false)

const submitComment = async () => {
  if (!content.value.trim()) return
  
  try {
    loading.value = true
    const response = await commentAPI.createComment(props.postId, {
      content: content.value
    })
    
    emit('commentAdded', response.data)
    content.value = ''
  } catch (error) {
    console.error('添加评论失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="comment-form">
    <textarea 
      v-model="content"
      placeholder="添加评论..."
      rows="3"
    ></textarea>
    <div class="form-footer">
      <span v-if="content.length > 0" class="char-count">{{ content.length }}/500</span>
      <button 
        @click="submitComment"
        :disabled="loading || !content.trim()"
        class="submit-button"
      >
        <span v-if="loading" class="loading-spinner"></span>
        {{ loading ? '提交中...' : '发布评论' }}
      </button>
    </div>
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
</style>