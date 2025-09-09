<script setup>
import { ref } from 'vue'
import { useMainStore } from '../store'
import { postAPI, likeAPI, commentAPI } from '../api'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['postDeleted'])

const store = useMainStore()
const newComment = ref('')
const showComments = ref(false)

const toggleLike = async () => {
  try {
    if (props.post.is_liked) {
      await likeAPI.unlikePost(props.post.id)
    } else {
      await likeAPI.likePost(props.post.id)
    }
    // 重新加载帖子数据或更新状态
    // 这里可以发送事件让父组件重新加载数据
  } catch (error) {
    console.error('点赞操作失败:', error)
  }
}

const addComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    await commentAPI.createComment(props.post.id, {
      content: newComment.value
    })
    newComment.value = ''
    // 重新加载帖子数据或更新状态
  } catch (error) {
    console.error('添加评论失败:', error)
  }
}

const deletePost = async () => {
  if (confirm('确定要删除这个帖子吗？')) {
    try {
      await postAPI.deletePost(props.post.id)
      emit('postDeleted', props.post.id)
    } catch (error) {
      console.error('删除帖子失败:', error)
    }
  }
}
</script>

<template>
  <div class="post-item">
    <div class="post-header">
      <h3>{{ post.author }}</h3>
      <span class="post-date">{{ new Date(post.created_at).toLocaleString() }}</span>
    </div>
    
    <div class="post-content">
      <p>{{ post.content }}</p>
      <div v-if="post.image" class="post-image">
        <img :src="post.image" alt="Post image" />
      </div>
    </div>
    
    <div class="post-actions">
      <button @click="toggleLike" :class="{ liked: post.is_liked }">
        {{ post.is_liked ? '取消点赞' : '点赞' }} ({{ post.likes_count }})
      </button>
      <button @click="showComments = !showComments">
        {{ showComments ? '隐藏评论' : '显示评论' }}
      </button>
      <button v-if="store.user && store.user.id === post.author_id" @click="deletePost">
        删除
      </button>
    </div>
    
    <div v-if="showComments" class="post-comments">
      <div class="comments-list">
        <div v-for="comment in post.comments" :key="comment.id" class="comment">
          <strong>{{ comment.author }}:</strong>
          <span>{{ comment.content }}</span>
        </div>
      </div>
      
      <div class="add-comment">
        <input 
          v-model="newComment" 
          placeholder="添加评论..." 
          @keyup.enter="addComment"
        />
        <button @click="addComment">发布</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: white;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.post-header h3 {
  margin: 0;
}

.post-date {
  color: #999;
  font-size: 0.9rem;
}

.post-content p {
  margin: 0.5rem 0;
}

.post-image img {
  max-width: 100%;
  border-radius: 4px;
}

.post-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.post-actions button {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.post-actions button:hover {
  background: #f5f5f5;
}

.post-actions button.liked {
  background: #42b883;
  color: white;
  border-color: #42b883;
}

.post-comments {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.comment {
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.add-comment {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.add-comment input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.add-comment button {
  padding: 0.5rem 1rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>