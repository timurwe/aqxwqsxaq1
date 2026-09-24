from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100)

class Grade(models.Model):
    number = models.PositiveBigIntegerField()

class Textbook(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    title = models.CharField(max_length=200) 
    author = models.CharField(max_length=100)

class Task(models.Model):
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE)
    number = models.CharField(max_length=50) 
    solution_text = models.TextField(blank=True, null=True)
    solution_image = models.ImageField(upload_to='solutions/', blank=True, null=True)
