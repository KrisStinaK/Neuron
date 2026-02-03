from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Course, Lesson, Enrollment

@login_required
def course_list(request):
    courses = Course.objects.filter(is_active=True)
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Проверка записей пользователя
    user_enrollments = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'user_enrollments': user_enrollments,
        'query': query,
    })

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    lessons = course.lessons.filter(is_published=True)

    # Проверка записи
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

    if request.method == 'POST':
        if not enrollment:
            Enrollment.objects.create(user=request.user, course=course)
            messages.success(request, 'Вы успешно записались на курс!')
        return redirect('course_detail', pk=pk)

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'enrollment': enrollment,
    })

@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course, is_published=True)

    # Проверка записи на курс
    enrollment = Enrollment.objects.filter(
        user=request.user, 
        course=course
    ).first()

    if not enrollment:
        messages.error(request, 'Сначала запишитесь на курс!')
        return redirect('course_detail', pk=course_id)

    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'enrollment': enrollment,
    })
