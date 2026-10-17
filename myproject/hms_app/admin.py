from django.contrib import admin
from .models import Department, Doctor, Patient, Appointment, Bill

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'specialization', 'consultation_fee', 'schedule')
    list_filter = ('department',)
    search_fields = ('name', 'specialization')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'gender', 'blood_group')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__user__username', 'doctor__name')

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'status', 'total_amount', 'paid_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__user__username', 'patient__phone')