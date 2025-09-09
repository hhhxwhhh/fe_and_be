<script setup>
import { ref, onMounted } from 'vue'
import { useMainStore } from '../store'
import PostForm from '../components/PostForm.vue'
import PostList from '../components/PostList.vue'
import HelloWorld from '../components/HelloWorld.vue'
import { postAPI } from '../api'
import { ElRow, ElCol, ElCard, ElSkeleton } from 'element-plus'

const store = useMainStore()
const loading = ref(false)

onMounted(async () => {
  await loadPosts()
})

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
</script>

<template>
  <div class="home">
    <HelloWorld />
    
    <el-row justify="center">
      <el-col :span="16">
        <el-card class="posts-card">
          <template #header>
            <div class="card-header">
              <span>帖子</span>
            </div>
          </template>
          
          <PostForm @post-created="loadPosts" />
          
          <div v-if="loading">
            <el-skeleton :rows="4" animated />
          </div>
          
          <PostList v-else />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.home {
  padding: 1rem;
}

.posts-card {
  margin-top: 2rem;
}

.card-header {
  font-size: 1.2rem;
  font-weight: bold;
}
</style>