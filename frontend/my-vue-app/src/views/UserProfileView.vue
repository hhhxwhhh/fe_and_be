()<script setup>
import { ref, onMounted } from 'vue'
import { useMainStore } from '../store'
import { authAPI } from '../api'
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
    loading.value=true;
    const userId = route.params.id;
    const response = await authAPI.userProfile(userId);
    user.value=response.data;
    // 获取用户帖子
    const postsResponse = await authAPI.userPosts(userId);
    userPosts.value = postsResponse.data||[];
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }finally {
    loading.value=false;
  }
}

const followUser = async () => {
  try {
    await authAPI.followUser(user.value.id);
    user.value.is_following = true;
    user.value.followers_count += 1;

    if (store.user && store.user.id === user.id){
      store.user.is_following = true;
      store.user.followers_count += 1;
    }
  } catch(error){
    console.error('关注用户失败:', error)
  }
}

const unfollowUser = async () => {
  try {
    await authAPI.unfollowUser(user.value.id);
    user.value.is_following = false;
    user.value.followers_count -= 1;
    if(store.user && store.user.id === user.id){
      store.user.is_following = false;
      store.user.followers_count -= 1;
    }
  } catch (error) {
    console.error('取消关注失败:', error)
  }
}



</script>

<template>
  <div class="profile">
    <div class="container">
      <div v-if="loading" class="loading">
        加载中...
      </div>
      <div v-else-if="user" class="profile-content">
        <div class="profile-header">
          <div class="avatar-section">
            <div class="avatar">
              <img v-if="user.avatar" :src="user.avatar" :alt="user.username">
              <div v-else class="default-avatar">{{ user.username.charAt(0).toUpperCase() }}</div>
            </div>
          </div>
          
          <div class="user-info-section">
            <div class="username-actions">
              <h1>{{ user.username }}</h1>
              <div v-if="store.user && store.user.id !== user.id" class="follow-actions">
                <button 
                  v-if="!user.is_following" 
                  class="follow-button" 
                  @click="followUser"
                >
                  关注
                </button>
                <button 
                  v-else 
                  class="unfollow-button" 
                  @click="unfollowUser"
                >
                  取消关注
                </button>
              </div>
            </div>
            
            <div class="stats">
              <div class="stat-item">
                <span class="stat-number">{{ user.posts?.length || 0 }}</span>
                <span class="stat-label">帖子</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ user.followers_count || 0 }}</span>
                <span class="stat-label">粉丝</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ user.following_count || 0 }}</span>
                <span class="stat-label">关注</span>
              </div>
            </div>
            
            <div class="user-details">
              <p v-if="user.bio" class="bio">{{ user.bio }}</p>
              <p v-if="user.birth_date" class="birth-date">
                <strong>生日:</strong> {{ user.birth_date }}
              </p>
              <p class="email">
                <strong>邮箱:</strong> {{ user.email }}
              </p>
            </div>
          </div>
        </div>
        
        <div class="user-posts">
          <h2>帖子</h2>
          <PostList :posts="userPosts" @post-deleted="userPosts = userPosts.filter(p => p.id !== $event)" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.profile-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.profile-header {
  display: flex;
  padding: 2rem;
  border-bottom: 1px solid #eee;
}

.avatar-section {
  margin-right: 2rem;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
  color: #666;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info-section {
  flex: 1;
}

.username-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.username-actions h1 {
  margin: 0;
}

.follow-button, .unfollow-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.follow-button {
  background-color: #42b883;
  color: white;
}

.unfollow-button {
  background-color: #f0f0f0;
  color: #333;
}

.stats {
  display: flex;
  margin-bottom: 1rem;
}

.stat-item {
  margin-right: 2rem;
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.2rem;
  font-weight: bold;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.user-details p {
  margin: 0.5rem 0;
}

.user-posts {
  padding: 2rem;
}

.user-posts h2 {
  margin-top: 0;
}

.loading {
  text-align: center;
  padding: 2rem;
}
</style>