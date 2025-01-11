from django import forms
from .models import (
    User, School, Student, Class, Subject, SchoolSubject, ClassSubject, 
    Grade, Result, Session, Term, Permission, Parent, ParentStudent
)

# Form for User
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'school', 'photo']
        widgets = {
            'password': forms.PasswordInput(),  # To render password fields
        }

# Form for School
class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'address', 'logo']

# Form for Student
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'admission_number', 'school', 'class_assigned', 'photo', 'gender', 'date_of_birth']

# Form for Class
class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'school']

# Form for Subject
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']

# Form for SchoolSubject
class SchoolSubjectForm(forms.ModelForm):
    class Meta:
        model = SchoolSubject
        fields = ['school', 'subject']

# Form for ClassSubject
class ClassSubjectForm(forms.ModelForm):
    class Meta:
        model = ClassSubject
        fields = ['class_assigned', 'school_subject']

# Form for Grade
class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'class_subject', 'teacher', 'session', 'term', 'ca_score', 'exam_score', 'total_score', 'letter_grade']

# Form for Result
class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'session', 'term', 'average', 'class_position']

# Form for Session
class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['name', 'school']

# Form for Term
class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['name', 'session']

# Form for Permission
class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['teacher', 'class_subject']

# Form for Parent
class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['name', 'email', 'password', 'school']
        widgets = {
            'password': forms.PasswordInput(),  # To render password fields
        }

# Form for ParentStudent
class ParentStudentForm(forms.ModelForm):
    class Meta:
        model = ParentStudent
        fields = ['parent', 'student']
