from django.urls import path
from . import views

urlpatterns = [
    
    # index -----------
    path('', views.index, name= 'index'),

    # Student ---------------
    path('student/', views.student_home, name='student_home'),
    path('student/login/', views.student_login, name='student_login'),
    path('manage_students/', views.manage_students, name='manage_students'),
    path('add-students/', views.add_students, name='add_students'),
    path('update_students/', views.update_students, name='update_students'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),


    # Teacher ---------------------
    path('teacher/', views.teacher_home, name='teacher_home'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),

    # Admin -------------------------
    path('admin/home', views.admin_home, name='admin_home'),
    path('admin/login/', views.admin_login, name='admin_login'),

    # path('train/', views.train_image, name='train_image'),
    # path('save_image/', views.save_image, name='save_image'),


]
