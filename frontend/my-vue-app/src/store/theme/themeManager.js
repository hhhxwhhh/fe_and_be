import { reactive } from 'vue'

// 主题配置
const themes = {
  light: {
    name: '浅色主题',
    class: 'light-theme',
    colors: {
      // --- 原有的变量 ---
      primary: '#409eff',
      background: '#f5f7fa',
      cardBackground: '#ffffff',
      textPrimary: '#303133',
      textSecondary: '#909399',
      border: '#dcdfe6',
      // --- 新增的 header 专属变量 ---
      headerBackground: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      headerText: '#ffffff',
      headerHoverBg: 'rgba(255, 255, 255, 0.1)', // 鼠标悬停/交互背景
      headerInputBg: 'rgba(255, 255, 255, 0.15)', // 输入框背景
      headerPlaceholderText: 'rgba(255, 255, 255, 0.7)' // 输入框占位符文字
    }
  },
  dark: {
    name: '深色主题',
    class: 'dark-theme',
    colors: {
      // --- 原有的变量 ---
      primary: '#409eff',
      background: '#1a1a1a',
      cardBackground: '#2d2d2d',
      textPrimary: '#ffffff',
      textSecondary: '#b2b2b2',
      border: '#444444',
      // --- 新增的 header 专属变量 ---
      headerBackground: 'linear-gradient(135deg, #2c3e50 0%, #34495e 100%)',
      headerText: '#e5e5e5', // 使用灰白色，不刺眼
      headerHoverBg: 'rgba(255, 255, 255, 0.08)', // 深色模式下透明度可以更低
      headerInputBg: 'rgba(255, 255, 255, 0.1)',
      headerPlaceholderText: 'rgba(255, 255, 255, 0.5)' // 深色模式下占位符可以更暗
    }
  }
}

// 初始化主题状态
const state = reactive({
  currentTheme: 'light',
  themes: themes
})

// 获取当前主题配置
const getCurrentTheme = () => {
  return state.themes[state.currentTheme]
}

// 切换主题
const toggleTheme = () => {
  state.currentTheme = state.currentTheme === 'light' ? 'dark' : 'light'
  applyTheme()
  // 保存到本地存储
  localStorage.setItem('chat-app-theme', state.currentTheme)
}

// 应用主题
const applyTheme = () => {
  // 移除所有可能存在的主题类
  Object.values(state.themes).forEach(theme => {
    document.body.classList.remove(theme.class)
  })

  // 添加当前主题对应的类
  const currentTheme = getCurrentTheme()
  document.body.classList.add(currentTheme.class)

  // 应用CSS变量
  const root = document.documentElement
  Object.entries(currentTheme.colors).forEach(([key, value]) => {
    root.style.setProperty(`--chat-${key}`, value)
  })
}

// 初始化主题
const initTheme = () => {
  // 从本地存储获取保存的主题
  const savedTheme = localStorage.getItem('chat-app-theme')
  if (savedTheme && state.themes[savedTheme]) {
    state.currentTheme = savedTheme
  } else {
    // 检查系统主题偏好
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      state.currentTheme = 'dark'
    }
  }

  applyTheme()
}

// 主题管理器
export const themeManager = {
  state,
  getCurrentTheme,
  toggleTheme,
  applyTheme,
  initTheme
}