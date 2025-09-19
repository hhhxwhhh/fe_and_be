<script setup>


const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: Number,
    default: 0
  }
})

// 判断是否为自己发送的消息
const isOwnMessage = props.message?.sender?.id === props.currentUserId
</script>

<template>
  <div 
    class="message-item"
    :class="{ 'own-message': isOwnMessage }"
  >
    <div class="message-content">
      <div class="message-sender" v-if="!isOwnMessage && message.sender">
        {{ message.sender.username }}
      </div>
      <div class="message-text">
        {{ message.content }}
      </div>
      <div class="message-time">
        {{ new Date(message.timestamp).toLocaleString() }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-item {
  display: flex;
  margin-bottom: 15px;
  max-width: 80%;
  animation: fadeIn 0.3s ease-out;
}

.message-item.own-message {
  align-self: flex-end;
  margin-left: auto;
}

.message-content {
  background-color: #f0f8ff;
  border-radius: 18px;
  padding: 12px 15px;
  position: relative;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.message-content:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.message-item.own-message .message-content {
  background-color: #42b883;
  color: white;
}

.message-sender {
  font-weight: bold;
  font-size: 0.9rem;
  margin-bottom: 5px;
  color: #2c3e50;
}

.message-item.own-message .message-sender {
  color: #fff;
  opacity: 0.9;
}

.message-text {
  word-wrap: break-word;
  line-height: 1.5;
  font-size: 1rem;
}

.message-time {
  font-size: 0.7rem;
  text-align: right;
  margin-top: 8px;
  color: #7f8c8d;
  font-style: italic;
}

.message-item.own-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

/* 添加消息气泡的尖角效果 */
.message-item:not(.own-message) .message-content::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 12px;
  width: 0;
  height: 0;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-right: 8px solid #f0f8ff;
}

.message-item.own-message .message-content::before {
  content: '';
  position: absolute;
  right: -8px;
  top: 12px;
  width: 0;
  height: 0;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-left: 8px solid #42b883;
}

/* 添加淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-item {
    max-width: 90%;
  }
  
  .message-text {
    font-size: 0.9rem;
  }
}
</style>