<script setup>
import { ref, onMounted } from 'vue'
import { useMainStore } from '../store'
import PostForm from '../components/PostForm.vue'
import PostList from '../components/PostList.vue'
import HelloWorld from '../components/HelloWorld.vue'
import { postAPI } from '../api'

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
    
    <div class="posts-section">
      <h2>帖子</h2>
      <PostForm @post-created="loadPosts" />
      
      <div v-if="loading" class="loading">
        加载中...
      </div>
      
      <PostList v-else />
    </div>
  </div>
</template>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.posts-section {
  margin-top: 2rem;
}

.posts-section h2 {
  text-align: center;
  margin-bottom: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
}
</style>