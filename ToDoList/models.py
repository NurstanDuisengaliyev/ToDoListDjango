from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return self.title


class Task(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    deadline = models.DateTimeField(default=timezone.now().replace(hour=23, minute=59, second=59))
    finished_date = models.DateTimeField(null=True, blank=True)

    category = models.ForeignKey(Category, models.SET_NULL, null=True, blank=True)

    # A Category can have a several tasks, while a task can be in one or zero categories
    # one-to-many relation between them

    def __str__(self):
        return self.title
