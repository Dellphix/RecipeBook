import uuid

from django.contrib import admin
from django.contrib.sites.models import Site
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Invitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True, editable=False)
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