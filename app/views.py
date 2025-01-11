from django.contrib.auth import logout
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from .models import Session, Subject, Grade, GradingScheme, ScoringScheme, Class, Permission, Student, Result, ResultToken
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum


class IndexView(TemplateView):
    template_name = 'app/index.html'  # Specify the template to render


class RoleBasedLoginView(LoginView):
    template_name = 'app/login.html'
    
    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

    def get_success_url(self):
        user = self.request.user
        if user.role == 'admin':
            return reverse('admin_dashboard')
        elif user.role == 'teacher':
            return reverse('teacher_dashboard')
        elif user.role == 'parent':
            return reverse('parent_dashboard')
        else:
            return reverse('login')  # Fallback in case of undefined role

# Logout View
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')

# Teacher Dashboard View
class TeacherDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'app/teacher_dashboard.html'
    redirect_field_name = 'next'  # Redirect back after login

    def get_context_data(self, **kwargs):
        user = self.request.user
        if not user.is_authenticated or user.role != 'teacher':
            return redirect('login')

        sessions = Session.objects.all()
        terms = ['First Term', 'Second Term', 'Third Term']
        permissions = Permission.objects.filter(teacher=user, school=user.school)

        if len(permissions) == 0:
          messages.error(self.request, "You currently don't have any permission to grade.")
          
        return {
            'sessions': sessions,
            'terms': terms,
            'permissions': permissions,
        }

# Grade Editor View
class GradeEditorView(LoginRequiredMixin, View):
    redirect_field_name = 'next'  # Redirect back after login
  
    def get(self, request, school, session, term, class_assigned, subject):
        if not request.user.is_authenticated or request.user.role != 'teacher':
            return redirect('login')

        students = Student.objects.filter(class_assigned__name=class_assigned, school__name=school, session__name=session)
        
        grades = []
        try:
            for student in students:
              grade, created = Grade.objects.get_or_create(
              student=student,
              subject__name=subject,
              class_assigned__name=class_assigned,
              session__name=session,
              term=term,
              defaults={
              'result': Result.objects.get(student=student, session__name=session, term=term),
              'class_assigned_id': class_assigned,
              'session_id': session,
              'term': term,
              'subject_id': subject,
              'student': student
            })
              grades.append(grade)
        except Result.DoesNotExist:
            messages.error(request, f"Results for {session} {term} {class_assigned} has not been generated. Please contact the school administrator.")
            return redirect('teacher_dashboard')
            
        scoring_scheme = ScoringScheme.objects.get(school=request.user.school)
        
        # Add pagination
        paginator = Paginator(sorted(grades, key=lambda grade: grade.student.name), 30)  # Show 20 grades per page
        page_number = request.GET.get('page', 1)  # Get the current page number from the URL
        page_obj = paginator.get_page(page_number)
        

        return render(request, 'app/grade_editor.html', {
            'class_name': class_assigned,
            'subject_name': subject,
            'grades': page_obj,  # Pass the paginated grades
            'page_obj': page_obj,  # Pass the pagination object for template
            'scoring_scheme': scoring_scheme
        })

    def post(self, request, school, session, term, class_assigned, subject):
        if not request.user.is_authenticated or request.user.role != 'teacher':
            return redirect('login')

        student_ids = [int(key.split('_')[-1]) for key in request.POST.keys() if key.startswith('ca_score_')]

        students = Student.objects.filter(id__in=student_ids)
        grades = Grade.objects.filter(
            student__in=students,
            subject__name=subject,
            class_assigned__name=class_assigned,
            session__name=session,
            term=term,
        )

        # Map existing grades by student ID for quick lookup
        grades_by_student = {grade.student.id: grade for grade in grades}

        updated_grades = []
        for student_id in student_ids:

            ca_score = request.POST.get(f'ca_score_{student_id}')
            exam_score = request.POST.get(f'exam_score_{student_id}')
            
            grade = grades_by_student.get(student_id)
            grade.ca_score = float(ca_score) if len(ca_score) > 0 else None
            grade.exam_score = float(exam_score) if len(exam_score) > 0 else None
            
            updated_grades.append(grade)

        # Use bulk_update to save changes efficiently
        with transaction.atomic():
            Grade.objects.bulk_update(updated_grades, ['ca_score', 'exam_score'])
            messages.success(request, "Item(s) saved successfully")
            
    
        # Determine button action
        if 'save_next' in request.POST:
            # Redirect to the next page if available
            current_page = int(request.POST.get('current_page', 1))
            total_pages = int(request.POST.get('total_pages', 1))
            if current_page < total_pages:
                return redirect(f"{request.path}?page={current_page + 1}")
        return redirect('teacher_dashboard')

class ResultCheckerView(View):
    def get(self, request):
        sessions = Session.objects.all()
        terms = ['First Term', 'Second Term', 'Third Term']
        
        context = {'sessions': sessions, 'terms': terms}
        return render(request, 'app/result_checker.html', context)


    def post(self, request):
        # Get the form data
        session_name = request.POST.get('session')
        term_name = request.POST.get('term')
        admission_number = request.POST.get('admission_number')
        pin = request.POST.get('pin')
        

        # Validate the input
        try:
            result = Result.objects.get(student__admission_number=admission_number, session__name=session_name, term=term_name)
            token = ResultToken.objects.get(pin=pin, result=result)
        except ObjectDoesNotExist: 
            messages.error(request, "Invalid credentials. Please contact the school administrator.")
            return HttpResponseRedirect('/result-checker/')
        

        # Check if token is valid or expired
        if token.is_expired():
            messages.error(request, "The token has expired. Please contact the school administrator.")
            return HttpResponseRedirect('/result-checker/')

        request.session['grant_access'] = result.id
        # Redirect to result view if successful
        return HttpResponseRedirect(f'/result/{result.id}/')

class ResultView(View):
    def get(self, request, result_id):
        # Fetch the result
        try:
            result = Result.objects.get(id=result_id)
        except ObjectDoesNotExist: 
            messages.error(request, "No such result exists.")
            return HttpResponseRedirect('/result-checker/')
        
     #   if request.session.get('grant_access', False) != result.id:
           # messages.error(request, "Provide the required credentials to view result.")
          #  return HttpResponseRedirect('/result-checker/')
        grades = result.grades.filter(ca_score__isnull=False, exam_score__isnull=False)
         
        return render(request, 'app/result.html', {
            'result': result,
            'grades': grades
        })
        
class AdminResultFilterView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'admin':
            return redirect('login')
            
        sessions = Session.objects.all()
        terms = ['First Term', 'Second Term', 'Third Term']
        classes = Class.objects.all()
        
        return render(request, 'app/admin_result_filter.html', {
            'sessions': sessions,
            'terms': terms,
            'classes': classes,
        })

    def post(self, request):
        if request.user.role != 'admin':
            return redirect('login')
            
        # Filter based on selected inputs
        session_id = request.POST.get('session')
        term_ids = request.POST.getlist('term')
        class_ids = request.POST.getlist('class')
        student_name = request.POST.get('student_name', '')

        results = Result.objects.filter(session_id=session_id, school=request.user.school)

        if term_ids:
            results = results.filter(term__in=term_ids)
        if class_ids:
            results = results.filter(student__class_assigned_id__in=class_ids)
        if student_name:
            results = results.filter(student__name__icontains=student_name)
        
            
                
        # Add pagination
        paginator = Paginator(results, 30)  # Show 30 results per page
        page_number = request.POST.get('page', 1)  # Get the current page number from the URL
        page_obj = paginator.get_page(page_number)
        

        return render(request, 'app/admin_result_list.html', {
            'results': page_obj,
            'page_obj': page_obj,
            'session': session_id,
            'term_ids': term_ids,
            'class_ids': class_ids,
            'student_name': student_name
        })

class AdminResultComputeView(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.role != 'admin':
            return redirect('login')
            
        session_id = request.POST.get('session')
        term = request.POST.get('term')
        class_ids = request.POST.getlist('class')

        # Validate inputs
        if not session_id or not term or not class_ids:
            messages.error(request, "Please provide session, term, and class(es).")
            return redirect('admin_dashboard')

        session = get_object_or_404(Session, name=session_id)
        classes = Class.objects.filter(name__in=class_ids)

        for class_assigned in classes:
            students = class_assigned.students.filter(school=request.user.school, session__name=session_id)
            school = request.user.school

            for student in students:
                # Get or create the result for this student, session, and term
                result, created = Result.objects.get_or_create(
                    school=school,
                    student=student,
                    session=session,
                    term=term,
                )

                # Get all grades for this student in the selected session and term
                grades = Grade.objects.filter(
                    student=student,
                    session=session,
                    term=term,
                    class_assigned=class_assigned,
                )

                # Update grades with letter grades and remarks
                grading_scheme = GradingScheme.objects.filter(school=school).order_by('-min_score')
                for grade in grades:
                    # Assign letter grade and remark
                    for scheme in grading_scheme:
                      if grade.total_score:
                        if scheme.min_score <= grade.total_score <= scheme.max_score:
                            grade.letter_grade = scheme.letter_grade
                            grade.remark = scheme.remark
                            break
                    
                with transaction.atomic():
                    Grade.objects.bulk_update(grades, ['letter_grade', 'remark'])

            # Assign subject positions within the class
            subjects = Grade.objects.filter(
                student__in = students,
                class_assigned=class_assigned,
                session=session,
                term=term,
            ).values('subject').distinct()

            for subject in subjects:
                subject_id = subject['subject']
                grades_in_subject = Grade.objects.filter(
                    student__in = students,
                    class_assigned=class_assigned,
                    session=session,
                    term=term,
                    subject_id=subject_id,
                ).annotate(score=F('ca_score')+F('exam_score')).order_by('-score')

                previous_grade_score = None
                grade_position = 1
                batch = 0
                for grade in grades_in_subject:
                    if previous_grade_score:
                      if not grade.total_score: # Exclude Student grades with NO SCORE from positions
                        pass # They don't take the course
                      elif previous_grade_score > grade.total_score:
                        grade_position = grade_position + batch
                        previous_grade_score = grade.total_score
                        grade.position = f"{grade_position}"
                        batch = 1
                      else:
                        grade.position = f"{grade_position}"
                        batch = batch + 1
                    else:
                      if not grade.total_score: # Exclude...
                        pass # They...
                      else:
                        previous_grade_score = grade.total_score
                        grade.position = f"{grade_position}"
                        batch = 1
                      
                          # Use bulk_update to save changes efficiently
                with transaction.atomic():
                    Grade.objects.bulk_update(grades_in_subject, ['position'])

            # Assign class positions
            results = Result.objects.filter(session=session, term=term, school=school, student__class_assigned=class_assigned)
            sorted_results = sorted(results, key=lambda x: x.average_score or 0, reverse=True)
            
            prev_avg_score = None
            position = 1
            batch = 0 # how many currently have the current position
            for result in sorted_results:
                if prev_avg_score:
                  if prev_avg_score > result.average_score:
                    position = position + batch
                    prev_avg_score = result.average_score
                    result.class_position = f"{position}"
                    batch = 1
                  else:
                    result.class_position = f"{position}"
                    batch = batch + 1
                else:
                  prev_avg_score = result.average_score
                  result.class_position = f"{position}"
                  batch = 1
            # Use bulk_update to save changes efficiently
            with transaction.atomic():
                Result.objects.bulk_update(sorted_results, ['class_position'])
        messages.success(request, f"{session} - {term} results generated successfully.")
        return redirect('admin_dashboard')


class AdminPermissionFilterView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'admin':
            return redirect('login')
            
        if not request.user.is_authenticated or request.user.role != 'admin':
            return redirect('login')
            
        classes = Class.objects.all()
        subjects = Subject.objects.all()
        
        return render(request, 'app/admin_permission_filter.html', {
            'classes': classes,
            'subjects': subjects,
        })

    def post(self, request):
        if request.user.role != 'admin':
            return redirect('login')
        
        if not request.user.is_authenticated or request.user.role != 'admin':
            return redirect('login')
            
        class_ids = request.POST.getlist('class')
        subject_ids = request.POST.getlist('subject')

        permissions = Permission.objects.filter(school=request.user.school)

        if class_ids:
            permissions = permissions.filter(class_assigned_id__in=class_ids)
        if subject_ids:
            permissions = permissions.filter(subject_id__in=subject_ids)

        return render(request, 'app/admin_permission_list.html', {
            'permissions': permissions,
        })

