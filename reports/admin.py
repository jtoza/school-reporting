from django.contrib import admin
from .models import *

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'current']
    list_filter = ['current']

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'academic_year']
    list_filter = ['academic_year', 'teacher']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'first_name', 'last_name', 'school_class']
    list_filter = ['school_class']
    search_fields = ['student_id', 'first_name', 'last_name']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'term', 'performance_level', 'academic_year']
    list_filter = ['term', 'performance_level', 'academic_year']
    search_fields = ['student__first_name', 'student__last_name', 'subject__name']

@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ['performance_level', 'subject', 'template_comment']
    list_filter = ['performance_level', 'subject']