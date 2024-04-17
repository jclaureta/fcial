from django.urls import path,include
from .views import *
from . import views


urlpatterns = [
    path('', index, name= 'index'),
    path('ajax/', ajax, name= 'ajax'),
    path('scan/',scan,name='scan'),
    path('profiles/', profiles, name= 'profiles'),
    path('details/', details, name= 'details'),
    path('add_profile/',add_profile,name='add_profile'),
    path('edit_profile/<int:id>/',edit_profile,name='edit_profile'),
    path('delete_profile/<int:id>/',delete_profile,name='delete_profile'),
    path('teacher/', teacher, name= 'teacher'),
    path('student/', student, name= 'student'),


    path('clear_history/',clear_history,name='clear_history'),
    path('reset/',reset,name='reset')

# # ###############################################################################
#     # Student ---------------
#     path('student/', views.student_home, name='student_home'),
#     path('student/login/', views.student_login, name='student_login'),
#     path('manage_students/', views.manage_students, name='manage_students'),
#     path('add-students/', views.add_students, name='add_students'),
#     path('update_students/', views.update_students, name='update_students'),
#     path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
#     path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),


#     # Teacher ---------------------
#     path('teacher/', views.teacher_home, name='teacher_home'),
#     path('teacher/login/', views.teacher_login, name='teacher_login'),

#     # Admin -------------------------
#     path('admin/home', views.admin_home, name='admin_home'),
#     path('admin/login/', views.admin_login, name='admin_login'),
#     path('manage_admin/', views.manage_admin, name='manage_admin'),
#     path('add-admin/', views.add_admin, name='add_admin'),
#     path('update_admin/', views.update_admin, name='update_admin'),
#     path('edit_admin/<int:admin_id>/', views.edit_admin, name='edit_admin'),
#     path('delete_admin/<int:admin_id>/', views.delete_admin, name='delete_admin'),
    
#     path('login/', views.login, name='login'),
#     path('about/', views.about, name='about'),
#     path('contact/', views.contact, name='contact'),

]
