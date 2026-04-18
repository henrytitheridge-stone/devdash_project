from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class UserProfile(models.Model):
    """
    An extension of the Django User model to store 
    default contact information and order history.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Handles automatic creation/update of a user profile 
    whenever a User object is created or saved.
    """
    if created:
        UserProfile.objects.create(user=instance)

    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
