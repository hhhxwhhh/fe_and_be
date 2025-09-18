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
    await store.fetchUnreadNotificationCount()
    
    // 每30秒检查一次新通知
    notificationInterval = setInterval(() => {
      store.fetchUnreadNotificationCount()
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
        {{ store.unreadNotificationsCount > 99 ? '99+' : store.unreadNotificationsCount }}
      </span>
    </button>
    
    <transition name="slide-fade">
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
          <div class="empty-icon">🔔</div>
          <p>暂无通知</p>
          <span>当有人与您互动时，您会在这里看到通知</span>
        </div>
        
        <div v-else class="notifications-list">
          <div 
            v-for="notification in store.notifications" 
            :key="notification.id"
            :class="['notification-item', { unread: !notification.is_read }]"
            @click="markAsRead(notification.id)"
          >
            <div class="notification-avatar">
              <div class="avatar-placeholder">
                {{ notification.actor.charAt(0).toUpperCase() }}
              </div>
            </div>
            <div class="notification-content">
              <p class="notification-message">{{ getNotificationMessage(notification) }}</p>
              <div class="notification-meta">
                <span class="time">{{ getTimeAgo(notification.created_at) }}</span>
                <span v-if="!notification.is_read" class="unread-indicator">未读</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="store.notifications.length > 0" class="notifications-footer">
          <button @click="showNotifications = false" class="close-button">
            关闭
          </button>
        </div>
      </div>
    </transition>
    
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
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.bell-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.bell-icon {
  font-size: 1.4rem;
  color: #555;
  transition: all 0.3s ease;
}

.bell-button:hover .bell-icon {
  color: #42b883;
  transform: rotate(15deg);
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: linear-gradient(135deg, #ff416c, #ff4b2b);
  color: white;
  border-radius: 10px;
  min-width: 20px;
  height: 20px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  box-shadow: 0 2px 5px rgba(255, 65, 108, 0.3);
  font-weight: 600;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 65, 108, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 65, 108, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 65, 108, 0);
  }
}

.notifications-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 380px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-top: 0.8rem;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
  animation: dropdownAppear 0.3s cubic-bezier(0.17, 0.67, 0.5, 1.2);
}

@keyframes dropdownAppear {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #eee;
  background: linear-gradient(90deg, #f8f9ff, #f0f4ff);
}

.notifications-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.mark-all-read {
  background: none;
  border: none;
  color: #42b883;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.mark-all-read:hover {
  background-color: rgba(66, 184, 131, 0.1);
  color: #2e8b57;
}

.no-notifications {
  padding: 3rem 2rem;
  text-align: center;
  color: #666;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.no-notifications p {
  font-size: 1.2rem;
  margin: 0 0 0.5rem 0;
  color: #555;
}

.no-notifications span {
  font-size: 0.9rem;
  color: #999;
}

.notifications-list {
  max-height: 350px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background-color: #f9f9ff;
}

.notification-item.unread {
  background-color: #f0f8ff;
  border-left: 3px solid #42b883;
}

.notification-item.unread:hover {
  background-color: #e8f4ff;
}

.notification-avatar {
  margin-right: 1rem;
}

.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1rem;
}

.notification-content {
  flex: 1;
}

.notification-message {
  margin: 0 0 0.5rem 0;
  font-size: 0.95rem;
  line-height: 1.4;
  color: #333;
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

.unread-indicator {
  font-size: 0.7rem;
  color: #42b883;
  background-color: rgba(66, 184, 131, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-weight: 500;
}

.notifications-footer {
  padding: 1rem;
  border-top: 1px solid #eee;
  text-align: center;
  background-color: #f9f9f9;
}

.close-button {
  padding: 0.5rem 1.5rem;
  background: linear-gradient(90deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.close-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
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

/* 动画效果 */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notifications-dropdown {
    width: 320px;
    right: -30px;
  }
  
  .notification-item {
    padding: 1rem;
  }
  
  .avatar-placeholder {
    width: 35px;
    height: 35px;
    font-size: 0.9rem;
  }
  
  .notification-message {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .notifications-dropdown {
    width: 280px;
    right: -10px;
  }
  
  .notifications-header {
    padding: 1rem;
  }
  
  .notification-item {
    padding: 0.8rem;
  }
  
  .notification-content {
    padding-right: 0.5rem;
  }
  
  .notification-message {
    font-size: 0.85rem;
  }
  
  .time {
    font-size: 0.7rem;
  }
}
</style>