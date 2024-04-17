from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .models import *
from .forms import *
import face_recognition
import cv2
import numpy as np
import winsound
from django.db.models import Q
from playsound import playsound
import os
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
import base64
from django.contrib.auth.models import User


last_face = 'no_face'
current_path = os.path.dirname(__file__)
sound_folder = os.path.join(current_path, 'sound/')
face_list_file = os.path.join(current_path, 'face_list.txt')
sound = os.path.join(sound_folder, 'beep.wav')

# INDEX PAGE
def index(request):
    return render(request, 'core/index.html')

# TEACHER PAGE
def teacher(request):
    scanned = LastFace.objects.all().order_by('date').reverse()
    present = Profile.objects.filter(present=True).order_by('updated').reverse()
    absent = Profile.objects.filter(present=False).order_by('section')
    context = {
        'scanned': scanned,
        'present': present,
        'absent': absent,
    }
    return render(request, 'core/teacher.html', context)

# STUDENT PAGE
def student(request):
    scanned = LastFace.objects.all().order_by('date').reverse()
    present = Profile.objects.filter(present=True).order_by('updated').reverse()
    absent = Profile.objects.filter(present=False).order_by('section')
    context = {
        'scanned': scanned,
        'present': present,
        'absent': absent,
    }
    return render(request, 'core/student.html', context)

# SEARCH BAR (NOT IMPLEMENTED)
def search(request):
    query = request.GET.get('q')
    # Perform search and return results
    # This is just a placeholder. You'll need to implement the actual search logic.
    results = MyModel.objects.filter(name__icontains=query)
    return render(request, 'search_results.html', {'results': results})

# LAST FACE DETECTED
def ajax(request):
    last_face = LastFace.objects.last()
    context = {
        'last_face': last_face
    }
    return render(request, 'core/ajax.html', context)

# VIDEO CAMERA SCANNER
def scan(request):
    global last_face

    known_face_encodings, known_face_names = load_known_faces()
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_small_frame = preprocess_frame(frame)
        process_this_frame = True

        face_locations = []  # Initialize face_locations at the start of the loop
        face_names = []  # Initialize face_names as well

        try:
            if process_this_frame:
                face_locations, face_encodings = detect_faces(rgb_small_frame)
                face_names = identify_faces(face_encodings, known_face_encodings, known_face_names)
                update_profiles(face_names, last_face)

        except Exception as e:
            print(f"An error occurred: {e}")

        process_this_frame = not process_this_frame
        display_results(frame, face_locations, face_names)

        if cv2.waitKey(1) & 0xFF == 13:  # Enter key
            break
    cleanup_video(video_capture)
    return HttpResponse('Scanner closed', last_face)

# FUNCTION TO LOOK AT THE FACES IN THE DATABASE
def load_known_faces():
    known_face_encodings = []
    known_face_names = []
    profiles = Profile.objects.all()
    for profile in profiles:
        image_of_person = face_recognition.load_image_file(f'media/{profile.image}')
        person_face_encoding = face_recognition.face_encodings(image_of_person)[0]
        known_face_encodings.append(person_face_encoding)
        known_face_names.append(f'{profile.image}'[:-4])
    return known_face_encodings, known_face_names

# THE FORMAT OF THE BOX AROUND THE FACE
def preprocess_frame(frame):
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    return small_frame[:, :, ::-1]  # Convert BGR to RGB

# FACE RECOGNITION FUNCTION DETERMINES THE CENTER OF THE FACE TO BE RECOGNIZED
def detect_faces(rgb_small_frame):
    face_locations = face_recognition.face_locations(rgb_small_frame)
    print(f"rgb_small_frame shape: {rgb_small_frame.shape}, type: {type(rgb_small_frame)}")
    print(f"Detected face locations: {face_locations}")

    if face_locations:
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    else:
        face_encodings = []

    return face_locations, face_encodings

# FUNCTION TO IDENTIFY THE FACES
def identify_faces(face_encodings, known_face_encodings, known_face_names):
    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        face_names.append(name)
    return face_names

# FUNCTION TO UPDATE THE PROFILES
def update_profiles(face_names, last_face):
    for name in face_names:
        if last_face != name:
            profile = Profile.objects.get(Q(image__icontains=name))
            if not profile.present:
                profile.present = True
                profile.save()
            last_face = LastFace(last_face=name)
            last_face.save()
            winsound.PlaySound(sound, winsound.SND_ASYNC)
            last_face = name

# FUNCTION THAT DRAWS THE BOUNDING BOX AROUND THE FACE
def display_results(frame, face_locations, face_names):
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
    cv2.imshow('Video', frame)

# LAUNCH THE VIDEO CAMERA TO CAPTURE THE FACE
def cleanup_video(video_capture):
    video_capture.release()
    cv2.destroyAllWindows()

# FOR HTML FUNCTION FOR PROFILE LIST
def profiles(request):
    scanned = LastFace.objects.all().order_by('date').reverse()
    profiles = Profile.objects.all()
    context = {
        'scanned': scanned,
        'profiles': profiles
    }
    return render(request, 'core/profiles.html', context)

# FOR HTML FUNCTION FOR PROFILE DETAILS
def details(request):
    try:
        last_face = LastFace.objects.last()
        profile = Profile.objects.get(Q(image__icontains=last_face))
    except:
        last_face = None
        profile = None

    context = {
        'profile': profile,
        'last_face': last_face
    }
    return render(request, 'core/details.html', context)

# FOR HTML FUNCTION TO ADD PROFILE
def add_profile(request):
    form = ProfileForm
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('profiles')
    context={'form':form}
    return render(request,'core/add_profile.html',context)

# FOR HTML FUNCTION TO EDIT PROFILE
def edit_profile(request,id):
    profile = Profile.objects.get(id=id)
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profiles')
    context={'form':form}
    return render(request,'core/add_profile.html',context)

# FOR HTML FUNCTION TO DELETE PROFILE
def delete_profile(request,id):
    profile = Profile.objects.get(id=id)
    profile.delete()
    return redirect('profiles')

# FOR HTML FUNCTION TO CLEAR HISTORY
def clear_history(request):
    history = LastFace.objects.all()
    history.delete()
    return redirect('profiles')

# FOR HTML FUNCTION TO RESET
def reset(request):
    profiles = Profile.objects.all()
    for profile in profiles:
        if profile.present == True:
            profile.present = False
            profile.save()
        else:
            pass
    return redirect('profiles')

###################################################################
#### NOT IMPLEMENTED ##############################################
###################################################################

def login(request):
    return render(request, 'login.html')


def contact(request):
    return render(request, 'contact.html')

# STUDENT HOME -------------
def student_home(request):
    # Handle admin dashboard logic here
    return render(request, 'student_home.html')

# MANAGE STUDENTS ----------
def manage_students(request):
    # Add your logic here to manage students
    return render(request, 'manage_students.html')

# MANAGE ADMIN
def manage_admin(request):
    # Add your logic here to manage students
    return render(request, 'manage_admin.html')


# ADD ADMIN ----------
def add_admin(request):
    if request.method == 'POST':
        form = AdminForm(request.POST, request.FILES)
        if form.is_valid():
            admin = form.save(commit=False)
            admin.save()

            # Get the uploaded image
            uploaded_image = request.FILES['image']

            # Define the directory path to save images
            image_directory = os.path.join(settings.MEDIA_ROOT, 'Admin_Images')

            # Create the directory if it doesn't exist
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)

            # Save the image with student_id as filename
            image_path = os.path.join(image_directory, f"{admin.admin_id}.jpg")
            with open(image_path, 'wb+') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)

            # Redirect to the same page after successful submission
            return redirect('add_admin')
    else:
        form = AdminForm()  # Define the form for GET request

    return render(request, 'add_admin.html', {'form': form})



# ADD STUDENTS ----------
def add_students(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.save()

            # Get the uploaded image
            uploaded_image = request.FILES['image']

            # Define the directory path to save images
            image_directory = os.path.join(settings.MEDIA_ROOT, 'Student_Images')

            # Create the directory if it doesn't exist
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)

            # Save the image with student_id as filename
            image_path = os.path.join(image_directory, f"{student.student_id}.jpg")
            with open(image_path, 'wb+') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)

            # Redirect to the same page after successful submission
            return redirect('add_students')
    else:
        form = StudentForm()  # Define the form for GET request

    return render(request, 'add_students.html', {'form': form})

# UPDATE STUDENTS ----------
def update_students(request):
    query = request.GET.get('query', '')
    students = Student.objects.filter(name__icontains=query) if query else Student.objects.none()
    context = {'students': students, 'query': query}
    return render(request, 'update_students.html', context)

# UPDATE ADMIN ----------
def update_admin(request):
    query = request.GET.get('query', '')
    admins = Admin.objects.filter(name__icontains=query) if query else Admin.objects.none()
    context = {'admins': admins, 'query': query}
    return render(request, 'update_admin.html', context)

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

# EDIT ADMIN ----------
def edit_admin(request, admin_id):
    admin = Admin.objects.get(pk=admin_id)
    if request.method == 'POST':
        form = AdminForm(request.POST, request.FILES, instance=admin)
        if form.is_valid():
            form.save()
            return redirect('update_admin')  # Redirect to update_admin page
    else:
        form = AdminForm(instance=admin)
    return render(request, 'edit_admin.html', {'form': form, 'admin': admin})

# DELETE STUDENT -----------

def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('update_students')
    else:
        return HttpResponseBadRequest("Invalid request method")
    
# DELETE ADMIN -----------

def delete_admin(request, admin_id):
    admin = get_object_or_404(Admin, pk=admin_id)
    if request.method == 'POST':
        admin.delete()
        return redirect('update_admin')
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

#######################################################
#######################################################
# def find_user_view(request):
#     if is_ajax(request):
#         photo = request.POST.get('photo')
#         _, str_img = photo.split(';base64')

#         # print(photo)
#         decoded_file = base64.b64decode(str_img)
#         print(decoded_file)

#         x = Log()
#         x.photo.save('upload.png', ContentFile(decoded_file))
#         x.save()

#         res = classify_face(x.photo.path)
#         if res:
#             user_exists = User.objects.filter(username=res).exists()
#             if user_exists:
#                 user = User.objects.get(username=res)
#                 profile = Profile.objects.get(user=user)
#                 x.profile = profile
#                 x.save()

#                 login(request, user)
#                 return JsonResponse({'success': True})
#         return JsonResponse({'success': False})