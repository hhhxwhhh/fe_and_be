<template>
    <div class="contacts-page">
        <div class="contacts-header">
            <h2>联系人</h2>
        </div>

        <div class="contacts-content">
            <UserList @user-selected="handleUserSelected" />
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import UserList from '../components/UserList.vue'

const router = useRouter()

const handleUserSelected = (user) => {
    router.push(`/messages/${user.id}`)
}
</script>

<style scoped>
.contacts-page {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    height: calc(100vh - 100px);
}

.contacts-header {
    margin-bottom: 20px;
}

.contacts-header h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #333;
}

.contacts-content {
    height: calc(100% - 60px);
}
</style>