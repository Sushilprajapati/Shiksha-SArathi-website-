from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),  # <-- new
    path('register/', views.register_view, name='register'),
    path('payment/<int:participant_id>/', views.payment_view, name='payment'),
    path('payment-success/<int:participant_id>/', views.payment_success, name='payment_success'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    path('', views.home_view, name='home'),  # home at root
    path('courses/', views.courses_view, name='courses'),
    path('materials/', views.materials_view, name='materials'),
    path('contact/', views.contact_view, name='contact'),
    # path('register/', views.register_view, name='register'),
    # path('payment/<int:participant_id>/', views.payment_view, name='payment'),
    # path('payment-success/<int:participant_id>/', views.payment_success, name='payment_success'),
    # path('thank-you/', views.thank_you_view, name='thank_you'),
    
]


