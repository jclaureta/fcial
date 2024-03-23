from django import forms
from .models import Student
from .models import Admin

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'dob', 'username', 'password', 'confirm_password', 'student_id', 'program', 'semester', 'section','college_email', 'personal_email', 'phone', 'address', 'emergency_contact_person', 'emergency_contact_phone', 'picture']

class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['name', 'dob', 'admin_id', 'username', 'password', 'confirm_password', 'college_email', 'personal_email', 'phone', 'address', 'picture']
