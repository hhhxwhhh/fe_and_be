import { reactive } from 'vue'

// 主题配置
const themes = {
  light: {
    name: '浅色主题',
    class: 'light-theme',
    colors: {
      primary: '#409eff',
      background: '#f0f2f5',
      cardBackground: '#ffffff',
      textPrimary: '#303133',
      textSecondary: '#909399',
      border: '#e4e7ed'
    }
  },
  dark: {
    name: '深色主题',
    class: 'dark-theme',
    colors: {
      primary: '#66b1ff',
      background: '#141414',
      cardBackground: '#1d1d1d',
      textPrimary: '#e5e5e5',
      textSecondary: '#a3a3a3',
      border: '#3a3a3a'
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