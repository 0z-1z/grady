from django.db import models

class GradeManager(models.Manager):
  
  # Only return grade for students with non-null values
    def get_queryset(self):
        return super().get_queryset().filter(ca_score__isnull=False, exam_score__isnull=False)
