# ai_gateway/views.py
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class AIBaseView(APIView):
    """AI 网关基类：处理通用的 Key 校验和 API 请求"""
    permission_classes = [IsAuthenticated]

    def call_deepseek(self, user, messages):
        api_key = user.deepseek_api_key
        if not api_key:
            return Response(
                {"error": "请先在个人中心配置您的 DeepSeek API Key 才能开启 AI 魔法✨"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False  # 第一版先稳扎稳打用非流式
        }

        try:
            # 这里的 URL 以后如果 DeepSeek 换了可以随时改
            url = "https://api.deepseek.com/chat/completions"
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return Response({"result": data['choices'][0]['message']['content']})
        
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"AI 连接失败：{str(e)}，请检查您的 Key 是否有效。"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AIGenerateView(AIBaseView):
    """1. 直接写文章 (Generate)"""
    def post(self, request):
        topic = request.data.get('topic')
        style = request.data.get('style', '幽默生动')
        
        if not topic:
            return Response({"error": "没有主题，AI 也巧妇难为无米之炊呀~"}, status=400)

        # 封装系统提示词和用户提示词
        messages = [
            {"role": "system", "content": "你是一个爆款文章写手。请输出高质量、排版精良的 Markdown 格式文章。"},
            {"role": "user", "content": f"请根据以下主题写一篇博客：{topic}，风格要求：{style}"}
        ]
        
        return self.call_deepseek(request.user, messages)

class AIPolishView(AIBaseView):
    """2. 智能润色 (Polish)"""
    def post(self, request):
        content = request.data.get('content')
        
        if not content:
            return Response({"error": "请先选中或输入需要润色的文字内容~"}, status=400)

        # 封装润色专用提示词
        messages = [
            {"role": "system", "content": "你是一个资深编辑。"},
            {"role": "user", "content": f"请纠正以下文本的语病，并让表述更生动专业，只返回修改后的结果，不要带任何解释：{content}"}
        ]
        
        return self.call_deepseek(request.user, messages)