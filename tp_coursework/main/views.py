import os
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, F
import json
import csv
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Event, Participant
from abc import ABC, abstractmethod


@csrf_exempt
def register_participant(request):
    if request.method == 'POST':
        event_id = request.POST['event_id']
        full_name = request.POST['fio']
        university = request.POST['university']
        faculty = request.POST['faculty']
        course = request.POST['course']
        group = request.POST['group']
        gender = request.POST['gender']
        email = request.POST['email']
        phone = request.POST['phone']
        birth_date = request.POST['birth_date']

        # Получаем мероприятие из базы
        event = get_object_or_404(Event, id=event_id)

        # Проверяем доступность мест
        if event.current_participants < event.max_participants:
            # Увеличиваем количество участников
            event.current_participants += 1
            event.save()

            # Сохраняем участника в базе
            Participant.objects.create(
                event=event,
                full_name=full_name,
                university=university,
                faculty=faculty,
                course=course,
                group=group,
                gender=gender,
                email=email,
                phone=phone,
                birth_date=birth_date
            )
            print(f"Регистрация на мероприятие {event_id}: {full_name}, {email}")
            return JsonResponse({'status': 'success', 'message': 'Вы успешно зарегистрировались на мероприятие.'})
        else:
            # Мест больше нет
            return JsonResponse({'status': 'error', 'message': 'К сожалению, мест на мероприятие больше нет.'})

    return JsonResponse({'status': 'error', 'message': 'Некорректный запрос.'})

def participants_list(request, event_id):
    participants = Participant.objects.filter(event_id=event_id)  # Получаем участников для конкретного мероприятия
    return render(request, 'participants_list.html', {'participants': participants})

def get_participants(request, event_id):
    try:
        participants = Participant.objects.filter(event_id=event_id)
        participant_data = [
            {
                'full_name': participant.full_name,
                'university': participant.university,
                'faculty': participant.faculty,
                'course': participant.course,
                'group': participant.group,
                'gender': participant.gender,
                'email': participant.email,
                'phone': participant.phone,
                'birth_date': participant.birth_date,
            }
            for participant in participants
        ]
        return JsonResponse({'status': 'success', 'participants': participant_data})
    except Participant.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Нет участников'})

def events_list(request):
    events = Event.objects.all()

    return render(request, 'main/events.html', {'events': events})

# Интерфейс калькулятора статистики
class StatisticCalculator(ABC):
    @abstractmethod
    def calculate(self, participants):
        pass

# Конкретные калькуляторы
class TotalParticipantsCalculator(StatisticCalculator):
    def calculate(self, participants):
        return participants.count()

class AverageAgeCalculator(StatisticCalculator):
    def calculate(self, participants):
        if not participants:  # Проверка на пустой QuerySet
            return 0
        total_age = sum((2025 - int(participant.birth_date.year)) for participant in participants)
        return total_age / len(participants)

class GenderDistributionCalculator(StatisticCalculator):
    def calculate(self, participants):
        return list(participants.values('gender').annotate(count=Count('gender')))

class UniversityDistributionCalculator(StatisticCalculator):
    def calculate(self, participants):
        return list(participants.values('university').annotate(count=Count('university')))

class FacultyDistributionCalculator(StatisticCalculator):
    def calculate(self, participants):
        return list(participants.values('faculty').annotate(count=Count('faculty')))

class CourseDistributionCalculator(StatisticCalculator):
    def calculate(self, participants):
        return list(participants.values('course').annotate(count=Count('course')))

class GroupDistributionCalculator(StatisticCalculator):
    def calculate(self, participants):
        return list(participants.values('group').annotate(count=Count('group')))

class MinAgeCalculator(StatisticCalculator):
    def calculate(self, participants):
        if not participants:
            return 0
        min_age = min(2025 - int(participant.birth_date.year) for participant in participants)
        return min_age

class MaxAgeCalculator(StatisticCalculator):
    def calculate(self, participants):
        if not participants:
            return 0
        max_age = max(2025 - int(participant.birth_date.year) for participant in participants)
        return max_age

# Фабрика калькуляторов
def create_statistic_calculator(statistic_type):
    calculators = {
        'total_participants': TotalParticipantsCalculator,
        'average_age': AverageAgeCalculator,
        'gender_distribution': GenderDistributionCalculator,
        'university_distribution': UniversityDistributionCalculator,
        'faculty_distribution': FacultyDistributionCalculator,
        'course_distribution': CourseDistributionCalculator,
        'group_distribution': GroupDistributionCalculator,
        'min_age': MinAgeCalculator,
        'max_age': MaxAgeCalculator,
    }
    calculator_class = calculators.get(statistic_type)
    if calculator_class:
        return calculator_class()
    else:
        raise ValueError(f"Неизвестный тип статистики: {statistic_type}")

# Представление Django
def event_statistics(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participants = Participant.objects.filter(event=event)
    statistics_to_calculate = request.GET.getlist('stats')

    statistics = {}

    if not statistics_to_calculate:
        statistics_to_calculate = [
            'total_participants', 'average_age', 'min_age', 'max_age', 'gender_distribution',
            'university_distribution', 'faculty_distribution',
            'course_distribution', 'group_distribution'
        ]

    for stat_type in statistics_to_calculate:
        try:
            calculator = create_statistic_calculator(stat_type)
            statistics[stat_type] = calculator.calculate(participants)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except ZeroDivisionError: # Обработка деления на ноль
            statistics[stat_type] = 0 # или другое значение по умолчанию

    return JsonResponse(statistics)


# Стратегия форматирования даты
class DateFormatStrategy(ABC):
    @abstractmethod
    def format_date(self, date):
        pass

class IsoFormatStrategy(DateFormatStrategy):
    def format_date(self, date):
        return str(date)

class RusFormatStrategy(DateFormatStrategy):
    def format_date(self, date):
        return date.strftime("%d.%m.%Y")

# Интерфейс экспортера
class Exporter(ABC):
    def __init__(self, date_format_strategy):
        self.date_format_strategy = date_format_strategy

    @abstractmethod
    def export(self, participants, file_path):
        pass

# Конкретные экспортеры
class JsonExporter(Exporter):
    def export(self, participants, file_path):
        data = [
            {
                'full_name': p.full_name,
                'university': p.university,
                'faculty': p.faculty,
                'course': p.course,
                'group': p.group,
                'gender': p.gender,
                'email': p.email,
                'phone': p.phone,
                'birth_date': self.date_format_strategy.format_date(p.birth_date),
            }
            for p in participants
        ]
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)

class CsvExporter(Exporter):
    def export(self, participants, file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ФИО', 'Университет', 'Факультет', 'Курс', 'Группа', 'Пол', 'Email', 'Телефон', 'Дата рождения'])
            for participant in participants:
                writer.writerow([
                    participant.full_name, participant.university, participant.faculty, participant.course,
                    participant.group, participant.gender, participant.email, participant.phone,
                    self.date_format_strategy.format_date(participant.birth_date),
                ])

# Фабрика экспортеров
def create_exporter(export_format, date_format):
    date_strategy = IsoFormatStrategy() if date_format == 'iso' else RusFormatStrategy()
    if export_format == 'json':
        return JsonExporter(date_strategy)
    elif export_format == 'csv':
        return CsvExporter(date_strategy)
    else:
        raise ValueError("Неподдерживаемый формат экспорта")

# Представление Django
def export_participants(request, event_id, export_format):
    event = get_object_or_404(Event, pk=event_id)
    participants = Participant.objects.filter(event=event)

    try:
        exporter = create_exporter(export_format, request.GET.get('date_format', 'iso')) # Получаем формат даты из GET-параметра
        file_path = os.path.join('exported_data', f'participants_{event_id}.{export_format}')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        exporter.export(participants, file_path)

        if export_format == 'csv':
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="participants_{event_id}.csv"'
                return response
        else:
            return JsonResponse({
                'status': 'success',
                'message': f'Данные экспортированы в {file_path}',
                'file_path': file_path,
            })

    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400) # Обработка ошибок
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Произошла ошибка при экспорте'}, status=500)