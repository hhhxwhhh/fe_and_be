<script setup>
import { computed } from 'vue'
import { themeManager } from '../store/theme/themeManager'

// 计算当前主题
const currentTheme = computed(() => themeManager.state.currentTheme)
const currentThemeConfig = computed(() => themeManager.getCurrentTheme())

// 切换主题
const toggleTheme = () => {
    themeManager.toggleTheme()
}
</script>

<template>
    <div class="theme-toggle" @click="toggleTheme" :title="`切换到${currentTheme === 'light' ? '深色' : '浅色'}主题`">
        <div class="theme-icon">
            <span v-if="currentTheme === 'light'">☀️</span>
            <span v-else>🌙</span>
        </div>
        <span class="theme-name">{{ currentThemeConfig.name }}</span>
    </div>
</template>

<style scoped>
.theme-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: var(--chat-cardBackground);
    border: 1px solid var(--chat-border);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.theme-toggle:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    background: var(--chat-background);
}

.theme-icon {
    font-size: 16px;
    transition: transform 0.3s ease;
}

.theme-toggle:hover .theme-icon {
    transform: rotate(15deg);
}

.theme-name {
    font-size: 14px;
    color: var(--chat-textPrimary);
    font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .theme-toggle {
        padding: 6px 10px;
    }

    .theme-name {
        font-size: 12px;
    }
}
</style>