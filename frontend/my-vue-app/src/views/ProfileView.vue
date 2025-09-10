<script setup>
import { ref, onMounted } from 'vue'
import { useMainStore } from '../store'
import { authAPI } from '../api'
import PostList from '../components/PostList.vue'
import { useRouter } from 'vue-router'

const store = useMainStore()
const router = useRouter()
const user = ref(null)
const userPosts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    // 获取当前用户信息
    const response = await authAPI.profile()
    user.value = response.data
    store.setUser(user.value)
    userPosts.value = user.value.posts || []
  } catch (error) {
    console.error('获取用户信息失败:', error)
  } finally {
    loading.value = false
  }
})

const editProfile = () => {
  // 跳转到编辑个人资料页面
  router.push('/edit-profile')
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
              <button class="edit-button" @click="editProfile">编辑资料</button>
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
          <h2>我的帖子</h2>
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
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.avatar-section {
  margin-right: 1.5rem;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #42b883;
  color: white;
  font-size: 2.5rem;
  font-weight: bold;
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
  font-size: 1.8rem;
}

.edit-button {
  padding: 0.4rem 1rem;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.edit-button:hover {
  background-color: #e0e0e0;
}

.stats {
  display: flex;
  margin-bottom: 1rem;
}

.stat-item {
  margin-right: 1.5rem;
}

.stat-number {
  font-weight: bold;
  font-size: 1.2rem;
  margin-right: 0.3rem;
}

.stat-label {
  color: #666;
}

.user-details .bio {
  margin: 0.5rem 0;
  line-height: 1.4;
}

.user-details p {
  margin: 0.3rem 0;
  color: #333;
}

.user-posts {
  padding: 1.5rem;
}

.user-posts h2 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
}

.loading {
  text-align: center;
  padding: 2rem;
}
</style>