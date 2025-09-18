<script setup>
import { ref, watch } from 'vue'
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
const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const passwordStrength = ref(0)

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const togglePasswordConfirmVisibility = () => {
  showPasswordConfirm.value = !showPasswordConfirm.value
}

// 计算密码强度
const calculatePasswordStrength = (password) => {
  let strength = 0
  if (password.length >= 8) strength++
  if (/[a-z]/.test(password)) strength++
  if (/[A-Z]/.test(password)) strength++
  if (/[0-9]/.test(password)) strength++
  if (/[^A-Za-z0-9]/.test(password)) strength++
  return Math.min(strength, 5)
}

// 监听密码输入变化
watch(() => form.value.password, (newPassword) => {
  passwordStrength.value = calculatePasswordStrength(newPassword)
})

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
      <div class="auth-header">
        <h2>创建账户</h2>
        <p>加入我们的社区，分享你的想法</p>
      </div>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <form @submit.prevent="register">
        <div class="form-group">
          <label for="username">用户名</label>
          <div class="input-wrapper">
            <span class="input-icon">👤</span>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              placeholder="请输入用户名"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="email">邮箱地址</label>
          <div class="input-wrapper">
            <span class="input-icon">✉️</span>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              placeholder="请输入邮箱地址"
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
              placeholder="请输入密码"
            />
            <button 
              type="button" 
              class="toggle-password"
              @click="togglePasswordVisibility"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
          
          <div v-if="form.password" class="password-strength">
            <div class="strength-meter">
              <div 
                class="strength-fill" 
                :class="`strength-${passwordStrength}`"
                :style="{ width: `${passwordStrength * 20}%` }"
              ></div>
            </div>
            <div class="strength-label">
              密码强度: 
              <span v-if="passwordStrength === 0">请输入密码</span>
              <span v-else-if="passwordStrength <= 2" class="weak">弱</span>
              <span v-else-if="passwordStrength <= 4" class="medium">中等</span>
              <span v-else class="strong">强</span>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label for="password_confirm">确认密码</label>
          <div class="input-wrapper">
            <span class="input-icon">🔒</span>
            <input
              id="password_confirm"
              v-model="form.password_confirm"
              :type="showPasswordConfirm ? 'text' : 'password'"
              required
              placeholder="请再次输入密码"
            />
            <button 
              type="button" 
              class="toggle-password"
              @click="togglePasswordConfirmVisibility"
            >
              {{ showPasswordConfirm ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>
        
        <button 
          type="submit" 
          :disabled="loading"
          class="submit-btn"
        >
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? '注册中...' : '创建账户' }}
        </button>
      </form>
      
      <div class="divider">
        <span>或</span>
      </div>
      
      <div class="social-login">
        <button class="social-btn">
          <span class="social-icon">🌐</span>
          <span>使用 Google 注册</span>
        </button>
        <button class="social-btn">
          <span class="social-icon">📘</span>
          <span>使用 Facebook 注册</span>
        </button>
      </div>
      
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

.form-group input::placeholder {
  color: #a0aec0;
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

.password-strength {
  margin-top: 0.75rem;
}

.strength-meter {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-0 { background: #e2e8f0; }
.strength-1 { background: #e74c3c; }
.strength-2 { background: #f39c12; }
.strength-3 { background: #3498db; }
.strength-4 { background: #2ecc71; }
.strength-5 { background: #27ae60; }

.strength-label {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #718096;
}

.strength-label .weak { color: #e74c3c; }
.strength-label .medium { color: #f39c12; }
.strength-label .strong { color: #27ae60; }

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
  margin-top: 0.5rem;
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

.error-message {
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