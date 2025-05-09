
from django.db import models
from django.conf import settings


class ResourceCategory(models.Model):
    """Categories for resources"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Resource Categories"


class Resource(models.Model):
    """Model for educational resources and video tutorials"""
    
    RESOURCE_TYPES = (
        ('video', 'Video Tutorial'),
        ('pdf', 'PDF Document'),
        ('article', 'Article'),
        ('guide', 'Guide'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='resources/')
    thumbnail = models.ImageField(upload_to='resource_thumbnails/', null=True, blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_resources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
