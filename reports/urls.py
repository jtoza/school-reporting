from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('class/<int:pk>/', views.class_detail, name='class_detail'),
    path('student/<int:student_id>/results/', views.student_results, name='student_results'),
    path('student/<int:student_id>/add-result/', views.add_result, name='add_result'),
    path('class/<int:class_id>/add-student/', views.add_student, name='add_student'),
    path('student/<int:student_id>/download-report/', views.download_report, name='download_report'),
    path('student/<int:student_id>/profile/', views.student_profile, name='student_profile'),
]