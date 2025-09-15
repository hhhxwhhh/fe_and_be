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
        <el-card class="welcome-card">
          <template #header>
            <div class="card-header">
              <span>欢迎来到社区论坛</span>
            </div>
          </template>
          <div class="welcome-content">
            <p v-if="store.user">你好，{{ store.user.username }}！欢迎回到我们的社区。</p>
            
            <div class="stats-container">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-statistic title="帖子总数" :value="stats.totalPosts" />
                </el-col>
                <el-col :span="8">
                  <el-statistic title="点赞总数" :value="stats.totalLikes" />
                </el-col>
                <el-col :span="8">
                  <el-statistic title="评论总数" :value="stats.totalComments" />
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最新帖子 -->
    <el-row justify="center">
      <el-col :span="20">
        <el-card class="posts-card">
          <template #header>
            <div class="card-header">
              <span>最新帖子</span>
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
            <p>为了维护良好的社区环境，请遵守以下规则:</p>
            <ul>
              <li>友善交流，互相尊重</li>
              <li>不发布违法、不实或不当内容</li>
              <li>不进行人身攻击或恶意诋毁</li>
              <li>积极参与讨论，分享有价值的内容</li>
              <li>帮助他人解决问题</li>
            </ul>
            <ElDivider />
            <p>让我们一起创造更美好的交流环境！</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.forum {
  padding: 1rem;
}

.welcome-card,
.posts-card,
.about-card {
  margin-top: 2rem;
}

.card-header {
  font-size: 1.2rem;
  font-weight: bold;
}

.welcome-content p {
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.stats-container {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #f5f8fa;
  border-radius: 8px;
}

.posts-summary {
  margin: 1rem 0;
  padding: 0.5rem;
  background-color: #f9f9f9;
  border-radius: 4px;
  font-style: italic;
}

.no-posts {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.about-content ul {
  padding-left: 1.5rem;
  margin: 1rem 0;
}

.about-content li {
  margin-bottom: 0.5rem;
}

a {
  color: #42b883;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>