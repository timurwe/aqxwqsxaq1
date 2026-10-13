from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Предмет")

    def __str__(self):
        return self.name

class Grade(models.Model):
    number = models.PositiveBigIntegerField(verbose_name="Класс")

    def __str__(self):
        return f"{self.number} класс"

class Textbook(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Класс")
    title = models.CharField(max_length=200, verbose_name="Название учебника") 
    author = models.CharField(max_length=100, verbose_name="Автор")

    def __str__(self):
        return f"{self.title} ({self.author}) - {self.grade}"

class Task(models.Model):
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, verbose_name="Учебник")
    number = models.CharField(max_length=50, verbose_name="Номер задания") 
    solution_text = models.TextField(blank=True, null=True, verbose_name="Текст решения")
    solution_image = models.ImageField(upload_to='solutions/', blank=True, null=True, verbose_name="Фото решения")

    def __str__(self):
        return f"Задание №{self.number} ({self.textbook})"