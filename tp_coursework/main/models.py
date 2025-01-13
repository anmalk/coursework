from django.db import models
import datetime


class Event(models.Model):
    EVENT_TYPES = [
        ('conference', 'Конференция'),
        ('workshop', 'Мастер-класс'),
        ('seminar', 'Семинар'),
        ('webinar', 'Вебинар'),
    ]

    name = models.CharField(max_length=200)
    max_participants = models.IntegerField(default=300, verbose_name="Максимальное количество участников")
    current_participants = models.IntegerField(default=0, verbose_name="Количество записавшихся участников")
    date = models.DateField()
    place = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Тип мероприятия", default='conference')

    def __str__(self):
        return self.name

    def can_register(self):
        return self.current_participants < self.max_participants

    def register_participant(self):
        if self.can_register():
            self.current_participants += 1
            self.save()
            return True
        return False

class Participant(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='participants')
    full_name = models.CharField(max_length=200, default='Не указано')  # Значение по умолчанию
    university = models.CharField(max_length=200, default='Не указано')  # Значение по умолчанию
    faculty = models.CharField(max_length=200, default='Не указано')  # Значение по умолчанию
    course = models.CharField(max_length=20, default='Не указано')  # Значение по умолчанию
    group = models.CharField(max_length=50, default='Не указано')  # Значение по умолчанию
    gender = models.CharField(max_length=10, default='Не указано')  # Значение по умолчанию
    email = models.EmailField(default='example@example.com')  # Значение по умолчанию
    phone = models.CharField(max_length=20, default='Не указано')  # Значение по умолчанию
    birth_date = models.DateField(default=datetime.date.today)  # Значение по умолчанию

    def __str__(self):
        return self.full_name