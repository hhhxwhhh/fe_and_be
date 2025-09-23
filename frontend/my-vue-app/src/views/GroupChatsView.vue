<template>
    <div class="group-chats-page">
        <div class="group-chats-header">
            <h2>群聊</h2>
            <el-button type="primary" @click="showCreateGroupModal = true" class="create-group-btn">
                创建群聊
            </el-button>
        </div>

        <div class="group-chats-list">
            <div v-for="group in groupChats" :key="group.id" class="group-chat-item" @click="openGroupChat(group)">
                <div class="group-avatar">
                    <img v-if="group.avatar" :src="group.avatar" :alt="group.name">
                    <div v-else class="avatar-placeholder">
                        {{ group.name.charAt(0).toUpperCase() }}
                    </div>
                </div>
                <div class="group-info">
                    <div class="group-name">{{ group.name }}</div>
                    <div class="group-meta">
                        <span class="member-count">{{ group.member_count }} 人</span>
                        <span v-if="group.last_message" class="last-message">
                            {{ group.last_message.sender.username }}: {{ truncateMessage(group.last_message.content) }}
                        </span>
                    </div>
                </div>
            </div>

            <div v-if="groupChats.length === 0" class="no-group-chats">
                暂无群聊，创建一个群聊开始聊天吧！
            </div>
        </div>

        <!-- 创建群聊模态框 -->
        <el-dialog v-model="showCreateGroupModal" title="创建群聊" width="400px">
            <el-form :model="newGroup" @submit.prevent="createGroup">
                <el-form-item label="群聊名称">
                    <el-input v-model="newGroup.name" required />
                </el-form-item>
                <el-form-item label="群聊描述">
                    <el-input v-model="newGroup.description" type="textarea" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showCreateGroupModal = false">取消</el-button>
                <el-button type="primary" @click="createGroup">创建</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { messageAPI } from '../api'

const router = useRouter()
const groupChats = ref([])
const showCreateGroupModal = ref(false)
const newGroup = ref({
    name: '',
    description: ''
})

onMounted(async () => {
    await fetchGroupChats()
})

const fetchGroupChats = async () => {
    try {
        const response = await messageAPI.getConversations()
        groupChats.value = response.data.group_chats || []
    } catch (error) {
        console.error('获取群聊列表失败:', error)
        ElMessage.error('获取群聊列表失败')
    }
}

const openGroupChat = (group) => {
    router.push(`/group-chat/${group.id}`)
}

const createGroup = async () => {
    if (!newGroup.value.name.trim()) {
        ElMessage.warning('请输入群聊名称')
        return
    }

    try {
        await messageAPI.createGroupChat(newGroup.value)
        showCreateGroupModal.value = false
        ElMessage.success('群聊创建成功')
        newGroup.value = { name: '', description: '' }
        await fetchGroupChats()
    } catch (error) {
        console.error('创建群聊失败:', error)
        ElMessage.error('创建群聊失败')
    }
}

const truncateMessage = (message) => {
    if (!message) return ''
    return message.length > 20 ? message.substring(0, 20) + '...' : message
}
</script>

<style scoped>
.group-chats-page {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.group-chats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.group-chats-header h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #333;
}

.create-group-btn {
    background: linear-gradient(135deg, #409eff, #337ecc);
    border: none;
    color: white;
}

.group-chats-list {
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.group-chat-item {
    display: flex;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    transition: background-color 0.2s;
}

.group-chat-item:hover {
    background-color: #f9f9f9;
}

.group-chat-item:last-child {
    border-bottom: none;
}

.group-avatar {
    margin-right: 15px;
}

.group-avatar img {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
}

.avatar-placeholder {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #42b883, #3498db);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 1.2rem;
}

.group-info {
    flex: 1;
    min-width: 0;
}

.group-name {
    font-weight: bold;
    margin-bottom: 5px;
    color: #333;
}

.group-meta {
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.member-count {
    font-size: 0.8rem;
    color: #999;
}

.last-message {
    font-size: 0.9rem;
    color: #666;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.no-group-chats {
    text-align: center;
    padding: 40px 20px;
    color: #999;
}
</style>