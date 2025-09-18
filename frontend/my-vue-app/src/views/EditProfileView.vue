<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '../store'
import { authAPI } from '../api'
import { ElForm, ElFormItem, ElInput, ElButton, ElUpload, ElMessage, ElCard } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const store = useMainStore()
const router = useRouter()

const form = ref({
  username: '',
  email: '',
  bio: '',
  birth_date: ''
})

const loading = ref(false)
const avatarUrl = ref('')
const avatarFile= ref(null)

onMounted(async () => {
  try {
    const response = await authAPI.profile()
    const userData = response.data
    form.value = {
      username: userData.username,
      email: userData.email,
      bio: userData.bio || '',
      birth_date: userData.birth_date || ''
    }
    avatarUrl.value = userData.avatar || ''
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
})

const handleAvatarSuccess = (uploadFile) => {
  avatarUrl.value = URL.createObjectURL(uploadFile.raw)
  avatarFile.value = uploadFile.raw
}

const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('头像必须是 JPG 或 PNG 格式!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

const submitForm = async () => {
  try {
    loading.value = true
    const formData = new FormData()
    
    // 添加表单数据
    Object.keys(form.value).forEach(key => {
      if (form.value[key] !== null && form.value[key] !== undefined) {
        formData.append(key, form.value[key])
      }
    })

    if(avatarFile.value)
    {
      formData.append('avatar', avatarFile.value)
    }
    
    const response = await authAPI.updateProfile(formData)
    store.setUser(response.data)
    ElMessage.success('资料更新成功')
    router.push('/profile')
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败: ' + (error.response?.data?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const cancel = () => {
  router.push('/profile')
}
</script>

<template>
  <div class="edit-profile">
    <div class="profile-container">
      <div class="header-section">
        <h1>编辑个人资料</h1>
        <p>更新您的个人信息，让其他人更好地了解您</p>
      </div>
      
      <el-card class="profile-card">
        <el-form 
          :model="form" 
          label-position="top" 
          class="profile-form"
        >
          <div class="form-section">
            <h2>基本信息</h2>
            <div class="avatar-upload-section">
              <div class="avatar-upload">
                <el-upload
                  class="avatar-uploader"
                  action=""
                  :show-file-list="false"
                  :before-upload="beforeAvatarUpload"
                  :auto-upload="false"
                  :on-change="handleAvatarSuccess"
                >
                  <div class="avatar-preview">
                    <img v-if="avatarUrl" :src="avatarUrl" class="avatar" />
                    <div v-else class="avatar-placeholder">
                      <el-icon class="avatar-icon"><Plus /></el-icon>
                    </div>
                  </div>
                </el-upload>
                <div class="avatar-info">
                  <h3>个人头像</h3>
                  <p class="avatar-tip">支持 JPG/PNG 格式，大小不超过 2MB</p>
                </div>
              </div>
            </div>
            
            <div class="form-grid">
              <el-form-item label="用户名" class="form-item">
                <el-input 
                  v-model="form.username" 
                  placeholder="请输入用户名"
                  size="large"
                />
              </el-form-item>
              
              <el-form-item label="邮箱" class="form-item">
                <el-input 
                  v-model="form.email" 
                  type="email" 
                  placeholder="请输入邮箱地址"
                  size="large"
                />
              </el-form-item>
              
              <el-form-item label="生日" class="form-item">
                <el-input 
                  v-model="form.birth_date" 
                  type="date" 
                  placeholder="选择您的生日"
                  size="large"
                />
              </el-form-item>
            </div>
          </div>
          
          <div class="form-section">
            <h2>个人简介</h2>
            <el-form-item label="" class="bio-item">
              <el-input 
                v-model="form.bio" 
                type="textarea" 
                :rows="5"
                placeholder="介绍一下自己，例如兴趣爱好、职业等..."
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </div>
          
          <div class="form-actions">
            <el-button @click="cancel" size="large" class="cancel-button">
              取消
            </el-button>
            <el-button 
              type="primary" 
              @click="submitForm" 
              :loading="loading"
              size="large"
              class="submit-button"
            >
              保存更改
            </el-button>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.edit-profile {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
  padding: 30px 0;
}

.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.header-section h1 {
  font-size: 2.2rem;
  color: #333;
  margin-bottom: 10px;
  font-weight: 700;
}

.header-section p {
  font-size: 1.1rem;
  color: #666;
  max-width: 600px;
  margin: 0 auto;
}

.profile-card {
  border-radius: 20px;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.08);
  border: none;
  overflow: hidden;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9);
}

.profile-card :deep(.el-card__body) {
  padding: 0;
}

.profile-form {
  padding: 30px;
}

.form-section {
  margin-bottom: 30px;
}

.form-section h2 {
  font-size: 1.4rem;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
  position: relative;
}

.form-section h2::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 1px;
}

.avatar-upload-section {
  margin-bottom: 30px;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-preview {
  cursor: pointer;
  transition: all 0.3s ease;
}

.avatar-preview:hover {
  transform: scale(1.05);
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.avatar-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #fff;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.avatar-icon {
  font-size: 2.5rem;
  color: white;
}

.avatar-info h3 {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  color: #333;
}

.avatar-tip {
  margin: 0;
  font-size: 0.9rem;
  color: #999;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.form-item :deep(.el-form-item__label) {
  font-weight: 500;
  color: #555;
  font-size: 1rem;
}

.form-item :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 8px 15px;
}

.bio-item :deep(.el-textarea__inner) {
  border-radius: 10px;
  padding: 15px;
  font-size: 1rem;
  min-height: 120px;
}

.bio-item :deep(.el-input__count) {
  background: transparent;
  color: #999;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.cancel-button {
  padding: 12px 30px;
  border-radius: 30px;
  font-size: 1rem;
  font-weight: 500;
  border: 1px solid #ddd;
  transition: all 0.3s ease;
}

.cancel-button:hover {
  background-color: #f5f5f5;
  transform: translateY(-2px);
}

.submit-button {
  padding: 12px 30px;
  border-radius: 30px;
  font-size: 1rem;
  font-weight: 500;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border: none;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .edit-profile {
    padding: 20px 0;
  }
  
  .profile-container {
    padding: 0 15px;
  }
  
  .header-section h1 {
    font-size: 1.8rem;
  }
  
  .header-section p {
    font-size: 1rem;
  }
  
  .profile-card {
    border-radius: 15px;
  }
  
  .profile-form {
    padding: 20px;
  }
  
  .form-section h2 {
    font-size: 1.3rem;
  }
  
  .avatar-upload {
    flex-direction: column;
    text-align: center;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .form-item :deep(.el-form-item__label) {
    font-size: 0.95rem;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .cancel-button,
  .submit-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .header-section h1 {
    font-size: 1.6rem;
  }
  
  .profile-form {
    padding: 15px;
  }
  
  .form-section {
    margin-bottom: 25px;
  }
  
  .avatar {
    width: 100px;
    height: 100px;
  }
  
  .avatar-placeholder {
    width: 100px;
    height: 100px;
  }
  
  .avatar-icon {
    font-size: 2rem;
  }
}
</style>