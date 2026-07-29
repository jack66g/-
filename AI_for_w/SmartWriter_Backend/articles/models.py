from django.db import models
from django.conf import settings

class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
    )
    
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="文章正文") # 存储 Markdown 格式
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # 统计数据
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Interaction(models.Model):
    ACTION_CHOICES = (
        (1, '点赞'),
        (2, '踩'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='interactions')
    action_type = models.IntegerField(choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 联合唯一索引：防止同一个用户对同一篇文章多次点赞/踩
        unique_together = ('user', 'article')

class Report(models.Model):
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processed', '已处理'),
    )
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_reports')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField(verbose_name="举报理由")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"举报: {self.article.title} - {self.get_status_display()}"
