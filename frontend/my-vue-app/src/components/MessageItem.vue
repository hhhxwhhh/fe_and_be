<script setup>
defineProps({
  message: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: Number,
    required: true
  }
})
</script>

<template>
  <div class="message-item">
    <div class="message-content">
      {{ message.content }}
    </div>
    <div class="message-meta">
      <span class="timestamp">
        {{ new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
      </span>
      <span v-if="message.sender.id === currentUserId" class="read-status">
        {{ message.is_read ? '已读' : '未读' }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.message-item {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 18px;
  background-color: #f1f1f1;
  position: relative;
}

.message-item.own {
  background-color: #42b883;
  color: white;
}

.message-content {
  word-wrap: break-word;
  line-height: 1.4;
}

.message-meta {
  display: flex;
  justify-content: flex-end;
  margin-top: 5px;
}

.timestamp {
  font-size: 0.7rem;
  color: #999;
}

.own .timestamp {
  color: rgba(255, 255, 255, 0.8);
}

.read-status {
  font-size: 0.7rem;
  color: #999;
  margin-left: 5px;
}

.own .read-status {
  color: rgba(255, 255, 255, 0.8);
}
</style>