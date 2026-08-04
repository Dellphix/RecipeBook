import uuid

from django.db import models
from django_summernote.fields import SummernoteTextField
from thumbnails.fields import ImageField
from django.utils.translation import gettext_lazy

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
    method = SummernoteTextField(null=True)
    is_public = models.BooleanField(default=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True)

    def __str__(self):
        return self.name

    def is_viewable_by(self, user):
        return self.is_public or self.user_id == user.id

    def ingredients(self):
        return self.ingredient_set.all()

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

class Unit(models.TextChoices):
    NONE = "none", gettext_lazy("")
    KILOGRAM = "kg", gettext_lazy("kg")
    GRAM = "g", gettext_lazy("g")
    LITRE = "l", gettext_lazy("l")
    MILLILITRE = "ml", gettext_lazy("ml")
    CUP = "cup", gettext_lazy("cup")
    TABLESPOON = "tbsp", gettext_lazy("tbsp")
    TEASPOON = "tsp", gettext_lazy("tsp")
    OUNCE = "oz", gettext_lazy("oz")
    POUND = "lb", gettext_lazy("lb")

class Ingredient(models.Model):
    quantity = models.DecimalField(decimal_places=2, max_digits=100)
    unit = models.CharField(max_length=5,
        choices=Unit,
        default=Unit.NONE)
    description = models.CharField(max_length=200)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.description
