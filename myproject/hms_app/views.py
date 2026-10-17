from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from .models import Patient, Doctor, Appointment, Department, Bill, MedicalRecord
from .forms import PatientRegistrationForm, AppointmentBookingForm


@login_required
def profile_view(request):
    user = request.user
    context = {'user': user}

    if user.is_staff:
        # Admin Profile Context
        context['role'] = 'Administrator'
        context['total_doctors'] = Doctor.objects.count()
        context['total_patients'] = Patient.objects.count()
    else:
        # Patient Profile Context
        patient = Patient.objects.filter(user=user).first()
        context['role'] = 'Patient'
        context['patient'] = patient
        if patient:
            context['appointments_count'] = Appointment.objects.filter(patient=patient).count()
            context['bills_count'] = Bill.objects.filter(patient=patient).count()

    return render(request, 'profile.html', context)





def about_page(request):
    return render(request, 'about.html')

def features_page(request):
    return render(request, 'features.html')

def contact_page(request):
    return render(request, 'contact.html')




def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('patient_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout  
from django.contrib.auth.models import User
from .forms import PatientRegistrationForm

def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            # 1. Create a user account.
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # 2. Save the patient profile.
            patient = form.save(commit=False)
            patient.user = user
            patient.save()
            
            # 3. If an old user/admin session is active, log it out.
            logout(request)
            
            # 4. Trigger the success message.
            messages.success(request, "Registration successful! Please log in to your account.")
            
            # 5. Redirect the user to the login page.
            return redirect('login')
        else:
            messages.error(request, "Please check the errors in the form.")
    else:
        form = PatientRegistrationForm()
        
    return render(request, 'auth/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

# --- ADMIN VIEWS ---
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    context = {
        'total_patients': Patient.objects.count(),
        'total_doctors': Doctor.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'pending_appointments': Appointment.objects.filter(status='Pending').count(),
        'total_revenue': Bill.objects.filter(status='Paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'recent_appointments': Appointment.objects.order_by('-id')
    }
    return render(request, 'admin_views/dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def update_appointment_status(request, pk, status):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = status
    appointment.save()
    return redirect('admin_dashboard')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Patient, Appointment

# If your models include a Billing/Invoice model, import it:
# from .models import Bill  # e.g., Bill / Invoice model

@login_required
def patient_dashboard(request):
    patient = getattr(request.user, 'patient', None)
    if not patient:
        patient, _ = Patient.objects.get_or_create(user=request.user)

    # Fetch all appointments for the patient along with their doctors and departments.
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor', 'department').order_by('-appointment_date', '-appointment_time')

    context = {
        'patient': patient,
        'appointments': appointments,
    }
    return render(request, 'patient_views/dashboard.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from .models import Appointment, Patient, Bill

def is_admin(user):
    return user.is_authenticated and user.is_staff

# 1. Admin: Treat Patient List (Confirmed Appointments Only)
@user_passes_test(is_admin)
def admin_treat_patients_list(request):
    confirmed_appointments = Appointment.objects.filter(status='Confirmed').select_related('patient__user', 'doctor', 'department').order_by('appointment_date', 'appointment_time')
    return render(request, 'admin_views/treat_patient_list.html', {
        'appointments': confirmed_appointments
    })

# 2. Admin: Treat Patient Form & Complete Treatment
@user_passes_test(is_admin)
def admin_treat_patient_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment.objects.select_related('patient__user', 'doctor', 'department'), id=appointment_id)

    if request.method == 'POST':
        additional_fee_str = request.POST.get('additional_fee', '0')
        treatment_notes = request.POST.get('treatment_notes', '')

        try:
            additional_fee = Decimal(additional_fee_str) if additional_fee_str else Decimal('0.00')
        except:
            additional_fee = Decimal('0.00')

        consultation_fee = Decimal(str(appointment.doctor.consultation_fee))

       # Create or update the bill.
        bill, created = Bill.objects.get_or_create(
            appointment=appointment,
            defaults={
                'patient': appointment.patient,
                'consultation_fee': consultation_fee,
                'additional_fee': additional_fee,
                'treatment_notes': treatment_notes,
                'status': 'Pending'
            }
        )
        if not created:
            bill.additional_fee = additional_fee
            bill.treatment_notes = treatment_notes
            bill.save()

       # Set the appointment status to Completed.
        appointment.status = 'Completed'
        appointment.save()

        messages.success(request, f"Treatment completed for {appointment.patient.user.get_full_name() or appointment.patient.user.username}. Bill generated successfully!")
        return redirect('admin_treat_patients')

    context = {
        'appointment': appointment,
        'consultation_fee': appointment.doctor.consultation_fee,
    }
    return render(request, 'admin_views/treat_patient_form.html', context)

# 3. Patient: Pending Bills View
@login_required
def patient_pending_bills(request):
    patient = getattr(request.user, 'patient', None)
    if not patient:
        patient, _ = Patient.objects.get_or_create(user=request.user)

    pending_bills = Bill.objects.filter(patient=patient, status='Pending').select_related('appointment__doctor', 'appointment__department').order_by('-created_at')

    return render(request, 'patient_views/pending_bills.html', {
        'patient': patient,
        'pending_bills': pending_bills,
    })

# 4. Patient: Pay Bill View
@login_required
def patient_pay_bill(request, bill_id):
    patient = request.user.patient
    bill = get_object_or_404(Bill, id=bill_id, patient=patient, status='Pending')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'Online')
        bill.status = 'Paid'
        bill.payment_method = payment_method
        bill.paid_at = timezone.now()
        bill.save()

        messages.success(request, f"Payment of ₹{bill.total_amount} completed successfully!")
        return redirect('patient_pending_bills')

    return render(request, 'patient_views/pay_bill.html', {'bill': bill})




from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AppointmentBookingForm
from .models import Patient, Appointment

@login_required
def book_appointment(request):
    # Ensure the logged-in user has a patient profile.
    patient = getattr(request.user, 'patient', None)
    if not patient:
        patient, _ = Patient.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            messages.success(request, "Appointment successfully booked!")
            return redirect('patient_dashboard')
        else:
            # If validation fails, display the errors in the console and messages.
            print("Booking Form Errors:", form.errors)
            messages.error(request, f"Please fix errors: {form.errors}")
    else:
        form = AppointmentBookingForm()

    return render(request, 'patient_views/book_appointment.html', {'form': form})





from .forms import DepartmentForm, DoctorForm

# ----------------- DEPARTMENT CRUD -----------------
@user_passes_test(lambda u: u.is_staff)
def manage_departments(request):
    departments = Department.objects.all()
    form = DepartmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('manage_departments')
    return render(request, 'admin_views/manage_departments.html', {'departments': departments, 'form': form})

@user_passes_test(lambda u: u.is_staff)
def edit_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=dept)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('manage_departments')
    return render(request, 'admin_views/edit_department.html', {'form': form, 'department': dept})

@user_passes_test(lambda u: u.is_staff)
def delete_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    dept.delete()
    return redirect('manage_departments')

# ----------------- DOCTOR CRUD -----------------
@user_passes_test(lambda u: u.is_staff)
def manage_doctors(request):
    doctors = Doctor.objects.select_related('department').all()
    form = DoctorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('manage_doctors')
    return render(request, 'admin_views/manage_doctors.html', {'doctors': doctors, 'form': form})

@user_passes_test(lambda u: u.is_staff)
def edit_doctor(request, pk):
    doc = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, instance=doc)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('manage_doctors')
    return render(request, 'admin_views/edit_doctor.html', {'form': form, 'doctor': doc})

@user_passes_test(lambda u: u.is_staff)
def delete_doctor(request, pk):
    doc = get_object_or_404(Doctor, pk=pk)
    doc.delete()
    return redirect('manage_doctors')





from django.http import JsonResponse
from .models import Doctor

def get_department_doctors(request, dept_id):
    doctors = Doctor.objects.filter(department_id=dept_id).values(
        'id', 'name', 'specialization', 'schedule', 'consultation_fee'
    )
    return JsonResponse(list(doctors), safe=False)