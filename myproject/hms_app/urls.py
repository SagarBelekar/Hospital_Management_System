from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.patient_register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # Public Informational Pages
    path('about/', views.about_page, name='about'),
    path('features/', views.features_page, name='features'),
    path('contact/', views.contact_page, name='contact'),
    
    # Admin URLs
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('appointment/<int:pk>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    
    # Patient URLs
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),

    # Profile Route
    path('profile/', views.profile_view, name='profile'),



    # Department CRUD
    path('admin-panel/departments/', views.manage_departments, name='manage_departments'),
    path('admin-panel/departments/edit/<int:pk>/', views.edit_department, name='edit_department'),
    path('admin-panel/departments/delete/<int:pk>/', views.delete_department, name='delete_department'),

    # Doctor CRUD
    path('admin-panel/doctors/', views.manage_doctors, name='manage_doctors'),
    path('admin-panel/doctors/edit/<int:pk>/', views.edit_doctor, name='edit_doctor'),
    path('admin-panel/doctors/delete/<int:pk>/', views.delete_doctor, name='delete_doctor'),


    path('api/doctors-by-dept/<int:dept_id>/', views.get_department_doctors, name='doctors_by_dept'),


    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('my-bills/', views.patient_pending_bills, name='patient_pending_bills'),



    # Admin URLs
    path('admin-panel/treat-patients/', views.admin_treat_patients_list, name='admin_treat_patients'),
    path('admin-panel/treat-patient/<int:appointment_id>/', views.admin_treat_patient_detail, name='admin_treat_patient_detail'),

    # Patient URLs
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('my-bills/', views.patient_pending_bills, name='patient_pending_bills'),
    path('pay-bill/<int:bill_id>/', views.patient_pay_bill, name='patient_pay_bill'),
]