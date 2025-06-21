from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('study-goals/', views.study_goals, name='study_goals'),
    path('journal/', views.journal_page, name='journal'),
    path('mood-tracker/', views.mood_tracker, name='mood_tracker'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('drawing/', views.drawing, name='drawing'), 
    path('monthly-summary/', views.monthly_mood_summary, name='monthly_mood_summary'),
    path('youtube-search/', views.youtube_search, name='youtube_search'),  

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
