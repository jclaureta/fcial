from django.shortcuts import render, HttpResponse, redirect
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


last_face = 'no_face'
current_path = os.path.dirname(__file__)
sound_folder = os.path.join(current_path, 'sound/')
face_list_file = os.path.join(current_path, 'face_list.txt')
sound = os.path.join(sound_folder, 'beep.wav')


def index(request):
    scanned = LastFace.objects.all().order_by('date').reverse()
    present = Profile.objects.filter(present=True).order_by('updated').reverse()
    absent = Profile.objects.filter(present=False).order_by('section')
    context = {
        'scanned': scanned,
        'present': present,
        'absent': absent,
    }
    return render(request, 'core/index.html', context)


def search(request):
    query = request.GET.get('q')
    # Perform search and return results
    # This is just a placeholder. You'll need to implement the actual search logic.
    results = MyModel.objects.filter(name__icontains=query)
    return render(request, 'search_results.html', {'results': results})


def ajax(request):
    last_face = LastFace.objects.last()
    context = {
        'last_face': last_face
    }
    return render(request, 'core/ajax.html', context)

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

def preprocess_frame(frame):
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    return small_frame[:, :, ::-1]  # Convert BGR to RGB

def detect_faces(rgb_small_frame):
    face_locations = face_recognition.face_locations(rgb_small_frame)
    print(f"rgb_small_frame shape: {rgb_small_frame.shape}, type: {type(rgb_small_frame)}")
    print(f"Detected face locations: {face_locations}")

    if face_locations:
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    else:
        face_encodings = []

    return face_locations, face_encodings


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

def display_results(frame, face_locations, face_names):
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
    cv2.imshow('Video', frame)

def cleanup_video(video_capture):
    video_capture.release()
    cv2.destroyAllWindows()

def profiles(request):
    profiles = Profile.objects.all()
    context = {
        'profiles': profiles
    }
    return render(request, 'core/profiles.html', context)


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


def add_profile(request):
    form = ProfileForm
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('profiles')
    context={'form':form}
    return render(request,'core/add_profile.html',context)


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


def delete_profile(request,id):
    profile = Profile.objects.get(id=id)
    profile.delete()
    return redirect('profiles')


def clear_history(request):
    history = LastFace.objects.all()
    history.delete()
    return redirect('index')


def reset(request):
    profiles = Profile.objects.all()
    for profile in profiles:
        if profile.present == True:
            profile.present = False
            profile.save()
        else:
            pass
    return redirect('index')



