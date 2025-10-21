from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Original URLs
    path('class/<int:pk>/', views.class_detail, name='class_detail'),
    path('student/<int:student_id>/results/', views.student_results, name='student_results'),
    path('student/<int:student_id>/add-result/', views.add_result, name='add_result'),
    path('class/<int:class_id>/add-student/', views.add_student, name='add_student'),
    path('student/<int:student_id>/download-report/', views.download_report, name='download_report'),
    path('student/<int:student_id>/profile/', views.student_profile, name='student_profile'),
    
    # Assignment URLs
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/subject/<int:subject_id>/', views.assignment_list, name='assignment_list_by_subject'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_id>/edit/', views.assignment_edit, name='assignment_edit'),
    path('assignments/<int:assignment_id>/delete/', views.assignment_delete, name='assignment_delete'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('submissions/<int:submission_id>/grade/', views.grade_assignment, name='grade_assignment'),
    
    # Student Contact URLs
    path('student-contact/', views.student_contact_home, name='student_contact_home'),
    path('student-contact/select-class/', views.student_contact_class_select, name='student_contact_class_select'),
    path('student-contact/<str:class_level>/', views.student_contact_form, name='student_contact_form'),
    path('student-contact/list/', views.student_contact_list, name='student_contact_list'),
]