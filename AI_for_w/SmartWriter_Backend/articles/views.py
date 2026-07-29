# articles/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import timedelta

# 核心模型与序列化器
from users.models import User
from .models import Article, Interaction, Report
from .serializers import ArticleSerializer, ReportSerializer
from users.serializers import UserSerializer

# === 1. 文章业务接口 (普通用户工作台 + 公共广场) ===
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """
        权限控制：
        - 发现页(public)和详情(retrieve)开放。
        - 其他操作需登录。
        """
        if self.action in ['public', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        
        # 1. 管理员拥有上帝视角，看全站所有文章
        if user.is_authenticated and user.role == 'admin':
            return Article.objects.all().order_by('-created_at')

        # 2. 核心修正：增加 'report' 到白名单
        # 当用户进行 详情(retrieve)、点赞(interact)、举报(report) 时，
        # 必须允许他们查找到别人的（已发布的）文章。
        if self.action in ['interact', 'retrieve', 'public', 'report']:
            from django.db.models import Q
            if user.is_authenticated:
                # 允许看到：已发布的文章 OR 自己写的草稿/文章
                return Article.objects.filter(
                    Q(status='published') | Q(author=user)
                ).order_by('-created_at')
            # 未登录用户只能看到已发布的
            return Article.objects.filter(status='published').order_by('-created_at')

        # 3. 对于 我的创作库(list)、修改(update)、删除(destroy)
        # 严格限制：只能看到/操作自己写的文章
        if user.is_authenticated:
            return Article.objects.filter(author=user).order_by('-created_at')
            
        return Article.objects.none()

    def perform_create(self, serializer):
        # 自动关联当前登录用户为作者
        serializer.save(author=self.request.user)

    # --- 公共发现页接口：GET /api/articles/public/ ---
    @action(detail=False, methods=['get'])
    def public(self, request):
        articles = Article.objects.filter(status='published').order_by('-created_at')
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)

    # --- 点赞/踩切换接口：POST /api/articles/{id}/interact/ ---
    @action(detail=True, methods=['post'])
    def interact(self, request, pk=None):
        article = self.get_object()
        action_type = request.data.get('type') # 1:点赞, 2:踩
        
        if action_type not in [1, 2]:
            return Response({"error": "非法操作类型"}, status=status.HTTP_400_BAD_REQUEST)

        interaction = Interaction.objects.filter(user=request.user, article=article).first()
        if interaction:
            if interaction.action_type == action_type:
                interaction.delete()
                if action_type == 1: article.like_count -= 1
                else: article.dislike_count -= 1
            else:
                if action_type == 1:
                    article.like_count += 1
                    article.dislike_count -= 1
                else:
                    article.like_count -= 1
                    article.dislike_count += 1
                interaction.action_type = action_type
                interaction.save()
        else:
            Interaction.objects.create(user=request.user, article=article, action_type=action_type)
            if action_type == 1: article.like_count += 1
            else: article.dislike_count += 1
        
        article.save()
        return Response({
            "like_count": article.like_count,
            "dislike_count": article.dislike_count,
            "current_interact": action_type if not interaction or interaction.action_type != action_type else 0
        })

    # --- 提交举报接口：POST /api/articles/{id}/report/ ---
    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        article = self.get_object()
        reason = request.data.get('reason')
        if not reason:
            return Response({"error": "请提供举报理由"}, status=status.HTTP_400_BAD_REQUEST)

        Report.objects.create(
            reporter=request.user,
            article=article,
            reason=reason
        )
        return Response({"message": "举报已提交，感谢您的监督！"})


# === 2. 管理员专属：数据大屏接口 (真实聚合统计) ===
class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        
        # 基础数据统计
        stats = {
            "total_users": User.objects.count(),
            "total_articles": Article.objects.count(),
            "today_articles": Article.objects.filter(created_at__date=today).count(),
            "pending_reports": Report.objects.filter(status='pending').count(),
        }

        # --- 核心：计算过去 7 天真实趋势 ---
        start_date = today - timedelta(days=6)
        
        # 聚合查询：按天分组并计数
        daily_counts = (
            Article.objects.filter(created_at__date__range=[start_date, today])
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        # 补全 7 天日期字典，防止某天投稿量为0时图表断裂
        date_map = { (start_date + timedelta(days=i)).strftime('%m-%d'): 0 for i in range(7) }
        
        for entry in daily_counts:
            date_str = entry['date'].strftime('%m-%d')
            date_map[date_str] = entry['count']

        # 封装为 Echarts 喜欢的格式
        stats["chart_data"] = {
            "dates": list(date_map.keys()),
            "counts": list(date_map.values())
        }

        return Response(stats)


# === 3. 管理员专属：用户管理 (封禁/解封) ===
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'patch']

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response({"error": "不能封禁自己"}, status=400)
        user.is_active = not user.is_active
        user.save()
        return Response({"is_active": user.is_active})


# === 4. 管理员专属：举报处理中心 (修正后的方案一) ===
class AdminReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def audit(self, request, pk=None):
        """处理举报：直接删除违规文章。"""
        report = self.get_object()
        article = report.article
        
        if article:
            # 关键：调用 delete 之后，当前的 report 会因为 CASCADE 被联动删除
            article.delete()
            # 既然 report 已经被联动删除了，就不能再调用 report.save()，直接返回成功即可
            return Response({"message": "违规文章已清理，相关举报记录已同步销毁。"})
        
        # 如果文章已经被别人先删了，但举报记录还“活着”，我们就处理这条孤儿记录
        report.status = 'processed'
        report.save()
        return Response({"message": "举报记录已标记为处理完成。"})


# === 5. 管理员专属：文章大盘 (用于全量管理) ===
class AdminArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAdminUser]