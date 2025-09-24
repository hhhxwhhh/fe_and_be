<template>
    <div class="search-page">
        <div class="search-header">
            <div class="search-input-container">
                <el-input v-model="searchQuery" placeholder="搜索用户或帖子..." class="search-input" size="large"
                    @keyup.enter="performSearch">
                    <template #prefix>
                        <el-icon>
                            <Search />
                        </el-icon>
                    </template>
                </el-input>
                <el-button type="primary" @click="performSearch" size="large" class="search-button">
                    搜索
                </el-button>
            </div>

            <div class="search-filters">
                <el-radio-group v-model="searchType" @change="performSearch">
                    <el-radio-button label="all">全部</el-radio-button>
                    <el-radio-button label="posts">帖子</el-radio-button>
                    <el-radio-button label="users">用户</el-radio-button>
                </el-radio-group>
            </div>
        </div>

        <div class="search-results" v-loading="loading">
            <div v-if="!loading && !searchQuery" class="empty-placeholder">
                <el-icon>
                    <Search />
                </el-icon>
                <p>请输入关键词进行搜索</p>
            </div>

            <div v-else-if="!loading && searchQuery && !hasResults" class="no-results">
                <el-icon>
                    <Document />
                </el-icon>
                <p>没有找到与 "{{ searchQuery }}" 相关的结果</p>
            </div>

            <div v-else>
                <!-- 用户搜索结果 -->
                <div v-if="searchType === 'all' || searchType === 'users'" class="results-section">
                    <h3>用户 ({{ users.length }})</h3>
                    <div class="users-grid">
                        <div v-for="user in users" :key="user.id" class="user-card" @click="goToUserProfile(user.id)">
                            <el-avatar :size="50" :src="user.avatar" class="user-avatar">
                                {{ user.username.charAt(0).toUpperCase() }}
                            </el-avatar>
                            <div class="user-info">
                                <h4 class="username">{{ user.username }}</h4>
                                <p class="user-bio">{{ user.bio || '暂无简介' }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 帖子搜索结果 -->
                <div v-if="searchType === 'all' || searchType === 'posts'" class="results-section">
                    <h3>帖子 ({{ posts.length }})</h3>
                    <div class="posts-list">
                        <PostItem v-for="post in posts" :key="post.id" :post="post" @post-deleted="handlePostDeleted" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElInput, ElButton, ElIcon, ElRadioGroup, ElRadioButton, ElAvatar } from 'element-plus'
import { Search, Document } from '@element-plus/icons-vue'
import { searchAPI } from '../api'
import PostItem from './PostItem.vue'

const router = useRouter()

// 搜索相关数据
const searchQuery = ref('')
const searchType = ref('all')
const loading = ref(false)
const users = ref([])
const posts = ref([])

// 计算属性
const hasResults = computed(() => {
    return users.value.length > 0 || posts.value.length > 0
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
        const response = await searchAPI.search(searchQuery.value, searchType.value)
        const results = response.data.results

        users.value = results.users || []
        posts.value = results.posts || []
    } catch (error) {
        console.error('搜索失败:', error)
        users.value = []
        posts.value = []
    } finally {
        loading.value = false
    }
}

// 跳转到用户资料页
const goToUserProfile = (userId) => {
    router.push(`/user-profile/${userId}`)
}

// 处理帖子删除事件
const handlePostDeleted = (postId) => {
    posts.value = posts.value.filter(post => post.id !== postId)
}

// 组件挂载时检查路由参数
onMounted(() => {
    const query = new URLSearchParams(window.location.search).get('q')
    const type = new URLSearchParams(window.location.search).get('type')

    if (query) {
        searchQuery.value = query
        if (type) {
            searchType.value = type
        }
        performSearch()
    }
})
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

.search-input-container {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.search-input {
    flex: 1;
}

.search-button {
    width: 100px;
}

.search-filters {
    display: flex;
    justify-content: center;
}

.search-results {
    min-height: 400px;
}

.empty-placeholder,
.no-results {
    text-align: center;
    padding: 60px 20px;
    color: #909399;
}

.empty-placeholder .el-icon,
.no-results .el-icon {
    font-size: 48px;
    margin-bottom: 16px;
    color: #C0C4CC;
}

.results-section {
    margin-bottom: 40px;
}

.results-section h3 {
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #EBEEF5;
    color: #303133;
}

.users-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}

.user-card {
    display: flex;
    align-items: center;
    padding: 15px;
    border: 1px solid #EBEEF5;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
}

.user-card:hover {
    border-color: #409EFF;
    box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.1);
}

.user-info {
    margin-left: 15px;
    flex: 1;
    overflow: hidden;
}

.username {
    margin: 0 0 5px 0;
    font-size: 16px;
    font-weight: 500;
    color: #303133;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-bio {
    margin: 0;
    font-size: 14px;
    color: #909399;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.posts-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

@media (max-width: 768px) {
    .search-page {
        padding: 10px;
    }

    .search-input-container {
        flex-direction: column;
    }

    .search-button {
        width: 100%;
    }

    .users-grid {
        grid-template-columns: 1fr;
    }
}
</style>