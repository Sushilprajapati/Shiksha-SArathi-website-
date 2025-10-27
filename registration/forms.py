from django import forms
from .models import Participant, Course # Ensure Course is imported
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date

# ====================================================================
# 1. Validators
# ====================================================================

name_validator = RegexValidator(
    r'^[A-Za-z\s\.]+$', 
    message="Name can contain letters, spaces and dots only."
)

phone_validator = RegexValidator(
    r'^\d{10}$', 
    message="Enter a valid 10-digit phone number."
)

def validate_photo(file):
    """Validates file size (max 5MB) and type (JPG/PNG)."""
    max_mb = 5
    allowed_content_types = ['image/jpeg', 'image/png']
    
    if file:
        if hasattr(file, 'content_type') and file.content_type not in allowed_content_types:
            raise ValidationError('Only JPG and PNG images are allowed.')
        
        if file.size > max_mb * 1024 * 1024:
            raise ValidationError(f'Photo file size must be less than or equal to {max_mb} MB.')

def validate_dob(dob):
    """Validates Date of Birth (not future date and min age 5)."""
    if dob > date.today():
        raise ValidationError('Date of birth cannot be in the future.')
        
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    if age < 5:
        raise ValidationError('Participant must be at least 5 years old.')

# ====================================================================
# 2. Form Definition: ParticipantForm
# ====================================================================

class ParticipantForm(forms.ModelForm):
    # --- Custom Fields (Overriding Model Fields) ---
    
    # 1. full_name: Required and validated
    full_name = forms.CharField(
        max_length=100,
        validators=[name_validator],
        widget=forms.TextInput(attrs={'placeholder': 'Your Full Name','class': 'form-input', 'required': True})
    )

    # 2. phone_number: Required, validated, and uses numeric input mode
    phone_number = forms.CharField(
        max_length=10,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your 10-digit phone number',
            'class': 'form-input',
            'inputmode': 'numeric',
            'pattern': r'\d{10}',
            'title': 'Enter a valid 10-digit phone number',
            'required': True
        })
    )

    # 3. email: Optional
    email = forms.EmailField(
        required=False, 
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email (Optional)','class':'form-input'})
    )
    
    # 4. course: ModelChoiceField to select a course from the database
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Desired Course",
        empty_label="Select a Course for Enrollment",
        required=True, # This field is mandatory for registration
        widget=forms.Select(attrs={'class': 'form-input'})
    )


    class Meta:
        model = Participant
        # We include 'registered_course' from the model and the custom 'course' field here, 
        # but the views.py will need to handle mapping the form's 'course' to the model's 'registered_course'.
        fields = [
            'full_name', 'dob', 'gender', 'photo',
            'school_name', 'school_class', 'school_address',
            'phone_number', 'email', 'course' # 'course' is the explicit ModelChoiceField
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type':'date','class':'form-input', 'required': True}),
            'gender': forms.Select(attrs={'class':'form-input', 'required': True}, choices=[('', 'Select Gender'), ('Male','Male'), ('Female','Female'), ('Other','Other')]),
            'school_name': forms.TextInput(attrs={'placeholder':'Your School Name','class':'form-input', 'required': True}),
            'school_class': forms.NumberInput(attrs={'placeholder':'Class (1-12)','class':'form-input','min':1,'max':12, 'required': True}),
            'school_address': forms.TextInput(attrs={'placeholder':'Your Full Address','class':'form-input', 'required': True}),
            # Photo is treated as required for now. Remove 'required': True if optional.
            'photo': forms.ClearableFileInput(attrs={'class':'w-full', 'accept':'image/jpeg,image/png', 'required': True}) 
        }

    # ====================================================================
    # 3. Clean Methods (Server-Side Validation)
    # ====================================================================
    
    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            validate_dob(dob)
        return dob

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            validate_photo(photo)
        # Note: If photo is REQUIRED, you need extra logic here if ClearableFileInput allows clearing.
        return photo

    def clean_school_class(self):
        cls = self.cleaned_data.get('school_class')
        if cls is not None:
            if cls < 1 or cls > 12:
                raise ValidationError("Class must be between 1 and 12.")
        return cls

    def clean_school_name(self):
        name = self.cleaned_data.get('school_name')
        if not name or len(name.strip()) < 2:
            raise ValidationError("Enter a valid school name (min 2 characters).")
        return name

    def clean_school_address(self):
        addr = self.cleaned_data.get('school_address')
        if not addr or len(addr.strip()) < 5:
            raise ValidationError("Address must be at least 5 characters.")
        return addr
    
    # Final cleanup to link the custom 'course' field to the model instance before saving
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Manually link the selected course to the Participant model's Foreign Key field
        instance.registered_course = self.cleaned_data['course']
        if commit:
            instance.save()
        return instance