<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMainStore } from '../store'
import { postAPI } from '../api'
import { ElRow, ElCol, ElCard, ElSkeleton, ElStatistic, ElDivider, ElButton } from 'element-plus'
import { useRouter } from 'vue-router'

const store = useMainStore()
const router = useRouter()
const loading = ref(false)
const stats = ref({
  totalPosts: 0,
  totalLikes: 0,
  totalComments: 0
})

onMounted(async () => {
  await loadPosts()
  calculateStats()
})

const posts = computed(() => store.posts.slice(0, 5)) // 只显示前5个帖子作为预览

const loadPosts = async () => {
  try {
    loading.value = true
    const response = await postAPI.getPosts()
    store.setPosts(response.data)
  } catch (error) {
    console.error('加载帖子失败:', error)
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  stats.value.totalPosts = store.posts.length
  stats.value.totalLikes = store.posts.reduce((sum, post) => sum + (post.likes_count || 0), 0)
  stats.value.totalComments = store.posts.reduce((sum, post) => sum + (post.comments?.length || 0), 0)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

// 新增：导航到关注流页面
const goToFollowing = () => {
  router.push('/following')
}

// 新增：导航到论坛页面
const goToForum = () => {
  router.push('/forum')
}
</script>
<template>
  <div class="home">
    <!-- 主要欢迎区域 -->
    <el-row justify="center">
      <el-col :span="24">
        <div class="hero-section">
          <div class="hero-content">
            <div class="hero-overlay"></div>
            <div class="hero-text">
              <h1 class="hero-title">欢迎来到社交网络社区</h1>
              <p class="hero-subtitle">一个分享想法、经验和知识的友好平台</p>
              
              <div class="hero-actions" v-if="!store.user">
                <el-button type="primary" size="large" @click="goToLogin" round class="hero-btn">登录</el-button>
                <el-button type="success" size="large" @click="goToRegister" round class="hero-btn">注册</el-button>
              </div>
              
              <div class="hero-stats" v-else>
                <p class="welcome-text">你好，{{ store.user.username }}！欢迎回到社区。</p>
                <div class="user-navigation">
                  <el-button type="primary" @click="goToFollowing" round class="hero-btn">查看关注</el-button>
                  <el-button type="success" @click="goToForum" round class="hero-btn forum-btn">进入论坛</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 社区统计数据 -->
    <el-row justify="center" class="stats-section">
      <el-col :span="22">
        <div class="stats-container">
          <el-row :gutter="30" justify="center">
            <el-col :span="8" :xs="24" class="stat-item">
              <div class="stat-card">
                <div class="stat-icon posts-icon">
                  <i class="el-icon-document"></i>
                </div>
                <div class="stat-info">
                  <el-statistic title="帖子总数" :value="stats.totalPosts" />
                </div>
              </div>
            </el-col>
            <el-col :span="8" :xs="24" class="stat-item">
              <div class="stat-card">
                <div class="stat-icon likes-icon">
                  <i class="el-icon-thumb"></i>
                </div>
                <div class="stat-info">
                  <el-statistic title="点赞总数" :value="stats.totalLikes" />
                </div>
              </div>
            </el-col>
            <el-col :span="8" :xs="24" class="stat-item">
              <div class="stat-card">
                <div class="stat-icon comments-icon">
                  <i class="el-icon-chat-dot-round"></i>
                </div>
                <div class="stat-info">
                  <el-statistic title="评论总数" :value="stats.totalComments" />
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
    </el-row>
    
    <!-- 主要内容区域 -->
    <el-row justify="center" class="content-section">
      <el-col :span="16" class="posts-section">
        <el-card class="preview-card latest-posts-card">
          <template #header>
            <div class="card-header">
              <span>最新帖子</span>
              <el-tag type="success" class="card-tag">NEW</el-tag>
            </div>
          </template>
          
          <div v-if="loading">
            <el-skeleton :rows="3" animated />
          </div>
          
          <div v-else-if="posts && posts.length > 0" class="posts-preview">
            <div 
              v-for="post in posts" 
              :key="post.id" 
              class="post-preview-item"
              @click="() => router.push(`/post/${post.id}`)"
            >
              <h3 class="post-title">{{ post.content.substring(0, 60) }}{{ post.content.length > 60 ? '...' : '' }}</h3>
              <div class="post-meta">
                <span class="author">作者: {{ post.author }}</span>
                <span class="date">{{ formatDate(post.created_at) }}</span>
                <span class="likes">👍 {{ post.likes_count || 0 }}</span>
                <span class="comments">💬 {{ post.comments?.length || 0 }}</span>
              </div>
            </div>
            
            <div class="view-all">
              <el-button 
                type="primary" 
                link 
                @click="() => router.push('/forum')"
                v-if="store.user"
              >
                查看所有帖子 →
              </el-button>
              <el-button 
                type="primary" 
                link 
                @click="goToLogin"
                v-else
              >
                登录查看更多帖子 →
              </el-button>
            </div>
          </div>
          
          <div v-else class="no-posts">
            <p>暂无帖子</p>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧栏 -->
      <el-col :span="7" class="sidebar">
        <!-- 关注用户 -->
        <div class="sidebar-section">
          <el-card class="features-card following-card" v-if="store.user">
            <template #header>
              <div class="card-header">
                <span>我的关注</span>
                <el-badge :value="store.user.following_count || 0" class="card-badge">
                  <el-button size="small" type="primary" @click="goToFollowing">查看</el-button>
                </el-badge>
              </div>
            </template>
            
            <div class="following-content">
              <div class="following-stats">
                <div class="stat-item">
                  <div class="stat-number">{{ store.user.following_count || 0 }}</div>
                  <div class="stat-label">关注</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">{{ store.user.follower_count || 0 }}</div>
                  <div class="stat-label">粉丝</div>
                </div>
              </div>
              <el-button type="primary" @click="goToFollowing" style="margin-top: 15px;" round class="full-width-btn">
                查看关注用户的内容
              </el-button>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
    
    <!-- 社区特色部分（移到底部） -->
    <el-row justify="center" class="community-features-section">
      <el-col :span="22">
        <el-card class="features-card community-card">
          <template #header>
            <div class="card-header">
              <span>社区特色</span>
            </div>
          </template>
          
          <div class="features-container">
            <el-row :gutter="30">
              <el-col :span="8" :xs="24" class="feature-col">
                <div class="feature-item">
                  <div class="feature-icon">👥</div>
                  <h3>友好社区</h3>
                  <p>友善交流，互相尊重的社区环境</p>
                </div>
              </el-col>
              <el-col :span="8" :xs="24" class="feature-col">
                <div class="feature-item">
                  <div class="feature-icon">💡</div>
                  <h3>知识分享</h3>
                  <p>分享你的想法、经验和知识</p>
                </div>
              </el-col>
              <el-col :span="8" :xs="24" class="feature-col">
                <div class="feature-item">
                  <div class="feature-icon">💬</div>
                  <h3>积极讨论</h3>
                  <p>积极参与讨论，帮助他人解决问题</p>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<style scoped>
.home {
  padding: 0;
  max-width: 100%;
  margin: 0 auto;
}

.hero-section {
  position: relative;
  height: 500px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0 0 20px 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.hero-content {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: url('https://images.unsplash.com/photo-1502810365585-56ffa3619e0f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80');
  background-size: cover;
  background-position: center;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
}

.hero-text {
  position: relative;
  text-align: center;
  color: white;
  z-index: 2;
  max-width: 800px;
  padding: 0 20px;
}

.hero-title {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  animation: fadeInDown 1s ease;
}

.hero-subtitle {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  animation: fadeInUp 1s ease 0.2s both;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
  animation: fadeInUp 1s ease 0.4s both;
}

.hero-stats {
  animation: fadeInUp 1s ease 0.4s both;
}

.welcome-text {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.user-navigation {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.hero-btn {
  padding: 12px 30px;
  font-size: 1.1rem;
  border: none;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.hero-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}

.forum-btn {
  background: #28a745;
  border-color: #28a745;
}

.stats-section {
  margin: -80px 0 50px 0;
  position: relative;
  z-index: 10;
}

.stats-container {
  padding: 20px;
}

.stat-item {
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 30px;
  text-align: center;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stat-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 30px;
  color: white;
}

.posts-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.likes-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.comments-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-info {
  flex: 1;
}

.stat-info :deep(.el-statistic__head) {
  font-size: 18px;
  color: #666;
  margin-bottom: 10px;
}

.stat-info :deep(.el-statistic__content) {
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.content-section {
  max-width: 1200px;
  margin: 0 auto 50px;
  padding: 0 20px;
  gap: 30px;
}

.community-features-section {
  max-width: 1200px;
  margin: 0 auto 50px;
  padding: 0 20px;
}


.posts-section {
  flex: 1;
}

.sidebar {
  width: auto;
}

.sidebar-section {
  position: sticky;
  top: 20px;
}

.preview-card {
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  border: none;
  overflow: hidden;
}

.latest-posts-card {
  border-top: 4px solid #409eff;
}

.preview-card :deep(.el-card__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  padding: 20px;
}

.card-header {
  font-size: 1.4rem;
  font-weight: 600;
  text-align: center;
  color: #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-tag {
  font-size: 12px;
}

.card-badge :deep(.el-badge__content) {
  background-color: #409eff;
}

.posts-preview {
  padding: 1rem 0;
}

.post-preview-item {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: all 0.3s ease;
}

.post-preview-item:hover {
  background-color: #f8f9fa;
  transform: translateX(5px);
}

.post-preview-item:last-child {
  border-bottom: none;
}

.post-title {
  margin: 0 0 0.8rem 0;
  font-size: 1.2rem;
  color: #333;
  font-weight: 600;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: #666;
}

.view-all {
  text-align: center;
  margin-top: 1.5rem;
  padding: 1rem;
}

.no-posts {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.features-card {
  margin-bottom: 25px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  border: none;
  overflow: hidden;
}

.following-card {
  border-top: 4px solid #67c23a;
}

.community-card {
  border-top: 4px solid #e6a23c;
}

.features-card :deep(.el-card__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  padding: 20px;
}

.features-container {
  padding: 1rem 0;
}

.feature-col {
  display: flex;
  align-items: stretch;
}

.feature-item {
  text-align: center;
  padding: 1.5rem;
  transition: all 0.3s ease;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.feature-item:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-item h3 {
  margin: 0 0 0.8rem 0;
  font-size: 1.3rem;
  color: #333;
  font-weight: 600;
}

.feature-item p {
  margin: 0;
  color: #666;
  font-size: 1rem;
  line-height: 1.5;
  flex: 1;
}

.following-content {
  text-align: center;
  padding: 1.5rem;
}

.following-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 15px;
}

.stat-item {
  text-align: center;
  margin-bottom: 0;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.full-width-btn {
  width: 100%;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 992px) {
  .hero-section {
    height: 400px;
  }
  
  .hero-title {
    font-size: 2.2rem;
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
  }
  

  .posts-section, .sidebar {
    width: 100%;
  }
  
  .sidebar {
    order: -1;
    margin-bottom: 30px;
  }
  
  .sidebar-section {
    position: static;
  }
}

@media (max-width: 768px) {
  .hero-section {
    height: 350px;
    border-radius: 0 0 10px 10px;
  }
  
  .hero-title {
    font-size: 1.8rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .user-navigation {
    flex-direction: column;
    gap: 15px;
  }
  
  .stats-section {
    margin: -60px 0 30px 0;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .stat-info :deep(.el-statistic__content) {
    font-size: 22px;
  }
  
  .post-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
  }
}
</style>