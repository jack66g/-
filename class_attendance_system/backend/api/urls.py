from django.urls import path
from .views import LoginView, RecognizeView, LeaveView, AttendanceView, AdminUserView, FaceRegisterView, AttendanceStatsView # 引入它

urlpatterns = [
    path('login/', LoginView.as_view(), name='api-login'),
    path('recognize/', RecognizeView.as_view(), name='api-recognize'),
    path('leaves/', LeaveView.as_view(), name='api-leaves'),
    path('attendance/', AttendanceView.as_view(), name='api-attendance'),
    # 增加这行录入人脸的接口
    path('face/register/', FaceRegisterView.as_view(), name='api-face-register'),
    # 2. 确保加上了这一行！并且注意最后面要有斜杠 '/'
    path('admin/users/', AdminUserView.as_view(), name='api-admin-users'),
   
    path('stats/', AttendanceStatsView.as_view(), name='api-stats'),
]