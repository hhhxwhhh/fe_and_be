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
    
    const { access, user } = response.data
    
    localStorage.setItem('token', access)
    store.setUser(user)
    
    // 注册成功后跳转到论坛页面
    router.push('/forum')
  } catch (err) {
    // 显示详细的错误信息
    if (err.response?.data) {
      const errorData = err.response.data;
      if (typeof errorData === 'object') {
        const errorMessages = [];
        for (const [field, messages] of Object.entries(errorData)) {
          if (Array.isArray(messages)) {
            errorMessages.push(`${field}: ${messages.join(', ')}`);
          } else {
            errorMessages.push(`${field}: ${messages}`);
          }
        }
        error.value = errorMessages.join('; ');
      } else {
        error.value = errorData;
      }
    } else {
      error.value = err.response?.data?.detail || '注册失败'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-container">
      <h2>用户注册</h2>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
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
        
        <button 
          type="submit" 
          :disabled="loading"
          class="btn btn-primary"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <p class="switch-page">
        已有账户？ 
        <router-link to="/login">立即登录</router-link>
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

.error-message {
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