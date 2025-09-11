<script setup>
import {ref,onMounted} from 'vue'
import {useMainStore} from '../store'
import PostList from '../components/PostList.vue'
import { postAPI } from '../api'

const store =useMainStore();
const loading =ref(false);

onMounted(async () => { 
    await store.loadFollowingPosts();
})

const loadFollowingPosts = async ()=> {
    try{
        loading.value=true;
        const response = await postAPI.getPosts();
        store.setPosts(response.data);
    }catch(error){
        console.error('加载帖子失败:',error);
    }finally{
        loading.value=false;
    }
}
</script>

<template>
    <div class="following-feed">
      <div class="container">
        <h1>关注用户的帖子</h1>
        <div v-if="loading" class="loading">
          加载中...
        </div>
        <div v-else>
          <PostList 
            :posts="store.posts" 
            @post-deleted="loadFollowingPosts"
          />
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
  
  .following-feed h1 {
    color: #333;
    margin-bottom: 1rem;
  }
  
  .loading {
    text-align: center;
    padding: 2rem;
  }
  </style>