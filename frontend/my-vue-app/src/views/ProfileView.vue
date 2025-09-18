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
              
              <div class="user-bio" v-if="user.bio">
                <p>{{ user.bio }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 用户详细信息 -->
        <div class="user-details-section">
          <el-row :gutter="30">
            <el-col :span="16">
              <el-card class="info-card">
                <div class="card-header">
                  <h3>个人信息</h3>
                </div>
                <div class="card-content">
                  <div class="info-item">
                    <i class="el-icon-message"></i>
                    <div class="info-text">
                      <span class="info-label">邮箱</span>
                      <span class="info-value">{{ user.email }}</span>
                    </div>
                  </div>
                  <div class="info-item" v-if="user.birth_date">
                    <i class="el-icon-date"></i>
                    <div class="info-text">
                      <span class="info-label">生日</span>
                      <span class="info-value">{{ user.birth_date }}</span>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="8">
              <el-card class="stats-card">
                <div class="card-header">
                  <h3>统计信息</h3>
                </div>
                <div class="card-content">
                  <div class="stats-grid">
                    <div class="stat-box">
                      <div class="stat-value">{{ user.posts?.length || 0 }}</div>
                      <div class="stat-label">帖子</div>
                    </div>
                    <div class="stat-box">
                      <div class="stat-value">{{ user.followers_count || 0 }}</div>
                      <div class="stat-label">粉丝</div>
                    </div>
                    <div class="stat-box">
                      <div class="stat-value">{{ user.following_count || 0 }}</div>
                      <div class="stat-label">关注</div>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <!-- 用户帖子 -->
        <div class="user-posts">
          <div class="section-header">
            <h2 class="section-title">个人帖子</h2>
            <div class="section-divider"></div>
          </div>
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.profile-content {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

/* 头部样式 */
.profile-header {
  position: relative;
  height: 350px;
  background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  overflow: hidden;
}

.profile-header::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
  transform: rotate(30deg);
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 3rem;
  display: flex;
  align-items: center;
  z-index: 2;
}

.avatar-section {
  margin-right: 3rem;
}

.avatar-ring {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  animation: rotate 10s linear infinite;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.avatar-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar {
  width: 148px;
  height: 148px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  color: #42b883;
  font-size: 3.5rem;
  font-weight: bold;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
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
  margin-bottom: 1.5rem;
}

.username {
  margin: 0;
  font-size: 2.8rem;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.edit-button {
  padding: 12px 30px;
  font-size: 1.1rem;
  font-weight: 500;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
}

.edit-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
}

.user-stats {
  display: flex;
  gap: 3rem;
  margin-bottom: 1.5rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stat-label {
  font-size: 1.1rem;
  opacity: 0.9;
  letter-spacing: 0.5px;
}

.user-bio {
  max-width: 80%;
  font-size: 1.2rem;
  line-height: 1.6;
  opacity: 0.9;
}

.user-bio p {
  margin: 0;
}

/* 用户详细信息区域 */
.user-details-section {
  padding: 2.5rem 3rem 1rem;
}

.card-header {
  margin-bottom: 1.5rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  position: relative;
  padding-bottom: 0.8rem;
}

.card-header h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50px;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
}

.info-card, .stats-card {
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
  border: none;
  overflow: hidden;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
}

.info-card:hover, .stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
}

.info-card :deep(.el-card__body), 
.stats-card :deep(.el-card__body) {
  padding: 1.8rem;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item i {
  font-size: 1.5rem;
  color: #667eea;
  margin-right: 1rem;
  width: 30px;
  text-align: center;
}

.info-text {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 0.9rem;
  color: #999;
  margin-bottom: 0.2rem;
}

.info-value {
  font-size: 1.1rem;
  color: #333;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-box {
  text-align: center;
  padding: 1.2rem 0;
  border-radius: 10px;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  transition: all 0.3s ease;
}

.stat-box:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.3rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

/* 帖子部分 */
.user-posts {
  padding: 0 3rem 3rem;
}

.section-header {
  margin: 2rem 0 1.5rem;
}

.section-title {
  font-size: 1.8rem;
  color: #333;
  margin: 0 0 1rem;
  font-weight: 600;
}

.section-divider {
  height: 3px;
  width: 60px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
}

/* 加载状态 */
.loading {
  padding: 3rem;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
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
@media (max-width: 992px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .avatar-section {
    margin-right: 0;
    margin-bottom: 2rem;
  }
  
  .username-actions {
    justify-content: center;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .user-bio {
    max-width: 100%;
    text-align: center;
  }
  
  .user-details-section {
    padding: 2rem;
  }
}

@media (max-width: 768px) {
  .profile-header {
    height: auto;
    padding: 2rem 0;
  }
  
  .header-content {
    padding: 1.5rem;
  }
  
  .avatar-ring {
    width: 130px;
    height: 130px;
  }
  
  .avatar {
    width: 118px;
    height: 118px;
    font-size: 2.8rem;
  }
  
  .username {
    font-size: 2.2rem;
  }
  
  .user-stats {
    gap: 1.5rem;
  }
  
  .stat-value {
    font-size: 1.8rem;
  }
  
  .user-details-section {
    padding: 1.5rem;
  }
  
  .user-posts {
    padding: 0 1.5rem 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .profile-container {
    padding: 0 0.5rem;
  }
  
  .username {
    font-size: 1.8rem;
  }
  
  .edit-button {
    padding: 10px 20px;
    font-size: 1rem;
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
  
  .info-item {
    flex-direction: column;
    text-align: center;
  }
  
  .info-item i {
    margin-right: 0;
    margin-bottom: 0.5rem;
  }
}
</style>