from django.contrib import admin
from .models import Classroom
from django.utils.html import format_html

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_code', 'teacher', 'created_at', 'get_students')  # Added get_students
    list_filter = ('teacher', 'created_at')
    search_fields = ('name', 'class_code', 'teacher__username')
    ordering = ('-created_at',)
    filter_horizontal = ('sheets',)

    def get_students(self, obj):
        students = obj.students.all()  # This gets all students through the related name
        if not students:
            return "No students"
        student_list = [f"{student.name} {student.surname_1}" for student in students]
        return format_html("<br>".join(student_list))
    
    get_students.short_description = 'Students'  # Column header in admin
