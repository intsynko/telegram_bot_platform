from django.db import models

# Create your models here.

class Form(models.Model):
    name = models.CharField(max_length=255)
    final_message = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class FormField(models.Model):
    FIELD_TYPES = [
        ('string', 'Строка'),
        ('int', 'Число'),
        ('decimal', 'Дробное число'),
        ('date', 'Дата'),
        ('time', 'Время'),
        ('datetime', 'Дата и Время'),
        ('bool', 'Галочка'),
        ('list', 'Список'),
        ('phone', 'Телефон'),
        ('email', 'Почта'),
        ('file', 'Файл'),
        ('link', 'Ссылка'),
    ]
    form = models.ForeignKey(Form, related_name='fields', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    hidden = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    default_value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()})"

class FieldValidation(models.Model):
    VALIDATION_TYPES = [
        ('min', 'Minimum'),
        ('max', 'Maximum'),
        ('list', 'List'),
    ]
    field = models.ForeignKey(FormField, related_name='validations', on_delete=models.CASCADE)
    validation_type = models.CharField(max_length=20, choices=VALIDATION_TYPES)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.get_validation_type_display()})"
