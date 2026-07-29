# server_core/admin_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from django.utils import timezone
from users.models import User
from articles.models import Article, Report
from users.serializers import UserSerializer
from articles.serializers import ArticleSerializer
from rest_framework import serializers

# 专门给举报记录用的简单序列化器
class ReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)
    class Meta:
        model = Report
        fields = '__all__'

# 1. 后台首页数据统计
class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser] # 仅限超级管理员

    def get(self, request):
        today = timezone.now().date()
        stats = {
            "total_users": User.objects.count(),
            "total_articles": Article.objects.count(),
            "today_articles": Article.objects.filter(created_at__date=today).count(),
            "pending_reports": Report.objects.filter(status=0).count(),
        }
        return Response(stats)

# 2. 用户管理 (封禁/解封)
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'patch'] # 只允许查看和局部修改

# 3. 举报处理中心
class AdminReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def audit(self, request, pk=None):
        """
        处理举报：删除违规文章 + 标记举报已处理
        """
        report = self.get_object()
        article = report.article
        
        # 1. 删除违规文章 (也可以改成 status='banned'，这里直接删除更狠)
        if article:
            article.delete()
        
        # 2. 标记举报已处理
        report.status = 1
        report.save()
        
        return Response({"message": "违规内容已清理，举报处理完毕！"})