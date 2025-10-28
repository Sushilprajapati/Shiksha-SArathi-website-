from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
# ध्यान दें: StudentRegistration को आपके models.py के हिसाब से Participant से बदला गया है।
from .models import Course, Participant 
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
    try:
        # अगर आप होम पेज पर कोर्स डेटा दिखाना चाहते हैं
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
    # कोर्स को Fetch करें
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == "POST":
        
        # यहाँ आपको अपने Participant मॉडल के सभी Fields के हिसाब से डेटा लेना होगा।
        # मैंने सिर्फ रजिस्ट्रेशन से सम्बंधित मुख्य फील्ड्स रखे हैं, बाकी आप जोड़ सकते हैं।
        
        full_name = request.POST.get('full_name') # Participant मॉडल के हिसाब से field नाम
        phone_number = request.POST.get('phone_number') # Participant मॉडल के हिसाब से field नाम
        email = request.POST.get('email', '') # Optional हो सकता है

        # 1. Participant ऑब्जेक्ट बनाएं (StudentRegistration के बजाय)
        registration = Participant.objects.create(
            registered_course=course,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            # अन्य Participant fields यहाँ जोड़ें, जैसे: dob, gender, photo, school_name, school_class, school_address
            # उदाहरण:
            # dob=request.POST.get('dob'),
            # gender=request.POST.get('gender'),
            # school_name=request.POST.get('school_name'),
            # school_class=request.POST.get('school_class'),
            # school_address=request.POST.get('school_address'),
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
    # Participant ऑब्जेक्ट Fetch करें (StudentRegistration के बजाय)
    registration = get_object_or_404(Participant, id=registration_id)
    
    # Razorpay Client को सिर्फ इस फंक्शन के अंदर Initialize करें
    try:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    except Exception as e:
        messages.error(request, "Payment configuration error. Contact support.")
        print(f"Razorpay Client Initialization Error: {e}")
        return redirect('courses_view')

    # यहाँ price आपके Course मॉडल से आ रहा है।
    # Participant मॉडल में 'amount' field नहीं है, इसलिए हम Course.fee का उपयोग कर रहे हैं।
    amount_to_pay = registration.registered_course.fee 
    amount_in_paisa = int(amount_to_pay * 100) 

    # Razorpay Order बनाएं
    order_data = {
        'amount': amount_in_paisa,
        'currency': 'INR',
        'receipt': str(registration.id),
        'payment_capture': '1' 
    }
    
    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        context = {
            'registration': registration,
            'amount_in_rupees': amount_to_pay, # display के लिए रुपये में
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': RAZORPAY_KEY_ID,
            'amount_in_paisa': amount_in_paisa,
            'callback_url': request.build_absolute_uri('/payment-status/'), 
        }
        return render(request, 'registration/payment.html', context)
        
    except Exception as e:
        messages.error(request, "Could not create payment order. Check Razorpay keys.")
        print(f"Razorpay Order Creation Error: {e}")
        # अगर order fail हो जाए तो रजिस्ट्रेशन पेज पर वापस भेजें
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

            # Verification सफल: Participant ऑब्जेक्ट अपडेट करें
            
            # Note: Razorpay order ID अक्सर 'order_XXX' फॉर्मेट में होता है।
            # हमें order ID से registration ID को निकालना मुश्किल हो सकता है।
            # हम इसे बाद में Fetch कर सकते हैं या Payment View से data पास कर सकते हैं।
            
            # Log में order ID से receipt ID (registration ID) निकालने का प्रयास करें
            # यह मानकर कि receipt ID को order_data में registration.id के रूप में सेट किया गया था
            
            # यहाँ हम Payment Status से order_id निकालकर, Participant को उसके order_id से Find करेंगे।
            # चूँकि आपने order ID को model में save किया है, हम उसका उपयोग कर सकते हैं।
            
            registration = Participant.objects.get(razorpay_order_id=razorpay_order_id)
            
            registration.payment_completed = True # 'payment_status' के बजाय 'payment_completed'
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
# 6. Utility Views
#-----------------------------------------------------------
def success_view(request):
    return render(request, 'registration/success.html')

def failure_view(request):
    return render(request, 'registration/failure.html')

def about_sir_view(request):
    return render(request, 'registration/about_sir.html')
