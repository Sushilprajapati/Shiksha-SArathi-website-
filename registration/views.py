import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from .models import Participant
from .forms import ParticipantForm
from django.conf import settings

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def home_view(request):
    return render(request, 'home/home.html')

def register_view(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST, request.FILES)
        if form.is_valid():
            participant = form.save()
            return redirect('payment', participant_id=participant.id)
    else:
        form = ParticipantForm()
    return render(request, 'registration/register.html', {'form': form})

def payment_view(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    
    if not participant.payment_completed:
        amount_paise = 10000  # 100 INR
        razorpay_order = razorpay_client.order.create(dict(
            amount=amount_paise,
            currency='INR',
            payment_capture='1'
        ))
        participant.razorpay_order_id = razorpay_order['id']
        participant.save()
    else:
        return redirect('thank_you')

    return render(request, 'registration/payment.html', {
        'participant': participant,
        'razorpay_order': razorpay_order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    })

def payment_success(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    participant.payment_completed = True
    participant.save()
    return redirect('thank_you')

def thank_you_view(request):
    return render(request, 'registration/thank_you.html')


# nwe work 
from django.shortcuts import render, redirect, get_object_or_404
from .models import Branch, Course, StudyMaterial
from .forms import ParticipantForm
from django.urls import reverse
from .models import ContactMessage

def home_view(request):
    branches = Branch.objects.all()
    featured_courses = Course.objects.filter(is_active=True)[:6]
    materials = StudyMaterial.objects.order_by('-published_at')[:6]
    return render(request, 'registration/home.html', {
        'branches': branches,
        'featured_courses': featured_courses,
        'materials': materials,
    })

def courses_view(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'registration/courses.html', {'courses': courses})

def materials_view(request):
    materials = StudyMaterial.objects.order_by('-published_at')
    return render(request, 'registration/materials.html', {'materials': materials})

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        ContactMessage.objects.create(name=name, email=email, phone=phone, message=message)
        return redirect('thank_you')  # reuse your thank_you page or show a specific contact-success page
    return render(request, 'registration/contact.html')
