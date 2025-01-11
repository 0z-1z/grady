from django.contrib import admin
from .models import (
    User, School, Student, Class, Subject, GradingScheme, SchoolSubject,
    SchoolClassSubject, Grade, Result, ResultToken, Session, Permission,
    ScoringScheme
)

# Registering models in the admin panel
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'school')
    list_filter = ('role', 'school')
    search_fields = ('username', 'email')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'admission_number', 'school', 'session', 'class_assigned', 'gender', 'date_of_birth')
    list_filter = ('school', 'session', 'class_assigned', 'gender')
    search_fields = ('name', 'admission_number')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SchoolSubject)
class SchoolSubjectAdmin(admin.ModelAdmin):
    list_display = ('school', 'subject')
    list_filter = ('school',)


@admin.register(SchoolClassSubject)
class SchoolClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('class_assigned', 'subject', 'school')
    list_filter = ('class_assigned', 'school')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'class_assigned', 'session', 'term', 'total_score', 'letter_grade')
    list_filter = ('session', 'term')
    search_fields = ('student__name',)

@admin.register(GradingScheme)
class GradingSchemeAdmin(admin.ModelAdmin):
    list_display = ('school', 'letter_grade', 'min_score', 'max_score', 'remark')
    list_filter = ('school',)
    
    def save_model(self, request, obj, form, change):
        # Ensure grading ranges for the same school do not overlap
        existing_schemes = GradingScheme.objects.filter(school=obj.school)
        for scheme in existing_schemes:
            if scheme != obj and (
                (obj.min_score >= scheme.min_score and obj.min_score <= scheme.max_score) or
                (obj.max_score >= scheme.min_score and obj.max_score <= scheme.max_score)
            ):
                raise ValueError("Grading ranges for the same school cannot overlap.")
        super().save_model(request, obj, form, change)

# Admin for the ScoringScheme model
@admin.register(ScoringScheme)
class ScoringSchemeAdmin(admin.ModelAdmin):
    list_display = ('school', 'max_ca_score', 'max_exam_score')  # Fields to display in the list view
    search_fields = ('school__name',)  # Enable search by school name
    list_filter = ('school',)  # Add filter options by school


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'term', 'average', 'class_position')
    list_filter = ('school', 'session', 'term')
    

@admin.register(ResultToken)
class ResultTokenAdmin(admin.ModelAdmin):
    list_display = ('result', 'pin', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('pin', 'result__student__name', 'result__session__name', 'result__term')

    @admin.display(boolean=True)
    def is_expired(self, obj):
        return obj.is_expired()



@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'class_assigned', 'school')
    list_filter = ('school',)
