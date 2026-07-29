# articles/admin_views.py
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from users.models import User
from .models import Article, Report
from .serializers import ArticleSerializer, ReportSerializer
from users.serializers import UserSerializer

# 1. 后台首页：数据统计大屏接口
class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser] # 只有管理员能看

    def get(self, request):
        today = timezone.now().date()
        stats = {
            "total_users": User.objects.count(),
            "total_articles": Article.objects.count(),
            "today_articles": Article.objects.filter(created_at__date=today).count(),
            "pending_reports": Report.objects.filter(status='pending').count(),
        }
        # 这里的数据以后可以对接前端 Echarts 绘制饼图或柱状图
        return Response(stats)

# 2. 用户管理：封禁/解封 (修改 is_active)
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'patch'] # 禁止直接删除和创建

    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        """一键封禁/解封"""
        user = self.get_object()
        if user == request.user:
            return Response({"error": "你不能封禁你自己！"}, status=400)
        
        user.is_active = not user.is_active
        user.save()
        status_text = "激活" if user.is_active else "封禁"
        return Response({"message": f"用户 {user.username} 已被 {status_text}"})

# 3. 内容管理：文章大盘 (强制下架)
class AdminArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAdminUser]

    # 管理员拥有删除任何文章的权力
    def destroy(self, request, *args, **kwargs):
        article = self.get_object()
        title = article.title
        article.delete()
        return Response({"message": f"文章《{title}》已被强制删除"})

# 4. 举报处理中心
class AdminReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def audit(self, request, pk=None):
        """处理举报：确认违规并删除文章"""
        report = self.get_object()
        article = report.article
        
        # 如果文章还存在，直接删除
        if article:
            article.delete()
        
        # 标记举报为已处理
        report.status = 'processed'
        report.save()
        
        return Response({"message": "审核完成：违规文章已清理，举报记录已标记为已处理。"})