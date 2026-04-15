from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('update/<int:pk>/', views.task_update, name='task_update'),
    path('delete/<int:pk>/', views.task_delete, name='task_delete'),
    path('profile/', views.profile, name='profile'),  # ✅ ADD THIS
    path('signup/', views.signup, name='signup'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('reschedule/<int:pk>/', views.reschedule_task, name='reschedule_task'), # ⭐ ADD THIS
    path('test-notify/', views.test_notification),
    
]
