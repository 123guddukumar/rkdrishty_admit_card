from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('student/add/', views.add_student, name='add_student'),
    path('student/edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('student/delete/<int:pk>/', views.delete_student, name='delete_student'),
    
    # Excel Tools
    path('student/import/', views.bulk_import_excel, name='bulk_import_excel'),
    path('student/export/', views.export_excel, name='export_excel'),
    
    # REST APIs
    path('api/generate-card/', views.generate_card_api, name='generate_card_api'),
    path('api/generate-all/', views.generate_all_api, name='generate_all_api'),
    path('api/download-card/', views.download_card_api, name='download_card_api'),
    path('api/download-zip/', views.download_zip_api, name='download_zip_api'),
    path('api/task-status/', views.task_status_api, name='task_status_api'),
]
