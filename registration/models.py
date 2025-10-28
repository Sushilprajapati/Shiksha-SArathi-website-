from django.db import models
from django.utils.translation import gettext_lazy as _

# Choices defined for better data consistency
GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

# ===== Branch =====
class Branch(models.Model):
    name = models.CharField(max_length=150)
    address = models.TextField() 
    phone = models.CharField(max_length=20, blank=True)
    map_embed = models.TextField(blank=True, help_text="Optional iframe embed or Google Maps link")

    def __str__(self):
        return self.name

# ===== Course =====
class Course(models.Model):
    name = models.CharField(max_length=200)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    short_desc = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    fee = models.IntegerField(default=0)  # in rupees
    duration = models.CharField(max_length=100, blank=True)  # e.g. "6 months"
    thumbnail = models.ImageField(upload_to='course_thumbs/', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

# ===== Participant =====
class Participant(models.Model):
    full_name = models.CharField(max_length=100)
    dob = models.DateField()
    # Using choices for consistency
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES) 
    photo = models.ImageField(upload_to='photos/') 
    school_name = models.CharField(max_length=100)
    school_class = models.IntegerField()
    school_address = models.TextField()
    # Added db_index for faster lookups
    phone_number = models.CharField(max_length=10, db_index=True) 
    # Optional field (blank=True)
    email = models.EmailField(blank=True) 

    payment_completed = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    registered_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"{self.full_name} - {self.school_name}"

    class Meta:
        verbose_name_plural = "Participants"
        unique_together = ('phone_number', 'full_name') 


# ===== Other Models (Unchanged) =====
class StudyMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='materials/')
    price = models.IntegerField(default=0)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LiveLecture(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    lecture_link = models.URLField()
    schedule_time = models.DateTimeField()

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

# ===== Testimonial (Missing Model Added) =====
class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    school_class = models.IntegerField(null=True, blank=True)
    testimonial_text = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.name}"
