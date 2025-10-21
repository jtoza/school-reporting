from django import forms
from .models import AssessmentResult, AcademicYear, Student, SchoolClass, SubjectAssignment, AssignmentSubmission, StudentContact
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'date_of_birth', 'user']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.school_class = kwargs.pop('school_class', None)
        super().__init__(*args, **kwargs)
        # Only show parent users in the user dropdown
        self.fields['user'].queryset = User.objects.filter(user_type='parent')
        self.fields['user'].required = False
        self.fields['user'].help_text = "Optional: Link to parent account"

class AssessmentResultForm(forms.ModelForm):
    class Meta:
        model = AssessmentResult
        fields = ['subject', 'term', 'academic_year', 'performance_level', 'teacher_comment']
        widgets = {
            'term': forms.Select(choices=AssessmentResult.TERMS),
            'performance_level': forms.Select(choices=AssessmentResult.PERFORMANCE_LEVELS),
            'teacher_comment': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show current academic year
        current_year = AcademicYear.objects.filter(current=True).first()
        if current_year:
            self.fields['academic_year'].initial = current_year
            self.fields['academic_year'].widget = forms.HiddenInput()

class SubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = SubjectAssignment
        fields = ['title', 'description', 'subject', 'assignment_type', 
                 'due_date', 'max_points', 'instructions', 'attachment', 'is_published']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'instructions': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set current academic year as initial
        current_year = AcademicYear.objects.filter(current=True).first()
        if current_year:
            self.fields['academic_year'] = forms.ModelChoiceField(
                queryset=AcademicYear.objects.all(),
                initial=current_year,
                widget=forms.HiddenInput()
            )
        
        # If user is provided, filter subjects to only those the teacher can assign
        if self.user and self.user.is_teacher():
            # You might want to filter subjects based on what the teacher teaches
            # For now, we'll show all subjects
            pass

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submitted_file', 'submission_text']
        widgets = {
            'submission_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your submission here...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['submitted_file'].help_text = 'Upload your completed assignment file (PDF, Word, etc.)'
        self.fields['submission_text'].help_text = 'Or type your submission directly here'

class GradeAssignmentForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['grade', 'teacher_feedback', 'is_graded']
        widgets = {
            'teacher_feedback': forms.Textarea(attrs={'rows': 4}),
        }

class StudentContactForm(forms.ModelForm):
    class Meta:
        model = StudentContact
        fields = [
            'class_level', 'parent_name', 'parent_id_number', 'parent_phone',
            'parent_email', 'child_name', 'child_admission_number',
            'emergency_contact', 'home_address', 'special_notes'
        ]
        widgets = {
            'home_address': forms.Textarea(attrs={'rows': 3}),
            'special_notes': forms.Textarea(attrs={'rows': 3}),
            'class_level': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.teacher:
            instance.teacher = self.teacher
        if commit:
            instance.save()
        return instance