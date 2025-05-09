
from django.db import models
from django.conf import settings


class RepairRequest(models.Model):
    """Model for gadget repair requests"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    
    DEVICE_CHOICES = (
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet'),
        ('smartphone', 'Smartphone'),
        ('printer', 'Printer'),
        ('other', 'Other')
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='repair_requests'
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_repairs'
    )
    device_type = models.CharField(max_length=20, choices=DEVICE_CHOICES)
    device_model = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class RepairMedia(models.Model):
    """Model for media attached to repair requests (images/videos)"""
    
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='repair_media/')
    file_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video')])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Media for {self.repair_request.title}"


class RepairComment(models.Model):
    """Model for comments on repair requests"""
    
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.full_name} on {self.repair_request.title}"
