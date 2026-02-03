from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ChatRoom, ChatMessage
from courses.models import Course

@login_required
def chat_rooms(request):
    course_id = request.GET.get('course_id')
    rooms = ChatRoom.objects.all()

    if course_id:
        course = get_object_or_404(Course, pk=course_id)
        rooms = rooms.filter(course=course)

    return render(request, 'chat/rooms.html', {'rooms': rooms})

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, pk=room_id)
    messages = room.messages.all()[:50]  # Последние 50 сообщений

    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages,
    })

@require_http_methods(["POST"])
@login_required
def send_message(request, room_id):
    room = get_object_or_404(ChatRoom, pk=room_id)
    content = request.POST.get('content')

    if content:
        message = ChatMessage.objects.create(
            room=room,
            user=request.user,
            content=content.strip()
        )

        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'user': message.user.username,
                'timestamp': message.timestamp.isoformat(),
                'avatar': message.user.avatar.url if message.user.avatar else ''
            }
        })

    return JsonResponse({'success': False, 'error': 'Пустое сообщение'})