from django.shortcuts import render
from django.http import HttpResponse
from .models import Event
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def register_participant(request):
    if request.method == 'POST':
        event_id = request.POST['event_id']
        fio = request.POST['fio']
        university = request.POST['university']
        faculty = request.POST['faculty']
        course = request.POST['course']
        group = request.POST['group']
        gender = request.POST['gender']
        email = request.POST['email']
        phone = request.POST['phone']
        birth_date = request.POST['birth_date']

        # Логика сохранения данных в базу
        print(f"Регистрация на мероприятие {event_id}: {fio}, {email}")

        return redirect('events_list')
def index(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')
def events_list(request):
    events = Event.objects.all()
    return render(request, 'main/events.html', {'events': events})