from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    student_class = models.CharField(max_length=100)
    batch = models.CharField(max_length=100, blank=True, null=True, default="Batch 2026")
    aadhaar_number = models.CharField(max_length=14)

    registration_number = models.CharField(max_length=100, unique=True)
    mobile_number = models.CharField(max_length=15)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField()
    
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    signature = models.ImageField(upload_to='student_signatures/', blank=True, null=True)
    
    card_jpg = models.FileField(upload_to='generated_cards/', blank=True, null=True)
    card_pdf = models.FileField(upload_to='generated_cards/', blank=True, null=True)
    
    is_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.registration_number})"

class ActivityLog(models.Model):
    action = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.action} by {self.user.username if self.user else 'System'} at {self.timestamp}"

class BulkTask(models.Model):
    TASK_TYPES = [
        ('BULK_GENERATE', 'Bulk Card Generation'),
        ('BULK_ZIP', 'Bulk ZIP Creation'),
        ('EXCEL_IMPORT', 'Excel Import'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    task_type = models.CharField(max_length=100, choices=TASK_TYPES)
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.status} ({self.processed_records}/{self.total_records})"
