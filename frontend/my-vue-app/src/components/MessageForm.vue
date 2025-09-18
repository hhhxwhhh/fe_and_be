<script setup>
import { ref } from 'vue'

const emit = defineEmits(['send'])

const content = ref('')
const loading = ref(false)

const sendMessage = async () => {
  if (!content.value.trim() || loading.value) return
  
  loading.value = true
  try {
    await emit('send', content.value.trim())
    content.value = ''
  } finally {
    loading.value = false
  }
}

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <div class="message-form">
    <textarea
      v-model="content"
      placeholder="输入消息..."
      :disabled="loading"
      @keydown="handleKeydown"
      rows="1"
    ></textarea>
    <button 
      @click="sendMessage" 
      :disabled="!content.trim() || loading"
      class="send-button"
    >
      发送
    </button>
  </div>
</template>

<style scoped>
.message-form {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

textarea {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 20px;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
  max-height: 150px;
}

textarea:focus {
  border-color: #42b883;
}

.send-button {
  padding: 12px 20px;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background: #3aa876;
}

.send-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>