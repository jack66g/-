from django.contrib import admin
from .models import Student, Attendance, Leave

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_no', 'get_username', 'class_name')
    def get_username(self, obj): return obj.user.username
    get_username.short_description = '姓名'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'check_in_time', 'status')
    list_filter = ('status', 'check_in_time')

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('student', 'status', 'apply_time')
    list_editable = ('status',) # 老师可以直接在列表页改状态，非常方便
