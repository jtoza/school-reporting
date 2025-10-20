from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from reports.models import SchoolClass, Student, AssessmentResult

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome {user.username}')
            
            # Redirect based on user type
            if user.is_teacher():
                return redirect('teacher_dashboard')
            elif user.is_parent():
                return redirect('parent_dashboard')
            else:
                return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_teacher():
        return redirect('teacher_dashboard')
    elif request.user.is_parent():
        return redirect('parent_dashboard')
    else:
        return render(request, 'accounts/dashboard.html')

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher():
        messages.error(request, 'Access denied. Teacher area only.')
        return redirect('dashboard')
    
    # Get classes taught by this teacher with student counts
    classes = SchoolClass.objects.filter(teacher=request.user).prefetch_related('student_set')
    
    # Get recent results entered by this teacher
    recent_results = AssessmentResult.objects.filter(
        student__school_class__teacher=request.user
    ).select_related('student', 'subject')[:5]
    
    # Calculate stats
    total_students = sum(cl.student_set.count() for cl in classes)
    total_results = AssessmentResult.objects.filter(
        student__school_class__teacher=request.user
    ).count()
    
    context = {
        'classes': classes,
        'recent_results': recent_results,
        'total_students': total_students,
        'total_results': total_results,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)

@login_required
def parent_dashboard(request):
    if not request.user.is_parent():
        messages.error(request, 'Access denied. Parent area only.')
        return redirect('dashboard')
    
    # Get students belonging to this parent with their classes and recent results
    students = Student.objects.filter(user=request.user).select_related('school_class')
    
    # Get recent results for all children
    recent_results = AssessmentResult.objects.filter(
        student__user=request.user
    ).select_related('student', 'subject')[:5]
    
    context = {
        'students': students,
        'recent_results': recent_results,
    }
    return render(request, 'accounts/parent_dashboard.html', context)

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')