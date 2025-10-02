<template>
    <div class="user-search">
        <el-input v-model="searchQuery" placeholder="搜索用户..." clearable @input="handleSearch">
            <template #prefix>
                <el-icon>
                    <Search />
                </el-icon>
            </template>
        </el-input>

        <div v-if="searchResults.length > 0" class="search-results">
            <div v-for="user in searchResults" :key="user.id" class="user-item" @click="selectUser(user)">
                <el-avatar :src="user.avatar" size="small">
                    {{ user.username.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="user-info">
                    <div class="username">{{ user.username }}</div>
                    <div class="user-bio">{{ user.bio || '暂无简介' }}</div>
                </div>
            </div>
        </div>

        <div v-else-if="searchQuery && searchResults.length === 0" class="no-results">
            没有找到相关用户
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { authAPI } from '@/api'

const searchQuery = ref('')
const searchResults = ref([])
const emit = defineEmits(['user-selected'])

let searchTimeout = null

const handleSearch = () => {
    if (searchTimeout) {
        clearTimeout(searchTimeout)
    }

    if (!searchQuery.value.trim()) {
        searchResults.value = []
        return
    }

    // 防抖处理
    searchTimeout = setTimeout(async () => {
        try {
            const response = await authAPI.searchUsers(searchQuery.value)
            searchResults.value = response.data
        } catch (error) {
            console.error('搜索用户失败:', error)
        }
    }, 300)
}

const selectUser = (user) => {
    emit('user-selected', user)
    searchQuery.value = ''
    searchResults.value = []
}
</script>

<style scoped>
.user-search {
    position: relative;
}

.search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    max-height: 300px;
    overflow-y: auto;
    z-index: 1000;
    margin-top: 5px;
}

.user-item {
    display: flex;
    align-items: center;
    padding: 10px 15px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.user-item:hover {
    background-color: #f5f7fa;
}

.user-info {
    margin-left: 10px;
    flex: 1;
    min-width: 0;
}

.username {
    font-weight: 500;
    color: #303133;
    margin-bottom: 2px;
}

.user-bio {
    font-size: 12px;
    color: #909399;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.no-results {
    text-align: center;
    padding: 20px;
    color: #909399;
    font-size: 14px;
}
</style>