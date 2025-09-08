<script setup>
import { ref, onMounted } from 'vue'
import { useMainStore } from '../store'
import { authAPI } from '../api'
import PostList from '../components/PostList.vue'

const store = useMainStore()
const user = ref(null)
const userPosts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    // 获取当前用户信息
    const response = await authAPI.profile()
    user.value = response.data
    store.setUser(user.value)
    
    // 在实际应用中，这里应该获取用户发布的帖子
    // 由于我们没有这个API，暂时留空
    userPosts.value = []
  } catch (error) {
    console.error('获取用户信息失败:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="profile">
    <div class="container">
      <div v-if="loading" class="loading">
        加载中...
      </div>
      <div v-else-if="user" class="profile-content">
        <h1>{{ user.username }} 的个人资料</h1>
        <div class="user-info">
          <p><strong>邮箱:</strong> {{ user.email }}</p>
          <p v-if="user.bio"><strong>简介:</strong> {{ user.bio }}</p>
          <p v-if="user.birth_date"><strong>生日:</strong> {{ user.birth_date }}</p>
        </div>
        
        <h2>我的帖子</h2>
        <PostList :posts="userPosts" @post-deleted="userPosts = userPosts.filter(p => !p.deleted)" />
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

.profile-content h1 {
  margin-bottom: 1rem;
}

.user-info {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
}

.user-info p {
  margin: 0.5rem 0;
}
</style>