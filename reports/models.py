from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AcademicYear(models.Model):
    name = models.CharField(max_length=20)  # e.g., "2024-2025"
    current = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.current:
            # Ensure only one current academic year
            AcademicYear.objects.filter(current=True).update(current=False)
        super().save(*args, **kwargs)

class SchoolClass(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Grade 5A"
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "School Classes"
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'parent'})
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class AssessmentResult(models.Model):
    PERFORMANCE_LEVELS = [
        ('exceeding', 'Exceeding Expectations'),
        ('meeting', 'Meeting Expectations'),
        ('approaching', 'Approaching Expectations'),
        ('below', 'Below Expectations'),
    ]
    
    TERMS = [
        (1, 'Term 1'),
        (2, 'Term 2'),
        (3, 'Term 3'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.IntegerField(choices=TERMS)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    performance_level = models.CharField(max_length=20, choices=PERFORMANCE_LEVELS)
    teacher_comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'term', 'academic_year']
    
    def __str__(self):
        return f"{self.student} - {self.subject} - Term {self.term}"

class ReportComment(models.Model):
    performance_level = models.CharField(max_length=20, choices=AssessmentResult.PERFORMANCE_LEVELS)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    template_comment = models.TextField()
    
    def __str__(self):
        return f"{self.get_performance_level_display()} - {self.subject}"