"""
URL configuration for server_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# server_core/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# server_core/urls.py
from users.views import RegisterView

# 1. 引入业务视图 (全部从 articles.views 引入，不搞新文件)
from articles.views import (
    ArticleViewSet, 
    AdminStatsView, 
    AdminUserViewSet, 
    AdminReportViewSet
)

# 2. 引入用户与认证视图
from users.views import UserProfileView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

# 3. 引入 AI 网关视图
from ai_gateway.views import AIGenerateView, AIPolishView

# --- 路由器配置 ---

# 普通用户路由
router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='articles')

# 管理员专属路由 (挂载在 api/admin/ 路径下)
admin_router = DefaultRouter()
admin_router.register(r'mgr/users', AdminUserViewSet, basename='admin-users')
admin_router.register(r'mgr/reports', AdminReportViewSet, basename='admin-reports')

# --- 总路由表 ---

urlpatterns = [
    # 传统的 Django 管理后台 (备用)
    path('admin/', admin.site.urls),

    path('api/register/', RegisterView.as_view(), name='register'),

    # 1. 文章业务接口 (包含 /api/articles/ 和 /api/articles/public/)
    path('api/', include(router.urls)), 

    # 2. 管理员数据看板接口
    path('api/admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    
    # 3. 管理员管控接口 (包含 /api/admin/mgr/users/ 和 /api/admin/mgr/reports/)
    path('api/admin/', include(admin_router.urls)),
    
    # 4. 个人中心接口 (查看和修改自己的 API Key 等)
    path('api/users/me/', UserProfileView.as_view(), name='user_profile'), 
    
    # 5. JWT 认证接口 (登录与刷新)
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 6. AI 引擎接口 (生成与润色)
    path('api/ai/generate/', AIGenerateView.as_view(), name='ai_generate'),
    path('api/ai/polish/', AIPolishView.as_view(), name='ai_polish'),
]