from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Event, Participant
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, F
import json
import csv

from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Event, Participant

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
def index(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')
def events_list(request):
    events = Event.objects.all()
    return render(request, 'main/events.html', {'events': events})


def event_statistics(request, event_id):
    # Get the event by ID or return a 404 if it doesn't exist
    event = get_object_or_404(Event, id=event_id)

    # Total number of participants
    total_participants = Participant.objects.filter(event=event).count()

    # Gender distribution
    gender_distribution = Participant.objects.filter(event=event).values('gender').annotate(count=Count('gender'))

    # Average age of participants
    participants = Participant.objects.filter(event=event)
    total_age = sum((2025 - int(participant.birth_date.year)) for participant in participants)
    average_age = total_age / len(participants) if participants else 0

    # Distribution by university
    university_distribution = Participant.objects.filter(event=event).values('university').annotate(count=Count('university'))

    # Distribution by faculty
    faculty_distribution = Participant.objects.filter(event=event).values('faculty').annotate(count=Count('faculty'))

    # Distribution by course
    course_distribution = Participant.objects.filter(event=event).values('course').annotate(count=Count('course'))

    # Distribution by group
    group_distribution = Participant.objects.filter(event=event).values('group').annotate(count=Count('group'))

    # Prepare the statistics as a dictionary
    statistics = {
        'total_participants': total_participants,
        'gender_distribution': list(gender_distribution),
        'average_age': average_age,
        'university_distribution': list(university_distribution),
        'faculty_distribution': list(faculty_distribution),
        'course_distribution': list(course_distribution),
        'group_distribution': list(group_distribution)
    }

    # Return the statistics in JSON format
    return JsonResponse(statistics)
def get_event_statistics(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        total_participants = event.current_participants
        available_places = event.max_participants - total_participants
        fill_percentage = (total_participants / event.max_participants) * 100 if event.max_participants else 0

        # Returning the statistics as JSON
        return JsonResponse({
            'status': 'success',
            'total_participants': total_participants,
            'available_places': available_places,
            'fill_percentage': fill_percentage
        })
    except Event.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Event not found'}, status=404)

def export_participants_json(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    participants = Participant.objects.filter(event=event)
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
            'birth_date': str(p.birth_date),  # Преобразование даты в строку
        }
        for p in participants
    ]
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})  # Добавил ensure_ascii

def export_participants_csv(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    participants = Participant.objects.filter(event=event)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="participants_{event.id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ФИО', 'Университет', 'Факультет', 'Курс', 'Группа', 'Пол', 'Email', 'Телефон', 'Дата рождения'])  # Заголовки

    for participant in participants:
        writer.writerow([
            participant.full_name,
            participant.university,
            participant.faculty,
            participant.course,
            participant.group,
            participant.gender,
            participant.email,
            participant.phone,
            participant.birth_date,
        ])
    return response