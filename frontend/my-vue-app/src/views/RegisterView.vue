<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '../store'
import { authAPI } from '../api'

const router = useRouter()
const store = useMainStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: ''
})

const loading = ref(false)
const error = ref('')

const register = async () => {
  try {
    if (form.value.password !== form.value.password_confirm) {
      error.value = '两次输入的密码不一致'
      return
    }
    
    loading.value = true
    error.value = ''
    
    const response = await authAPI.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password
    })
    
    const { token, user } = response.data
    
    localStorage.setItem('token', token)
    store.setUser(user)
    
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register">
    <div class="container">
      <h2>注册</h2>
      <form @submit.prevent="register">
        <div class="form-group">
          <label for="username">用户名:</label>
          <input 
            id="username"
            v-model="form.username"
            type="text"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱:</label>
          <input 
            id="email"
            v-model="form.email"
            type="email"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码:</label>
          <input 
            id="password"
            v-model="form.password"
            type="password"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password_confirm">确认密码:</label>
          <input 
            id="password_confirm"
            v-model="form.password_confirm"
            type="password"
            required
          />
        </div>
        
        <div v-if="error" class="error">
          {{ error }}
        </div>
        
        <button 
          type="submit" 
          :disabled="loading"
          class="btn btn-primary"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <p>
        已有账户？ <router-link to="/login">登录</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}

.container {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background-color: #42b883;
  color: white;
}

.btn:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-bottom: 1rem;
  text-align: center;
}
</style>