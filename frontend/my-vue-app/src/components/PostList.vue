<script setup>
import PostItem from './PostItem.vue'

defineProps({
  posts: {
    type: Array,
    default: () => []
  }
})

defineEmits(['postDeleted'])
</script>

<template>
  <div class="post-list">
    <div v-if="!posts || posts.length === 0" class="no-posts">
      暂无帖子，快来发布第一个吧！
    </div>
    <template v-else>
      <PostItem 
        v-for="post in posts"
        :key="post.id"
        :post="post"
        @post-deleted="$emit('postDeleted')"
      />
    </template>
  </div>
</template>
<style scoped>
.post-list {
  margin-top: 1rem;
}

.no-posts {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style>