<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '../store'
import { authAPI } from '../api'

const router = useRouter()
const store = useMainStore()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

const login = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await authAPI.login(form.value)
    const { access, user } = response.data
    
    localStorage.setItem('token', access)
    store.setUser(user)
    
    // 登录成功后跳转到论坛页面
    router.push('/forum')
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-container">
      <h2>登录</h2>
      <form @submit.prevent="login">
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
        
        <div v-if="error" class="error">
          {{ error }}
        </div>
        
        <button 
          type="submit" 
          :disabled="loading"
          class="btn btn-primary"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <p class="switch-page">
        还没有账户？ 
        <router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}

.auth-container {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background-color: #42b883;
  color: white;
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background-color: #359c6d;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #e74c3c;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: #fdf2f2;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.switch-page {
  text-align: center;
  margin-top: 1rem;
}

.switch-page a {
  color: #42b883;
  text-decoration: none;
}

.switch-page a:hover {
  text-decoration: underline;
}
</style>