<script setup>
import { ref } from 'vue'
import CommentForm from './CommentForm.vue'

// 这个组件接收一条评论作为 prop
const props = defineProps({
  comment: {
    type: Object,
    required: true
  }
})

// 定义一个 emit，用于通知父组件有新的回复被添加
const emit = defineEmits(['replyAdded'])

// 控制回复输入框的显示/隐藏
const showReplyForm = ref(false)

// 当回复成功后，由 CommentForm 组件调用
const handleReplyAdded = (newReply) => {
  // 如果当前评论还没有 replies 数组，就创建一个
  if (!props.comment.replies) {
    props.comment.replies = []
  }
  props.comment.replies.push(newReply)
  // 关闭回复框
  showReplyForm.value = false
  // 通知顶层的 PostItem 组件
  emit('replyAdded', newReply)
}
</script>

<template>
  <div class="comment-item">
    <div class="comment-main">
      <div class="comment-header">
        <strong>{{ comment.author.username }}</strong>
        <span class="comment-date">{{ new Date(comment.created_at).toLocaleDateString() }}</span>
      </div>
      <div class="comment-content">
        <p>{{ comment.content }}</p>
        <div v-if="comment.image" class="comment-image">
          <img :src="comment.image" alt="Comment image" />
        </div>
      </div>
      <div class="comment-actions">
        <button @click="showReplyForm = !showReplyForm" class="reply-button">回复</button>
      </div>
    </div>

    <!-- 回复输入框 -->
    <div v-if="showReplyForm" class="reply-form-container">
      <CommentForm 
        :post-id="comment.post" 
        :parent-id="comment.id" 
        @comment-added="handleReplyAdded" 
        is-reply 
      />
    </div>

    <!-- 递归地显示所有回复 -->
    <div v-if="comment.replies && comment.replies.length > 0" class="comment-replies">
      <CommentItem 
        v-for="reply in comment.replies" 
        :key="reply.id" 
        :comment="reply"
        @reply-added="emit('replyAdded', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.comment-item {
  margin-bottom: 1rem;
}

.comment-main {
  padding: 1rem;
  background: var(--chat-cardBackground);
  border: 1px solid var(--chat-border);
  border-radius: 8px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.comment-header strong {
  color: var(--chat-textPrimary);
  font-weight: 600;
}

.comment-date {
  font-size: 0.75rem;
  color: var(--chat-textSecondary);
}

.comment-content {
  color: var(--chat-textPrimary);
  line-height: 1.5;
}

.comment-image {
  margin-top: 0.5rem;
}

.comment-image img {
  max-width: 100%;
  border-radius: 8px;
}

.comment-actions {
  margin-top: 0.5rem;
  text-align: right;
}

.reply-button {
  background: none;
  border: none;
  color: var(--chat-textSecondary);
  cursor: pointer;
  font-size: 0.85rem;
}
.reply-button:hover {
  color: var(--chat-primary);
}

.reply-form-container {
  margin-top: 1rem;
  padding-left: 2rem; /* 给回复框加一点缩进 */
}

.comment-replies {
  margin-top: 1rem;
  padding-left: 2.5rem; /* 给回复列表加一点缩进 */
  border-left: 2px solid var(--chat-border);
}
</style>