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
const showPassword = ref(false)

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

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
      <div class="auth-header">
        <h2>欢迎回来</h2>
        <p>请登录您的账户</p>
      </div>
      
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="email">邮箱地址</label>
          <div class="input-wrapper">
            <span class="input-icon">✉️</span>
            <input 
              id="email"
              v-model="form.email"
              type="email"
              required
              placeholder="请输入您的邮箱"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <div class="input-wrapper">
            <span class="input-icon">🔒</span>
            <input 
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              placeholder="请输入您的密码"
            />
            <button 
              type="button" 
              class="toggle-password"
              @click="togglePasswordVisibility"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>
        
        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" />
            <span>记住我</span>
          </label>
          <a href="#" class="forgot-password">忘记密码？</a>
        </div>
        
        <div v-if="error" class="error">
          {{ error }}
        </div>
        
        <button 
          type="submit" 
          :disabled="loading"
          class="submit-btn"
        >
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? '登录中...' : '登录账户' }}
        </button>
      </form>
      
      <div class="divider">
        <span>或</span>
      </div>
      
      <div class="social-login">
        <button class="social-btn">
          <span class="social-icon">🌐</span>
          <span>使用 Google 登录</span>
        </button>
        <button class="social-btn">
          <span class="social-icon">📘</span>
          <span>使用 Facebook 登录</span>
        </button>
      </div>
      
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
  min-height: 80vh;
  padding: 1rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.auth-container {
  width: 100%;
  max-width: 450px;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  background: white;
  transition: all 0.3s ease;
}

.auth-container:hover {
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h2 {
  margin: 0;
  font-size: 1.8rem;
  color: #2c3e50;
  font-weight: 700;
}

.auth-header p {
  margin: 0.5rem 0 0;
  color: #7f8c8d;
  font-size: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.6rem;
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.95rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: #95a5a6;
  z-index: 1;
}

.form-group input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 1px solid #e0e6ed;
  border-radius: 10px;
  box-sizing: border-box;
  font-size: 1rem;
  transition: all 0.2s ease;
  background-color: #f8fafc;
}

.form-group input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
  background-color: #fff;
}

.toggle-password {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  color: #7f8c8d;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.remember-me {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #7f8c8d;
}

.remember-me input {
  margin-right: 0.5rem;
}

.forgot-password {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.forgot-password:hover {
  text-decoration: underline;
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 1rem;
  background: linear-gradient(45deg, #42b883, #3498db);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(66, 184, 131, 0.3);
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #3aa876, #2980b9);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(66, 184, 131, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  border-bottom: 1px solid #e0e6ed;
}

.divider span {
  padding: 0 1rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.9rem;
  border: 1px solid #e0e6ed;
  border-radius: 10px;
  background: white;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.social-btn:hover {
  border-color: #42b883;
  background: #f8fafc;
  transform: translateY(-1px);
}

.social-icon {
  font-size: 1.1rem;
}

.error {
  color: #e74c3c;
  margin-bottom: 1rem;
  padding: 1rem;
  background-color: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 10px;
  font-size: 0.9rem;
}

.switch-page {
  text-align: center;
  margin-top: 1rem;
  color: #7f8c8d;
  font-size: 0.95rem;
}

.switch-page a {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.switch-page a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .auth-container {
    padding: 1.5rem;
  }
  
  .auth-header h2 {
    font-size: 1.5rem;
  }
}
</style>