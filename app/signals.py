from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import User, School, Student

# Helper function to delete old image
def delete_old_image(instance, field_name):
    try:
        old_instance = type(instance).objects.get(pk=instance.pk)
        old_image = getattr(old_instance, field_name)
        new_image = getattr(instance, field_name)
        if old_image and old_image != new_image:
            old_image.delete(save=False)
    except type(instance).DoesNotExist:
        pass

# Signal to delete old image on update
@receiver(pre_save, sender=User)
@receiver(pre_save, sender=School)
@receiver(pre_save, sender=Student)
def delete_previous_image_on_update(sender, instance, **kwargs):
    if sender == User:
        delete_old_image(instance, 'photo')
    elif sender == School:
        delete_old_image(instance, 'logo')
    elif sender == Student:
        delete_old_image(instance, 'photo')

# Signal to delete image on instance delete
@receiver(post_delete, sender=User)
@receiver(post_delete, sender=School)
@receiver(post_delete, sender=Student)
def delete_image_on_delete(sender, instance, **kwargs):
    if sender == User and instance.photo:
        instance.photo.delete(save=False)
    elif sender == School and instance.logo:
        instance.logo.delete(save=False)
    elif sender == Student and instance.photo:
        instance.photo.delete(save=False)
