<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useMainStore } from '../store'
import { useRouter } from 'vue-router'

const store = useMainStore()
const router = useRouter()
const showNotifications = ref(false)

let notificationInterval = null

onMounted(async () => {
  if (store.user) {
    await store.fetchUnreadNotificationsCount()
    
    // 每30秒检查一次新通知
    notificationInterval = setInterval(() => {
      store.fetchUnreadNotificationsCount()
    }, 30000)
  }
})

onBeforeUnmount(() => {
  if (notificationInterval) {
    clearInterval(notificationInterval)
  }
})

const toggleNotifications = async () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    await store.fetchNotifications()
  }
}

const markAsRead = async (notificationId) => {
  await store.markNotificationAsRead(notificationId)
}

const markAllAsRead = async () => {
  await store.markAllNotificationsAsRead()
}

const getNotificationMessage = (notification) => {
  switch (notification.notification_type) {
    case 'like':
      return `${notification.actor} 点赞了你的帖子`
    case 'comment':
      return `${notification.actor} 评论了你的帖子: "${notification.comment}"`
    case 'follow':
      return `${notification.actor} 关注了你`
    default:
      return `${notification.actor} 与你互动`
  }
}

const getTimeAgo = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)
  
  if (seconds < 60) return '刚刚'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟前`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时前`
  return `${Math.floor(seconds / 86400)}天前`
}
</script>

<template>
  <div class="notification-bell">
    <button @click="toggleNotifications" class="bell-button">
      <span class="bell-icon">🔔</span>
      <span v-if="store.unreadNotificationsCount > 0" class="notification-badge">
        {{ store.unreadNotificationsCount }}
      </span>
    </button>
    
    <div v-if="showNotifications" class="notifications-dropdown">
      <div class="notifications-header">
        <h3>通知</h3>
        <button 
          v-if="store.notifications.some(n => !n.is_read)" 
          @click="markAllAsRead"
          class="mark-all-read"
        >
          全部标记为已读
        </button>
      </div>
      
      <div v-if="store.notifications.length === 0" class="no-notifications">
        暂无通知
      </div>
      
      <div v-else class="notifications-list">
        <div 
          v-for="notification in store.notifications" 
          :key="notification.id"
          :class="['notification-item', { unread: !notification.is_read }]"
          @click="markAsRead(notification.id)"
        >
          <div class="notification-content">
            <p>{{ getNotificationMessage(notification) }}</p>
            <div class="notification-meta">
              <span class="time">{{ getTimeAgo(notification.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="showNotifications" class="overlay" @click="showNotifications = false"></div>
  </div>
</template>

<style scoped>
.notification-bell {
  position: relative;
}

.bell-button {
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
  padding: 0.5rem;
}

.bell-icon {
  font-size: 1.2rem;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #e74c3c;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notifications-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 350px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  margin-top: 0.5rem;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.notifications-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.mark-all-read {
  background: none;
  border: none;
  color: #42b883;
  cursor: pointer;
  font-size: 0.9rem;
}

.mark-all-read:hover {
  text-decoration: underline;
}

.no-notifications {
  padding: 2rem;
  text-align: center;
  color: #666;
}

.notifications-list {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background-color: #f9f9f9;
}

.notification-item.unread {
  background-color: #e8f4fc;
}

.notification-item.unread:hover {
  background-color: #d1e7f9;
}

.notification-content p {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.notification-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.time {
  font-size: 0.8rem;
  color: #999;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: 999;
}

@media (max-width: 768px) {
  .notifications-dropdown {
    width: 300px;
    right: -50px;
  }
}
</style>