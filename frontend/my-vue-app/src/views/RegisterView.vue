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
    
    router.push('/')
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
  <div class="register">
    <div class="register-form">
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
          class="submit-btn"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
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

.register-form {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.register-form h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #359c6d;
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #ffecec;
  color: #d8000c;
  border: 1px solid #ffd2d2;
  border-radius: 4px;
}
</style>