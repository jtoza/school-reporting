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

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'section']
    list_filter = ['name']

@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'assignment_type', 'due_date', 'created_by', 'is_published']
    list_filter = ['assignment_type', 'is_published', 'academic_year', 'subject']
    search_fields = ['title', 'description']
    date_hierarchy = 'due_date'

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at', 'is_graded', 'grade']
    list_filter = ['is_graded', 'submitted_at']
    search_fields = ['assignment__title', 'student__first_name', 'student__last_name']

@admin.register(StudentContact)
class StudentContactAdmin(admin.ModelAdmin):
    list_display = ['child_name', 'parent_name', 'class_level', 'parent_phone', 'teacher']
    list_filter = ['class_level', 'teacher']
    search_fields = ['child_name', 'parent_name', 'parent_id_number', 'parent_phone']
    readonly_fields = ['created_at', 'updated_at']