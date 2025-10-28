from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from .models import Course, StudentRegistration
import razorpay
import json

#-----------------------------------------------------------
# Razorpay Keys (Settings से लें)
#-----------------------------------------------------------
RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET


#-----------------------------------------------------------
# 1. Home View
#-----------------------------------------------------------
def home_view(request):
    # डेटाबेस कनेक्शन फेल होने पर क्रैश से बचने के लिए try-except
    try:
        # अगर आप होम पेज पर कोर्स डेटा दिखाना चाहते हैं तो
        courses = Course.objects.filter(is_active=True).order_by('-id')[:3] 
    except Exception as e:
        print(f"Database connection error in home_view: {e}")
        courses = [] # खाली लिस्ट के साथ पेज लोड करें
        
    context = {
        'courses': courses
    }
    return render(request, 'registration/home.html', context)


#-----------------------------------------------------------
# 2. Courses View
#-----------------------------------------------------------
def courses_view(request):
    # डेटाबेस कनेक्शन फेल होने पर क्रैश से बचने के लिए try-except
    try:
        courses = Course.objects.filter(is_active=True)
    except Exception as e:
        print(f"Database connection error in courses_view: {e}")
        courses = [] # खाली लिस्ट के साथ पेज लोड करें
        
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
        student_name = request.POST.get('student_name')
        father_name = request.POST.get('father_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        
        # 1. Registration ऑब्जेक्ट बनाएं
        registration = StudentRegistration.objects.create(
            course=course,
            student_name=student_name,
            father_name=father_name,
            email=email,
            phone_number=phone_number,
            amount=course.price 
        )
        
        # 2. Payment Page पर redirect करें
        return redirect('payment_view', registration_id=registration.id)
    
    context = {
        'course': course
    }
    return render(request, 'registration/register.html', context)


#-----------------------------------------------------------
# 4. Payment View
#-----------------------------------------------------------
def payment_view(request, registration_id):
    registration = get_object_or_404(StudentRegistration, id=registration_id)
    
    # Razorpay Client को सिर्फ इस फंक्शन के अंदर Initialize करें
    # यह सुनिश्चित करता है कि Razorpay keys के बिना app crash न हो
    try:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    except Exception as e:
        messages.error(request, "Payment gateway configuration error. Please contact support.")
        print(f"Razorpay Client Initialization Error: {e}")
        return redirect('courses_view')

    # Razorpay amount expects the amount in the smallest currency unit (Paisa)
    amount_in_paisa = int(registration.amount * 100) 

    # Razorpay Order बनाएं
    order_data = {
        'amount': amount_in_paisa,
        'currency': 'INR',
        'receipt': str(registration.id),
        'payment_capture': '1' # Auto capture the payment
    }
    
    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        # Razorpay Checkout form के लिए Context तैयार करें
        context = {
            'registration': registration,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': RAZORPAY_KEY_ID,
            'amount_in_paisa': amount_in_paisa,
            'callback_url': request.build_absolute_uri('/payment-status/'), # Status चेक करने का URL
        }
        return render(request, 'registration/payment.html', context)
        
    except Exception as e:
        messages.error(request, "Could not create payment order. Check Razorpay keys.")
        print(f"Razorpay Order Creation Error: {e}")
        return redirect('register_view', course_id=registration.course.id)


#-----------------------------------------------------------
# 5. Payment Status View (Callback URL)
#-----------------------------------------------------------
def payment_status_view(request):
    if request.method == "POST":
        try:
            # POST data को JSON से डिकोड करें
            response = json.loads(request.body.decode('utf-8'))
            
            razorpay_payment_id = response.get('razorpay_payment_id')
            razorpay_order_id = response.get('razorpay_order_id')
            razorpay_signature = response.get('razorpay_signature')
            
            # Razorpay Client को फिर से Initialize करें
            razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

            # Signature verify करें (सुरक्षा के लिए ज़रूरी)
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Verification सफल: रजिस्ट्रेशन अपडेट करें
            registration = StudentRegistration.objects.get(
                id=razorpay_order_id.split('_')[1] # Receipt id से registration id निकालें
            )
            registration.payment_status = True
            registration.razorpay_order_id = razorpay_order_id
            registration.razorpay_payment_id = razorpay_payment_id
            registration.save()
            
            messages.success(request, "Payment Successful! Your registration is complete.")
            return redirect('success_view')

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Invalid Signature.")
            return redirect('failure_view')
        except Exception as e:
            messages.error(request, "An unknown error occurred during payment processing.")
            print(f"Payment Status Error: {e}")
            return redirect('failure_view')

    return redirect('courses_view') # अगर GET request हो तो courses पर भेज दें

#-----------------------------------------------------------
# 6. Utility Views
#-----------------------------------------------------------
def success_view(request):
    return render(request, 'registration/success.html')

def failure_view(request):
    return render(request, 'registration/failure.html')

def about_sir_view(request):
    return render(request, 'registration/about_sir.html')
