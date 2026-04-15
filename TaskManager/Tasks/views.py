from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from .models import Profile
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .forms import TaskForm
from django.http import HttpResponse
from datetime import date, timedelta
from django.utils import timezone
# READ
from datetime import date, timedelta

from django.utils import timezone
from datetime import date, timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
@login_required
def task_list(request):

    query = request.GET.get('q', '')

    tasks = Task.objects.filter(user=request.user)

    if query:
        tasks = tasks.filter(title__icontains=query)

    # 📅 DATE GROUPING
    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_tasks = tasks.filter(deadline__date=today)
    tomorrow_tasks = tasks.filter(deadline__date=tomorrow)
    later_tasks = tasks.exclude(deadline__date__in=[today, tomorrow])

    # ⏰ NOW TIME
    now = timezone.now()
    soon = now + timedelta(hours=1)

    # 🔴 OVERDUE TASKS
    overdue_tasks = tasks.filter(
        completed=False,
        deadline__lt=now
    )

    # ⚡ DUE IN 1 HOUR
    urgent_tasks = tasks.filter(
        completed=False,
        deadline__lte=soon,
        deadline__gte=now
    )

    # 🔥 AUTO RESCHEDULE HIGH PRIORITY (SAFE)
    for task in overdue_tasks:
        if task.priority == 'high':
            if task.deadline and task.deadline.date() < today:
                task.deadline = task.deadline + timedelta(days=1)
                task.save()

    return render(request, 'Tasks/task_list.html', {
        'today_tasks': today_tasks,
        'tomorrow_tasks': tomorrow_tasks,
        'later_tasks': later_tasks,
        'overdue_tasks': overdue_tasks,
        'urgent_tasks': urgent_tasks,
        'query': query
    })
@login_required
def reschedule_task(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)

    task.deadline = task.deadline + timedelta(days=1)
    task.save()

    return redirect('task_list')

# CREATE

@login_required
def task_create(request):
    form = TaskForm(request.POST or None)

    if form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()

        return redirect('task_list')

    return render(request, 'Tasks/task_form.html', {
        'form': form
    })

# UPDATE
@login_required
def task_update(request, pk):

    task = get_object_or_404(Task, id=pk, user=request.user)

    form = TaskForm(request.POST or None, instance=task)

    if form.is_valid():
        form.save()
        return redirect('task_list')

    return render(request, 'Tasks/task_form.html', {
        'form': form,
        'task': task
    })
# DELETE
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'Tasks/task_confirm_delete.html', {'task': task})

login_required
def profile(request):
    profile = request.user.profile
    user = request.user

    if request.method == "POST":
        # 👤 User fields
        user.email = request.POST.get("email")

        # 🧾 Profile fields
        profile.full_name = request.POST.get("full_name")
        profile.bio = request.POST.get("bio")

        # 🖼 Avatar
        if request.FILES.get("avatar"):
            profile.avatar = request.FILES["avatar"]

        user.save()
        profile.save()

        return redirect("profile")

    return render(request, "Tasks/profile.html", {
        "profile": profile
    })

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")
        full_name = request.POST.get("full_name")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            password=password1,
            email=email
        )

        # Save profile info
        profile = user.profile
        profile.full_name = full_name
        profile.save()

        return redirect("login")

    return render(request, "Tasks/signup.html")

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)

    return render(request, 'Tasks/task_detail.html', {
        'task': task
    })
    
def send_ws_notification(title, message):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "send_notification",
            "data": {
                "title": title,
                "message": message
            }
        }
    )

def test_notification(request):

    channel_layer = get_channel_layer()

    if channel_layer is None:
        return HttpResponse("Channel layer not configured ❌")

    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "send_notification",
            "data": {
                "title": "Test",
                "message": "Notification system working!"
            }
        }
    )

    return HttpResponse("Notification sent ✅")


def google_verify(request):
    return HttpResponse("google-site-verification: google1234567890abcdef.html")