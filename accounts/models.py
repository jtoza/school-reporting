from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('admin', 'Administrator'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True)
    
    def is_teacher(self):
        return self.user_type == 'teacher'
    
    def is_parent(self):
        return self.user_type == 'parent'
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"