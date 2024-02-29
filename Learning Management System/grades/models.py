from django.db import models
from django.contrib.auth.models import User, Group


# Create your models here.
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    weight = models.IntegerField(default=100)
    points = models.IntegerField(default=100)
    
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    grader = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='graded_set')
    file = models.FileField()
    score = models.FloatField(blank=True, null=True)
    