<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMainStore } from '../store'
import { postAPI } from '../api'
import PostItem from '../components/PostItem.vue'

const route = useRoute()
const router= useRouter();
const store = useMainStore()
const post = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await postAPI.getPost(route.params.id)
    post.value = response.data
  } catch (error) {
    console.error('获取帖子失败:', error)
  } finally {
    loading.value = false
  }
})

const handlePostDeleted = () => {
  router.push('/')
}

</script>

<template>
  <div class="post-detail">
    <div class="container">
      <div v-if="loading" class="loading">
        加载中...
      </div>
      <div v-else-if="post">
        <PostItem :post="post" @post-deleted="handlePostDeleted" />
      </div>
      <div v-else>
        <p>找不到该帖子</p>
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

.loading {
  text-align: center;
  padding: 2rem;
}
</style>