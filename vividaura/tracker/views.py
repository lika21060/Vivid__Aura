
import base64
import datetime
import urllib.parse
from calendar import monthrange
from datetime import timedelta
from urllib.parse import urlparse


import requests


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import (
    
    JournalEntryForm,
    MoodEntryForm,
    RegisterForm,
    StudyGoalForm,
)
from .models import Drawing, JournalEntry, MoodEntry, StudyGoal
from .utils import search_youtube_videos

@login_required
def monthly_mood_summary(request):
    streak = calculate_mood_streak(request.user)
    today = timezone.now().date()
    current_year = today.year
    current_month = today.month
    month_name = today.strftime('%B')

    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(current_year, current_month)[1])

 
    entries = MoodEntry.objects.filter(
        user=request.user,
        date__range=(first_day, last_day)
    )

    mood_data = {entry.date: (entry.mood, entry.focus, entry.energy) for entry in entries}

    full_month = []
    for day in range(1, last_day.day + 1):
        date = first_day.replace(day=day)
        if date in mood_data:
            mood, focus, energy = mood_data[date]
        else:
            mood, focus, energy = "Not logged", "-", "-"
        full_month.append({
            'date': date.strftime('%B %d'),
            'mood': mood,
            'focus': focus,
            'energy': energy,
        })

    return render(request, 'monthly_summary.html', {
        'full_month': full_month,
        'month_name': month_name,
        'year': current_year,
        'mood_streak': streak,
    })



@login_required
def spotify_login(request):
    client_id = settings.SPOTIFY_CLIENT_ID
    redirect_uri = settings.SPOTIFY_REDIRECT_URI
    scope = "user-read-playback-state user-modify-playback-state streaming"

    auth_url = (
        "https://accounts.spotify.com/authorize?"
        + urllib.parse.urlencode({
            "response_type": "code",
            "client_id": client_id,
            "scope": scope,
            "redirect_uri": redirect_uri,
            "show_dialog": "true",
        })
    )
    return redirect(auth_url)

@login_required
def spotify_callback(request):
    code = request.GET.get('code')
    if not code:
        return render(request, 'error.html', {'error': 'Authorization failed or denied.'})

    token_url = 'https://accounts.spotify.com/api/token'
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = 'YOUR_SPOTIFY_CLIENT_SECRET'  
    redirect_uri = settings.SPOTIFY_REDIRECT_URI

    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }

    r = requests.post(token_url, data=data, headers=headers)
    if r.status_code != 200:
        return render(request, 'error.html', {'error': 'Failed to get access token.'})

    token_info = r.json()
    access_token = token_info['access_token']
    refresh_token = token_info.get('refresh_token')


    request.session['spotify_access_token'] = access_token
    request.session['spotify_refresh_token'] = refresh_token

    return redirect('drawing')



@login_required
def drawing(request):
    if request.method == 'POST':
        image_base64 = request.POST.get('image_base64')
        if image_base64:
            drawing = Drawing(user=request.user, image_base64=image_base64)
            drawing.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No image data received.'})

    spotify_url = request.GET.get('spotify_url', '')
    spotify_path = ''
    if spotify_url:
        try:
            parsed = urlparse(spotify_url)
            spotify_path = parsed.path
        except Exception:
            spotify_path = ''

    videos = []
    query = request.GET.get('query')
    if query:
        videos = search_youtube_videos(query, settings.YOUTUBE_API_KEY)

    drawings = Drawing.objects.filter(user=request.user).order_by('-created_at')
    streak = calculate_mood_streak(request.user)

    return render(request, 'drawing.html', {
        'drawings': drawings,
        'spotify_url': spotify_url,
        'spotify_path': spotify_path,
        'videos': videos,
        'query': query or '',
        'mood_streak': streak,
    })
# Home page
def home(request):
    quote = get_quote_of_the_day()
    streak = calculate_mood_streak(request.user)
    return render(request, 'home.html', {
        'quote_of_the_day': quote,
        'mood_streak': streak,
    })


@login_required
def study_goals(request):
    streak = calculate_mood_streak(request.user)

    if request.method == 'POST':
        if 'mark_completed' in request.POST:
            goal_id = request.POST['mark_completed']
            goal = get_object_or_404(StudyGoal, id=goal_id, user=request.user)
            goal.completed = True
            if not goal.completed_on:
                goal.completed_on = timezone.now().date()
            goal.save()
            messages.success(request, 'Goal marked as completed!')
            return redirect('study_goals')

        elif 'delete_goal' in request.POST:
            goal_id = request.POST['delete_goal']
            goal = get_object_or_404(StudyGoal, id=goal_id, user=request.user)
            goal.delete()
            messages.success(request, 'Goal deleted successfully.')
            return redirect('study_goals')

        elif 'edit_goal_id' in request.POST:
            goal_id = request.POST['edit_goal_id']
            goal = get_object_or_404(StudyGoal, id=goal_id, user=request.user)
            form = StudyGoalForm(request.POST, instance=goal)
            if form.is_valid():
                updated_goal = form.save(commit=False)
                if updated_goal.completed and not updated_goal.completed_on:
                    updated_goal.completed_on = timezone.now().date()
                updated_goal.save()
                messages.success(request, 'Goal updated.')
                return redirect('study_goals')
            else:
            
                current_goals = StudyGoal.objects.filter(user=request.user, completed=False)
                completed_goals = StudyGoal.objects.filter(user=request.user, completed=True)
                new_form = StudyGoalForm()
                return render(request, 'study_goals.html', {
                    'form': new_form,
                    'current_goals': current_goals,
                    'completed_goals': completed_goals,
                    'mood_streak': streak,
                    'edit_form': form,
                    'edit_goal_id': goal_id,
                })

    
        else:
            form = StudyGoalForm(request.POST)
            if form.is_valid():
                study_goal = form.save(commit=False)
                study_goal.user = request.user
                if study_goal.completed and not study_goal.completed_on:
                    study_goal.completed_on = timezone.now().date()
                study_goal.save()
                messages.success(request, 'Your goal was added successfully!')
                return redirect('study_goals')
            else:
                current_goals = StudyGoal.objects.filter(user=request.user, completed=False)
                completed_goals = StudyGoal.objects.filter(user=request.user, completed=True)
                return render(request, 'study_goals.html', {
                    'form': form,
                    'current_goals': current_goals,
                    'completed_goals': completed_goals,
                    'mood_streak': streak,
                })
    else:
        form = StudyGoalForm()
        current_goals = StudyGoal.objects.filter(user=request.user, completed=False)
        completed_goals = StudyGoal.objects.filter(user=request.user, completed=True)
        return render(request, 'study_goals.html', {
            'form': form,
            'current_goals': current_goals,
            'completed_goals': completed_goals,
            'mood_streak': streak,
        })


@login_required
def journal_page(request):
    streak = calculate_mood_streak(request.user)

    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            journal_entry = form.save(commit=False)
            journal_entry.user = request.user
            journal_entry.save()
            messages.success(request, "Your journal entry was saved!")
            return redirect('journal')
    else:
        form = JournalEntryForm()

    entries = JournalEntry.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'journal.html', {'form': form, 'entries': entries, 'mood_streak': streak})


@login_required
def mood_tracker(request):
    message = None
    streak = calculate_mood_streak(request.user)

    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            mood_entry = form.save(commit=False)
            mood_entry.user = request.user
            mood_entry.save()
            message = get_motivational_message(mood_entry.mood, mood_entry.focus)
            form = MoodEntryForm()
            streak = calculate_mood_streak(request.user)
    else:
        form = MoodEntryForm()

    moods = MoodEntry.objects.filter(user=request.user).order_by('-date')
    return render(request, 'mood_tracker.html', {
        'form': form,
        'moods': moods,
        'message': message,
        'mood_streak': streak,
    })


def get_motivational_message(mood, focus):
    if mood in ['sad', 'anxious']:
        return "Take breaks, not breakdowns 💙"
    elif mood == 'happy' and focus >= 8:
        return "You're on fire 🔥"
    elif focus <= 3:
        return "Stay calm and breathe. You've got this 🌱"
    else:
        return "Keep going, you're doing great ✨"


def get_quote_of_the_day():
    QUOTES = [
        "Believe in yourself and all that you are. 💪✨",
        "Your potential is endless. Keep going, you're doing great! 🌟🌈",
        "The only way to do great work is to love what you do. 💖🙌",
        "Don’t stop when you’re tired. Stop when you’re done! 🏃‍♀️💥",
        "Small steps every day add up to big results. 🌱🌼",
        "Every day is a new opportunity to grow. 🌻📈",
        "Stay positive, work hard, and make it happen. 💫💪",
        "You are stronger than you think. 🌟💪 Keep pushing forward!",
        "Dream big, work hard, stay focused, and surround yourself with good vibes. 💖🌟",
        "The best way to predict the future is to create it. 🖌️🌠",
        "Progress, not perfection. 🌟✨",
        "Keep going, you're closer than you think. 💪🌸",
        "You’ve got this! Your strength is bigger than any challenge. 💖💫",
        "Don’t wait for the perfect moment, create it. 🎨🌈",
        "Success is the sum of small efforts, repeated day in and day out. 🏆💪",
        "Let your dreams be your wings. 🕊️💭",
        "Believe you can and you’re halfway there. 💪🌻",
        "Good things take time, be patient with yourself. ⏳💖",
        "Make today amazing. 🌞✨ You're the author of your own story!",
    ]
    index = datetime.date.today().toordinal() % len(QUOTES)
    return QUOTES[index]


def calculate_mood_streak(user):
    if not user.is_authenticated:
        return 0

    entries = MoodEntry.objects.filter(user=user).order_by('-date')
    if not entries.exists():
        return 0

    streak = 1
    today = timezone.now().date()
    prev_date = today

    for entry in entries:
        if entry.date == prev_date or entry.date == prev_date - timedelta(days=1):
            if entry.date == prev_date - timedelta(days=1):
                streak += 1
            prev_date = entry.date
        else:
            break

    return streak


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in.')
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def youtube_search(request):
    query = request.GET.get('query', '').strip()
    videos = []

    if query:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'type': 'video',
            'q': query,
            'key': settings.YOUTUBE_API_KEY,
            'maxResults': 5,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                if 'id' in item and 'videoId' in item['id']:
                    videos.append(item)

    streak = calculate_mood_streak(request.user)

    return render(request, 'youtube_search.html', {
        'query': query,
        'videos': videos,
        'mood_streak': streak,   # <-- add mood_streak here
    })



