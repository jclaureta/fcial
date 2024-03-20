# forms.py

from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'dob', 'username', 'password', 'confirm_password', 'student_id', 'program', 'semester', 'section','college_email', 'personal_email', 'phone', 'address', 'emergency_contact_person', 'emergency_contact_phone', 'picture']
