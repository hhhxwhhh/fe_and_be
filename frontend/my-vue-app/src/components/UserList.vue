<template>
    <div class="user-list">
        <h3>用户列表</h3>
        <div class="search-box">
            <input v-model="searchTerm" placeholder="搜索用户..." class="search-input" />
        </div>
        <div class="users-container">
            <div v-for="user in filteredUsers" :key="user.id" class="user-item" @click="selectUser(user)">
                <div class="user-avatar">
                    <img v-if="user.avatar" :src="user.avatar" :alt="user.username" />
                    <div v-else class="avatar-placeholder">
                        {{ user.username.charAt(0).toUpperCase() }}
                    </div>
                </div>
                <div class="user-info">
                    <div class="username">{{ user.username }}</div>
                </div>
            </div>

            <div v-if="filteredUsers.length === 0" class="no-users">
                没有找到用户
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { authAPI } from '../api'

const emit = defineEmits(['user-selected'])

const users = ref([])
const searchTerm = ref('')

const filteredUsers = computed(() => {
    if (!searchTerm.value) {
        return users.value
    }

    const term = searchTerm.value.toLowerCase()
    return users.value.filter(user =>
        user.username.toLowerCase().includes(term)
    )
})

const selectUser = (user) => {
    emit('user-selected', user)
}

const fetchUsers = async () => {
    try {
        const response = await authAPI.getUsers()
        users.value = response.data
    } catch (error) {
        console.error('获取用户列表失败:', error)
    }
}

onMounted(() => {
    fetchUsers()
})
</script>

<style scoped>
.user-list {
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.user-list h3 {
    margin-top: 0;
    color: #333;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}

.search-box {
    margin-bottom: 15px;
}

.search-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 14px;
}

.search-input:focus {
    outline: none;
    border-color: #409eff;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.users-container {
    flex: 1;
    overflow-y: auto;
}

.user-item {
    display: flex;
    align-items: center;
    padding: 10px;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.2s;
}

.user-item:hover {
    background-color: #f5f5f5;
}

.user-avatar {
    margin-right: 10px;
}

.user-avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}

.avatar-placeholder {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #42b883, #3498db);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
}

.user-info {
    flex: 1;
}

.username {
    font-weight: 500;
    color: #333;
}

.no-users {
    text-align: center;
    padding: 20px;
    color: #999;
}
</style>