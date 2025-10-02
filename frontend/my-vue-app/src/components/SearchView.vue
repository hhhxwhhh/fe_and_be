<template>
    <div class="search-page">
        <div class="search-header">
            <el-input v-model="searchQuery" placeholder="搜索用户或帖子..." class="search-input" size="large"
                @keyup.enter="performSearch">
                <template #prefix>
                    <el-icon>
                        <Search />
                    </el-icon>
                </template>
                <template #append>
                    <el-button :icon="Search" @click="performSearch" />
                </template>
            </el-input>
        </div>

        <div class="search-content">
            <el-tabs v-model="activeTab" @tab-change="handleTabChange">
                <el-tab-pane label="用户" name="users">
                    <div v-if="loading" class="loading">
                        <el-skeleton :rows="5" animated />
                    </div>

                    <div v-else-if="users.length > 0" class="search-results">
                        <div v-for="user in users" :key="user.id" class="user-item" @click="goToUserProfile(user.id)">
                            <el-avatar :src="user.avatar" :size="50">
                                {{ user.username.charAt(0).toUpperCase() }}
                            </el-avatar>
                            <div class="user-info">
                                <div class="username">{{ user.username }}</div>
                                <div class="user-bio">{{ user.bio || '暂无简介' }}</div>
                                <div class="user-stats">
                                    <span>粉丝: {{ user.followers_count || 0 }}</span>
                                    <span>关注: {{ user.following_count || 0 }}</span>
                                </div>
                            </div>
                            <div class="user-actions">
                                <el-button v-if="!user.is_following && user.id !== currentUser.id" type="primary"
                                    size="small" @click.stop="followUser(user)" :loading="followingLoading[user.id]">
                                    关注
                                </el-button>
                                <el-button v-else-if="user.is_following && user.id !== currentUser.id" size="small"
                                    @click.stop="unfollowUser(user)" :loading="followingLoading[user.id]">
                                    已关注
                                </el-button>
                            </div>
                        </div>
                    </div>

                    <div v-else-if="searchQuery && !loading" class="no-results">
                        <el-empty description="没有找到相关用户" />
                    </div>
                </el-tab-pane>

                <el-tab-pane label="帖子" name="posts">
                    <div v-if="loading" class="loading">
                        <el-skeleton :rows="5" animated />
                    </div>

                    <div v-else-if="posts.length > 0" class="search-results">
                        <div v-for="post in posts" :key="post.id" class="post-item" @click="goToPost(post.id)">
                            <div class="post-header">
                                <el-avatar :src="post.author.avatar" :size="40">
                                    {{ post.author.username.charAt(0).toUpperCase() }}
                                </el-avatar>
                                <div class="post-author">
                                    <div class="author-name">{{ post.author.username }}</div>
                                    <div class="post-time">{{ formatTime(post.created_at) }}</div>
                                </div>
                            </div>
                            <div class="post-content">
                                {{ post.content }}
                            </div>
                            <div class="post-stats">
                                <span><i class="el-icon-chat-dot-round"></i> {{ post.comments_count || 0 }}</span>
                                <span><i class="el-icon-thumb"></i> {{ post.likes_count || 0 }}</span>
                            </div>
                        </div>
                    </div>

                    <div v-else-if="searchQuery && !loading" class="no-results">
                        <el-empty description="没有找到相关帖子" />
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { searchAPI, authAPI, postAPI } from '@/api'
import { useMainStore } from '@/store'

const route = useRoute()
const router = useRouter()
const store = useMainStore()

const searchQuery = ref(route.query.q || '')
const activeTab = ref('users')
const users = ref([])
const posts = ref([])
const loading = ref(false)
const followingLoading = ref({})

// 获取当前用户
const currentUser = computed(() => store.user)

// 页面加载时执行搜索
onMounted(() => {
    if (searchQuery.value) {
        performSearch()
    }
})

// 执行搜索
const performSearch = async () => {
    if (!searchQuery.value.trim()) {
        users.value = []
        posts.value = []
        return
    }

    loading.value = true
    try {
        if (activeTab.value === 'users') {
            const response = await searchAPI.searchUsers(searchQuery.value)
            users.value = response.data
            posts.value = []
        } else if (activeTab.value === 'posts') {
            const response = await searchAPI.searchPosts(searchQuery.value)
            posts.value = response.data
            users.value = []
        }
    } catch (error) {
        console.error('搜索失败:', error)
    } finally {
        loading.value = false
    }
}

// 处理标签页切换
const handleTabChange = () => {
    performSearch()
}

// 关注用户
const followUser = async (user) => {
    followingLoading.value[user.id] = true
    try {
        await authAPI.followUser(user.id)
        user.is_following = true
        store.addFollowing(user.id)
    } catch (error) {
        console.error('关注用户失败:', error)
    } finally {
        followingLoading.value[user.id] = false
    }
}

// 取消关注用户
const unfollowUser = async (user) => {
    followingLoading.value[user.id] = true
    try {
        await authAPI.unfollowUser(user.id)
        user.is_following = false
        store.removeFollowing(user.id)
    } catch (error) {
        console.error('取消关注用户失败:', error)
    } finally {
        followingLoading.value[user.id] = false
    }
}

// 跳转到用户个人资料页
const goToUserProfile = (userId) => {
    router.push(`/user-profile/${userId}`)
}

// 跳转到帖子详情页
const goToPost = (postId) => {
    router.push(`/post/${postId}`)
}

// 格式化时间
const formatTime = (timeString) => {
    const date = new Date(timeString)
    return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.search-page {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.search-header {
    margin-bottom: 30px;
}

.search-input {
    width: 100%;
}

.search-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.user-item {
    display: flex;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background-color 0.2s;
}

.user-item:hover {
    background-color: #f9f9f9;
}

.user-item:last-child {
    border-bottom: none;
}

.user-info {
    flex: 1;
    margin: 0 15px;
    min-width: 0;
}

.username {
    font-weight: 500;
    color: #303133;
    margin-bottom: 5px;
    font-size: 16px;
}

.user-bio {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-stats {
    font-size: 12px;
    color: #909399;
}

.user-stats span {
    margin-right: 10px;
}

.user-actions {
    flex-shrink: 0;
}

.post-item {
    padding: 15px 0;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background-color 0.2s;
}

.post-item:hover {
    background-color: #f9f9f9;
}

.post-item:last-child {
    border-bottom: none;
}

.post-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.post-author {
    margin-left: 10px;
}

.author-name {
    font-weight: 500;
    color: #303133;
    font-size: 14px;
}

.post-time {
    font-size: 12px;
    color: #909399;
}

.post-content {
    font-size: 14px;
    color: #606266;
    line-height: 1.5;
    margin-bottom: 10px;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.post-stats {
    font-size: 12px;
    color: #909399;
}

.post-stats span {
    margin-right: 15px;
}

.no-results {
    padding: 40px 0;
}

.construction {
    padding: 40px 0;
}
</style>