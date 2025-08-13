from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserSession
from django.utils import timezone

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    session = UserSession.objects.create(user=user)

@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    try:
        session = UserSession.objects.filter(user=user, logout_time__isnull=True).latest('login_time')
        session.logout_time = timezone.now()
        session.save()
    except UserSession.DoesNotExist:
        pass
