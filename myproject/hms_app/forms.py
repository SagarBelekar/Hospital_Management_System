from django import forms
from django.contrib.auth.models import User
from .models import Patient, Appointment, MedicalRecord, Prescription, Department, Doctor

class PatientRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Patient
        fields = ['gender', 'dob', 'blood_group', 'phone', 'address', 'emergency_contact']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username


class AppointmentBookingForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="- Select an option -",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_department'})
    )

    class Meta:
        model = Appointment
        fields = ['department', 'doctor', 'appointment_date', 'appointment_time', 'symptoms']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe symptoms or reason...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # To accept the selected doctor using JavaScript.
        self.fields['doctor'].queryset = Doctor.objects.all()


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department Name (e.g. Cardiology)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'department', 'specialization', 'contact_number', 'consultation_fee', 'schedule']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doctor Full Name (e.g. Dr. Rajesh Sharma)'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cardiologist'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit Phone'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fee in ₹'}),
            'schedule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mon-Fri: 10:00 AM - 02:00 PM'}),
        }