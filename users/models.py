import uuid

from django.contrib import admin
from django.contrib.sites.models import Site
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from mysite import settings


class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.email

class UserProfile(models.Model):  # new
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_handler(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()

class Invitation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=True, blank=True, editable=False)
    code = models.UUIDField(
         default = uuid.uuid4,
         editable = False)

    def __str__(self):
        return self.code.hex

    @admin.display(
        boolean=True,
        description="Used?",
    )
    def was_used(self):
        return self.user is not None

    def link(self):
        current_site = Site.objects.get_current()
        return current_site.domain + reverse("invitation", kwargs={'code': self.code})