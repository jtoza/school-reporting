from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from .models import SchoolClass, Student, AssessmentResult, AcademicYear, Subject
from .forms import AssessmentResultForm, StudentForm
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