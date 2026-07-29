# users/serializers.py
from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 1. 补齐字段：必须包含 date_joined 和 is_active 前端才能正常显示
        fields = [
            'id', 
            'username', 
            'email', 
            'role', 
            'deepseek_api_key', 
            'date_joined', 
            'is_active'
        ]
        
        # 2. 保护机制：这些字段由系统生成或管理，普通用户不可通过接口修改
        # 注意：is_active 没放进来，是因为管理员需要通过 patch 修改它
        read_only_fields = ['id', 'username', 'role', 'date_joined']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    登录序列化器：在返回 JWT Token 的同时，额外返回角色和用户名
    用于前端 LoginView.vue 的角色分流逻辑
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # 将自定义字段塞入返回的 JSON 数据中
        data['role'] = self.user.role
        data['username'] = self.user.username
        
        return data