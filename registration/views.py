from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
# [1] StudyMaterial, Participant और LiveLecture को इम्पोर्ट किया गया
from .models import Course, Participant, StudyMaterial, LiveLecture
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
    return render(request, 'registration/home.html', context)


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
# 3. Registration View
#-----------------------------------------------------------
def register_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == "POST":
        
        # Participant मॉडल के Fields (आपको यहाँ form से सभी fields fetch करने होंगे)
        full_name = request.POST.get('full_name') 
        phone_number = request.POST.get('phone_number') 
        email = request.POST.get('email', '') 
        
        # अन्य fields (उदाहरण के लिए, आपको इन्हें form से भेजना होगा)
        dob = request.POST.get('dob') # Ensure correct date format is handled
        gender = request.POST.get('gender')
        school_name = request.POST.get('school_name')
        school_class = request.POST.get('school_class') # Ensure it's an integer
        school_address = request.POST.get('school_address')

        # Participant ऑब्जेक्ट बनाएं
        registration = Participant.objects.create(
            registered_course=course,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            dob=dob, # Example field
            gender=gender, # Example field
            school_name=school_name, # Example field
            school_class=school_class, # Example field
            school_address=school_address, # Example field
        )
        
        return redirect('payment_view', registration_id=registration.id)
    
    context = {
        'course': course
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
        
        # ऑर्डर ID को Participant मॉडल में सेव करें
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

            # Signature verify करें
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Verification सफल: Participant ऑब्जेक्ट को order ID से ढूंढें और अपडेट करें
            registration = Participant.objects.get(razorpay_order_id=razorpay_order_id)
            
            registration.payment_completed = True
            registration.razorpay_payment_id = razorpay_payment_id
            registration.save()
            
            messages.success(request, "Payment Successful! Your registration is complete.")
            return redirect('success_view')

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
# 6. Materials View
#-----------------------------------------------------------
def materials_view(request):
    try:
        materials = StudyMaterial.objects.filter(price__gt=0).order_by('-published_at') 
        
    except Exception as e:
        print(f"Database error in materials_view: {e}")
        materials = []
        
    context = {
        'materials': materials
    }
    return render(request, 'registration/materials.html', context)

#-----------------------------------------------------------
# 7. Lectures View (नया जोड़ा गया)
#-----------------------------------------------------------
def lectures_view(request):
    try:
        # सभी Live Lectures को Fetch करें
        lectures = LiveLecture.objects.all().order_by('schedule_time') 
        
    except Exception as e:
        print(f"Database error in lectures_view: {e}")
        lectures = []
        
    context = {
        'lectures': lectures
    }
    # सुनिश्चित करें कि आपके पास 'registration/lectures.html' template file मौजूद है
    return render(request, 'registration/lectures.html', context)


#-----------------------------------------------------------
# 8. Utility Views
#-----------------------------------------------------------
def success_view(request):
    return render(request, 'registration/success.html')

def failure_view(request):
    return render(request, 'registration/failure.html')

def about_sir_view(request):
    return render(request, 'registration/about_sir.html')
