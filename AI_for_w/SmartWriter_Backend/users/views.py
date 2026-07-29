# users/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
# users/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from .models import User

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    个人中心：支持获取信息 (Retrieve) 和 修改信息 (Update)
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 无论前端传什么 ID，后端永远只返回当前登录用户的对象
        # 彻底杜绝通过修改 URL ID 去偷看别人资料的可能性
        return self.request.user

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义登录视图：返回 Token 的同时带上 role 和 username
    """
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [] # 注册不需要登录权限

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if User.objects.filter(username=username).exists():
            return Response({"error": "这个账号已经被别人抢占啦！"}, status=status.HTTP_400_BAD_REQUEST)

        # 创建普通用户
        User.objects.create(
            username=username,
            password=make_password(password), # 记得加密密码！
            email=email,
            role='user' # 默认注册为普通创作者
        )

        return Response({"message": "注册成功"}, status=status.HTTP_201_CREATED)