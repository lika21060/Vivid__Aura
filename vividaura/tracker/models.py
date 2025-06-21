from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone 


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class MoodEntry(models.Model):
    MOOD_CHOICES = [
    ('😃 Happy', '😃 Happy'),
    ('😢 Sad', '😢 Sad'),
    ('😡 Angry', '😡 Angry'),
    ('😴 Tired', '😴 Tired'),
    ('😌 Relaxed', '😌 Relaxed'),
    ('😰 Anxious', '😰 Anxious'),
    ('🤩 Excited', '🤩 Excited'),
    ]

    ENERGY_CHOICES = [
        (i, i) for i in range(1, 11)  
    ]

    FOCUS_CHOICES = [
        (i, i) for i in range(1, 11) 
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mood_entries")
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    energy = models.IntegerField(choices=ENERGY_CHOICES, default=5)  
    focus = models.IntegerField(choices=FOCUS_CHOICES, default=5)   
    note = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.username}: {self.mood} - {self.date}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()  


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="journal_entries")
    content = models.TextField("Write about your day", null=True, blank=True) 
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    

class StudyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class Drawing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_base64 = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Drawing by {self.user.username} at {self.created_at}'