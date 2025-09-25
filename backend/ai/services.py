import openai
from django.conf import settings
import os


class DeepSeekService:
    def __init__(self):
        """
        初始化DeepSeek服务
        DeepSeek API与OpenAI API兼容，可以直接使用openai库
        """
        # 尝试从多个来源获取API密钥
        api_key = "sk-7ab60319c915461981cc306de014a2e1"

        # 如果没有获取到API密钥，则抛出异常
        if not api_key:
            raise ValueError(
                "DeepSeek API key is not set. Please set DEEPSEEK_API_KEY in settings or environment variable."
            )

        self.client = openai.OpenAI(
            api_key=api_key, base_url="https://api.deepseek.com/v1"
        )

    def chat_completion(
        self,
        messages,
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=2048,
        **kwargs
    ):
        try:
            # 过滤掉None值的参数
            kwargs = {k: v for k, v in kwargs.items() if v is not None}

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return {
                "status": "success",
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_text(
        self, prompt, model="deepseek-chat", temperature=0.7, max_tokens=2048, **kwargs
    ):
        messages = [{"role": "user", "content": prompt}]

        # 过滤掉None值的参数
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        return self.chat_completion(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
