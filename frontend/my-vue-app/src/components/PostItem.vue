<script setup>
import { ref } from 'vue'
import { useMainStore } from '../store'
import { postAPI, likeAPI, commentAPI, authAPI } from '../api'
import { useRouter } from 'vue-router'
import CommentForm from './CommentForm.vue'
import CommentItem from './CommentItem.vue' 

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['postDeleted'])

const store = useMainStore()
const router = useRouter()
const showComments = ref(false)

const toggleLike = async () => {
  try {
    let response;
    // 根据当前点赞状态决定调用哪个API方法
    if (props.post.is_liked) {
      // 当前已点赞，需要取消点赞
      response = await likeAPI.unlikePost(props.post.id);
    } else {
      // 当前未点赞，需要点赞
      response = await likeAPI.likePost(props.post.id);
    }

    // 使用后端返回的数据更新前端状态
    props.post.is_liked = response.data.liked;
    props.post.likes_count = response.data.likes_count;
    store.toggleLike(props.post.id, response.data.liked);
  } catch (error) {
    console.error('点赞操作失败:', error);
  }
}

const handleCommentAdded = (newComment) => {
  // 这个函数现在只处理顶层评论
  if (!props.post.comments) {
    props.post.comments = []
  }
  props.post.comments.unshift(newComment) // 用 unshift 让新评论显示在最上面
}

const handleReplyAdded = (newReply) => {
  // 当有新的回复时，我们只需要简单地增加总评论数
  // 因为 CommentItem 内部已经处理了 replies 数组的更新
  props.post.comments_count += 1 
}

const deletePost = async () => {
  if (confirm('确定要删除这个帖子吗？')) {
    try {
      await postAPI.deletePost(props.post.id);
      emit('postDeleted', props.post.id);
    } catch (error) {
      console.error('删除帖子失败:', error);
      alert('删除帖子失败');
    }
  }
}

const followUser = async (userId) => {
  try {
    await authAPI.followUser(userId);
    props.post.is_following = true;
    // 更新当前用户 
    if (store.user && store.user.id === userId) {
      store.user.is_following = true;
      store.user.follwoing_count += 1;
    }
  } catch (error) {
    console.error('关注用户失败:', error)
  }
}

const unfollowUser = async (userId) => {
  try {
    await authAPI.unfollowUser(userId);
    props.post.is_following = false;
    if (store.user && store.user.id === userId) {
      store.user.is_following = false;
      store.user.followers_count -= 1;
    }
  } catch (error) {
    console.error('取消关注失败:', error)
  }
}

const goToUserProfile = (userId) => {
  router.push(`/user-profile/${userId}`)
}
</script>

<template>
  <div class="post-item">
    <div class="post-header">
      <div class="post-author">
        <h3 @click="goToUserProfile(post.author_id)" class="author-link">{{ post.author.username }}</h3>
        <div v-if="store.user && store.user.id !== post.author_id" class="follow-actions">
          <button v-if="!post.is_following" @click="followUser(post.author_id)" class="follow-button">
            关注
          </button>
          <button v-else @click="unfollowUser(post.author_id)" class="unfollow-button">
            已关注
          </button>
        </div>
      </div>
      <span class="post-date">{{ new Date(post.created_at).toLocaleString() }}</span>
    </div>

    <div class="post-content">
      <p>{{ post.content }}</p>
      <div v-if="post.image" class="post-image">
        <img :src="post.image" alt="Post image" />
      </div>
    </div>

    <div class="post-actions">
      <button @click="toggleLike" :class="{ liked: post.is_liked }" class="action-button">
        <span class="heart-icon" :class="{ filled: post.is_liked }">❤</span>
        {{ post.likes_count }}
      </button>
      <button @click="showComments = !showComments" class="action-button">
        <span class="comment-icon">💬</span>
        {{ post.comments ? post.comments.length : 0 }}
      </button>
      <button v-if="store.user && store.user.id === post.author_id" @click="deletePost"
        class="action-button delete-button">
        <span class="delete-icon">🗑</span>
      </button>
    </div>

    <div v-if="showComments" class="post-comments">
      <div class="comments-list">
        <CommentItem 
          v-for="comment in post.comments" 
          :key="comment.id" 
          :comment="comment"
          @reply-added="handleReplyAdded"
       />

        <div v-if="!post.comments || post.comments.length === 0" class="no-comments">
          暂无评论，来抢沙发吧！
        </div>
      </div>

      <CommentForm :post-id="post.id" @comment-added="handleCommentAdded" />
    </div>
  </div>
</template>

<style scoped>
.comment-image {
  margin-top: 0.5rem;
}

.comment-image img {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}



.post-item {
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: none;
}

.post-item:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #eee;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-link {
  margin: 0;
  cursor: pointer;
  color: #2c3e50;
  font-weight: 600;
  font-size: 1.1rem;
  transition: color 0.2s;
}

.author-link:hover {
  color: #42b883;
}

.follow-button,
.unfollow-button {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
}

.follow-button {
  background: linear-gradient(45deg, #42b883, #3498db);
  color: white;
  box-shadow: 0 2px 6px rgba(66, 184, 131, 0.3);
}

.follow-button:hover {
  background: linear-gradient(45deg, #3aa876, #2980b9);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(66, 184, 131, 0.4);
}

.unfollow-button {
  background: #f1f2f6;
  color: #6c757d;
  border: 1px solid #e2e6ea;
}

.unfollow-button:hover {
  background: #e2e6ea;
}

.post-date {
  color: #8d99ae;
  font-size: 0.85rem;
}

.post-content p {
  margin: 1rem 0;
  font-size: 1rem;
  line-height: 1.6;
  color: #343a40;
}

.post-image {
  margin: 1rem 0;
}

.post-image img {
  max-width: 100%;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.post-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  background: #f8f9fa;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  color: #495057;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.action-button:hover {
  background: #e9ecef;
  transform: translateY(-1px);
}

.action-button.liked {
  background: #fff5f5;
  color: #e74c3c;
}

.heart-icon {
  transition: transform 0.2s;
}

.heart-icon.filled {
  transform: scale(1.2);
}

.delete-button {
  margin-left: auto;
  background: #fff5f5;
  color: #e74c3c;
}

.delete-button:hover {
  background: #ffecec;
}

.post-comments {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.comments-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 1rem;
  padding-right: 0.5rem;
}

.comment {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.comment-header strong {
  color: #2c3e50;
}

.comment-date {
  font-size: 0.75rem;
  color: #8d99ae;
}

.comment-content {
  color: #495057;
  line-height: 1.5;
}

.no-comments {
  text-align: center;
  color: #8d99ae;
  font-style: italic;
  padding: 1rem;
}

.add-comment {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.comment-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  transition: border-color 0.2s;
  font-size: 0.95rem;
}

.comment-input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
}

.comment-button {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(45deg, #42b883, #3498db);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(66, 184, 131, 0.3);
}

.comment-button:hover {
  background: linear-gradient(45deg, #3aa876, #2980b9);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(66, 184, 131, 0.4);
}

/* 滚动条样式 */
.comments-list::-webkit-scrollbar {
  width: 6px;
}

.comments-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.comments-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.comments-list::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>