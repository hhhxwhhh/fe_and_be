<script setup>
import { ref, onMounted } from 'vue'
import { useMainStore } from '../store'
import { authAPI } from '../api'
import PostList from '../components/PostList.vue'
import { useRouter } from 'vue-router'
import { ElSkeleton, ElCard, ElRow, ElCol, ElButton } from 'element-plus'

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

const handlePostDeleted = async (postId) => { 
  userPosts.value = userPosts.value.filter(post => post.id !== postId)

  if(store.user && store.user.posts){
    store.user.posts = store.user.posts.filter(post => post.id !== postId)
  }
}
</script>

<template>
  <div class="profile">
    <div class="profile-container">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="8" animated />
      </div>
      
      <div v-else-if="user" class="profile-content">
        <!-- 用户信息头部 -->
        <div class="profile-header">
          <div class="header-overlay"></div>
          <div class="header-content">
            <div class="avatar-section">
              <div class="avatar-wrapper">
                <div class="avatar-ring">
                  <div class="avatar">
                    <img v-if="user.avatar" :src="user.avatar" :alt="user.username">
                    <div v-else class="default-avatar">{{ user.username.charAt(0).toUpperCase() }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="user-info-section">
              <div class="username-actions">
                <h1 class="username">{{ user.username }}</h1>
                <el-button 
                  type="primary" 
                  @click="editProfile" 
                  round 
                  class="edit-button"
                >
                  编辑资料
                </el-button>
              </div>
              
              <div class="user-stats">
                <div class="stat-item">
                  <div class="stat-value">{{ user.posts?.length || 0 }}</div>
                  <div class="stat-label">帖子</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ user.followers_count || 0 }}</div>
                  <div class="stat-label">粉丝</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ user.following_count || 0 }}</div>
                  <div class="stat-label">关注</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 用户详细信息 -->
        <el-card class="user-details-card">
          <div class="user-details">
            <el-row :gutter="20">
              <el-col :span="24">
                <div class="detail-item" v-if="user.bio">
                  <h3>个人简介</h3>
                  <p class="bio">{{ user.bio }}</p>
                </div>
                
                <div class="detail-item">
                  <h3>联系信息</h3>
                  <div class="contact-info">
                    <p class="email">
                      <i class="el-icon-message"></i>
                      <span>{{ user.email }}</span>
                    </p>
                    <p v-if="user.birth_date" class="birth-date">
                      <i class="el-icon-date"></i>
                      <span>{{ user.birth_date }}</span>
                    </p>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
        
        <!-- 用户帖子 -->
        <div class="user-posts">
          <h2 class="section-title">个人帖子</h2>
          <PostList :posts="userPosts" @post-deleted="handlePostDeleted" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
  padding: 20px 0;
}

.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1rem;
}

.profile-content {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
}

/* 头部样式 */
.profile-header {
  position: relative;
  height: 300px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  overflow: hidden;
}

.header-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
}

.header-content {
  position: relative;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  z-index: 2;
}

.avatar-section {
  margin-right: 2rem;
}

.avatar-ring {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
  animation: rotate 8s linear infinite;
}

.avatar-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar {
  width: 130px;
  height: 130px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  color: #42b883;
  font-size: 3rem;
  font-weight: bold;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info-section {
  flex: 1;
  color: white;
}

.username-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.username {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.edit-button {
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.edit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.user-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.stat-label {
  font-size: 1rem;
  opacity: 0.9;
}

/* 用户详细信息卡片 */
.user-details-card {
  margin: -40px 2rem 2rem;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  border: none;
  overflow: hidden;
  position: relative;
}

.user-details-card :deep(.el-card__body) {
  padding: 1.8rem;
}

.detail-item {
  margin-bottom: 1.5rem;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-item h3 {
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  color: #333;
  font-weight: 600;
  position: relative;
  padding-bottom: 0.5rem;
}

.detail-item h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
}

.bio {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #555;
  margin: 0;
}

.contact-info p {
  display: flex;
  align-items: center;
  margin: 0.8rem 0;
  font-size: 1.1rem;
  color: #555;
}

.contact-info i {
  margin-right: 10px;
  color: #667eea;
  font-size: 1.2rem;
}

/* 帖子部分 */
.user-posts {
  padding: 0 2rem 2rem;
}

.section-title {
  font-size: 1.8rem;
  color: #333;
  margin: 2rem 0 1.5rem;
  font-weight: 600;
  position: relative;
  padding-bottom: 0.8rem;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
}

/* 加载状态 */
.loading {
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  margin: 20px;
}

/* 动画 */
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-header {
    height: auto;
    padding: 2rem 0;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    padding: 1rem;
  }
  
  .avatar-section {
    margin-right: 0;
    margin-bottom: 1.5rem;
  }
  
  .avatar-ring {
    width: 120px;
    height: 120px;
  }
  
  .avatar {
    width: 110px;
    height: 110px;
    font-size: 2.5rem;
  }
  
  .username-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .username {
    font-size: 2rem;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .user-details-card {
    margin: -60px 1rem 1.5rem;
  }
  
  .user-posts {
    padding: 0 1rem 1.5rem;
  }
  
  .section-title {
    font-size: 1.5rem;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .profile-container {
    padding: 0 0.5rem;
  }
  
  .header-content {
    padding: 1rem 0.5rem;
  }
  
  .user-stats {
    gap: 1rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .stat-label {
    font-size: 0.9rem;
  }
  
  .user-details-card :deep(.el-card__body) {
    padding: 1.2rem;
  }
  
  .contact-info p {
    font-size: 1rem;
  }
}
</style>