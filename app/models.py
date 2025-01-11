from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from .managers import GradeManager

import os
from datetime import datetime

def image_path_generator(foldername):
    def image_path(instance, filename):
        # Extract the file extension
        ext = filename.split('.')[-1]
        # Create a new filename with username and current date
        new_filename = f"{getattr(instance, 'name', instance.username)}_{datetime.now().strftime('%Y%m%d')}.{ext}"

        # Define the folder to save the file (e.g., 'user_images/')
        return os.path.join(foldername, new_filename)
    return image_path


# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    ]
    photo = models.ImageField(upload_to=image_path_generator('user_photos/'), blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='users', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # New instance
            if not self.has_usable_password():  # Check if the password is already hashed
                self.set_password(self.password)
        else:  # Existing instance, check if password has changed
            old_user = User.objects.get(pk=self.pk)
            if old_user.password != self.password:
                self.set_password(self.password)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username  

# School Model
class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    logo = models.ImageField(upload_to=image_path_generator('school_logos/'), blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    motto = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    mobile_alt = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return self.name  

# Student Model
class Student(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=50, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='students')
    class_assigned = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, related_name='students')
    photo = models.ImageField(upload_to=image_path_generator('student_photos/'), blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.name} : {self.class_assigned}"

# Class Model
class Class(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    abbr = models.CharField(max_length=5, null=True, blank=True)
  
    def __str__(self):
        return self.name

# Subject Model (Shared across schools)
class Subject(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    abbr = models.CharField(max_length=5, null=True, blank=True)
    
    def __str__(self):
        return self.name  

# SchoolSubject Model (Linking Subject to School)
class SchoolSubject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='school_subjects')
    
    def __str__(self):
      return f"{self.subject} : {self.school}"

# ClassSubject Model (Linking SchoolSubject to Class)
class SchoolClassSubject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='school_class_subjects')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='school_class_subjects')
    
    def __str__(self):
      return f"{self.subject} : {self.class_assigned} : {self.school}"

# Grade Model
class Grade(models.Model):
    TERM_CHOICES = [
      ('First Term', 'First Term'),
      ('Second Term', 'Second Term'),
      ('Third Term', 'Third Term')
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='grades')
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='grades')
    term = models.CharField(max_length=11, choices=TERM_CHOICES)
    result = models.ForeignKey('Result', on_delete=models.CASCADE, related_name='grades')
    ca_score = models.FloatField(null=True, blank=True)
    exam_score = models.FloatField(null=True, blank=True)
    letter_grade = models.CharField(max_length=2, null=True, blank=True)
    position = models.CharField(max_length=10, null=True, blank=True)
    remark = models.CharField(max_length=11, null=True, blank=True)
    
    objects = models.Manager() # For all grades
    filtered = GradeManager() # For non-null grades
    
    @property
    def total_score(self):
      try:
        return self.ca_score + self.exam_score
      except TypeError:
        return self.ca_score if self.ca_score is not None else self.exam_score
    
    def __str__(self):
      return f"Grade {self.student} : {self.subject} : {self.session} : {self.term}"

class GradingScheme(models.Model):
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='grading_schemes')
    min_score = models.FloatField()
    max_score = models.FloatField()
    letter_grade = models.CharField(max_length=2)
    remark = models.CharField(max_length=50)

    class Meta:
        unique_together = ('school', 'min_score', 'max_score')

    def __str__(self):
        return f"Grading Scheme: {self.school} : {self.letter_grade} ({self.min_score}-{self.max_score})"


class ScoringScheme(models.Model):
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='scoring_scheme')
    max_ca_score = models.IntegerField()  # Maximum score for Continuous Assessment
    max_exam_score = models.IntegerField()  # Maximum score for exam_score
    
    

# Result Model
class Result(models.Model):
    TERM_CHOICES = [
      ('First Term', 'First Term'),
      ('Second Term', 'Second Term'),
      ('Third Term', 'Third Term')
    ]
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='results')
    term = models.CharField(max_length=11, choices=TERM_CHOICES)
    average = models.FloatField(null=True, blank=True)
    class_position = models.CharField(max_length=10, null=True, blank=True)
    
    @property
    def total_score(self):
        """Calculate the total score of all grades related to this result."""
        total = self.grades.aggregate(total=models.Sum('ca_score') + models.Sum('exam_score'))['total']
        return total or 0  # Return 0 if no grades exist or scores are null

    @property
    def average_score(self):
        """Calculate the average score of all grades related to this result."""
        grades_count = self.grades.filter(Q(ca_score__isnull=False) | Q(exam_score__isnull=False)).count()
        if grades_count == 0:  # Avoid division by zero
            return 0
        return self.total_score / grades_count
    
    def __str__(self):
      return f'Result : {self.student} : {self.session} : {self.term} : {self.school}'


class ResultToken(models.Model):
    pin = models.CharField(max_length=255, unique=True)  # A unique key to identify the token
    result = models.ForeignKey('Result', on_delete=models.CASCADE, related_name='tokens')
    created_at = models.DateTimeField(auto_now_add=True)  # To track when the token was created
    expires_at = models.DateTimeField(null=True, blank=True)  # Optional expiration time

    def __str__(self):
        return f"Token for {self.result.student.name} - {self.result.term}, {self.result.session.name}"

    def is_expired(self):
        """
        Check if the token has expired.
        """
        from django.utils.timezone import now
        return self.expires_at and now() > self.expires_at


# Session Model
class Session(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    
    def __str__(self):
        return self.name

# Permission Model
class Permission(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions', limit_choices_to={'role': 'teacher'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='permissions')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='permissions')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='permissions')
    
    def __str__(self):
      return f'{self.school}-{self.class_assigned}-{self.subject}'
