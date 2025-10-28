from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from .models import Course, Participant, StudyMaterial, LiveLecture, ContactMessage, Testimonial 
import razorpay
import json

# Razorpay Keys (Settings से लें)
RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET


#-----------------------------------------------------------
# 1. Home View
#-----------------------------------------------------------
def home_view(request):
    try:
        courses = Course.objects.filter(is_active=True).order_by('-id')[:3] 
    except Exception as e:
        print(f"Database connection error in home_view: {e}")
        courses = []
        
    context = {
        'courses': courses
    }
    return render(request, 'registration/index.html', context)

#-----------------------------------------------------------
# 2. Courses View
#-----------------------------------------------------------
def courses_view(request):
    try:
        courses = Course.objects.filter(is_active=True)
    except Exception as e:
        print(f"Database connection error in courses_view: {e}")
        courses = []
        
    context = {
        'courses': courses
    }
    return render(request, 'registration/courses.html', context)

#-----------------------------------------------------------
# 3. Registration View (UPDATED)
# यह फंक्शन अब course_id=None होने पर भी रजिस्ट्रेशन पेज दिखाएगा
#-----------------------------------------------------------
def register_view(request, course_id=None): 
    course = None
    # सारे एक्टिव कोर्स को fetch करें (ड्रॉपडाउन के लिए)
    course_list = Course.objects.filter(is_active=True).order_by('name')

    # 1. URL से course_id मिला
    if course_id:
        course = get_object_or_404(Course, id=course_id)
    
    
    if request.method == "POST":
        
        # Participant मॉडल के Fields 
        full_name = request.POST.get('full_name')  
        phone_number = request.POST.get('phone_number') 
        email = request.POST.get('email', '') 
        
        # अन्य fields
        dob = request.POST.get('dob')  
        gender = request.POST.get('gender')
        school_name = request.POST.get('school_name')
        school_class = request.POST.get('school_class')
        school_address = request.POST.get('school_address')
        
        # POST data से कोर्स ID प्राप्त करें (फॉर्म से)
        posted_course_id = request.POST.get('course') 
        
        # 2. कोर्स सुनिश्चित करें: अगर course URL से नहीं मिला, तो POST data का उपयोग करें।
        if not course and posted_course_id:
            try:
                course = Course.objects.get(id=posted_course_id)
            except Course.DoesNotExist:
                messages.error(request, "Selected course is invalid.")
                # error के मामले में रजिस्ट्रेशन पेज को फिर से दिखाएँ
                context = {'course_list': course_list, 'course': None}
                return render(request, 'registration/register.html', context)
        
        # 3. अंतिम चेक: अगर कोर्स अभी भी None है, तो error दें और फॉर्म फिर से दिखाएँ
        if not course:
            messages.error(request, "Please select a course to complete registration.")
            context = {'course_list': course_list, 'course': None}
            return render(request, 'registration/register.html', context)
            
        # 4. Participant ऑब्जेक्ट बनाएं
        registration = Participant.objects.create(
            registered_course=course,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            dob=dob, 
            gender=gender, 
            school_name=school_name, 
            school_class=school_class, 
            school_address=school_address, 
            # Note: Photo field is skipped here for simplicity in manual POST handling
        )
        
        return redirect('payment_view', registration_id=registration.id)
    
    # GET Request: रजिस्ट्रेशन पेज दिखाएँ (course_id=None होने पर भी यह चलेगा)
    context = {
        'course': course, 
        'course_list': course_list # ड्रॉपडाउन के लिए सभी कोर्स भेजें
    }
    return render(request, 'registration/register.html', context)


#-----------------------------------------------------------
# 4. Payment View
#-----------------------------------------------------------
def payment_view(request, registration_id):
    registration = get_object_or_404(Participant, id=registration_id)
    
    try:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    except Exception as e:
        messages.error(request, "Payment configuration error. Contact support.")
        print(f"Razorpay Client Initialization Error: {e}")
        return redirect('courses_view')

    amount_to_pay = registration.registered_course.fee 
    amount_in_paisa = int(amount_to_pay * 100) 

    order_data = {
        'amount': amount_in_paisa,
        'currency': 'INR',
        'receipt': str(registration.id),
        'payment_capture': '1' 
    }
    
    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        registration.razorpay_order_id = razorpay_order['id']
        registration.save() 

        context = {
            'registration': registration,
            'amount_in_rupees': amount_to_pay,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': RAZORPAY_KEY_ID,
            'amount_in_paisa': amount_in_paisa,
            'callback_url': request.build_absolute_uri('payment_status_view'), 
        }
        return render(request, 'registration/payment.html', context)
        
    except Exception as e:
        messages.error(request, "Could not create payment order. Check Razorpay keys.")
        print(f"Razorpay Order Creation Error: {e}")
        return redirect('register_view', course_id=registration.registered_course.id)


#-----------------------------------------------------------
# 5. Payment Status View (Callback URL)
#-----------------------------------------------------------
def payment_status_view(request):
    if request.method == "POST":
        try:
            response = json.loads(request.body.decode('utf-8'))
            
            razorpay_payment_id = response.get('razorpay_payment_id')
            razorpay_order_id = response.get('razorpay_order_id')
            razorpay_signature = response.get('razorpay_signature')
            
            razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

            registration = Participant.objects.get(razorpay_order_id=razorpay_order_id)
            
            registration.payment_completed = True
            registration.razorpay_payment_id = razorpay_payment_id
            registration.save()
            
            messages.success(request, "Payment Successful! Your registration is complete.")
            return redirect('payment_success', participant_id=registration.id) 

        except Participant.DoesNotExist:
            messages.error(request, "Registration not found for this payment.")
            return redirect('failure_view')
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Invalid Signature.")
            return redirect('failure_view')
        except Exception as e:
            messages.error(request, "An unknown error occurred during payment processing.")
            print(f"Payment Status Error: {e}")
            return redirect('failure_view')

    return redirect('courses_view')

#-----------------------------------------------------------
# 6. Payment Success View
#-----------------------------------------------------------
def payment_success(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    context = {
        'participant': participant,
        'course': participant.registered_course
    }
    return render(request, 'registration/success.html', context)


#-----------------------------------------------------------
# 7. Contact View
#-----------------------------------------------------------
def contact_view(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            message = request.POST.get('message')
            
            if name and message:
                ContactMessage.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    message=message
                )
                messages.success(request, "Thank you! Your message has been sent successfully.")
                return redirect('thank_you_view') 
            else:
                messages.error(request, "Please fill out your name and message.")
        
        except Exception as e:
            messages.error(request, "An error occurred while sending your message.")
            print(f"Contact form submission error: {e}")

    context = {} 
    return render(request, 'registration/contact.html', context)

#-----------------------------------------------------------
# 8. Other App Views
#-----------------------------------------------------------
def materials_view(request):
    try:
        materials = StudyMaterial.objects.filter(price__gt=0).order_by('-published_at') 
    except Exception as e:
        print(f"Database error in materials_view: {e}")
        materials = []
    context = {'materials': materials}
    return render(request, 'registration/materials.html', context)

def lectures_view(request):
    try:
        lectures = LiveLecture.objects.all().order_by('schedule_time') 
    except Exception as e:
        print(f"Database error in lectures_view: {e}")
        lectures = []
    context = {'lectures': lectures}
    return render(request, 'registration/lectures.html', context)

#-----------------------------------------------------------
# 9. Testimonials View 
#-----------------------------------------------------------
def testimonials_view(request):
    try:
        testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at') 
    except Exception as e:
        print(f"Database error in testimonials_view: {e}")
        testimonials = []
        
    context = {
        'testimonials': testimonials
    }
    return render(request, 'registration/testimonials.html', context)


#-----------------------------------------------------------
# 10. Utility Views
#-----------------------------------------------------------
def failure_view(request):
    context = {} 
    return render(request, 'registration/failure.html', context)

def about_sir_view(request):
    context = {} 
    return render(request, 'registration/about.html', context)
    
def thank_you_view(request):
    context = {} 
    return render(request, 'registration/thank_you.html', context)
