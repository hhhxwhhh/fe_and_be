<script setup>
import { ref } from 'vue'
import { useMainStore } from '../store'
import { likeAPI, commentAPI, postAPI } from '../api'
import CommentForm from './CommentForm.vue'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['postDeleted'])

const store = useMainStore()
const showComments = ref(false)
const comments = ref(props.post.comments || [])
const newComment = ref('')

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  return new Date(dateString).toLocaleDateString('zh-CN', options)
}

const toggleLike = async () => {
  try {
    if (props.post.likes?.find(like => like.user === store.user?.id)) {
      // 取消点赞
      await likeAPI.unlikePost(props.post.id)
    } else {
      // 点赞
      await likeAPI.likePost(props.post.id)
    }
    store.toggleLike(props.post.id)
  } catch (error) {
    console.error('点赞操作失败:', error)
  }
}

const addComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    const response = await commentAPI.createComment(props.post.id, {
      content: newComment.value
    })
    
    comments.value.push(response.data)
    newComment.value = ''
  } catch (error) {
    console.error('添加评论失败:', error)
  }
}

const deletePost = async () => {
  if (!confirm('确定要删除这个帖子吗？')) return
  
  try {
    await postAPI.deletePost(props.post.id)
    emit('postDeleted')
  } catch (error) {
    console.error('删除帖子失败:', error)
  }
}
</script>

<template>
  <div class="post-item">
    <div class="post-header">
      <div class="user-info">
        <h4>{{ post.author.username }}</h4>
        <span class="post-date">{{ formatDate(post.created_at) }}</span>
      </div>
      <div v-if="store.user && store.user.id === post.author.id" class="post-actions">
        <button @click="deletePost" class="btn-delete">删除</button>
      </div>
    </div>
    
    <div class="post-content">
      <p>{{ post.content }}</p>
      <div v-if="post.image" class="post-image">
        <img :src="post.image" alt="Post image" />
      </div>
    </div>
    
    <div class="post-stats">
      <div class="likes" @click="toggleLike">
        <span :class="{ liked: post.likes?.find(like => like.user === store.user?.id) }">
          👍 {{ post.likes?.length || 0 }}
        </span>
      </div>
      <div class="comments-count" @click="showComments = !showComments">
        💬 {{ comments.length }}
      </div>
    </div>
    
    <div class="post-comments" v-if="showComments">
      <div class="comments-list">
        <div v-for="comment in comments" :key="comment.id" class="comment">
          <div class="comment-author">{{ comment.author.username }}</div>
          <div class="comment-content">{{ comment.content }}</div>
          <div class="comment-date">{{ formatDate(comment.created_at) }}</div>
        </div>
      </div>
      
      <CommentForm 
        :post-id="post.id" 
        @comment-added="(comment) => comments.push(comment)"
      />
    </div>
  </div>
</template>

<style scoped>
.post-item {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.user-info h4 {
  margin: 0;
  color: #333;
}

.post-date {
  font-size: 0.8rem;
  color: #888;
}

.btn-delete {
  background: none;
  border: none;
  color: red;
  cursor: pointer;
  font-size: 0.9rem;
}

.post-content {
  margin-bottom: 1rem;
}

.post-content p {
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.post-image img {
  max-width: 100%;
  border-radius: 4px;
}

.post-stats {
  display: flex;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  padding: 0.5rem 0;
  margin-bottom: 1rem;
}

.likes, .comments-count {
  margin-right: 1rem;
  cursor: pointer;
  user-select: none;
}

.liked {
  color: #42b883;
  font-weight: bold;
}

.comments-list {
  margin-bottom: 1rem;
}

.comment {
  background: #f9f9f9;
  border-radius: 4px;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.comment-author {
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.comment-content {
  margin-bottom: 0.25rem;
}

.comment-date {
  font-size: 0.8rem;
  color: #888;
}
</style>