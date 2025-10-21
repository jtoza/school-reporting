from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from .models import SchoolClass, Student, AssessmentResult, AcademicYear, Subject, SubjectAssignment, AssignmentSubmission, StudentContact
from .forms import AssessmentResultForm, StudentForm, SubjectAssignmentForm, AssignmentSubmissionForm, GradeAssignmentForm, StudentContactForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io

@login_required
def class_detail(request, pk):
    # Only allow teachers to access their own classes
    school_class = get_object_or_404(SchoolClass, pk=pk, teacher=request.user)
    
    students = Student.objects.filter(school_class=school_class)
    
    context = {
        'class': school_class,
        'students': students,
    }
    return render(request, 'reports/class_detail.html', context)

@login_required
def student_results(request, student_id):
    # Only allow parents to access their own children's results
    student = get_object_or_404(Student, id=student_id, user=request.user)
    
    # Get all results for this student, ordered by term and subject
    results = AssessmentResult.objects.filter(student=student).select_related('subject').order_by('term', 'subject__name')
    
    # Create simple lists for each term (no complex dictionary)
    term1_results = [r for r in results if r.term == 1]
    term2_results = [r for r in results if r.term == 2]
    term3_results = [r for r in results if r.term == 3]
    
    context = {
        'student': student,
        'term1_results': term1_results,
        'term2_results': term2_results,
        'term3_results': term3_results,
        'has_results': any([term1_results, term2_results, term3_results])
    }
    return render(request, 'reports/student_results.html', context)

@login_required
def add_result(request, student_id):
    # Only allow teachers to add results for students in their classes
    student = get_object_or_404(Student, id=student_id)
    
    # Check if the current teacher teaches this student's class
    if student.school_class.teacher != request.user:
        messages.error(request, 'You can only add results for students in your classes.')
        return redirect('teacher_dashboard')
    
    # Get current academic year
    current_year = AcademicYear.objects.filter(current=True).first()
    
    if request.method == 'POST':
        form = AssessmentResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            result.student = student
            result.save()
            messages.success(request, f'Result added successfully for {student.first_name}!')
            return redirect('reports:class_detail', pk=student.school_class.id)
    else:
        # Pre-fill the form with current academic year
        form = AssessmentResultForm(initial={'academic_year': current_year})
    
    context = {
        'form': form,
        'student': student,
        'current_year': current_year,
    }
    return render(request, 'reports/add_result.html', context)

@login_required
def add_student(request, class_id):
    # Only allow teachers to add students to their own classes
    school_class = get_object_or_404(SchoolClass, id=class_id, teacher=request.user)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, school_class=school_class)
        if form.is_valid():
            student = form.save(commit=False)
            student.school_class = school_class
            student.save()
            messages.success(request, f'Student {student.first_name} {student.last_name} added successfully!')
            return redirect('reports:class_detail', pk=school_class.id)
    else:
        form = StudentForm(school_class=school_class)
    
    context = {
        'form': form,
        'school_class': school_class,
    }
    return render(request, 'reports/add_student.html', context)

@login_required
def download_report(request, student_id):
    # Only allow parents to download their own children's reports
    student = get_object_or_404(Student, id=student_id, user=request.user)
    
    # Get all results for this student
    results = AssessmentResult.objects.filter(student=student).select_related('subject').order_by('term', 'subject__name')
    
    # Create the PDF object
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center aligned
    )
    
    # Title
    title = Paragraph(f"ACADEMIC REPORT CARD", title_style)
    elements.append(title)
    
    # Student Information
    student_info = [
        f"Student: {student.first_name} {student.last_name}",
        f"Student ID: {student.student_id}",
        f"Class: {student.school_class.name}",
        f"Academic Year: {student.school_class.academic_year}",
        f"Date Generated: {timezone.now().strftime('%Y-%m-%d')}"
    ]
    
    for info in student_info:
        elements.append(Paragraph(info, styles['Normal']))
        elements.append(Spacer(1, 12))
    
    elements.append(Spacer(1, 24))
    
    # Group results by term
    term_results = {}
    for result in results:
        if result.term not in term_results:
            term_results[result.term] = []
        term_results[result.term].append(result)
    
    # Create table for each term
    for term in sorted(term_results.keys()):
        # Term header
        term_header = Paragraph(f"TERM {term} RESULTS", styles['Heading2'])
        elements.append(term_header)
        elements.append(Spacer(1, 12))
        
        # Table data
        table_data = [['Subject', 'Performance Level', 'Teacher Comment']]
        
        for result in term_results[term]:
            table_data.append([
                result.subject.name,
                result.get_performance_level_display(),
                result.teacher_comment or "No comment"
            ])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 24))
    
    # If no results
    if not results:
        no_data = Paragraph("No assessment results available yet.", styles['BodyText'])
        elements.append(no_data)
    
    # Build PDF
    doc.build(elements)
    
    # File response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{student.student_id}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    return response

@login_required
def student_profile(request, student_id):
    # Only allow teachers to view profiles of students in their classes
    student = get_object_or_404(Student, id=student_id)
    
    if student.school_class.teacher != request.user:
        messages.error(request, 'Access denied.')
        return redirect('teacher_dashboard')
    
    # Get all results for this student
    results = AssessmentResult.objects.filter(student=student).select_related('subject').order_by('term', 'subject__name')
    
    context = {
        'student': student,
        'results': results,
    }
    return render(request, 'reports/student_profile.html', context)

# ===== ASSIGNMENT VIEWS =====

@login_required
def assignment_list(request, grade_id=None, subject_id=None):
    # Teachers see assignments they created, students/parents see published assignments
    if request.user.is_teacher():
        assignments = SubjectAssignment.objects.filter(created_by=request.user)
    else:
        assignments = SubjectAssignment.objects.filter(is_published=True)
    
    # Get current academic year
    current_year = AcademicYear.objects.filter(current=True).first()
    if current_year:
        assignments = assignments.filter(academic_year=current_year)
    
    # Filter by subject if provided
    if subject_id:
        subject = get_object_or_404(Subject, id=subject_id)
        assignments = assignments.filter(subject=subject)
    else:
        subject = None
    
    # Get available subjects for filters
    subjects = Subject.objects.all()
    
    context = {
        'assignments': assignments,
        'subject': subject,
        'subjects': subjects,
        'current_subject_id': subject_id,
        'current_year': current_year,
    }
    return render(request, 'reports/assignment_list.html', context)

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(SubjectAssignment, id=assignment_id)
    
    # Check permissions
    if not assignment.is_published and not request.user.is_teacher():
        messages.error(request, "You don't have permission to view this assignment.")
        return redirect('reports:assignment_list')
    
    if request.user.is_teacher() and assignment.created_by != request.user:
        messages.error(request, "You can only view assignments you created.")
        return redirect('reports:assignment_list')
    
    # Check if student has submitted this assignment
    user_submission = None
    if request.user.is_parent():
        # Get the student object for this parent
        student = Student.objects.filter(user=request.user).first()
        if student:
            user_submission = AssignmentSubmission.objects.filter(
                assignment=assignment, 
                student=student
            ).first()
    
    # Get all submissions for teachers
    submissions = None
    if request.user.is_teacher() and assignment.created_by == request.user:
        submissions = AssignmentSubmission.objects.filter(assignment=assignment)
    
    context = {
        'assignment': assignment,
        'user_submission': user_submission,
        'submissions': submissions,
    }
    return render(request, 'reports/assignment_detail.html', context)

@login_required
def assignment_create(request):
    if not request.user.is_teacher():
        messages.error(request, "Only teachers can create assignments.")
        return redirect('reports:assignment_list')
    
    current_year = AcademicYear.objects.filter(current=True).first()
    if not current_year:
        messages.error(request, "No current academic year set. Please contact administrator.")
        return redirect('reports:assignment_list')
    
    if request.method == 'POST':
        form = SubjectAssignmentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.academic_year = current_year
            assignment.save()
            messages.success(request, f'Assignment "{assignment.title}" created successfully!')
            return redirect('reports:assignment_list')
    else:
        form = SubjectAssignmentForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create New Assignment',
        'current_year': current_year,
    }
    return render(request, 'reports/assignment_form.html', context)

@login_required
def assignment_edit(request, assignment_id):
    if not request.user.is_teacher():
        messages.error(request, "Only teachers can edit assignments.")
        return redirect('reports:assignment_list')
    
    assignment = get_object_or_404(SubjectAssignment, id=assignment_id, created_by=request.user)
    
    if request.method == 'POST':
        form = SubjectAssignmentForm(request.POST, request.FILES, instance=assignment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Assignment "{assignment.title}" updated successfully!')
            return redirect('reports:assignment_detail', assignment_id=assignment.id)
    else:
        form = SubjectAssignmentForm(instance=assignment, user=request.user)
    
    context = {
        'form': form,
        'title': 'Edit Assignment',
        'assignment': assignment
    }
    return render(request, 'reports/assignment_form.html', context)

@login_required
def assignment_delete(request, assignment_id):
    if not request.user.is_teacher():
        messages.error(request, "Only teachers can delete assignments.")
        return redirect('reports:assignment_list')
    
    assignment = get_object_or_404(SubjectAssignment, id=assignment_id, created_by=request.user)
    
    if request.method == 'POST':
        title = assignment.title
        assignment.delete()
        messages.success(request, f'Assignment "{title}" deleted successfully!')
        return redirect('reports:assignment_list')
    
    context = {
        'assignment': assignment
    }
    return render(request, 'reports/assignment_confirm_delete.html', context)

@login_required
def submit_assignment(request, assignment_id):
    if not request.user.is_parent():
        messages.error(request, "Only students (through parent accounts) can submit assignments.")
        return redirect('reports:assignment_list')
    
    assignment = get_object_or_404(SubjectAssignment, id=assignment_id, is_published=True)
    
    # Get the student for this parent
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, "No student profile found for your account.")
        return redirect('reports:assignment_list')
    
    # Check if already submitted
    existing_submission = AssignmentSubmission.objects.filter(assignment=assignment, student=student).first()
    if existing_submission:
        messages.warning(request, "You have already submitted this assignment.")
        return redirect('reports:assignment_detail', assignment_id=assignment.id)
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = student
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('reports:assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentSubmissionForm()
    
    context = {
        'form': form,
        'assignment': assignment,
        'student': student,
    }
    return render(request, 'reports/assignment_submit.html', context)

@login_required
def grade_assignment(request, submission_id):
    if not request.user.is_teacher():
        messages.error(request, "Only teachers can grade assignments.")
        return redirect('reports:assignment_list')
    
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    
    # Check if the teacher created this assignment
    if submission.assignment.created_by != request.user:
        messages.error(request, "You can only grade assignments you created.")
        return redirect('reports:assignment_list')
    
    if request.method == 'POST':
        form = GradeAssignmentForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, f'Assignment graded for {submission.student.first_name}!')
            return redirect('reports:assignment_detail', assignment_id=submission.assignment.id)
    else:
        form = GradeAssignmentForm(instance=submission)
    
    context = {
        'form': form,
        'submission': submission,
    }
    return render(request, 'reports/grade_assignment.html', context)

# ===== STUDENT CONTACT VIEWS =====

@login_required
def student_contact_home(request):
    """Home page for student contact system"""
    if not request.user.is_teacher():
        messages.error(request, 'Access denied. Teachers only.')
        return redirect('home')
    
    return render(request, 'reports/student_contact_home.html')

@login_required
def student_contact_class_select(request):
    """Page where teacher selects their class"""
    if not request.user.is_teacher():
        messages.error(request, 'Access denied. Teachers only.')
        return redirect('home')
    
    if request.method == 'POST':
        class_level = request.POST.get('class_level')
        if class_level:
            return redirect('reports:student_contact_form', class_level=class_level)
    
    return render(request, 'reports/student_contact_class_select.html')

@login_required
def student_contact_form(request, class_level):
    """Form for entering student contact details"""
    if not request.user.is_teacher():
        messages.error(request, 'Access denied. Teachers only.')
        return redirect('home')
    
    # Get the display name for the class level
    class_display = dict(StudentContact.CLASS_LEVELS).get(class_level, class_level)
    
    if request.method == 'POST':
        form = StudentContactForm(request.POST, teacher=request.user)
        if form.is_valid():
            student_contact = form.save()
            if 'save_add' in request.POST:
                messages.success(request, f'Contact information for {student_contact.child_name} saved successfully!')
                return redirect('reports:student_contact_form', class_level=class_level)
            else:
                messages.success(request, f'Contact information for {student_contact.child_name} saved successfully!')
                return redirect('reports:student_contact_list')
    else:
        form = StudentContactForm(initial={'class_level': class_level}, teacher=request.user)
    
    context = {
        'form': form,
        'class_level': class_level,
        'class_display': class_display,
    }
    return render(request, 'reports/student_contact_form.html', context)

@login_required
def student_contact_list(request):
    """View for teachers to see all their student contacts"""
    if not request.user.is_teacher():
        messages.error(request, 'Access denied. Teachers only.')
        return redirect('home')
    
    contacts = StudentContact.objects.filter(teacher=request.user)
    
    # Filter by class level if provided
    class_level = request.GET.get('class_level')
    if class_level:
        contacts = contacts.filter(class_level=class_level)
    
    context = {
        'contacts': contacts,
        'class_levels': StudentContact.CLASS_LEVELS,
        'current_class': class_level,
    }
    return render(request, 'reports/student_contact_list.html', context)