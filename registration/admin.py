# from django.contrib import admin
# from django.utils.html import format_html
# from .models import Participant

# @admin.register(Participant)
# class ParticipantAdmin(admin.ModelAdmin):
#     list_display = ('full_name', 'school_name', 'school_class', 'phone_number', 'dob', 'gender', 'photo_tag')
#     search_fields = ('full_name', 'school_name', 'phone_number')
#     list_filter = ('gender', 'school_class')

#     readonly_fields = ('photo_tag',)  # agar chaho ki admin edit na kare

#     def photo_tag(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;"/>', obj.photo.url)
#         return "-"
#     photo_tag.short_description = 'Photo'


# # new work 
# from django.contrib import admin
# from .models import Participant, Branch, Course, StudyMaterial, ContactMessage

# # @admin.register(Participant)
# # class ParticipantAdmin(admin.ModelAdmin):
# #     list_display = ('full_name','school_name','school_class','phone_number','dob','gender','payment_completed')
# #     search_fields = ('full_name','school_name','phone_number')

# @admin.register(Branch)
# class BranchAdmin(admin.ModelAdmin):
#     list_display = ('name','address','phone')

# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('title','fee','duration','is_active')
#     search_fields = ('title',)

# @admin.register(StudyMaterial)
# class MaterialAdmin(admin.ModelAdmin):
#     list_display = ('title','course','price','published_at')
#     search_fields = ('title',)

# @admin.register(ContactMessage)
# class ContactAdmin(admin.ModelAdmin):
#     list_display = ('name','email','phone','created_at','responded')
#     list_filter = ('responded',)




from django.contrib import admin
from django.utils.html import format_html
from .models import Participant, Branch, Course, StudyMaterial, LiveLecture, ContactMessage

# Participant admin
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'school_name',
        'school_class',
        'phone_number',
        'dob',
        'gender',
        'payment_completed',
        'photo_tag'
    )
    search_fields = ('full_name', 'school_name', 'phone_number')
    list_filter = ('gender', 'school_class', 'payment_completed')
    readonly_fields = ('photo_tag',)

    def photo_tag(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover;" />',
                obj.photo.url
            )
        return "-"
    photo_tag.short_description = 'Photo'


# Branch admin
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    search_fields = ('name', 'address')


# Course admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'is_active')
    list_filter = ('branch', 'is_active')
    search_fields = ('name', 'description')


# StudyMaterial admin
@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'published_at')
    list_filter = ('course',)
    search_fields = ('title',)


# LiveLecture admin
@admin.register(LiveLecture)
class LiveLectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'schedule_time')
    list_filter = ('course',)
    search_fields = ('title',)


# ContactMessage admin
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'responded')
    list_filter = ('responded',)
    search_fields = ('name', 'email', 'phone')
