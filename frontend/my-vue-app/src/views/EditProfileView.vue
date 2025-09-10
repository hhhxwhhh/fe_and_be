<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '../store'
import { authAPI } from '../api'
import { ElForm, ElFormItem, ElInput, ElButton, ElUpload, ElMessage } from 'element-plus'
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
    <div class="container">
      <h1>编辑个人资料</h1>
      
      <el-form 
        :model="form" 
        label-position="top" 
        class="profile-form"
      >
        <div class="avatar-upload">
          <el-upload
            class="avatar-uploader"
            action=""
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            :auto-upload="false"
            :on-change="handleAvatarSuccess"
          >
            <img v-if="avatarUrl" :src="avatarUrl" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <p class="avatar-tip">点击上传头像</p>
        </div>
        
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        
        <el-form-item label="邮箱">
          <el-input v-model="form.email" type="email" />
        </el-form-item>
        
        <el-form-item label="生日">
          <el-input v-model="form.birth_date" type="date" />
        </el-form-item>
        
        <el-form-item label="个人简介">
          <el-input 
            v-model="form.bio" 
            type="textarea" 
            :rows="4"
            placeholder="介绍一下自己..."
          />
        </el-form-item>
        
        <div class="form-actions">
          <el-button @click="cancel">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitForm" 
            :loading="loading"
          >
            保存
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.edit-profile {
  padding: 20px 0;
}

.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.profile-form {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.avatar-upload {
  text-align: center;
  margin-bottom: 30px;
}

.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
  display: block;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 50%;
  line-height: 120px;
  cursor: pointer;
  transition: all 0.3s;
}

.avatar-uploader-icon:hover {
  border-color: #42b883;
}

.avatar-tip {
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.form-actions .el-button {
  min-width: 100px;
}
</style>