<template>
    <div class="group-chat-page">
        <div class="group-chat-header">
            <button @click="router.push('/messages')" class="back-button">←</button>
            <div class="group-info">
                <div class="group-avatar">
                    <img v-if="group.avatar" :src="group.avatar" :alt="group.name">
                    <div v-else class="avatar-placeholder">
                        {{ group.name.charAt(0).toUpperCase() }}
                    </div>
                </div>
                <div class="group-name">{{ group.name }}</div>
            </div>
            <div class="group-actions">
                <el-dropdown @command="handleGroupAction">
                    <el-button class="menu-button">
                        <el-icon>
                            <More />
                        </el-icon>
                    </el-button>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item command="addMember">添加成员</el-dropdown-item>
                            <el-dropdown-item command="viewMembers">查看成员</el-dropdown-item>
                            <el-dropdown-item command="leaveGroup">退出群聊</el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </div>
        </div>

        <div ref="messagesContainer" class="messages-container">
            <div v-for="(message, index) in messages" :key="message?.id || index" class="message-wrapper"
                :class="{ 'own-message': isOwnMessage(message) }">
                <MessageItem :message="message" :current-user-id="store.user?.id || 0" @edit="handleEditMessage"
                    @delete="handleDeleteMessage" @revoke="handleRevokeMessage" />
            </div>

            <div v-if="messages.length === 0" class="no-messages">
                还没有消息，开始对话吧！
            </div>
        </div>

        <div class="message-form-container">
            <MessageForm @send="handleSendMessage" />
        </div>

        <!-- 添加成员模态框 -->
        <el-dialog v-model="showAddMemberModal" title="添加成员" width="400px">
            <el-select v-model="selectedUser" filterable placeholder="选择用户" style="width: 100%">
                <el-option v-for="user in availableUsers" :key="user.id" :label="user.username" :value="user.id" />
            </el-select>
            <template #footer>
                <el-button @click="showAddMemberModal = false">取消</el-button>
                <el-button type="primary" @click="addMember">添加</el-button>
            </template>
        </el-dialog>

        <!-- 成员列表模态框 -->
        <el-dialog v-model="showMembersModal" title="群成员" width="400px">
            <div class="members-list">
                <div v-for="member in group.members" :key="member.id" class="member-item">
                    <el-avatar :src="member.avatar" size="small">{{ member.username.charAt(0).toUpperCase()
                        }}</el-avatar>
                    <span class="member-name">{{ member.username }}</span>
                    <span v-if="member.id === group.created_by.id" class="owner-tag">群主</span>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useMainStore } from '../store'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { More } from '@element-plus/icons-vue'
import MessageForm from '../components/MessageForm.vue'
import MessageItem from '../components/MessageItem.vue'
import { messageAPI, authAPI } from '../api'
import websocket from '../services/websocket'

const store = useMainStore()
const route = useRoute()
const router = useRouter()

const group = ref({
    members: []
})
const messages = ref([])
const messagesContainer = ref(null)

// 模态框相关
const showAddMemberModal = ref(false)
const showMembersModal = ref(false)
const selectedUser = ref('')
const availableUsers = ref([])

onMounted(async () => {
    await initializeGroupChat()
})

const initializeGroupChat = async () => {
    const groupId = route.params.groupId
    if (!groupId) {
        router.push('/messages')
        return
    }

    try {
        // 获取群聊信息
        await fetchGroupInfo(groupId)
        // 获取群聊消息
        await fetchGroupMessages(groupId)
        // 滚动到底部
        scrollToBottom()
    } catch (error) {
        console.error('初始化群聊失败:', error)
        ElMessage.error('初始化群聊失败')
    }
}

const fetchGroupInfo = async (groupId) => {
    try {
        const response = await messageAPI.getGroupChat(groupId)
        group.value = response.data
    } catch (error) {
        console.error('获取群聊信息失败:', error)
        throw error
    }
}

const fetchGroupMessages = async (groupId) => {
    try {
        const response = await messageAPI.getGroupMessages(groupId)
        messages.value = response.data || []
    } catch (error) {
        console.error('获取群聊消息失败:', error)
        throw error
    }
}

const handleSendMessage = async (formData) => {
    const groupId = route.params.groupId
    if (!groupId) return

    try {
        // 添加群聊ID到表单数据
        if (!formData.has('group')) {
            formData.append('group', groupId)
        }

        // 通过WebSocket发送消息
        await websocket.sendGroupMessage(groupId, formData)

        // 重新获取消息列表
        await fetchGroupMessages(groupId)
        scrollToBottom()
    } catch (error) {
        console.error('发送群聊消息失败:', error)
        ElMessage.error('发送消息失败')
    }
}

const isOwnMessage = (message) => {
    if (!message || !message.sender) return false
    const currentUserId = store.user?.id || 0
    return message.sender.id === currentUserId
}

const scrollToBottom = () => {
    nextTick(() => {
        if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
    })
}

const handleGroupAction = (command) => {
    switch (command) {
        case 'addMember':
            showAddMemberModal.value = true
            fetchAvailableUsers()
            break
        case 'viewMembers':
            showMembersModal.value = true
            break
        case 'leaveGroup':
            leaveGroup()
            break
    }
}

const fetchAvailableUsers = async () => {
    try {
        const response = await authAPI.getUsers()
        // 过滤掉已经是群成员的用户
        const groupMemberIds = group.value.members.map(m => m.id)
        availableUsers.value = response.data.filter(user => !groupMemberIds.includes(user.id))
    } catch (error) {
        console.error('获取用户列表失败:', error)
        ElMessage.error('获取用户列表失败')
    }
}

const addMember = async () => {
    if (!selectedUser.value) {
        ElMessage.warning('请选择用户')
        return
    }

    try {
        await messageAPI.addGroupMember(route.params.groupId, selectedUser.value)
        ElMessage.success('添加成员成功')
        showAddMemberModal.value = false
        selectedUser.value = ''
        // 重新获取群聊信息
        await fetchGroupInfo(route.params.groupId)
    } catch (error) {
        console.error('添加成员失败:', error)
        ElMessage.error('添加成员失败')
    }
}

const leaveGroup = async () => {
    try {
        await ElMessageBox.confirm('确定要退出群聊吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        })

        await messageAPI.removeGroupMember(route.params.groupId, store.user.id)
        ElMessage.success('已退出群聊')
        router.push('/messages')
    } catch (error) {
        if (error !== 'cancel') {
            console.error('退出群聊失败:', error)
            ElMessage.error('退出群聊失败')
        }
    }
}

const handleEditMessage = (message) => {
    // 群聊消息编辑功能
    ElMessage.info('群聊消息编辑功能待实现')
}

const handleDeleteMessage = (message) => {
    // 群聊消息删除功能
    ElMessage.info('群聊消息删除功能待实现')
}

const handleRevokeMessage = (messageId) => {
    // 群聊消息撤回功能
    ElMessage.info('群聊消息撤回功能待实现')
}
</script>

<style scoped>
.group-chat-page {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 100px);
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
    border-radius: 15px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    overflow: hidden;
}

.group-chat-header {
    display: flex;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    margin-bottom: 15px;
    background: rgba(255, 255, 255, 0.85);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}

.group-chat-header:hover {
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
}

.back-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    font-size: 1rem;
    cursor: pointer;
    color: white;
    margin-right: 15px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
}

.back-button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.group-info {
    display: flex;
    align-items: center;
    flex: 1;
}

.group-avatar img {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
    margin-right: 15px;
    border: 3px solid #fff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.group-avatar img:hover {
    transform: scale(1.05);
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
    margin-right: 15px;
    border: 3px solid #fff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    font-size: 1.2rem;
    transition: all 0.3s ease;
}

.avatar-placeholder:hover {
    transform: scale(1.05);
}

.group-name {
    font-weight: 600;
    font-size: 1.3rem;
    color: #2c3e50;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.group-actions {
    display: flex;
    align-items: center;
}

.menu-button {
    background: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.menu-button:hover {
    background: #e0e0e0;
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px 15px;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 12px;
    margin-bottom: 15px;
    backdrop-filter: blur(5px);
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
    scrollbar-width: thin;
    scrollbar-color: #409eff #e0e0e0;
}

.messages-container::-webkit-scrollbar {
    width: 6px;
}

.messages-container::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

.messages-container::-webkit-scrollbar-thumb {
    background: #409eff;
    border-radius: 10px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
    background: #337ecc;
}

.message-wrapper {
    display: flex;
    margin-bottom: 15px;
    animation: fadeIn 0.3s ease-out;
}

.message-wrapper.own-message {
    justify-content: flex-end;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.no-messages {
    text-align: center;
    padding: 40px 20px;
    color: #999;
    font-style: italic;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 10px;
    margin: auto;
}

.members-list {
    max-height: 300px;
    overflow-y: auto;
}

.member-item {
    display: flex;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid #eee;
}

.member-item:last-child {
    border-bottom: none;
}

.member-name {
    margin-left: 10px;
    flex: 1;
}

.owner-tag {
    background: #409eff;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 12px;
}
</style>