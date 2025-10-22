from django.db import models

class Participant(models.Model):
    full_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    photo = models.ImageField(upload_to='photos/')
    school_name = models.CharField(max_length=100)
    school_class = models.IntegerField()
    school_address = models.TextField()
    phone_number = models.CharField(max_length=10)
    email = models.EmailField(blank=True, null=True)

    payment_completed = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.school_name}"



# new work 
# registration/models.py (append this)
from django.db import models

class Branch(models.Model):
    name = models.CharField(max_length=150)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    map_embed = models.TextField(blank=True, help_text="Optional iframe embed or Google Maps link")

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    short_desc = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    fee = models.IntegerField(default=0)  # rupees
    duration = models.CharField(max_length=100, blank=True)  # e.g. "6 months"
    thumbnail = models.ImageField(upload_to='course_thumbs/', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class StudyMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='materials/')
    price = models.IntegerField(default=0)  # 0 = free
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"
