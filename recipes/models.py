from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, default=None)
    prep_time = models.IntegerField(default=0)
    cook_time = models.IntegerField(default=0)
    serves = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name