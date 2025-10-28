
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('courses/', views.courses_view, name='courses'),
    path('materials/', views.materials_view, name='materials'),
    path('lectures/', views.lectures_view, name='lectures'),
    path('register/', views.register_view, name='register'),
    path('payment/<int:participant_id>/', views.payment_view, name='payment'),
    path('payment-success/<int:participant_id>/', views.payment_success, name='payment_success'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    path('contact/', views.contact_view, name='contact'),
    # [1] FIX: about_view को about_sir_view में बदला गया
    path('about-sir/', views.about_sir_view, name='about'),
    # [2] FIX: testimonials_view को views.py में जोड़ना होगा
    path('testimonials/', views.testimonials_view, name='testimonials'),
]
