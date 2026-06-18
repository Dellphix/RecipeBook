import uuid

from django.db import models
from django.contrib.auth.models import User
from thumbnails.fields import ImageField

from mysite import settings


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=200)
    image = ImageField(upload_to='recipes/',
                       resize_source_to="large",
                       pregenerated_sizes=["small"],
                       null=True,
                       default=None,
                       blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    prep_time = models.IntegerField(default=0)
    cook_time = models.IntegerField(default=0)
    serves = models.IntegerField(default=0)
    source = models.CharField(max_length=200, default='', blank=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True)

    def __str__(self):
        return self.name

    def is_viewable_by(self, user):
        return self.is_public or self.user_id == user.id

    def save(self, *args, **kwargs):
        if self.id:
            old = Recipe.objects.get(id=self.id)
            print(old)
            if old.image and self.image and self.image.url != old.image.url:
                old.image.delete()
        super().save(*args, **kwargs)

    def delete(self, using = None, keep_parents = False):
        if self.image:
            self.image.delete()
        super().delete(using, keep_parents)