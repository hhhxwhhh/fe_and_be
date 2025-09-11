<script setup>
import { ref } from 'vue'
import { useMainStore } from '../store'
import { postAPI, likeAPI, commentAPI, authAPI } from '../api'
import { useRouter } from 'vue-router'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['postDeleted'])

const store = useMainStore()
const router = useRouter()
const newComment = ref('')
const showComments = ref(false)

const toggleLike = async () => {
  try {
    const response = await likeAPI.likePost(props.post.id);
    props.post.is_liked=response.data.liked;
    if(response.data.liked){
      props.post.likes_count = (props.post.likes_count || 0)+1;
    }else{
      props.post.likes_count = Math.max(0, props.post.likes_count-1);
    }
    store.toggleLike(props.post.id,response.data.liked);
  } catch (error) {
    console.error('点赞操作失败:', error)
  }
}

const addComment = async () => {
  if(!newComment.value.trim()){
    return;
  }
  try{
    const response = await commentAPI.createComment(
      props.post.id,
      {
        content: newComment.value
      })
    newComment.value = '';
    if(!props.post.comments){
      props.post.comments = [];
    }
    store.addCommentToPost(props.post.id, response.data)
    }catch(error){
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

const followUser = async (userId) => {
  try {
    await authAPI.followUser(userId);
    props.post.is_following = true;
    if(store.user && store.user.id === userId){
      store.user.is_following = true;
    }
  } catch(error){
    console.error('关注用户失败:', error)
  }
}

const unfollowUser = async (userId) => {
  try{
    await authAPI.unfollowUser(userId);
    props.post.is_following = false;
    if(store.user && store.user.id === userId){
      store.user.is_following = false;
    }
  } catch(error){
    console.error('取消关注失败:', error)
  }
}

const goToUserProfile = (userId) => {
  router.push(`/profile/${userId}`)
}

</script>

<template>
  <div class="post-item">
    <div class="post-header">
      <div class="post-author">
        <h3 @click="goToUserProfile(post.author_id)" class="author-link">{{ post.author }}</h3>
        <div v-if="store.user && store.user.id !== post.author_id" class="follow-actions">
          <button 
            v-if="!post.is_following" 
            @click="followUser(post.author_id)"
            class="follow-button"
          >
            关注
          </button>
          <button 
            v-else 
            @click="unfollowUser(post.author_id)"
            class="unfollow-button"
          >
            取消关注
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

.post-author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.author-link {
  margin: 0;
  cursor: pointer;
  color: #42b883;
}

.author-link:hover {
  text-decoration: underline;
}

.follow-button, .unfollow-button {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.follow-button {
  background-color: #42b883;
  color: white;
}

.unfollow-button {
  background-color: #f0f0f0;
  color: #333;
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