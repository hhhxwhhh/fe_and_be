<template>
    <div class="ai-chat-page">
        <div class="page-header">
            <el-page-header title="返回" @back="$router.back()">
                <template #content>
                    <div class="header-content">
                        <div class="header-icon">
                            <el-icon size="24">
                                <ChatDotRound />
                            </el-icon>
                        </div>
                        <div class="header-text">
                            <h1>AI智能助手</h1>
                            <p class="header-subtitle">基于DeepSeek大语言模型</p>
                        </div>
                    </div>
                </template>
            </el-page-header>
        </div>

        <div class="content-wrapper">
            <el-row :gutter="20">
                <el-col :xs="24" :sm="24" :md="16" :lg="18">
                    <div class="chat-container">
                        <!-- 模型选择 -->
                        <div class="model-selection">
                            <el-select v-model="selectedModel" placeholder="选择模型" size="small" @change="onModelChange">
                                <el-option v-for="model in availableModels" :key="model.value" :label="model.label"
                                    :value="model.value">
                                </el-option>
                            </el-select>
                            <el-button type="danger" plain size="small" @click="clearHistory"
                                style="margin-left: 10px;">
                                清空历史
                            </el-button>
                        </div>

                        <!-- 历史对话区域 -->
                        <div class="history-section" v-if="chatHistory.length">
                            <div class="history-list">
                                <div v-for="(chat, index) in chatHistory" :key="index" class="chat-item">
                                    <div class="chat-header">
                                        <div class="user-message">
                                            <div class="avatar user-avatar">
                                                <el-icon>
                                                    <User />
                                                </el-icon>
                                            </div>
                                            <div class="message-content">
                                                <div class="message-header">
                                                    <span class="username">您</span>
                                                    <span class="timestamp">{{ formatTime(chat.timestamp) }}</span>
                                                </div>
                                                <div class="message-text">{{ chat.prompt }}</div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="chat-response">
                                        <div class="avatar ai-avatar">
                                            <el-icon>
                                                <MagicStick />
                                            </el-icon>
                                        </div>
                                        <div class="message-content">
                                            <div class="message-header">
                                                <span class="username">AI助手</span>
                                                <span class="usage-info">Tokens: {{ chat.usage?.total_tokens || 'N/A'
                                                    }}</span>
                                            </div>
                                            <div class="message-text">{{ chat.response }}</div>
                                            <div class="message-actions">
                                                <el-button type="primary" link @click="copyResponse(chat.response)">
                                                    <el-icon>
                                                        <CopyDocument />
                                                    </el-icon>
                                                    复制
                                                </el-button>
                                                <el-button type="primary" link @click="regenerateResponse(index)">
                                                    <el-icon>
                                                        <Refresh />
                                                    </el-icon>
                                                    重新生成
                                                </el-button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 新对话输入区域 -->
                        <div class="input-section">
                            <AIChatInput @response-generated="addToHistory" ref="aiChatInput" :model="selectedModel"
                                :context-messages="getContextMessages()" />
                        </div>
                    </div>
                </el-col>

                <el-col :xs="24" :sm="24" :md="8" :lg="6">
                    <div class="sidebar">
                        <el-card class="feature-card" shadow="never">
                            <template #header>
                                <div class="card-header">
                                    <el-icon>
                                        <Star />
                                    </el-icon>
                                    <span>使用场景</span>
                                </div>
                            </template>
                            <ul class="feature-list">
                                <li>
                                    <el-icon>
                                        <Edit />
                                    </el-icon>
                                    <span>内容创作辅助</span>
                                </li>
                                <li>
                                    <el-icon>
                                        <Document />
                                    </el-icon>
                                    <span>代码生成与解释</span>
                                </li>
                                <li>
                                    <el-icon>
                                        <Document />
                                    </el-icon>
                                    <span>学习资料整理</span>
                                </li>
                                <li>
                                    <el-icon>
                                        <MagicStick />
                                    </el-icon>
                                    <span>创意文案生成</span>
                                </li>
                                <li>
                                    <el-icon>
                                        <QuestionFilled />
                                    </el-icon>
                                    <span>问题解答</span>
                                </li>
                            </ul>
                        </el-card>

                        <el-card class="feature-card" shadow="never">
                            <template #header>
                                <div class="card-header">
                                    <el-icon>
                                        <Lightning />
                                    </el-icon>
                                    <span>使用提示</span>
                                </div>
                            </template>
                            <ul class="feature-list">
                                <li>
                                    <el-icon>
                                        <InfoFilled />
                                    </el-icon>
                                    <span>问题描述越具体，结果越精准</span>
                                </li>
                                <li>
                                    <el-icon>
                                        <InfoFilled />
                                    </el-icon>
                                    <span>可要求AI以特定格式输出</span>
                                </li>
                                <li>
                                    <el-icon>
                                        <InfoFilled />
                                    </el-icon>
                                    <span>支持多轮对话上下文</span>
                                </li>
                                <li>
                                    <el-icon>
                                        <InfoFilled />
                                    </el-icon>
                                    <span>注意保护个人隐私信息</span>
                                </li>
                            </ul>
                        </el-card>

                        <el-card class="feature-card" shadow="never">
                            <template #header>
                                <div class="card-header">
                                    <el-icon>
                                        <Setting />
                                    </el-icon>
                                    <span>技术说明</span>
                                </div>
                            </template>
                            <div class="tech-info">
                                <p>基于DeepSeek大语言模型，支持多种文本生成任务。</p>
                                <div class="model-info">
                                    <el-tag type="primary" size="small">{{ selectedModel }}</el-tag>
                                    <el-tag type="success" size="small">2048 tokens</el-tag>
                                </div>
                            </div>
                        </el-card>
                    </div>
                </el-col>
            </el-row>
        </div>
    </div>
</template>

<script>
import {
    ChatDotRound,
    User,
    MagicStick,
    CopyDocument,
    Refresh,
    Star,
    Edit,
    Document,
    QuestionFilled,
    InfoFilled,
    Setting,
    Lightning
} from '@element-plus/icons-vue';
import AIChatInput from '../components/AIChatInput.vue';

export default {
    name: 'AIChatView',
    components: {
        AIChatInput,
        ChatDotRound,
        User,
        MagicStick,
        CopyDocument,
        Refresh,
        Star,
        Edit,
        Document,
        QuestionFilled,
        InfoFilled,
        Setting,
        Lightning
    },
    data() {
        return {
            chatHistory: [],
            selectedModel: 'deepseek-chat',
            availableModels: [
                { label: 'DeepSeek Chat', value: 'deepseek-chat' },
                { label: 'DeepSeek Coder', value: 'deepseek-coder' }
            ]
        };
    },
    methods: {
        addToHistory(prompt, response, usage) {
            this.chatHistory.unshift({
                prompt,
                response,
                usage,
                timestamp: new Date()
            });
        },
        copyResponse(text) {
            navigator.clipboard.writeText(text)
                .then(() => {
                    this.$message.success('已复制到剪贴板');
                })
                .catch(() => {
                    this.$message.error('复制失败');
                });
        },
        regenerateResponse(index) {
            const chat = this.chatHistory[index];
            // 移除该项并重新生成
            this.chatHistory.splice(index, 1);
            // 触发重新生成
            this.$refs.aiChatInput.inputPrompt = chat.prompt;
            this.$nextTick(() => {
                this.$refs.aiChatInput.generateResponse();
            });
        },
        clearHistory() {
            this.chatHistory = [];
            this.$message.success('历史记录已清空');
        },
        formatTime(date) {
            return new Date(date).toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        onModelChange() {
            this.$message.success(`已切换到 ${this.availableModels.find(m => m.value === this.selectedModel)?.label} 模型`);
        },
        getContextMessages() {
            // 将最近几轮对话作为上下文传递
            const context = [];
            // 取最近5轮对话作为上下文
            const recentChats = this.chatHistory.slice(0, 5).reverse();
            for (const chat of recentChats) {
                context.push({ role: 'user', content: chat.prompt });
                context.push({ role: 'assistant', content: chat.response });
            }
            return context;
        }
    }
};
</script>

<style scoped>
.ai-chat-page {
    padding: 0;
    height: calc(100vh - 60px);
    background: linear-gradient(135deg, #f0f2f5 0%, #e6e9f0 100%);
}

.page-header {
    background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
    padding: 15px 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
    display: flex;
    align-items: center;
    color: white;
}

.header-icon {
    margin-right: 15px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.header-text h1 {
    margin: 0 0 5px 0;
    font-size: 24px;
    font-weight: 600;
}

.header-subtitle {
    margin: 0;
    font-size: 14px;
    opacity: 0.9;
}

.content-wrapper {
    padding: 20px;
    height: calc(100% - 80px);
    overflow-y: auto;
}

.chat-container {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    padding: 24px;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.model-selection {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 20px;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
}

.section-header h2 {
    margin: 0;
    color: #303133;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 20px;
    font-weight: 600;
}

.history-list {
    flex: 1;
    overflow-y: auto;
    padding-right: 10px;
    margin-bottom: 20px;
}

.chat-item {
    margin-bottom: 25px;
    background: #fafbff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    border: 1px solid #f0f2f5;
}

.chat-header,
.chat-response {
    display: flex;
    margin-bottom: 15px;
}

.chat-response {
    margin-top: 15px;
    margin-bottom: 0;
}

.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    flex-shrink: 0;
}

.user-avatar {
    background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
    color: white;
}

.ai-avatar {
    background: linear-gradient(135deg, #7209b7 0%, #f72585 100%);
    color: white;
}

.message-content {
    flex: 1;
}

.message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.username {
    font-weight: 600;
    color: #303133;
}

.timestamp,
.usage-info {
    font-size: 12px;
    color: #909399;
}

.message-text {
    background: white;
    padding: 15px;
    border-radius: 10px;
    line-height: 1.6;
    white-space: pre-wrap;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
    border: 1px solid #f0f2f5;
}

.message-actions {
    margin-top: 12px;
    display: flex;
    gap: 15px;
}

.input-section {
    margin-top: auto;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.sidebar {
    display: flex;
    flex-direction: column;
    gap: 20px;
    height: 100%;
}

.feature-card {
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
    border: none;
    background: #fafbff;
}

.feature-card :deep(.el-card__header) {
    background: #f0f2f5;
    border-bottom: 1px solid #e2e5ec;
    padding: 15px 20px;
    border-radius: 12px 12px 0 0 !important;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    color: #303133;
}

.feature-list {
    padding: 0;
    margin: 0;
}

.feature-list li {
    list-style: none;
    padding: 12px 0;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    border-bottom: 1px solid #f0f2f5;
}

.feature-list li:last-child {
    border-bottom: none;
}

.feature-list li .el-icon {
    color: #4361ee;
    margin-top: 2px;
}

.tech-info p {
    margin: 0 0 15px 0;
    line-height: 1.6;
    color: #606266;
    font-size: 14px;
}

.model-info {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

@media (max-width: 768px) {
    .content-wrapper {
        padding: 15px;
    }

    .chat-container {
        padding: 15px;
    }

    .page-header {
        padding: 12px 20px;
    }

    .header-text h1 {
        font-size: 20px;
    }

    .model-selection {
        flex-direction: column;
        align-items: flex-end;
    }
}
</style>