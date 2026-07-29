"""
软 JWT 认证：过期/无效 Token 不抛 401，降级为匿名用户。
这样公开接口（如 /api/articles/public/）就不会因为
localStorage 中残留的过期 Token 而返回 401 了。
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SoftJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            # Token 过期或无效时，不抛异常，返回 None = 匿名用户
            # 权限检查由各视图的 permission_classes 自行决定
            return None
