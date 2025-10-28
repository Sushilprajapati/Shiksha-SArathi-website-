from django.shortcuts import render, redirect, get_object_or_404
from .models import Branch, Course, StudyMaterial, LiveLecture, Participant, ContactMessage
from .forms import ParticipantForm
from django.conf import settings
import razorpay # razorpay library import की गई

# IMPORTANT FIX: Razorpay client initialization को हटा दिया गया है
# इसे सिर्फ payment_view() के अंदर initialize करेंगे।
# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Home / Dashboard
def home_view(request):
    try:
        branches = Branch.objects.all()
        featured_courses = Course.objects.filter(is_active=True)[:6]
        latest_materials = StudyMaterial.objects.order_by('-published_at')[:6]
        upcoming_lectures = LiveLecture.objects.order_by('schedule_time')[:5]
    except Exception as e:
        # अगर कोई डेटाबेस एरर है तो कम से कम होम पेज को खाली डेटा के साथ लोड करें
        # Production में हमेशा logs देखें।
        print(f"Database Error in home_view: {e}") 
        branches, featured_courses, latest_materials, upcoming_lectures = [], [], [], []

    return render(request, 'registration/index.html', {
        'branches': branches,
        'featured_courses': featured_courses,
        'latest_materials': latest_materials,
        'upcoming_lectures': upcoming_lectures,
    })

# Courses Page
def courses_view(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'registration/courses.html', {'courses': courses})

# about
def about_view(request):
    # This will render a new template: registration/about.html
    return render(request, 'registration/about.html')

# testimonial
def testimonials_view(request):
    # This renders the new template where you can put all testimonials
    return render(request, 'registration/testimonials.html')

# Materials Page
def materials_view(request):
    materials = StudyMaterial.objects.order_by('-published_at')
    return render(request, 'registration/materials.html', {'materials': materials})

# Live Lectures Page
def lectures_view(request):
    lectures = LiveLecture.objects.order_by('schedule_time')
    return render(request, 'registration/lectures.html', {'lectures': lectures})

# Registration
def register_view(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST, request.FILES)
        if form.is_valid():
            participant = form.save()
            return redirect('payment', participant_id=participant.id)
    else:
        form = ParticipantForm()
    return render(request, 'registration/register.html', {'form': form})

# Payment
def payment_view(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    
    # FIX: Razorpay client को सिर्फ यहाँ initialize करें 
    # इससे पूरे views.py को क्रैश होने से बचाया जा सकता है।
    try:
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    except Exception as e:
        # अगर कीज गलत हैं तो यूजर को एरर दिखाएं (या लॉग करें)
        print(f"Razorpay Client Initialization Error: {e}")
        # यहां एक user-friendly error page पर redirect करना बेहतर है
        return render(request, 'registration/payment_error.html', {'error': 'Payment service is temporarily unavailable.'})
        
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

# Payment Success (No change needed)
def payment_success(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    participant.payment_completed = True
    participant.save()
    return redirect('thank_you')

# Thank You Page (No change needed)
def thank_you_view(request):
    return render(request, 'registration/thank_you.html')

# Contact (No change needed)
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        ContactMessage.objects.create(name=name, email=email, phone=phone, message=message)
        return redirect('thank_you')
    return render(request, 'registration/contact.html')
