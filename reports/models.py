from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'parent'}, null=True, blank=True)
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

class Grade(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Grade 1", "Grade 2"
    section = models.CharField(max_length=10, blank=True)  # e.g., "A", "B"
    
    def __str__(self):
        return f"{self.name} - {self.section}" if self.section else self.name

    class Meta:
        ordering = ['name']

class SubjectAssignment(models.Model):
    ASSIGNMENT_TYPES = [
        ('homework', 'Homework'),
        ('classwork', 'Classwork'),
        ('project', 'Project'),
        ('quiz', 'Quiz'),
        ('test', 'Test'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES, default='homework')
    due_date = models.DateTimeField()
    max_points = models.IntegerField(default=100)
    instructions = models.TextField(blank=True)
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
    
    def __str__(self):
        return f"{self.title} - {self.subject}"
    
    def is_past_due(self):
        return timezone.now() > self.due_date
    
    def days_until_due(self):
        delta = self.due_date - timezone.now()
        return delta.days if delta.days > 0 else 0

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(SubjectAssignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submission_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_feedback = models.TextField(blank=True)
    is_graded = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student} - {self.assignment}"

class StudentContact(models.Model):
    CLASS_LEVELS = [
        ('pp1', 'Pre-Primary 1 (PP1)'),
        ('pp2', 'Pre-Primary 2 (PP2)'),
        ('grade1', 'Grade 1'),
        ('grade2', 'Grade 2'),
        ('grade3', 'Grade 3'),
        ('grade4', 'Grade 4'),
        ('grade5', 'Grade 5'),
        ('grade6', 'Grade 6'),
        ('grade7', 'Grade 7'),
        ('grade8', 'Grade 8'),
    ]
    
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    class_level = models.CharField(max_length=10, choices=CLASS_LEVELS)
    parent_name = models.CharField(max_length=200)
    parent_id_number = models.CharField(max_length=20)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(blank=True)
    child_name = models.CharField(max_length=200)
    child_admission_number = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    home_address = models.TextField(blank=True)
    special_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['class_level', 'child_name']
        verbose_name_plural = "Student Contacts"
    
    def __str__(self):
        return f"{self.child_name} - {self.parent_name} ({self.get_class_level_display()})"