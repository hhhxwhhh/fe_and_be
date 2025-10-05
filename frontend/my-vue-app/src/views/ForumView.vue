<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMainStore } from '../store'
import PostForm from '../components/PostForm.vue'
import PostList from '../components/PostList.vue'
import { postAPI } from '../api'
import { ElRow, ElCol, ElCard, ElSkeleton, ElStatistic, ElDivider } from 'element-plus'

const store = useMainStore()
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

const posts = computed(() => store.posts)

const loadPosts = async () => {
  try {
    loading.value = true
    // 在论坛页面，无论用户是否登录，都显示所有帖子
    const response = await postAPI.getAllPosts(); 
    store.setPosts(response.data)
  } catch (error) {
    console.error('加载帖子失败:', error)
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  stats.value.totalPosts = posts.value.length
  stats.value.totalLikes = posts.value.reduce((sum, post) => sum + (post.likes_count || 0), 0)
  stats.value.totalComments = posts.value.reduce((sum, post) => sum + (post.comments?.length || 0), 0)
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

const handlePostDeleted =async () => {
  await loadPosts();
  calculateStats();
}
</script>

<template>
  <div class="forum">
    <!-- 欢迎区域 -->
    <el-row justify="center">
      <el-col :span="20">
        <div class="hero-section">
          <div class="hero-overlay"></div>
          <div class="hero-content">
            <h1 class="hero-title">欢迎来到社区论坛</h1>
            <p class="hero-subtitle">一个分享想法、经验和知识的友好平台</p>
            <p v-if="store.user" class="hero-user-greeting">你好，{{ store.user.username }}！欢迎回到我们的社区。</p>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 统计数据 -->
    <el-row justify="center" class="stats-section">
      <el-col :span="20">
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
    
    <!-- 发布帖子和帖子列表 -->
    <el-row justify="center">
      <el-col :span="20">
        <el-card class="posts-card">
          <template #header>
            <div class="card-header">
              <span>社区交流</span>
            </div>
          </template>
          
          <PostForm @post-created="loadPosts" />
          
          <div v-if="loading">
            <el-skeleton :rows="4" animated />
          </div>
          
          <div v-else-if="posts && posts.length > 0">
            <div class="posts-summary">
              <p>共有 {{ posts.length }} 篇帖子，最新帖子发布于 {{ formatDate(posts[0].created_at) }}</p>
            </div>
            <PostList :posts="posts" @post-deleted="handlePostDeleted" />
          </div>
          
          <div v-else class="no-posts">
            <div class="no-posts-icon">📝</div>
            <p>暂无帖子，快来发布第一个吧！</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 社区介绍 -->
    <el-row justify="center">
      <el-col :span="20">
        <el-card class="about-card">
          <template #header>
            <div class="card-header">
              <span>社区规则</span>
            </div>
          </template>
          <div class="about-content">
            <div class="rules-container">
              <div class="rule-item">
                <div class="rule-icon">🤝</div>
                <div class="rule-text">
                  <h3>友善交流</h3>
                  <p>互相尊重，营造和谐的交流氛围</p>
                </div>
              </div>
              <div class="rule-item">
                <div class="rule-icon">✅</div>
                <div class="rule-text">
                  <h3>内容规范</h3>
                  <p>不发布违法、不实或不当内容</p>
                </div>
              </div>
              <div class="rule-item">
                <div class="rule-icon">🛡️</div>
                <div class="rule-text">
                  <h3>禁止攻击</h3>
                  <p>不进行人身攻击或恶意诋毁</p>
                </div>
              </div>
              <div class="rule-item">
                <div class="rule-icon">💡</div>
                <div class="rule-text">
                  <h3>价值分享</h3>
                  <p>积极参与讨论，分享有价值的内容</p>
                </div>
              </div>
              <div class="rule-item">
                <div class="rule-icon">❤️</div>
                <div class="rule-text">
                  <h3>互助精神</h3>
                  <p>帮助他人解决问题，共同成长</p>
                </div>
              </div>
            </div>
            <ElDivider />
            <div class="community-message">
              <p>让我们一起创造更美好的交流环境！</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.forum {
  padding: 1rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
  min-height: 100vh;
}

/* 英雄区域样式 */
.hero-section {
  position: relative;
  height: 300px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
  margin-top: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
}

.hero-content {
  position: relative;
  text-align: center;
  color: white;
  z-index: 2;
  max-width: 800px;
  padding: 0 20px;
}

.hero-title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.hero-subtitle {
  font-size: 1.3rem;
  margin-bottom: 1.5rem;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.hero-user-greeting {
  font-size: 1.2rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.8rem 1.5rem;
  border-radius: 30px;
  display: inline-block;
  backdrop-filter: blur(5px);
}

/* 统计区域样式 */
.stats-section {
  margin: 2rem 0;
}

.stats-container {
  padding: 20px;
}

.stat-item {
  margin-bottom: 20px;
}

.stat-card {
  background: var(--chat-cardBackground); 
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
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
  color: var(--chat-textSecondary);
  margin-bottom: 10px;
}

.stat-info :deep(.el-statistic__content) {
  font-size: 28px;
  font-weight: 700;
  color: var(--chat-textPrimary);
}

/* 卡片样式 */
.posts-card,
.about-card {
  margin: 2rem 0;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  border: none;
  overflow: hidden;
}

.posts-card :deep(.el-card__header),
.about-card :deep(.el-card__header) {
  background: linear-gradient(90deg, #667eea, #764ba2);
  color: white;
  padding: 20px;
  border: none;
}

.card-header {
  font-size: 1.5rem;
  font-weight: 600;
}

.posts-summary {
  margin: 1.5rem 0;
  padding: 1rem;
  background: linear-gradient(90deg, #f8f9ff, #f0f4ff);
  border-radius: 10px;
  font-style: italic;
  color: #555;
  text-align: center;
}

.no-posts {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.no-posts-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

/* 社区规则样式 */
.rules-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 1.5rem 0;
}

.rule-item {
  display: flex;
  align-items: flex-start;
  padding: 1.5rem;
  background: #f8f9ff;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.rule-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  background: white;
}

.rule-icon {
  font-size: 2rem;
  margin-right: 1rem;
  min-width: 50px;
  text-align: center;
}

.rule-text h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  color: #333;
  font-weight: 600;
}

.rule-text p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.community-message {
  text-align: center;
  font-size: 1.2rem;
  color: #555;
  font-weight: 500;
}

.community-message p {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .hero-section {
    height: 250px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .stats-container {
    padding: 10px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-icon {
    width: 60px;
    height: 60px;
    font-size: 24px;
  }
  
  .stat-info :deep(.el-statistic__content) {
    font-size: 22px;
  }
}

@media (max-width: 768px) {
  .forum {
    padding: 0.5rem;
  }
  
  .hero-section {
    height: 220px;
    border-radius: 15px;
  }
  
  .hero-title {
    font-size: 1.8rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-user-greeting {
    font-size: 1rem;
    padding: 0.6rem 1rem;
  }
  
  .stats-section {
    margin: 1.5rem 0;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
    margin-bottom: 10px;
  }
  
  .stat-info :deep(.el-statistic__head) {
    font-size: 16px;
  }
  
  .stat-info :deep(.el-statistic__content) {
    font-size: 20px;
  }
  
  .posts-card,
  .about-card {
    margin: 1.5rem 0;
    border-radius: 15px;
  }
  
  .card-header {
    font-size: 1.3rem;
  }
  
  .rules-container {
    grid-template-columns: 1fr;
  }
  
  .rule-item {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .hero-section {
    height: 200px;
  }
  
  .hero-title {
    font-size: 1.5rem;
  }
  
  .hero-subtitle {
    font-size: 0.9rem;
  }
  
  .stat-item {
    margin-bottom: 15px;
  }
  
  .stat-card {
    padding: 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 18px;
  }
  
  .stat-info :deep(.el-statistic__head) {
    font-size: 14px;
  }
  
  .stat-info :deep(.el-statistic__content) {
    font-size: 18px;
  }
  
  .posts-summary {
    padding: 0.8rem;
    font-size: 0.9rem;
  }
  
  .rule-icon {
    font-size: 1.5rem;
    margin-right: 0.8rem;
  }
  
  .rule-text h3 {
    font-size: 1.1rem;
  }
  
  .rule-text p {
    font-size: 0.9rem;
  }
  
  .community-message {
    font-size: 1rem;
  }
}
</style>