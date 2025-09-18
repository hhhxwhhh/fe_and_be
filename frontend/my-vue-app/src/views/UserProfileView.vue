<script setup>
import { ref, onMounted } from 'vue'
import { useMainStore } from '../store'
import { authAPI, postAPI } from '../api'
import PostList from '../components/PostList.vue'
import { useRoute, useRouter } from 'vue-router'

const store = useMainStore()
const route = useRoute()
const router = useRouter()
const user = ref(null)
const userPosts = ref([])
const loading = ref(true)

onMounted(async () => {
  await loadUserProfile()
})

const loadUserProfile = async () => {
  try {
    loading.value = true
    const userId = route.params.id
    const response = await authAPI.userProfile(userId)
    user.value = response.data
    
    // 获取用户帖子 - 使用posts API而不是auth API
    const postsResponse = await postAPI.getUserPosts(userId)
    // 确保返回的是数组格式
    userPosts.value = Array.isArray(postsResponse.data) ? postsResponse.data : []
  } catch (error) {
    console.error('获取用户信息失败:', error)
    userPosts.value = [] // 确保即使出错也设置为空数组
  } finally {
    loading.value = false
  }
}

const followUser = async () => {
  try {
    await authAPI.followUser(user.value.id)
    user.value.is_following = true
    user.value.followers_count += 1

    if (store.user && store.user.id === user.value.id) {
      store.user.is_following = true
      store.user.followers_count += 1
    }
  } catch (error) {
    console.error('关注用户失败:', error)
  }
}

const unfollowUser = async () => {
  try {
    await authAPI.unfollowUser(user.value.id)
    user.value.is_following = false
    user.value.followers_count -= 1
    
    if (store.user && store.user.id === user.value.id) {
      store.user.is_following = false
      store.user.followers_count -= 1
    }
  } catch (error) {
    console.error('取消关注失败:', error)
  }
}

const sendMessage = () => {
  // 跳转到与该用户的私信对话页面
  router.push(`/messages/${user.value.id}`)
}
</script>

<template>
  <div class="profile-page">
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="user" class="profile-content">
      <div class="profile-header">
        <div class="profile-info">
          <div class="avatar-section">
            <img 
              v-if="user.avatar" 
              :src="user.avatar" 
              :alt="user.username"
              class="avatar"
            >
            <div v-else class="avatar-placeholder">
              {{ user.username.charAt(0).toUpperCase() }}
            </div>
          </div>
          
          <div class="user-details">
            <h1>{{ user.username }}</h1>
            <p v-if="user.bio" class="bio">{{ user.bio }}</p>
            
            <div class="user-stats">
              <span class="stat-item">
                <strong>{{ userPosts.length }}</strong>
                <span>帖子</span>
              </span>
              <span class="stat-item">
                <strong>{{ user.followers_count }}</strong>
                <span>粉丝</span>
              </span>
              <span class="stat-item">
                <strong>{{ user.following_count }}</strong>
                <span>关注</span>
              </span>
            </div>
          </div>
        </div>
        
        <div class="profile-actions">
          <button 
            v-if="store.user && store.user.id !== user.id"
            @click="followUser" 
            v-show="!user.is_following"
            class="follow-button"
          >
            关注
          </button>
          
          <button 
            v-if="store.user && store.user.id !== user.id"
            @click="unfollowUser" 
            v-show="user.is_following"
            class="unfollow-button"
          >
            已关注
          </button>
          
          <!-- 添加发送私信按钮 -->
          <button 
            v-if="store.user && store.user.id !== user.id"
            @click="sendMessage"
            class="message-button"
          >
            私信
          </button>
        </div>
      </div>
      
      <div class="profile-posts">
        <h2>帖子</h2>
        <PostList :posts="userPosts" />
      </div>
    </div>
  </div>
</template>

<!-- ... styles remain the same ... -->

<style scoped>
.profile-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30px;
  padding: 30px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

.profile-header:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.profile-info {
  display: flex;
  gap: 30px;
  flex: 1;
}

.avatar-section {
  flex-shrink: 0;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #f0f0f0;
}

.avatar-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #42b883, #3498db);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 2.5rem;
  border: 3px solid #ffffff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.user-details {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.user-details h1 {
  margin: 0 0 15px 0;
  font-size: 2rem;
  color: #2c3e50;
  font-weight: 700;
}

.bio {
  margin: 0 0 20px 0;
  color: #555;
  line-height: 1.6;
  font-size: 1.1rem;
}

.user-stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-item strong {
  font-size: 1.4rem;
  color: #2c3e50;
}

.stat-item span {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-top: 4px;
}

.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: center;
}

.follow-button, .unfollow-button, .message-button {
  padding: 10px 24px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  min-width: 100px;
}

.follow-button {
  background: linear-gradient(45deg, #42b883, #3498db);
  color: white;
  box-shadow: 0 4px 10px rgba(66, 184, 131, 0.3);
}

.follow-button:hover {
  background: linear-gradient(45deg, #3aa876, #2980b9);
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(66, 184, 131, 0.4);
}

.unfollow-button {
  background: #f1f2f6;
  color: #6c757d;
  border: 1px solid #e2e6ea;
}

.unfollow-button:hover {
  background: #e2e6ea;
  transform: translateY(-2px);
}

.message-button {
  background: #6c5ce7;
  color: white;
  box-shadow: 0 4px 10px rgba(108, 92, 231, 0.3);
}

.message-button:hover {
  background: #5d4de0;
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(108, 92, 231, 0.4);
}

.profile-posts {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.profile-posts h2 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 1.5rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 15px;
  }
  
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 20px;
  }
  
  .profile-info {
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }
  
  .user-details h1 {
    font-size: 1.7rem;
  }
  
  .user-stats {
    justify-content: center;
    gap: 20px;
  }
  
  .profile-actions {
    flex-direction: row;
    margin-top: 20px;
    justify-content: center;
  }
  
  .profile-posts {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .avatar {
    width: 100px;
    height: 100px;
  }
  
  .avatar-placeholder {
    width: 100px;
    height: 100px;
    font-size: 2rem;
  }
  
  .user-stats {
    gap: 15px;
  }
  
  .stat-item strong {
    font-size: 1.2rem;
  }
}
</style>



