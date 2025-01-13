from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Event, Participant
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

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


