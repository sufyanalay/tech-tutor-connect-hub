
from django.db import models
from django.conf import settings


class AcademicQuestion(models.Model):
    """Model for academic questions submitted by students"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('answered', 'Answered'),
        ('closed', 'Closed'),
    )
    
    SUBJECT_CHOICES = (
        ('mathematics', 'Mathematics'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('computer_science', 'Computer Science'),
        ('literature', 'Literature'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('economics', 'Economics'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='academic_questions'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_questions'
    )
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    session_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class AcademicQuestionMedia(models.Model):
    """Model for media attached to academic questions (images/documents)"""
    
    question = models.ForeignKey(AcademicQuestion, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='academic_media/')
    file_type = models.CharField(max_length=10, choices=[
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
    ])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Media for {self.question.title}"


class AcademicAnswer(models.Model):
    """Model for answers to academic questions"""
    
    question = models.ForeignKey(AcademicQuestion, on_delete=models.CASCADE, related_name='answers')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answer_text = models.TextField()
    attachment = models.FileField(upload_to='answer_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Answer to: {self.question.title}"
