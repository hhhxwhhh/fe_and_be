<script setup>
import PostItem from './PostItem.vue'

defineProps({
  posts: {
    type: Array,
    required: true
  }
})

defineEmits(['postDeleted'])
</script>

<template>
  <div class="post-list">
    <div v-if="posts.length === 0" class="no-posts">
      暂无帖子，快来发布第一个吧！
    </div>
    <PostItem 
      v-else
      v-for="post in posts"
      :key="post.id"
      :post="post"
      @post-deleted="$emit('postDeleted')"
    />
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