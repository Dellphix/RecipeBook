import uuid

from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images/', null=True, default=None, blank=True)
    tags = models.ManyToManyField(Tag)
    prep_time = models.IntegerField(default=0)
    cook_time = models.IntegerField(default=0)
    serves = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True)

    def __str__(self):
        return self.name

    def is_viewable_by(self, user):
        return self.is_public or self.user_id == user.id