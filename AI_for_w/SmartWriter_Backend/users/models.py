from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 使用角色区分权限：admin 或 user
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('user', '普通用户'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    # 允许为空，因为用户需要后续在个人中心手动填写
    deepseek_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="DeepSeek密钥")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
