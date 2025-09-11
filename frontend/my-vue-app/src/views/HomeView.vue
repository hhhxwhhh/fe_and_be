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
      <el-col :span="20">
        <el-card class="hero-card">
          <div class="hero-content">
            <h1 class="hero-title">欢迎来到社交网络社区</h1>
            <p class="hero-subtitle">一个分享想法、经验和知识的友好平台</p>
            
            <div class="hero-actions" v-if="!store.user">
              <el-button type="primary" size="large" @click="goToLogin">登录</el-button>
              <el-button type="success" size="large" @click="goToRegister">注册</el-button>
            </div>
            
            <div class="hero-stats" v-else>
              <p>你好，{{ store.user.username }}！欢迎回到社区。</p>
              <div class="user-navigation">
                <el-button type="primary" @click="goToFollowing">查看关注</el-button>
                <el-button type="success" @click="goToForum" style="margin-left: 10px;">进入论坛</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 社区统计数据 -->
    <el-row justify="center">
      <el-col :span="20">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span>社区数据</span>
            </div>
          </template>
          
          <div class="stats-container">
            <el-row :gutter="20" justify="center">
              <el-col :span="8" :xs="24">
                <el-statistic title="帖子总数" :value="stats.totalPosts" />
              </el-col>
              <el-col :span="8" :xs="24">
                <el-statistic title="点赞总数" :value="stats.totalLikes" />
              </el-col>
              <el-col :span="8" :xs="24">
                <el-statistic title="评论总数" :value="stats.totalComments" />
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最新帖子预览 -->
    <el-row justify="center">
      <el-col :span="20">
        <el-card class="preview-card">
          <template #header>
            <div class="card-header">
              <span>最新帖子</span>
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
    </el-row>
    
    <!-- 关注用户和社区特色 -->
    <el-row justify="center" :gutter="20">
      <el-col :span="12" v-if="store.user">
        <el-card class="following-card">
          <template #header>
            <div class="card-header">
              <span>我的关注</span>
            </div>
          </template>
          
          <div class="following-content">
            <p>您当前关注了 <strong>{{ store.user.following_count || 0 }}</strong> 个用户</p>
            <el-button type="primary" @click="goToFollowing" style="margin-top: 10px;">
              查看关注用户的内容
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="store.user ? 8 : 20">
        <el-card class="features-card">
          <template #header>
            <div class="card-header">
              <span>社区特色</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8" :md="24">
              <div class="feature-item">
                <div class="feature-icon">👥</div>
                <h3>友好社区</h3>
                <p>友善交流，互相尊重的社区环境</p>
              </div>
            </el-col>
            <el-col :span="8" :md="24">
              <div class="feature-item">
                <div class="feature-icon">💡</div>
                <h3>知识分享</h3>
                <p>分享你的想法、经验和知识</p>
              </div>
            </el-col>
            <el-col :span="8" :md="24">
              <div class="feature-item">
                <div class="feature-icon">💬</div>
                <h3>积极讨论</h3>
                <p>积极参与讨论，帮助他人解决问题</p>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.home {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.hero-card {
  margin-top: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.hero-content {
  padding: 2rem 1rem;
}

.hero-title {
  font-size: 2rem;
  margin-bottom: 1rem;
  font-weight: bold;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.hero-stats p {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.user-navigation {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.stats-card,
.preview-card,
.features-card,
.following-card {
  margin-top: 2rem;
}

.card-header {
  font-size: 1.3rem;
  font-weight: bold;
  text-align: center;
}

.stats-container {
  padding: 1rem 0;
}

.posts-preview {
  padding: 1rem 0;
}

.post-preview-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.3s;
}

.post-preview-item:hover {
  background-color: #f9f9f9;
}

.post-preview-item:last-child {
  border-bottom: none;
}

.post-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: #333;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.view-all {
  text-align: center;
  margin-top: 1rem;
}

.no-posts {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.following-content {
  text-align: center;
  padding: 1rem;
}

.features-card .el-row {
  margin-top: 1rem;
}

.feature-item {
  text-align: center;
  padding: 1rem;
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.feature-item h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.feature-item p {
  margin: 0;
  color: #666;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 1.5rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .post-meta {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .stats-container .el-col {
    margin-bottom: 1rem;
  }
  
  .stats-container .el-col:last-child {
    margin-bottom: 0;
  }
  
  .user-navigation {
    flex-direction: column;
    gap: 10px;
  }
  
  .el-row {
    flex-direction: column;
  }
  
  .el-col {
    width: 100%;
    margin-bottom: 20px;
  }
}
</style>