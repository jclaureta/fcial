from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

from attendance_system import settings
from .models import Student
from .forms import StudentForm
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import face_recognition
import os

import cv2
import numpy as np

from .forms import StudentForm


# INDEX ------------

def index(request):
    return render(request, 'index.html')

# STUDENT HOME -------------
def student_home(request):
    # Handle admin dashboard logic here
    return render(request, 'student_home.html')

# MANAGE STUDENTS ----------
def manage_students(request):
    # Add your logic here to manage students
    return render(request, 'manage_students.html')

# ADD STUDENTS ----------
def add_students(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})  # Return JSON response indicating success
    else:
        form = StudentForm()
    return render(request, 'add_students.html', {'form': form})

# UPDATE STUDENTS ----------
def update_students(request):
    query = request.GET.get('query', '')
    students = Student.objects.filter(name__icontains=query) if query else Student.objects.none()
    context = {'students': students, 'query': query}
    return render(request, 'update_students.html', context)

# EDIT STUDENT ----------
def edit_student(request, student_id):
    student = Student.objects.get(pk=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('update_students')  # Redirect to update_students page
    else:
        form = StudentForm(instance=student)
    return render(request, 'edit_student.html', {'form': form, 'student': student})

# DELETE STUDENT -----------

def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('update_students')
    else:
        return HttpResponseBadRequest("Invalid request method")

# STUDENT LOGIN ------------------

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('student_home')
        else:
            return render(request, 'student_login.html', {'error_message': 'Invalid username or password'})
    return render(request, 'student_login.html')

# TEACHER HOME
def teacher_home(request):
    # Handle admin dashboard logic here
    return render(request, 'teacher_home.html')

# TEACHER LOGIN -----------------

def teacher_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('teacher_home')
        else:
            return render(request, 'teacher_login.html', {'error_message': 'Invalid username or password'})
    return render(request, 'teacher_login.html')


# ADMIN HOME ----------------------

def admin_home(request):
    # Handle admin dashboard logic here
    return render(request, 'admin_home.html')

# ADMIN LOGIN ---------------------

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_home')
        else:
            return render(request, 'admin_login.html', {'error_message': 'Invalid username or password'})
    return render(request, 'admin_login.html')


# IMAGE TRAINING AND RECOGNITION ---------

