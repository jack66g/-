import os
import base64
import numpy as np
import cv2
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Student, Attendance, Leave
from .cv_module.face_utils import recognize_face, train_model

# ==========================================
# 极简序列化工具 (手动组装数据，确保前端解析一致)
# ==========================================
def serialize_attendance(attendance):
    return {
        "id": attendance.id,
        "student_name": attendance.student.user.username,
        "student_no": attendance.student.student_no,
        "class_name": attendance.student.class_name,
        "date": attendance.check_in_time.strftime("%Y-%m-%d"),
        "check_in_time": attendance.check_in_time.strftime("%H:%M:%S"),
        "status": attendance.get_status_display()
    }

def serialize_leave(leave):
    return {
        "id": leave.id,
        "student_name": leave.student.user.username,
        "reason": leave.reason,
        "apply_time": leave.apply_time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": leave.get_status_display()
    }

# ==========================================
# 1. 登录接口 (POST /api/login/)
# ==========================================
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            # 角色判定：超级管理员 -> admin, 职员(is_staff) -> teacher, 其它 -> student
            if user.is_superuser:
                role = 'admin'
            elif user.is_staff:
                role = 'teacher'
            else:
                role = 'student'
                
            student_id = user.student_profile.id if hasattr(user, 'student_profile') else None
            
            return Response({
                "message": "登录成功",
                "role": role,
                "username": user.username,
                "student_id": student_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)

# ==========================================
# 2. 人脸识别与签到接口 (POST /api/recognize/)
# ==========================================
class RecognizeView(APIView):
    def post(self, request):
        base64_image = request.data.get('image')
        if not base64_image:
            return Response({"error": "未提供图片数据"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            img_data = base64.b64decode(base64_image.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # 调用 OpenCV 进行识别
            result = recognize_face(img, model_path='api/cv_module/trainer.yml')
            
            if "error" in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
            student_id = result["student_id"]
            student = Student.objects.get(id=student_id)
            
            # 防重复打卡检查
            today = datetime.date.today()
            if Attendance.objects.filter(student=student, check_in_time__date=today).exists():
                return Response({"message": f"{student.user.username} 今日已签到"}, status=status.HTTP_200_OK)
            
            # 写入考勤
            Attendance.objects.create(student=student, status='present')
            
            return Response({
                "message": f"识别成功！欢迎 {student.user.username}",
                "confidence": result["confidence"]
            }, status=status.HTTP_200_OK)
            
        except Student.DoesNotExist:
            return Response({"error": "识别成功但数据库无匹配档案"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"图像处理失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==========================================
# 3. 请假管理接口 (GET / POST / PUT 审批)
# ==========================================
class LeaveView(APIView):
    def get(self, request):
        leaves = Leave.objects.all().order_by('-apply_time')
        data = [serialize_leave(l) for l in leaves]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        student_id = request.data.get('student_id')
        reason = request.data.get('reason')
        if not student_id or not reason:
            return Response({"error": "缺少必要参数"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(id=student_id)
            Leave.objects.create(student=student, reason=reason)
            return Response({"message": "请假申请已提交"}, status=status.HTTP_201_CREATED)
        except Student.DoesNotExist:
            return Response({"error": "学生档案不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 【教师审批专用】
    def put(self, request):
        leave_id = request.data.get('id')
        new_status = request.data.get('status') # 'approved' 或 'rejected'
        try:
            leave_record = Leave.objects.get(id=leave_id)
            leave_record.status = new_status
            leave_record.save()
            return Response({"message": "审批操作成功"}, status=status.HTTP_200_OK)
        except Leave.DoesNotExist:
            return Response({"error": "找不到该条申请"}, status=status.HTTP_404_NOT_FOUND)

# ==========================================
# 4. 考勤流水接口 (GET /api/attendance/)
# ==========================================
class AttendanceView(APIView):
    def get(self, request):
        records = Attendance.objects.all().order_by('-check_in_time')
        data = [serialize_attendance(r) for r in records]
        return Response(data, status=status.HTTP_200_OK)

# ==========================================
# 5. 管理员账号运维接口 (CRUD)
# ==========================================
class AdminUserView(APIView):
    def get(self, request):
        users = User.objects.all().exclude(is_superuser=True).order_by('-date_joined')
        data = []
        for u in users:
            role = 'teacher' if u.is_staff else 'student'
            class_name = u.student_profile.class_name if hasattr(u, 'student_profile') else '教务组'
            data.append({"id": u.id, "username": u.username, "role": role, "class_name": class_name})
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role')
        class_name = request.data.get('class_name', '未分配班级')

        if User.objects.filter(username=username).exists():
            return Response({"error": "账号已存在"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        if role == 'teacher':
            user.is_staff = True
            user.save()
        else:
            Student.objects.create(user=user, student_no=username, class_name=class_name)
        return Response({"message": "创建成功"}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        user_id = request.data.get('id')
        User.objects.filter(id=user_id).delete()
        return Response({"message": "删除成功"}, status=status.HTTP_200_OK)

# ==========================================
# 6. 人脸录入与自动化训练 (POST /api/face/register/)
# ==========================================
class FaceRegisterView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        images = request.data.get('images')

        dataset_dir = 'api/dataset'
        student_dir = os.path.join(dataset_dir, str(student_id))
        os.makedirs(student_dir, exist_ok=True)
        
        # 清理旧图
        for f in os.listdir(student_dir):
            os.remove(os.path.join(student_dir, f))

        try:
            for i, b64 in enumerate(images):
                img_data = base64.b64decode(b64.split(',')[1])
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cv2.imwrite(os.path.join(student_dir, f"f_{i}.jpg"), gray)

            # 触发训练
            train_model(dataset_path=dataset_dir, model_save_path='api/cv_module/trainer.yml')
            return Response({"message": "模型已更新"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==========================================
# 7. 教师数据大盘统计接口 (GET /api/stats/)
# ==========================================
class AttendanceStatsView(APIView):
    def get(self, request):
        today = datetime.date.today()
        total_stu = Student.objects.count()
        present = Attendance.objects.filter(check_in_time__date=today, status='present').count()
        leaves = Leave.objects.filter(status='approved').count() # 简化统计：所有已通过请假
        
        return Response({
            "total_students": total_stu,
            "present_count": present,
            "leave_count": leaves,
            "absent_count": max(0, total_stu - present - leaves)
        }, status=status.HTTP_200_OK)