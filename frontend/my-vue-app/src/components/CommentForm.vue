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
      rows="2"
    ></textarea>
    <button 
      @click="submitComment"
      :disabled="loading || !content.trim()"
      class="btn btn-primary"
    >
      {{ loading ? '提交中...' : '评论' }}
    </button>
  </div>
</template>

<style scoped>
.comment-form {
  margin-top: 1rem;
}

.comment-form textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  resize: vertical;
  margin-bottom: 0.5rem;
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