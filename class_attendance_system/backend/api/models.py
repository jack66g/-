from django.db import models
from django.contrib.auth.models import User

# 1. 学生模型：关联系统 User，增加学号和班级
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_no = models.CharField(max_length=20, unique=True, verbose_name="学号")
    class_name = models.CharField(max_length=50, verbose_name="班级名称")

    def __str__(self):
        return f"{self.user.username} ({self.student_no})"

# 2. 考勤记录模型
class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', '已签到'),
        ('late', '迟到'),
        ('absent', '缺勤'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    check_in_time = models.DateTimeField(auto_now_add=True, verbose_name="签到时间")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present', verbose_name="状态")

    def __str__(self):
        return f"{self.student.user.username} - {self.get_status_display()}"

# 3. 请假记录模型
class Leave(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审批'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leaves')
    reason = models.TextField(verbose_name="请假理由")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="审批状态")
    apply_time = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")

    def __str__(self):
        return f"{self.student.user.username} - {self.get_status_display()}"
