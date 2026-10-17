from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    name = models.CharField(max_length=120)
    specialization = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=15)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    schedule = models.CharField(max_length=200, help_text="e.g. Mon-Fri: 9:00 AM - 2:00 PM")

    def __str__(self):
        return f" {self.name} ({self.specialization})"

class Patient(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    symptoms = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.status})"
    

class MedicalRecord(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='record')
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    doctor_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.appointment.patient} ({self.created_at.strftime('%Y-%m-%d')})"

class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100, help_text="e.g. 500mg, twice a day after meals")
    duration = models.CharField(max_length=50, help_text="e.g. 5 days")

class LabReport(models.Model):
    STATUS_CHOICES = (('Requested', 'Requested'), ('Completed', 'Completed'))
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    test_name = models.CharField(max_length=150)
    test_result = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Requested')
    report_file = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# Existing models: Department, Doctor, Patient, Appointment...

class Bill(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    )

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='bills')
    appointment = models.OneToOneField('Appointment', on_delete=models.CASCADE, related_name='bill')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    additional_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    treatment_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.consultation_fee + self.additional_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill #{self.id} - {self.patient.user.username} - ₹{self.total_amount} ({self.status})"