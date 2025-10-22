from django import forms
from .models import Participant
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date

# Validators
name_validator = RegexValidator(r'^[A-Za-z\s\.]+$', message="Name can contain letters, spaces and dots only.")
phone_validator = RegexValidator(r'^\d{10}$', message="Enter a valid 10-digit phone number.")

def validate_photo(file):
    max_mb = 5
    allowed_content_types = ['image/jpeg', 'image/png']
    if file:
        if hasattr(file, 'content_type') and file.content_type not in allowed_content_types:
            raise ValidationError('Only JPG and PNG images are allowed.')
        if file.size > max_mb * 1024 * 1024:
            raise ValidationError(f'Photo file size must be <= {max_mb} MB.')

def validate_dob(dob):
    if dob > date.today():
        raise ValidationError('Date of birth cannot be in the future.')
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 5:
        raise ValidationError('Participant must be at least 5 years old.')

class ParticipantForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100,
        validators=[name_validator],
        widget=forms.TextInput(attrs={'placeholder': 'Your Full Name','class': 'w-full p-2 rounded-lg border'})
    )

    phone_number = forms.CharField(
        max_length=10,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number','class': 'w-full p-2 rounded-lg border','inputmode': 'numeric','pattern': r'\d{10}','title': 'Enter a valid 10-digit phone number'})
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email (optional)','class':'w-full p-2 rounded-lg border'})
    )

    class Meta:
        model = Participant
        fields = [
            'full_name', 'dob', 'gender', 'photo',
            'school_name', 'school_class', 'school_address',
            'phone_number', 'email'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type':'date','class':'w-full p-2 rounded-lg border'}),
            'gender': forms.Select(attrs={'class':'w-full p-2 rounded-lg border'}, choices=[('', 'Select Gender'), ('Male','Male'), ('Female','Female'), ('Other','Other')]),
            'school_name': forms.TextInput(attrs={'placeholder':'Your School Name','class':'w-full p-2 rounded-lg border'}),
            'school_class': forms.NumberInput(attrs={'placeholder':'Class (1-12)','class':'w-full p-2 rounded-lg border','min':1,'max':12}),
            'school_address': forms.TextInput(attrs={'placeholder':'Your Address','class':'w-full p-2 rounded-lg border'}),
            'photo': forms.ClearableFileInput(attrs={'class':'w-full', 'accept':'image/jpeg,image/png'})
        }

    # Clean methods
    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            validate_dob(dob)
        return dob

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            validate_photo(photo)
        return photo

    def clean_school_class(self):
        cls = self.cleaned_data.get('school_class')
        if cls is None:
            raise ValidationError("Class is required.")
        try:
            cls_int = int(cls)
        except (TypeError, ValueError):
            raise ValidationError("Enter a valid class number.")
        if cls_int < 1 or cls_int > 12:
            raise ValidationError("Class must be between 1 and 12.")
        return cls_int

    def clean_school_name(self):
        name = self.cleaned_data.get('school_name')
        if name and len(name.strip()) < 2:
            raise ValidationError("Enter a valid school name.")
        return name

    def clean_school_address(self):
        addr = self.cleaned_data.get('school_address')
        if not addr or len(addr.strip()) < 5:
            raise ValidationError("Address must be at least 5 characters.")
        return addr
