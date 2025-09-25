from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .services import DeepSeekService


# Create your views here.
class DeepSeekChatView(APIView):
    """调用DeepSeek模型进行对话"""

    permission_classes = [AllowAny]

    def post(self, request):
        messages = request.data.get("messages", [])
        model = request.data.get("model", "deepseek-chat")
        if not messages:
            return Response(
                {"error": "messages is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        temperature = request.data.get("temperature")
        max_tokens = request.data.get("max_tokens", 2048)

        deepseek_service = DeepSeekService()
        result = deepseek_service.chat_completion(
            messages, model=model, temperature=temperature, max_tokens=max_tokens
        )

        if result["status"] == "success":
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeepSeekGenerateTextView(APIView):
    """使用DeepSeek生成文本"""

    permission_classes = [AllowAny]

    def post(self, request):
        prompt = request.data.get("prompt", "")
        model = request.data.get("model", "deepseek-chat")

        if not prompt:
            return Response(
                {"status": "error", "message": "请输入prompt"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        temperature = request.data.get("temperature", 0.7)
        max_tokens = request.data.get("max_tokens", 2048)
        deepseek_service = DeepSeekService()
        result = deepseek_service.generate_text(
            prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens
        )
        if result["status"] == "success":
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
