<template>
    <div class="ai-chat-input">
        <el-input v-model="inputPrompt" type="textarea" placeholder="请输入您的问题或指令..." :rows="4" :disabled="isLoading"
            class="prompt-input" />

        <div class="controls">
            <el-button @click="clearInput" :disabled="isLoading || !inputPrompt" plain>
                清空
            </el-button>

            <el-button @click="generateResponse" type="primary" :loading="isLoading" :disabled="!inputPrompt.trim()">
                {{ isLoading ? '生成中...' : 'AI生成' }}
            </el-button>
        </div>

        <div v-if="aiResponse" class="response-container">
            <div class="response-header">
                <span>AI生成结果</span>
                <el-button @click="copyToClipboard" type="primary" link>复制</el-button>
            </div>
            <div class="ai-response">{{ aiResponse }}</div>
            <div v-if="usage" class="usage-info">
                Tokens使用: {{ usage.total_tokens }} (提示: {{ usage.prompt_tokens }}, 补全: {{ usage.completion_tokens }})
            </div>
        </div>

        <div v-if="error" class="error-message">
            <el-alert :title="error" type="error" show-icon />
        </div>
    </div>
</template>

<script>
import { generateText } from '@/api/ai';

export default {
    name: 'AIChatInput',
    data() {
        return {
            inputPrompt: '',
            aiResponse: '',
            usage: null,
            isLoading: false,
            error: ''
        };
    },
    methods: {
        async generateResponse() {
            this.error = '';
            this.aiResponse = '';
            this.usage = null;
            this.isLoading = true;

            try {
                const result = await generateText(this.inputPrompt);
                if (result.status === 'success') {
                    this.aiResponse = result.content;
                    this.usage = result.usage;
                    this.$emit('response-generated', this.inputPrompt, result.content, result.usage);
                } else {
                    this.error = result.message || '生成失败';
                }
            } catch (err) {
                this.error = err.response?.data?.message || 'AI生成失败，请稍后重试';
            } finally {
                this.isLoading = false;
            }
        },

        clearInput() {
            this.inputPrompt = '';
            this.aiResponse = '';
            this.usage = null;
            this.error = '';
        },

        async copyToClipboard() {
            try {
                await navigator.clipboard.writeText(this.aiResponse);
                this.$message.success('已复制到剪贴板');
            } catch (err) {
                this.$message.error('复制失败');
            }
        }
    }
};
</script>

<style scoped>
.ai-chat-input {
    margin: 1.5rem 0;
    padding: 1rem;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    background-color: #fff;
}

.controls {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 15px;
}

.response-container {
    margin-top: 20px;
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 6px;
}

.response-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    font-weight: bold;
}

.ai-response {
    white-space: pre-wrap;
    line-height: 1.6;
    margin-bottom: 10px;
}

.usage-info {
    font-size: 12px;
    color: #909399;
    text-align: right;
}

.error-message {
    margin-top: 15px;
}
</style>