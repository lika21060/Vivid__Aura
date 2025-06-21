from django import forms
from .models import MoodEntry, JournalEntry, StudyGoal, Drawing
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class DrawingForm(forms.ModelForm):
    class Meta:
        model = Drawing
        fields = ['image_base64']  

class StudyGoalForm(forms.ModelForm):
    class Meta:
        model = StudyGoal
        fields = ['title', 'description', 'deadline'] 
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter goal title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add details (optional)',
                'rows': 3
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood', 'note', 'energy', 'focus']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Write about your day...',
                'rows': 10,
                'cols': 60
            }),
        }
