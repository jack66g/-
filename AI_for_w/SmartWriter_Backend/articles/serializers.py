# articles/serializers.py
from rest_framework import serializers
from .models import Article, Interaction
# articles/serializers.py (部分代码，加上 ReportSerializer)
from rest_framework import serializers
from .models import Article, Report

class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    # 新增字段：让前端知道当前用户对该文章的操作状态 (0:无, 1:点赞, 2:踩)
    user_interact = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'author_name', 'status', 
                  'like_count', 'dislike_count', 'created_at', 'user_interact']
        read_only_fields = ['author', 'like_count', 'dislike_count', 'created_at']

    def get_user_interact(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            interaction = Interaction.objects.filter(user=user, article=obj).first()
            return interaction.action_type if interaction else 0
        return 0

class ReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'