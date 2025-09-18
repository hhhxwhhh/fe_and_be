<script setup>
import { ref, onMounted } from 'vue'
import { useMainStore } from '../store'
import { useRouter } from 'vue-router'
import MessageItem from '../components/MessageItem.vue'

const store = useMainStore()
const router = useRouter()
const conversations = ref([])

onMounted(async () => {
  await store.fetchConversations()
  conversations.value = store.conversations
})

const openConversation = (userId) => {
  router.push(`/messages/${userId}`)
}
</script>

<template>
  <div class="messages-page">
    <div class="messages-header">
      <h2>私信</h2>
    </div>
    
    <div class="conversations-list">
      <div 
        v-for="conversation in conversations" 
        :key="conversation.user?.id || conversation.id"
        class="conversation-item"
        @click="openConversation(conversation.user?.id)"
      >
        <div class="user-avatar">
          <img 
            v-if="conversation.user?.avatar" 
            :src="conversation.user.avatar" 
            :alt="conversation.user?.username"
          >
          <div v-else class="avatar-placeholder">
            {{ conversation.user?.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
        </div>
        <div class="conversation-info">
          <div class="user-name">{{ conversation.user?.username || '未知用户' }}</div>
          <div class="last-message">{{ conversation.last_message?.content || '无消息' }}</div>
        </div>
        <div class="conversation-meta">
          <div class="timestamp">
            {{ new Date(conversation.last_message?.timestamp || Date.now()).toLocaleDateString() }}
          </div>
          <div v-if="conversation.unread_count > 0" class="unread-count">
            {{ conversation.unread_count }}
          </div>
        </div>
      </div>
      
      <div v-if="conversations.length === 0" class="no-conversations">
        暂无私信
      </div>
    </div>
  </div>
</template>

<style scoped>
.messages-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.messages-header {
  margin-bottom: 20px;
}

.messages-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.conversations-list {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.conversation-item:hover {
  background-color: #f9f9f9;
}

.conversation-item:last-child {
  border-bottom: none;
}

.user-avatar {
  margin-right: 15px;
}

.user-avatar img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(45deg, #42b883, #3498db);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
}

.last-message {
  color: #666;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.timestamp {
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 5px;
}

.unread-count {
  background: #e74c3c;
  color: white;
  border-radius: 10px;
  padding: 2px 8px;
  font-size: 0.8rem;
}

.no-conversations {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}
</style>