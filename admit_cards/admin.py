from django.contrib import admin
from .models import Student, ActivityLog, BulkTask

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'student_class', 'batch', 'gender', 'is_generated', 'created_at')
    list_filter = ('student_class', 'batch', 'gender', 'is_generated')
    search_fields = ('name', 'registration_number', 'aadhaar_number', 'mobile_number')
    readonly_fields = ('card_jpg', 'card_pdf', 'is_generated', 'created_at', 'updated_at')
    
    actions = ['generate_admit_cards']

    def generate_admit_cards(self, request, queryset):
        from .generator import generate_admit_card_files
        generated = 0
        for student in queryset:
            try:
                jpg_file, pdf_file = generate_admit_card_files(student)
                student.card_jpg.save(jpg_file.name, jpg_file, save=False)
                student.card_pdf.save(pdf_file.name, pdf_file, save=False)
                student.is_generated = True
                student.save()
                generated += 1
            except Exception as e:
                self.message_user(request, f"Failed to generate card for {student.name}: {e}", level='ERROR')
        
        self.message_user(request, f"Successfully generated {generated} admit cards.")
        
    generate_admit_cards.short_description = "Generate admit cards for selected students"

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'timestamp', 'details')
    list_filter = ('action', 'user', 'timestamp')
    search_fields = ('action', 'details', 'user__username')
    readonly_fields = ('action', 'user', 'timestamp', 'details')

@admin.register(BulkTask)
class BulkTaskAdmin(admin.ModelAdmin):
    list_display = ('task_type', 'status', 'processed_records', 'total_records', 'updated_at')
    list_filter = ('task_type', 'status')
    readonly_fields = ('task_type', 'status', 'processed_records', 'total_records', 'error_message', 'created_at', 'updated_at')
