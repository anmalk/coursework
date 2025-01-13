from django.db import models


class Event(models.Model):
    EVENT_TYPES = [
        ('conference', 'Конференция'),
        ('workshop', 'Мастер-класс'),
        ('seminar', 'Семинар'),
        ('webinar', 'Вебинар'),
    ]

    name = models.CharField(max_length=200)
    count = models.IntegerField()
    date = models.DateField()
    place = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Тип мероприятия", default='conference')

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()})"


class Participant(models.Model):
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name="Мероприятие"
    )
    name = models.CharField(max_length=100, verbose_name="Имя участника")
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    def __str__(self):
        return f"{self.name} на {self.event.name}"