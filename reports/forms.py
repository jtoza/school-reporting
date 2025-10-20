from django import forms
from .models import AssessmentResult, AcademicYear, Student, SchoolClass
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